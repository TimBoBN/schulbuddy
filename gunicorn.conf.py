"""
Gunicorn WSGI Server Configuration für SchulBuddy
Production-ready WSGI server setup
"""
import multiprocessing
import os

# Server socket
bind = f"0.0.0.0:{os.environ.get('PORT', '5000')}"
backlog = 2048

# Worker processes - automatische Anpassung an Architektur
# Wenn GUNICORN_WORKERS vom entrypoint.sh gesetzt wurde (für ARM), verwende diesen Wert
workers = int(os.environ.get('GUNICORN_WORKERS', multiprocessing.cpu_count() + 1))  
worker_class = "sync"
worker_connections = 500  # Reduziert von 1000
timeout = 30
keepalive = 2

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 500  # Häufigere Restarts für RAM-Management
max_requests_jitter = 25

# Logging
loglevel = "info"
accesslog = "-"  # Log to stdout
errorlog = "-"   # Log to stderr
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = "schulbuddy"

# User and group (wenn als root gestartet)
user = "appuser"
group = "appuser"

# Preload app for better performance
preload_app = True

# Enable prometheus monitoring (optional)
# bind = ["0.0.0.0:5000", "0.0.0.0:8080"]

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Server mechanics
daemon = False
pidfile = "/tmp/gunicorn.pid"
tmp_upload_dir = None

# SSL (if needed)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"
