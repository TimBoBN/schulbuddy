# SchulBuddy Docker Makefile
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
