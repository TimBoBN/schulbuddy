# SchulBuddy Dockerfile - Multi-stage build für Multi-Architektur-Support
ARG PYTHON_VERSION=3.11
FROM --platform=$BUILDPLATFORM python:${PYTHON_VERSION}-slim as builder

# GitHub-spezifische Labels
LABEL org.opencontainers.image.source=https://github.com/TimBoBN/schulbuddy
LABEL org.opencontainers.image.description="SchulBuddy - Eine Anwendung zur Schulnotenerfassung und -verwaltung"
LABEL org.opencontainers.image.licenses=MIT

# Plattform-ARGs verfügbar machen
ARG BUILDPLATFORM
ARG TARGETPLATFORM

# Arbeitsverzeichnis setzen
WORKDIR /app

# System-Dependencies für den Builder installieren
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/*

# Requirements kopieren
COPY requirements.txt ./
COPY requirements-arm.txt ./

# Unterschiedliche Installation je nach Ziel-Architektur
RUN echo "Building for $TARGETPLATFORM on $BUILDPLATFORM" && \
    pip install --no-cache-dir --upgrade pip setuptools wheel && \
    if [ "$TARGETPLATFORM" = "linux/arm64" ] || [ "$TARGETPLATFORM" = "linux/arm/v7" ]; then \
        apt-get update && \
        apt-get install -y --no-install-recommends \
            libblas-dev \
            liblapack-dev \
            libatlas-base-dev \
            gfortran \
            && pip install --no-cache-dir -r requirements-arm.txt; \
    else \
        pip install --no-cache-dir -r requirements.txt; \
    fi

# Production Stage
FROM --platform=$TARGETPLATFORM python:${PYTHON_VERSION}-slim

# ARGs für Multi-Platform-Build
ARG TARGETPLATFORM

# Arbeitsverzeichnis setzen
WORKDIR /app

# System-Dependencies installieren
RUN apt-get update && apt-get install -y curl && \
    if [ "$TARGETPLATFORM" = "linux/arm64" ] || [ "$TARGETPLATFORM" = "linux/arm/v7" ]; then \
        apt-get install -y --no-install-recommends \
            libatlas-base-dev \
            libopenblas-base; \
    fi && \
    rm -rf /var/lib/apt/lists/*

# Python packages vom builder stage kopieren
COPY --from=builder /usr/local/lib/python${PYTHON_VERSION}/site-packages/ /usr/local/lib/python${PYTHON_VERSION}/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Stellen sicher, dass pip und setuptools auch in der finalen Phase aktualisiert sind
RUN pip install --no-cache-dir --upgrade pip setuptools

# App-Code kopieren
COPY . .

# Verzeichnisse erstellen
RUN mkdir -p static/uploads instance data && \
    chmod 755 static/uploads instance data

# Entrypoint script erstellen
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
echo "🚀 Starting SchulBuddy Container..."\n\
\n\
# Verzeichnisse erstellen und Berechtigungen setzen\n\
mkdir -p /app/data /app/static/uploads\n\
\n\
# Environment variables anzeigen\n\
echo "Environment: DOCKER_ENV=$DOCKER_ENV"\n\
echo "Database: $DATABASE_URL"\n\
echo "Port: $PORT"\n\
\n\
# Datenbank initialisieren falls nötig\n\
if [ ! -f "/app/data/schulbuddy.db" ]; then\n\
    echo "📋 Initializing database..."\n\
    python /app/init_db.py\n\
fi\n\
\n\
# App starten mit angepasster Worker-Anzahl je nach Architektur\n\
ARCH=$(uname -m)\n\
if [ "$ARCH" = "aarch64" ] || [ "$ARCH" = "armv7l" ]; then\n\
    # ARM-Architektur: weniger Worker\n\
    echo "🎓 Starting SchulBuddy with Gunicorn on ARM architecture (port $PORT)..."\n\
    export GUNICORN_WORKERS=2\n\
else\n\
    # Standard-Architektur\n\
    echo "🎓 Starting SchulBuddy with Gunicorn on port $PORT..."\n\
fi\n\
exec gunicorn --config gunicorn.conf.py wsgi:application\n\
' > entrypoint.sh && chmod +x entrypoint.sh

# Umgebungsvariablen setzen
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV DOCKER_ENV=1
ENV PYTHONPATH=/app

# Port freigeben
EXPOSE 5000

# Healthcheck hinzufügen
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Security hardening
# Setze Dateiberechtigungen und reduziere Angriffsfläche
RUN chmod -R 755 /app && \
    chmod 700 /app/entrypoint.sh && \
    # Read-only permissions für Code-Dateien
    find /app -type f -not -path "*/\.*" -not -path "*/data/*" -not -path "*/static/uploads/*" -exec chmod 644 {} \; && \
    # Entferne unnötige Tools und Dateien
    rm -rf /tmp/* /var/tmp/* /var/cache/* /var/log/* && \
    # Non-root user mit minimalen Berechtigungen erstellen
    adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app

# Setze niedrige Berechtigungen für den Container
USER appuser

# Definiere Volumes explizit als solche für bessere Transparenz
VOLUME ["/app/data", "/app/static/uploads"]

# Startkommando
CMD ["./entrypoint.sh"]
