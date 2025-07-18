# SchulBuddy Docker Makefile
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
