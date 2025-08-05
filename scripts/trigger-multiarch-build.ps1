# Multi-Architecture Build Trigger Script (PowerShell)
Write-Host "🚀 Triggering Multi-Architecture Build für SchulBuddy" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

# Check if we're in a git repository
try {
    $gitDir = git rev-parse --git-dir 2>$null
    if (!$gitDir) { throw }
} catch {
    Write-Host "❌ Fehler: Nicht in einem Git-Repository" -ForegroundColor Red
    exit 1
}

Write-Host "📋 Repository Status:" -ForegroundColor Yellow
$currentBranch = git branch --show-current
$currentCommit = git rev-parse --short HEAD
$remoteUrl = git remote get-url origin

Write-Host "Branch: $currentBranch" -ForegroundColor White
Write-Host "Commit: $currentCommit" -ForegroundColor White  
Write-Host "Remote: $remoteUrl" -ForegroundColor White

Write-Host ""
Write-Host "🔨 Triggering Workflows..." -ForegroundColor Green

# Push aktueller Branch um Workflows zu triggern
Write-Host "⬆️  Pushing current branch to trigger workflows..." -ForegroundColor Green
git push origin $currentBranch

Write-Host ""
Write-Host "✅ Workflows getriggert!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Du kannst den Fortschritt hier verfolgen:" -ForegroundColor Cyan
Write-Host "https://github.com/TimBoBN/schulbuddy/actions" -ForegroundColor Blue
Write-Host ""
Write-Host "🎯 Nach erfolgreichem Build werden folgende Images verfügbar sein:" -ForegroundColor Yellow
Write-Host "• docker.io/timbobn/schulbuddy:latest (Multi-Arch)" -ForegroundColor White
Write-Host "• docker.io/timbobn/schulbuddy:dev (Multi-Arch)" -ForegroundColor White
Write-Host "• ghcr.io/timbobn/schulbuddy:latest (Multi-Arch)" -ForegroundColor White
Write-Host "• ghcr.io/timbobn/schulbuddy:dev (Multi-Arch)" -ForegroundColor White
Write-Host ""
Write-Host "🐳 Test Multi-Arch Images:" -ForegroundColor Magenta
Write-Host "docker manifest inspect docker.io/timbobn/schulbuddy:latest" -ForegroundColor Gray
Write-Host "docker pull docker.io/timbobn/schulbuddy:latest" -ForegroundColor Gray
