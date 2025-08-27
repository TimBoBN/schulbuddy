# SchulBuddy Multi-Platform Dockerfile
# Optimiert für AMD64, ARM64 und ARMv7
FROM python:3.11.7-slim as builder

# Metadaten
LABEL org.opencontainers.image.source=https://github.com/TimBoBN/schulbuddy
LABEL org.opencontainers.image.description="SchulBuddy Multi-Platform - Schulnotenerfassung und -verwaltung"
LABEL org.opencontainers.image.licenses=MIT

# Arbeitsverzeichnis setzen
WORKDIR /app

# Requirements kopieren (verwende ARM-optimierte Requirements für alle Architekturen)
COPY requirements-arm.txt requirements.txt ./

# Set non-interactive frontend to avoid prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies for cryptography and other packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    libssl-dev \
    libffi-dev \
    pkg-config \
    gcc g++ make \
    libatlas-base-dev \
    zlib1g-dev libjpeg-dev libpng-dev libtiff-dev \
    ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Upgrade pip tools first to ensure we get prebuilt wheels
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-arm.txt

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

# Entrypoint Script aus Repository verwenden und explizit executable machen
RUN chmod +x /app/entrypoint.sh && \
    ls -la /app/entrypoint.sh && \
    echo "Entrypoint permissions set successfully"

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
    && find /app -type f -not -path "*/\.*" -not -path "*/data/*" -not -path "*/static/uploads/*" -exec chmod 644 {} \; \
    && rm -rf /tmp/* /var/tmp/* /var/cache/* /var/log/* \
    && adduser --disabled-password --gecos '' appuser \
    && chown -R appuser:appuser /app \
    && chmod 755 /app/entrypoint.sh

# Volumes (definiere Volumes, aber starte Container als root)
VOLUME ["/app/data", "/app/static/uploads"]

# Container startet als root, entrypoint.sh wechselt zu appuser
CMD ["/app/entrypoint.sh"]
