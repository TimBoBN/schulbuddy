# SchulBuddy Dockerfile
FROM python:3.11-slim

# Arbeitsverzeichnis setzen
WORKDIR /app

# System-Dependencies installieren
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Python-Dependencies installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App-Code kopieren
COPY . .

# Uploads-Ordner erstellen und Berechtigungen setzen
RUN mkdir -p static/uploads && chmod 755 static/uploads

# Port für Flask
EXPOSE 5000

# Umgebungsvariablen
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Non-root user erstellen
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

# App starten
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]
