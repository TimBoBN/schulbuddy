# Multi-Platform Build Trigger Script (PowerShell)
param(
    [string]$Version = "latest",
    [switch]$Help
)

if ($Help) {
    Write-Host "🚀 SchulBuddy Multi-Platform Build Trigger" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage:" -ForegroundColor Yellow
    Write-Host "  .\scripts\trigger-multiplatform.ps1 [-Version <version>] [-Help]" -ForegroundColor White
    Write-Host ""
    Write-Host "Parameter:" -ForegroundColor Yellow
    Write-Host "  -Version    Version Tag für das Multi-Platform Image (Standard: latest)" -ForegroundColor White
    Write-Host "  -Help       Zeigt diese Hilfe an" -ForegroundColor White
    Write-Host ""
    Write-Host "Beispiele:" -ForegroundColor Yellow
    Write-Host "  .\scripts\trigger-multiplatform.ps1" -ForegroundColor Gray
    Write-Host "  .\scripts\trigger-multiplatform.ps1 -Version dev" -ForegroundColor Gray
    Write-Host "  .\scripts\trigger-multiplatform.ps1 -Version v1.2.0" -ForegroundColor Gray
    exit 0
}

Write-Host "🚀 SchulBuddy Multi-Platform Build Trigger" -ForegroundColor Cyan
Write-Host "===========================================" -ForegroundColor Cyan
Write-Host "Version: $Version" -ForegroundColor Yellow

# Check if we're in a git repository
try {
    $gitDir = git rev-parse --git-dir 2>$null
    if (!$gitDir) { throw }
} catch {
    Write-Host "❌ Fehler: Nicht in einem Git-Repository" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "📋 Repository Status:" -ForegroundColor Yellow
$currentBranch = git branch --show-current
$currentCommit = git rev-parse --short HEAD
$remoteUrl = git remote get-url origin

Write-Host "Branch: $currentBranch" -ForegroundColor White
Write-Host "Commit: $currentCommit" -ForegroundColor White  
Write-Host "Remote: $remoteUrl" -ForegroundColor White

Write-Host ""
Write-Host "🔨 Triggering Multi-Platform Workflow..." -ForegroundColor Green

# GitHub CLI verwenden falls verfügbar
if (Get-Command gh -ErrorAction SilentlyContinue) {
    Write-Host "📡 Triggering via GitHub CLI..." -ForegroundColor Green
    try {
        gh workflow run "Multi-Platform Docker Build" --field version_tag=$Version
        Write-Host "✅ Workflow erfolgreich getriggert!" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  GitHub CLI Trigger fehlgeschlagen, verwende Git Push..." -ForegroundColor Yellow
        git push origin $currentBranch
    }
} else {
    Write-Host "⬆️  GitHub CLI nicht verfügbar, verwende Git Push..." -ForegroundColor Yellow
    git push origin $currentBranch
}

Write-Host ""
Write-Host "✅ Multi-Platform Build getriggert!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Du kannst den Fortschritt hier verfolgen:" -ForegroundColor Cyan
Write-Host "https://github.com/TimBoBN/schulbuddy/actions/workflows/docker-multiplatform.yml" -ForegroundColor Blue
Write-Host ""
Write-Host "🎯 Nach erfolgreichem Build werden folgende Images verfügbar sein:" -ForegroundColor Yellow

if ($currentBranch -eq "main" -or $Version -eq "latest") {
    Write-Host "• docker.io/timbobn/schulbuddy:latest-multiplatform" -ForegroundColor White
    Write-Host "• ghcr.io/timbobn/schulbuddy:latest-multiplatform" -ForegroundColor White
}

if ($currentBranch -eq "dev") {
    Write-Host "• docker.io/timbobn/schulbuddy:dev-multiplatform" -ForegroundColor White
    Write-Host "• ghcr.io/timbobn/schulbuddy:dev-multiplatform" -ForegroundColor White
}

Write-Host "• docker.io/timbobn/schulbuddy:$Version-multiplatform" -ForegroundColor White
Write-Host "• ghcr.io/timbobn/schulbuddy:$Version-multiplatform" -ForegroundColor White

Write-Host ""
Write-Host "🐳 Test Multi-Platform Images:" -ForegroundColor Magenta
Write-Host "docker manifest inspect docker.io/timbobn/schulbuddy:$Version-multiplatform" -ForegroundColor Gray
Write-Host "docker pull docker.io/timbobn/schulbuddy:$Version-multiplatform" -ForegroundColor Gray
Write-Host ""
Write-Host "🚀 Für Raspberry Pi:" -ForegroundColor Green
Write-Host "cp config/.env.multiplatform .env" -ForegroundColor Gray
Write-Host "docker-compose -f docker-compose.multiplatform.yml up -d" -ForegroundColor Gray
