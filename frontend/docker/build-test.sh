#!/bin/bash
# Script para testar o build do Docker com todas as variáveis de ambiente
# Usage: ./docker/build-test.sh

set -e

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Weni Roadmap Frontend - Docker Build Test ===${NC}"
echo ""

# Carregar variáveis do .env se existir
if [ -f .env ]; then
    echo -e "${YELLOW}Loading variables from .env file...${NC}"
    export $(grep -v '^#' .env | xargs)
else
    echo -e "${YELLOW}No .env file found, using defaults${NC}"
fi

# Valores padrão se não estiverem definidos
VITE_API_URL="${VITE_API_URL:-/api/v1}"
VITE_WEBCHAT_SOCKET_URL="${VITE_WEBCHAT_SOCKET_URL:-https://websocket.weni.ai}"
VITE_WEBCHAT_HOST="${VITE_WEBCHAT_HOST:-https://flows.weni.ai}"
VITE_WEBCHAT_CHANNEL_UUID="${VITE_WEBCHAT_CHANNEL_UUID:-}"
VITE_VOICE_MODE_ENABLED="${VITE_VOICE_MODE_ENABLED:-false}"
VITE_ELEVENLABS_API_KEY="${VITE_ELEVENLABS_API_KEY:-}"
VITE_ELEVENLABS_VOICE_ID="${VITE_ELEVENLABS_VOICE_ID:-pFZP5JQG7iQjIQuC4Bku}"
VITE_VOICE_MODE_LANGUAGE_CODE="${VITE_VOICE_MODE_LANGUAGE_CODE:-}"

echo ""
echo -e "${GREEN}Build arguments that will be passed:${NC}"
echo "VITE_API_URL: $VITE_API_URL"
echo "VITE_WEBCHAT_SOCKET_URL: $VITE_WEBCHAT_SOCKET_URL"
echo "VITE_WEBCHAT_HOST: $VITE_WEBCHAT_HOST"
echo "VITE_WEBCHAT_CHANNEL_UUID: ${VITE_WEBCHAT_CHANNEL_UUID:+<set>}${VITE_WEBCHAT_CHANNEL_UUID:-<not set>}"
echo "VITE_VOICE_MODE_ENABLED: $VITE_VOICE_MODE_ENABLED"
echo "VITE_ELEVENLABS_API_KEY: ${VITE_ELEVENLABS_API_KEY:+<set>}${VITE_ELEVENLABS_API_KEY:-<not set>}"
echo "VITE_ELEVENLABS_VOICE_ID: $VITE_ELEVENLABS_VOICE_ID"
echo "VITE_VOICE_MODE_LANGUAGE_CODE: ${VITE_VOICE_MODE_LANGUAGE_CODE:-<not set>}"
echo ""

# Verificar se variáveis críticas estão definidas
CRITICAL_MISSING=0
if [ -z "$VITE_WEBCHAT_CHANNEL_UUID" ]; then
    echo -e "${RED}WARNING: VITE_WEBCHAT_CHANNEL_UUID is not set${NC}"
    CRITICAL_MISSING=1
fi

if [ "$VITE_VOICE_MODE_ENABLED" = "true" ] && [ -z "$VITE_ELEVENLABS_API_KEY" ]; then
    echo -e "${RED}WARNING: Voice mode is enabled but VITE_ELEVENLABS_API_KEY is not set${NC}"
    CRITICAL_MISSING=1
fi

if [ $CRITICAL_MISSING -eq 1 ]; then
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Tag da imagem
IMAGE_TAG="${IMAGE_TAG:-weni-roadmap-frontend:test}"

echo ""
echo -e "${GREEN}Building Docker image: ${IMAGE_TAG}${NC}"
echo ""

# Build command
docker build \
  --build-arg VITE_API_URL="$VITE_API_URL" \
  --build-arg VITE_WEBCHAT_SOCKET_URL="$VITE_WEBCHAT_SOCKET_URL" \
  --build-arg VITE_WEBCHAT_HOST="$VITE_WEBCHAT_HOST" \
  --build-arg VITE_WEBCHAT_CHANNEL_UUID="$VITE_WEBCHAT_CHANNEL_UUID" \
  --build-arg VITE_VOICE_MODE_ENABLED="$VITE_VOICE_MODE_ENABLED" \
  --build-arg VITE_ELEVENLABS_API_KEY="$VITE_ELEVENLABS_API_KEY" \
  --build-arg VITE_ELEVENLABS_VOICE_ID="$VITE_ELEVENLABS_VOICE_ID" \
  --build-arg VITE_VOICE_MODE_LANGUAGE_CODE="$VITE_VOICE_MODE_LANGUAGE_CODE" \
  -f docker/Dockerfile \
  -t "$IMAGE_TAG" \
  .

echo ""
echo -e "${GREEN}=== Build completed successfully! ===${NC}"
echo ""
echo "To run the container:"
echo "  docker run -p 8080:8080 $IMAGE_TAG"
echo ""
echo "To inspect the image:"
echo "  docker run --rm $IMAGE_TAG ls -la /usr/share/nginx/html/"
echo ""
echo "To check environment variables in runtime:"
echo "  docker run --rm -e VITE_API_URL=https://custom-api.com $IMAGE_TAG env | grep VITE"
echo ""
