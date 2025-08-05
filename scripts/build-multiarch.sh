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

# Emulation für fremde Architekturen sicherstellen
echo "🧩 Setting up QEMU for cross-platform emulation..."
docker run --privileged --rm tonistiigi/binfmt --install all

# Build mit verbessertem Caching und BuildKit-Optionen
echo "🔄 Building multi-architecture images for $PLATFORMS..."
docker buildx build \
  --platform=$PLATFORMS \
  --tag "timbobn/schulbuddy:$TAG" \
  --tag "ghcr.io/timbobn/schulbuddy:$TAG" \
  --progress=plain \
  --push \
  --build-arg BUILDKIT_INLINE_CACHE=1 \
  --build-arg PYTHON_VERSION=3.11 \
  --cache-from=type=registry,ref=timbobn/schulbuddy:buildcache \
  --cache-to=type=registry,ref=timbobn/schulbuddy:buildcache,mode=max \
  .

# Erfolgreicher Build oder Fehlerfall
if [ $? -eq 0 ]; then
  echo "✅ Done building multi-architecture images!"
else
  echo "❌ Build failed. Trying to clear cache and build again..."
  docker buildx prune -f
  
  echo "🔄 Rebuilding after cache purge..."
  docker buildx build \
    --platform=$PLATFORMS \
    --tag "timbobn/schulbuddy:$TAG" \
    --tag "ghcr.io/timbobn/schulbuddy:$TAG" \
    --progress=plain \
    --push \
    --build-arg BUILDKIT_INLINE_CACHE=1 \
    --build-arg PYTHON_VERSION=3.11 \
    --no-cache \
    .
    
  if [ $? -eq 0 ]; then
    echo "✅ Build successful after cache purge!"
  else
    echo "❌ Build failed even after cache purge. Please check the errors above."
    exit 1
  fi
fi
