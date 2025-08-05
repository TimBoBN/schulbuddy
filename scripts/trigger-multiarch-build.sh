#!/bin/bash

# Multi-Architecture Build Trigger Script
echo "🚀 Triggering Multi-Architecture Build für SchulBuddy"
echo "=================================================="

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ Fehler: Nicht in einem Git-Repository"
    exit 1
fi

echo "📋 Repository Status:"
echo "Branch: $(git branch --show-current)"
echo "Commit: $(git rev-parse --short HEAD)"
echo "Remote: $(git remote get-url origin)"

echo ""
echo "🔨 Triggering Workflows..."

# Push aktueller Branch um Workflows zu triggern
echo "⬆️  Pushing current branch to trigger workflows..."
git push origin "$(git branch --show-current)"

echo ""
echo "✅ Workflows getriggert!"
echo ""
echo "📊 Du kannst den Fortschritt hier verfolgen:"
echo "https://github.com/TimBoBN/schulbuddy/actions"
echo ""
echo "🎯 Nach erfolgreichem Build werden folgende Images verfügbar sein:"
echo "• docker.io/timbobn/schulbuddy:latest (Multi-Arch)"
echo "• docker.io/timbobn/schulbuddy:dev (Multi-Arch)" 
echo "• ghcr.io/timbobn/schulbuddy:latest (Multi-Arch)"
echo "• ghcr.io/timbobn/schulbuddy:dev (Multi-Arch)"
echo ""
echo "🐳 Test Multi-Arch Images:"
echo "docker manifest inspect docker.io/timbobn/schulbuddy:latest"
echo "docker pull docker.io/timbobn/schulbuddy:latest"
