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

# Entrypoint script ausführbar machen
RUN chmod +x scripts/entrypoint.sh

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
CMD ["./scripts/entrypoint.sh"]
