# SchulBuddy Docker PowerShell Script
param(
    [string]$Action = "help"
)

function Show-Help {
    Write-Host "SchulBuddy Docker Commands:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  setup     - Erstelle .env Datei aus Vorlage" -ForegroundColor Green
    Write-Host "  build     - Docker Images bauen" -ForegroundColor Green
    Write-Host "  up        - Starte SchulBuddy (Produktion)" -ForegroundColor Green
    Write-Host "  down      - Stoppe alle Container" -ForegroundColor Green
    Write-Host "  dev       - Starte Development-Umgebung" -ForegroundColor Green
    Write-Host "  nginx     - Starte mit Nginx Reverse Proxy" -ForegroundColor Green
    Write-Host "  logs      - Zeige Logs" -ForegroundColor Green
    Write-Host "  shell     - Öffne Shell im Container" -ForegroundColor Green
    Write-Host "  health    - Prüfe Anwendungsstatus" -ForegroundColor Green
    Write-Host "  status    - Zeige Container-Status" -ForegroundColor Green
    Write-Host "  restart   - Starte Container neu" -ForegroundColor Green
    Write-Host "  backup    - Erstelle Backup" -ForegroundColor Green
    Write-Host "  clean     - Entferne Container und Images" -ForegroundColor Green
    Write-Host ""
    Write-Host "Verwendung: .\start.ps1 <command>" -ForegroundColor Yellow
}

switch ($Action.ToLower()) {
    "setup" {
        if (-not (Test-Path ".env")) {
            Copy-Item ".env.example" ".env"
            Write-Host "✅ .env Datei erstellt. Bitte anpassen!" -ForegroundColor Green
        } else {
            Write-Host "⚠️ .env Datei existiert bereits" -ForegroundColor Yellow
        }
    }
    "build" {
        docker-compose build
    }
    "up" {
        docker-compose up -d
        Write-Host "🚀 SchulBuddy gestartet: http://localhost:5000" -ForegroundColor Green
    }
    "down" {
        docker-compose down
    }
    "dev" {
        docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
    }
    "nginx" {
        docker-compose --profile with-nginx up -d
        Write-Host "🚀 SchulBuddy mit Nginx gestartet: http://localhost" -ForegroundColor Green
    }
    "logs" {
        docker-compose logs -f
    }
    "shell" {
        docker-compose exec schulbuddy bash
    }
    "health" {
        try {
            $response = Invoke-RestMethod -Uri "http://localhost:5000/health"
            Write-Host "✅ Health-Check erfolgreich:" -ForegroundColor Green
            Write-Host ($response | ConvertTo-Json)
        } catch {
            Write-Host "❌ Health-Check fehlgeschlagen" -ForegroundColor Red
        }
    }
    "status" {
        docker-compose ps
    }
    "restart" {
        docker-compose restart
    }
    "backup" {
        $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
        if (-not (Test-Path "backups")) {
            New-Item -ItemType Directory -Path "backups"
        }
        
        # Datenbank-Backup
        docker-compose exec schulbuddy cp /app/instance/schulbuddy.db "/app/instance/backup_$timestamp.db"
        $containerId = docker-compose ps -q schulbuddy
        docker cp "${containerId}:/app/instance/backup_$timestamp.db" "./backups/"
        
        # Uploads-Backup
        Compress-Archive -Path "static\uploads" -DestinationPath "backups\uploads_$timestamp.zip"
        
        Write-Host "✅ Backup erstellt: backups/backup_$timestamp.db und backups/uploads_$timestamp.zip" -ForegroundColor Green
    }
    "clean" {
        docker-compose down -v
        docker system prune -f
    }
    default {
        Show-Help
    }
}
