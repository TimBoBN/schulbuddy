# Multi-stage build
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

# Python packages von builder stage kopieren
COPY --from=builder /root/.local /usr/local

# App-Code kopieren
COPY . .

# Verzeichnisse erstellen
RUN mkdir -p static/uploads instance data

# Entrypoint script ausführbar machen
RUN chmod +x scripts/entrypoint.sh

# Umgebungsvariablen setzen
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV DOCKER_ENV=1
ENV PYTHONPATH=/app

# Port freigeben
EXPOSE 5000

# Startkommando
CMD ["./scripts/entrypoint.sh"]
