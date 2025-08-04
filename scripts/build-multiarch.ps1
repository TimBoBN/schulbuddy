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
  --cache-from=type=registry,ref=timbobn/schulbuddy:buildcache `
  --cache-to=type=registry,ref=timbobn/schulbuddy:buildcache,mode=max `
  .

Write-Host "✅ Done building multi-architecture images!"
