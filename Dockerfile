# SchulBuddy Dockerfile - Vereinfachter Build
# Feste Python-Version 3.11.7
FROM python:3.11.7-slim as builder

# Metadaten
LABEL org.opencontainers.image.source=https://github.com/TimBoBN/schulbuddy
LABEL org.opencontainers.image.description="SchulBuddy - Eine Anwendung zur Schulnotenerfassung und -verwaltung"
LABEL org.opencontainers.image.licenses=MIT

# Arbeitsverzeichnis setzen
WORKDIR /app

# Requirements kopieren
COPY requirements.txt ./

# Basis-Dependencies installieren
RUN apt-get update && \
    apt-get install -y gcc g++ make && \
    pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt && \
    rm -rf /var/lib/apt/lists/*

# Production Stage
FROM python:3.11.7-slim

# Arbeitsverzeichnis setzen
WORKDIR /app

# Basis-System-Dependencies installieren
RUN apt-get update && \
    apt-get install -y curl && \
    mkdir -p /usr/local/lib/python3.11/site-packages/ && \
    rm -rf /var/lib/apt/lists/*

# Python-Pakete aus Builder kopieren
COPY --from=builder /usr/local/ /usr/local/

# pip und setuptools aktualisieren
RUN pip install --no-cache-dir --upgrade pip setuptools

# App-Code kopieren
COPY . .

# Entrypoint Script aus Repository verwenden und executable machen
RUN chmod +x /app/entrypoint.sh

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

# Startkommando - verwende absoluten Pfad für bessere Kompatibilität
CMD ["/app/entrypoint.sh"]
