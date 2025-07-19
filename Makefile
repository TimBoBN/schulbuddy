# SchulBuddy Docker Makefile
<<<<<<< HEAD
.PHONY: help setup build start stop restart logs clean install update

# Standard-Ziel
.DEFAULT_GOAL := help

# Konfiguration
PORT ?= 5000
EXTERNAL_PORT ?= $(PORT)

help: ## Zeige diese Hilfe
	@echo "🚀 SchulBuddy Docker Commands:"
	@echo ""
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup: ## Erstelle .env-Datei (interaktiv)
	@echo "🔧 Setup wird gestartet..."
	@if [ -f scripts/setup-env.sh ]; then bash scripts/setup-env.sh; else echo "❌ scripts/setup-env.sh nicht gefunden!"; fi

build: ## Baue Docker Images
	@echo "🔨 Baue Docker Images..."
	docker-compose build --no-cache

start: ## Starte Services
	@echo "🚀 Starte SchulBuddy..."
	PORT=$(PORT) EXTERNAL_PORT=$(EXTERNAL_PORT) docker-compose up -d

stop: ## Stoppe Services  
	@echo "🛑 Stoppe SchulBuddy..."
	docker-compose down

restart: stop start ## Neustart der Services

logs: ## Zeige Logs
	@echo "📋 Zeige Logs..."
	docker-compose logs -f schulbuddy

status: ## Zeige Service-Status
	@echo "📊 Service-Status:"
	docker-compose ps

clean: ## Lösche Container, Images und Volumes
	@echo "🧹 Räume auf..."
	docker-compose down -v --rmi all

install: setup build start ## Vollständige Installation

update: ## Update auf neueste Version
	@echo "🔄 Update wird durchgeführt..."
	git pull
	$(MAKE) build
	$(MAKE) restart

# Port-spezifische Ziele
start-dev: ## Starte auf Port 3000 (Development)
	PORT=3000 EXTERNAL_PORT=3000 docker-compose up -d

start-prod: ## Starte auf Port 80 (Production)
	PORT=80 EXTERNAL_PORT=80 docker-compose up -d

# Entwickler-Tools
shell: ## Öffne Shell im Container
	docker-compose exec schulbuddy bash

db-backup: ## Erstelle Datenbank-Backup
	@echo "💾 Erstelle Datenbank-Backup..."
	docker-compose exec schulbuddy cp /app/data/schulbuddy.db /app/data/schulbuddy_backup_$(shell date +%Y%m%d_%H%M%S).db

db-restore: ## Stelle Datenbank wieder her (DB_FILE=backup.db)
	@if [ -z "$(DB_FILE)" ]; then echo "❌ Bitte DB_FILE angeben: make db-restore DB_FILE=backup.db"; exit 1; fi
	docker-compose exec schulbuddy cp /app/data/$(DB_FILE) /app/data/schulbuddy.db
	$(MAKE) restart

# Monitoring
health: ## Prüfe Gesundheit der Services
	@echo "🏥 Health Check..."
	curl -f http://localhost:$(EXTERNAL_PORT)/health || echo "❌ Service nicht erreichbar"

test-port: ## Teste Port-Konfiguration
	@echo "🔍 Teste Port $(EXTERNAL_PORT)..."
	curl -I http://localhost:$(EXTERNAL_PORT) || echo "❌ Port $(EXTERNAL_PORT) nicht erreichbar"
=======
.PHONY: help build up down logs shell clean backup dev prod

help: ## Zeige verfügbare Kommandos
	@echo "SchulBuddy Docker Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

setup: ## Erstelle .env Datei aus Vorlage
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "✅ .env Datei erstellt. Bitte anpassen!"; \
	else \
		echo "⚠️  .env Datei existiert bereits"; \
	fi

build: ## Docker Images bauen
	docker-compose build

up: ## Starte SchulBuddy (Produktion)
	docker-compose up -d

down: ## Stoppe alle Container
	docker-compose down

dev: ## Starte Development-Umgebung
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

dev-build: ## Baue und starte Development-Umgebung
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build

nginx: ## Starte mit Nginx Reverse Proxy
	docker-compose --profile with-nginx up -d

logs: ## Zeige Logs
	docker-compose logs -f

logs-app: ## Zeige nur App-Logs
	docker-compose logs -f schulbuddy

shell: ## Öffne Shell im Container
	docker-compose exec schulbuddy bash

health: ## Prüfe Anwendungsstatus
	@curl -s http://localhost:5000/health | python -m json.tool || echo "❌ Health-Check fehlgeschlagen"

status: ## Zeige Container-Status
	docker-compose ps

restart: ## Starte Container neu
	docker-compose restart

update: ## Update der Anwendung
	git pull
	docker-compose down
	docker-compose build --no-cache
	docker-compose up -d

backup: ## Erstelle Backup
	@mkdir -p backups
	@timestamp=$$(date +%Y%m%d_%H%M%S); \
	docker-compose exec schulbuddy cp /app/instance/schulbuddy.db /app/instance/backup_$$timestamp.db && \
	docker cp $$(docker-compose ps -q schulbuddy):/app/instance/backup_$$timestamp.db ./backups/ && \
	tar -czf backups/uploads_$$timestamp.tar.gz static/uploads/ && \
	echo "✅ Backup erstellt: backups/backup_$$timestamp.db und backups/uploads_$$timestamp.tar.gz"

clean: ## Entferne alle Container und Images
	docker-compose down -v
	docker system prune -f

clean-all: ## Entferne alles (VORSICHT!)
	docker-compose down -v --rmi all
	docker system prune -a -f

reset-db: ## Setze Datenbank zurück (VORSICHT!)
	@read -p "Alle Daten gehen verloren! Fortfahren? (y/N): " confirm && [ $$confirm = y ]
	docker-compose down
	rm -rf instance/
	docker-compose up -d
	@echo "✅ Datenbank zurückgesetzt"
>>>>>>> 04627b963babc5ecf9f1ddb34bf0f7bd3421bfff
