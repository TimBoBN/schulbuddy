# SchulBuddy Dockerfile - Multi-stage build für Multi-Architektur-Support
# Feste Python-Version 3.11.7
FROM --platform=$BUILDPLATFORM python:3.11.7-slim as builder

# Plattform-ARGs verfügbar machen
ARG BUILDPLATFORM
ARG TARGETPLATFORM

# Metadaten
LABEL org.opencontainers.image.source=https://github.com/TimBoBN/schulbuddy
LABEL org.opencontainers.image.description="SchulBuddy - Eine Anwendung zur Schulnotenerfassung und -verwaltung"
LABEL org.opencontainers.image.licenses=MIT

# Arbeitsverzeichnis setzen
WORKDIR /app

# Requirements kopieren
COPY requirements.txt requirements-arm.txt ./

# Basis-Dependencies für alle Architekturen
RUN apt-get update && \
    apt-get install -y gcc g++ make && \
    pip install --no-cache-dir --upgrade pip setuptools wheel

# AMD64 Build
RUN if [ "$TARGETPLATFORM" = "linux/amd64" ]; then \
    pip install --no-cache-dir -r requirements.txt; \
    fi

# ARM64 Build
RUN if [ "$TARGETPLATFORM" = "linux/arm64" ]; then \
    apt-get install -y libblas-dev liblapack-dev libatlas-base-dev gfortran && \
    pip install --no-cache-dir -r requirements-arm.txt; \
    fi

# ARMv7 Build
RUN if [ "$TARGETPLATFORM" = "linux/arm/v7" ]; then \
    apt-get install -y libblas-dev liblapack-dev libatlas-base-dev gfortran && \
    pip install --no-cache-dir -r requirements-arm.txt; \
    fi

# Aufräumen
RUN rm -rf /var/lib/apt/lists/*

# Production Stage
FROM --platform=$TARGETPLATFORM python:3.11.7-slim

# ARGs für Multi-Platform-Build
ARG TARGETPLATFORM

# Arbeitsverzeichnis setzen
WORKDIR /app

# Basis-System-Dependencies für alle Architekturen
RUN apt-get update && apt-get install -y curl && \
    mkdir -p /usr/local/lib/python3.11/site-packages/

# AMD64-spezifische Pakete
RUN if [ "$TARGETPLATFORM" = "linux/amd64" ]; then \
    echo "AMD64 build - no special dependencies needed"; \
    fi

# ARM64-spezifische Pakete
RUN if [ "$TARGETPLATFORM" = "linux/arm64" ]; then \
    apt-get install -y libatlas-base-dev libopenblas-base; \
    fi

# ARMv7-spezifische Pakete
RUN if [ "$TARGETPLATFORM" = "linux/arm/v7" ]; then \
    apt-get install -y libatlas-base-dev libopenblas-base; \
    fi

# Aufräumen für alle Architekturen
RUN rm -rf /var/lib/apt/lists/*

# Python-Pakete aus Builder kopieren
COPY --from=builder /usr/local/ /usr/local/

# pip und setuptools aktualisieren
RUN pip install --no-cache-dir --upgrade pip setuptools

# App-Code kopieren
COPY . .

# Entrypoint script erstellen
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
echo "🚀 Starting SchulBuddy Container..."\n\
\n\
# Verzeichnisse erstellen\n\
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

# Umgebungsvariablen und Port
ENV FLASK_APP=app.py \
    FLASK_ENV=production \
    DOCKER_ENV=1 \
    PYTHONPATH=/app

EXPOSE 5000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Security hardening und Berechtigungen
RUN mkdir -p static/uploads instance data \
    && chmod -R 755 /app static/uploads instance data \
    && chmod 700 /app/entrypoint.sh \
    && find /app -type f -not -path "*/\.*" -not -path "*/data/*" -not -path "*/static/uploads/*" -exec chmod 644 {} \; \
    && rm -rf /tmp/* /var/tmp/* /var/cache/* /var/log/* \
    && adduser --disabled-password --gecos '' appuser \
    && chown -R appuser:appuser /app

# Non-root user
USER appuser

# Volumes
VOLUME ["/app/data", "/app/static/uploads"]

# Startkommando
CMD ["./entrypoint.sh"]
