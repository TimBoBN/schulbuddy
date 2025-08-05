#!/bin/bash

# Multi-Platform Build Trigger Script
VERSION=${1:-"latest"}

if [[ "$1" == "--help" || "$1" == "-h" ]]; then
    echo "🚀 SchulBuddy Multi-Platform Build Trigger"
    echo "=========================================="
    echo ""
    echo "Usage:"
    echo "  ./scripts/trigger-multiplatform.sh [version] [--help]"
    echo ""
    echo "Parameter:"
    echo "  version     Version Tag für das Multi-Platform Image (Standard: latest)"
    echo "  --help      Zeigt diese Hilfe an"
    echo ""
    echo "Beispiele:"
    echo "  ./scripts/trigger-multiplatform.sh"
    echo "  ./scripts/trigger-multiplatform.sh dev"
    echo "  ./scripts/trigger-multiplatform.sh v1.2.0"
    exit 0
fi

echo "🚀 SchulBuddy Multi-Platform Build Trigger"
echo "==========================================="
echo "Version: $VERSION"

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ Fehler: Nicht in einem Git-Repository"
    exit 1
fi

echo ""
echo "📋 Repository Status:"
CURRENT_BRANCH=$(git branch --show-current)
CURRENT_COMMIT=$(git rev-parse --short HEAD)
REMOTE_URL=$(git remote get-url origin)

echo "Branch: $CURRENT_BRANCH"
echo "Commit: $CURRENT_COMMIT"
echo "Remote: $REMOTE_URL"

echo ""
echo "🔨 Triggering Multi-Platform Workflow..."

# GitHub CLI verwenden falls verfügbar
if command -v gh &> /dev/null; then
    echo "📡 Triggering via GitHub CLI..."
    if gh workflow run "Multi-Platform Docker Build" --field version_tag="$VERSION"; then
        echo "✅ Workflow erfolgreich getriggert!"
    else
        echo "⚠️  GitHub CLI Trigger fehlgeschlagen, verwende Git Push..."
        git push origin "$CURRENT_BRANCH"
    fi
else
    echo "⬆️  GitHub CLI nicht verfügbar, verwende Git Push..."
    git push origin "$CURRENT_BRANCH"
fi

echo ""
echo "✅ Multi-Platform Build getriggert!"
echo ""
echo "📊 Du kannst den Fortschritt hier verfolgen:"
echo "https://github.com/TimBoBN/schulbuddy/actions/workflows/docker-multiplatform.yml"
echo ""
echo "🎯 Nach erfolgreichem Build werden folgende Images verfügbar sein:"

if [[ "$CURRENT_BRANCH" == "main" || "$VERSION" == "latest" ]]; then
    echo "• docker.io/timbobn/schulbuddy:latest-multiplatform"
    echo "• ghcr.io/timbobn/schulbuddy:latest-multiplatform"
fi

if [[ "$CURRENT_BRANCH" == "dev" ]]; then
    echo "• docker.io/timbobn/schulbuddy:dev-multiplatform"
    echo "• ghcr.io/timbobn/schulbuddy:dev-multiplatform"
fi

echo "• docker.io/timbobn/schulbuddy:$VERSION-multiplatform"
echo "• ghcr.io/timbobn/schulbuddy:$VERSION-multiplatform"

echo ""
echo "🐳 Test Multi-Platform Images:"
echo "docker manifest inspect docker.io/timbobn/schulbuddy:$VERSION-multiplatform"
echo "docker pull docker.io/timbobn/schulbuddy:$VERSION-multiplatform"
echo ""
echo "🚀 Für Raspberry Pi:"
echo "cp config/.env.multiplatform .env"
echo "docker-compose -f docker-compose.multiplatform.yml up -d"
