# SchulBuddy Dockerfile - Multi-stage build für optimale Performance
FROM python:3.11-slim as builder

# Arbeitsverzeichnis setzen
WORKDIR /app

# Requirements kopieren und installieren
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Production Stage
FROM python:3.11-slim

# Arbeitsverzeichnis setzen
WORKDIR /app

# System-Dependencies installieren (für eventuelle native Extensions)
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python packages von builder stage kopieren
COPY --from=builder /root/.local /usr/local

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
# App starten\n\
echo "🎓 Starting SchulBuddy with Gunicorn on port $PORT..."\n\
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

# Non-root user erstellen (wichtig für Sicherheit)
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

# Startkommando
CMD ["./entrypoint.sh"]
