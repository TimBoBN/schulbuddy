#!/bin/bash
# Script zum lokalen Bauen von Multi-Architektur Docker Images

# Plattformen, für die gebaut werden soll
PLATFORMS="linux/amd64,linux/arm64,linux/arm/v7"

# Docker Buildx aktivieren und sicherstellen, dass ein Builder existiert
echo "🔧 Setting up Docker Buildx..."
docker buildx create --name multiarch-builder --use || true
docker buildx inspect multiarch-builder --bootstrap

# Image Tag aus Git oder Parameter übernehmen
if [ -z "$1" ]; then
  TAG="dev"
else
  TAG="$1"
fi

echo "🏷️ Using tag: $TAG"

# Lokale Image-Registry für Tests (optional)
echo "🔄 Building multi-architecture images for $PLATFORMS..."
docker buildx build \
  --platform=$PLATFORMS \
  --tag "timbobn/schulbuddy:$TAG" \
  --tag "ghcr.io/timbobn/schulbuddy:$TAG" \
  --progress=plain \
  --load \
  .

echo "✅ Done building multi-architecture images!"
