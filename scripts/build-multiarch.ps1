# PowerShell-Script zum lokalen Bauen von Multi-Architektur Docker Images

# Plattformen, für die gebaut werden soll
$PLATFORMS = "linux/amd64,linux/arm64,linux/arm/v7"

# Docker Buildx aktivieren und sicherstellen, dass ein Builder existiert
Write-Host "🔧 Setting up Docker Buildx..."
docker buildx create --name multiarch-builder --use 
docker buildx inspect multiarch-builder --bootstrap

# Image Tag aus Git oder Parameter übernehmen
if (-not $args[0]) {
  $TAG = "dev"
} else {
  $TAG = $args[0]
}

Write-Host "🏷️ Using tag: $TAG"

# Docker Desktop enthält bereits QEMU für cross-platform emulation
Write-Host "🔄 Building multi-architecture images for $PLATFORMS..."
docker buildx build `
  --platform=$PLATFORMS `
  --tag "timbobn/schulbuddy:$TAG" `
  --tag "ghcr.io/timbobn/schulbuddy:$TAG" `
  --progress=plain `
  --push `
  --build-arg BUILDKIT_INLINE_CACHE=1 `
  --build-arg PYTHON_VERSION=3.11 `
  --cache-from=type=registry,ref=timbobn/schulbuddy:buildcache `
  --cache-to=type=registry,ref=timbobn/schulbuddy:buildcache,mode=max `
  .

# Erfolgreicher Build oder Fehlerfall
if ($LASTEXITCODE -eq 0) {
  Write-Host "✅ Done building multi-architecture images!"
} else {
  Write-Host "❌ Build failed. Trying to clear cache and build again..."
  docker buildx prune -f
  
  Write-Host "🔄 Rebuilding after cache purge..."
  docker buildx build `
    --platform=$PLATFORMS `
    --tag "timbobn/schulbuddy:$TAG" `
    --tag "ghcr.io/timbobn/schulbuddy:$TAG" `
    --progress=plain `
    --push `
    --build-arg BUILDKIT_INLINE_CACHE=1 `
    --build-arg PYTHON_VERSION=3.11 `
    --no-cache `
    .
    
  if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Build successful after cache purge!"
  } else {
    Write-Host "❌ Build failed even after cache purge. Please check the errors above."
    exit 1
  }
}
