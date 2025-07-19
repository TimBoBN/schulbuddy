# SchulBuddy Docker Setup Script (Windows PowerShell)
Write-Host "SchulBuddy Docker Setup wird gestartet..." -ForegroundColor Green

# Wechsle zum Projekt-Hauptverzeichnis (parent directory)
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectDir = Split-Path -Parent $scriptDir
Set-Location $projectDir

# Prüfe ob .env existiert
if (Test-Path ".env") {
    Write-Host ".env-Datei existiert bereits!" -ForegroundColor Yellow
    $overwrite = Read-Host "Möchten Sie sie überschreiben? (y/N)"
    if ($overwrite -ne "y" -and $overwrite -ne "Y") {
        Write-Host "Setup abgebrochen. Bestehende .env-Datei beibehalten." -ForegroundColor Green
        exit 0
    }
}

# Erstelle .env von Template
if (Test-Path "config\.env.template") {
    Write-Host "Erstelle .env-Datei von config\.env.template..." -ForegroundColor Cyan
    Copy-Item "config\.env.template" ".env"
    Write-Host ".env-Datei erfolgreich erstellt!" -ForegroundColor Green
} elseif (Test-Path "config\.env.example") {
    Write-Host "Erstelle .env-Datei von config\.env.example..." -ForegroundColor Cyan
    Copy-Item "config\.env.example" ".env"
    Write-Host ".env-Datei erfolgreich erstellt!" -ForegroundColor Green
} else {
    Write-Host "Keine Vorlage gefunden! config\.env.template oder config\.env.example fehlt." -ForegroundColor Red
    exit 1
}

# Frage nach Port-Konfiguration
Write-Host ""
Write-Host "Port-Konfiguration:" -ForegroundColor Yellow
$port = Read-Host "Welchen Port moechten Sie verwenden? (Standard 5000)"
if ([string]::IsNullOrEmpty($port)) {
    $port = "5000"
}

# Update .env mit gewähltem Port
$envContent = Get-Content ".env"
$envContent = $envContent -replace "PORT=5000", "PORT=$port"
$envContent = $envContent -replace "EXTERNAL_PORT=5000", "EXTERNAL_PORT=$port"
$envContent | Set-Content ".env"

Write-Host "Port auf $port gesetzt!" -ForegroundColor Green

# Frage nach Secret Key
Write-Host ""
Write-Host "Sicherheit:" -ForegroundColor Yellow
$generateSecret = Read-Host "Moechten Sie einen neuen SECRET_KEY generieren? (Y/n)"
if ($generateSecret -ne "n" -and $generateSecret -ne "N") {
    # Generiere neuen Secret Key
    $bytes = New-Object byte[] 32
    $rng = [System.Security.Cryptography.RNGCryptoServiceProvider]::new()
    $rng.GetBytes($bytes)
    $newSecret = [System.Convert]::ToBase64String($bytes)
    
    $envContent = Get-Content ".env"
    $envContent = $envContent -replace "SECRET_KEY=.*", "SECRET_KEY=$newSecret"
    $envContent | Set-Content ".env"
    
    Write-Host "Neuer SECRET_KEY generiert!" -ForegroundColor Green
}

Write-Host ""
Write-Host "Setup abgeschlossen!" -ForegroundColor Green
Write-Host ""
Write-Host "Naechste Schritte:" -ForegroundColor Cyan
Write-Host "   1. Pruefen Sie die .env-Datei: notepad .env"
Write-Host "   2. Starten Sie die Anwendung: docker-compose up -d"
Write-Host "   3. Oeffnen Sie: http://localhost:$port"
Write-Host ""
Write-Host "Weitere Hilfe: Get-Content docs\PORT_CONFIG.md" -ForegroundColor Blue
