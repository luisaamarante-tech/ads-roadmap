# syntax = docker/dockerfile:1

# Weni Public Roadmap - Frontend

ARG NODE_VERSION="25"
ARG BASE_VERSION="alpine3.23"

# Build stage
FROM node:${NODE_VERSION}-${BASE_VERSION} AS build

# Cache busting - declared early to be available throughout the build
ARG CACHE_BUST

# Add build arguments for all Vite environment variables
ARG VITE_API_URL
ARG VITE_WEBCHAT_SOCKET_URL
ARG VITE_WEBCHAT_HOST
ARG VITE_WEBCHAT_CHANNEL_UUID
ARG VITE_VOICE_MODE_ENABLED
ARG VITE_ELEVENLABS_API_KEY
ARG VITE_ELEVENLABS_VOICE_ID
ARG VITE_VOICE_MODE_LANGUAGE_CODE

# Set them as environment variables so Vite can access them during build
ENV VITE_API_URL=${VITE_API_URL}
ENV VITE_WEBCHAT_SOCKET_URL=${VITE_WEBCHAT_SOCKET_URL}
ENV VITE_WEBCHAT_HOST=${VITE_WEBCHAT_HOST}
ENV VITE_WEBCHAT_CHANNEL_UUID=${VITE_WEBCHAT_CHANNEL_UUID}
ENV VITE_VOICE_MODE_ENABLED=${VITE_VOICE_MODE_ENABLED}
ENV VITE_ELEVENLABS_API_KEY=${VITE_ELEVENLABS_API_KEY}
ENV VITE_ELEVENLABS_VOICE_ID=${VITE_ELEVENLABS_VOICE_ID}
ENV VITE_VOICE_MODE_LANGUAGE_CODE=${VITE_VOICE_MODE_LANGUAGE_CODE}

WORKDIR /app

# Debug: Show received build args (values will be visible in build logs)
RUN echo "=== Build Arguments Received ===" && \
    echo "VITE_API_URL: ${VITE_API_URL:-<not set>}" && \
    echo "VITE_WEBCHAT_SOCKET_URL: ${VITE_WEBCHAT_SOCKET_URL:-<not set>}" && \
    echo "VITE_WEBCHAT_HOST: ${VITE_WEBCHAT_HOST:-<not set>}" && \
    echo "VITE_WEBCHAT_CHANNEL_UUID: ${VITE_WEBCHAT_CHANNEL_UUID:-<not set>}" && \
    echo "VITE_VOICE_MODE_ENABLED: ${VITE_VOICE_MODE_ENABLED:-<not set>}" && \
    echo "VITE_ELEVENLABS_API_KEY: ${VITE_ELEVENLABS_API_KEY:+<set>}${VITE_ELEVENLABS_API_KEY:-<not set>}" && \
    echo "VITE_ELEVENLABS_VOICE_ID: ${VITE_ELEVENLABS_VOICE_ID:-<not set>}" && \
    echo "VITE_VOICE_MODE_LANGUAGE_CODE: ${VITE_VOICE_MODE_LANGUAGE_CODE:-<not set>}" && \
    echo "==============================="

# Install dependencies
COPY package*.json ./
RUN --mount=type=cache,target=/root/.npm \
  apk add git \
  && npm clean-install

# Cache invalidation point #1: Invalidate COPY layer
# This ensures fresh source files (including public/webchat-audio.umd.js) are always copied
RUN echo "=== Cache Invalidation Point #1 ===" \
  && echo "CACHE_BUST: ${CACHE_BUST:-<not set>}" \
  && echo "This invalidates the COPY layer below" \
  && echo "===================================="

# Copy source and build
# .env.production is automatically loaded by Vite when NODE_ENV=production
COPY . .

# Cache invalidation point #2: Invalidate build layer
# This ensures npm build always runs with fresh files
RUN echo "=== Cache Invalidation Point #2 ===" \
  && echo "CACHE_BUST: ${CACHE_BUST:-<not set>}" \
  && echo "This invalidates the npm build layer below" \
  && echo "===================================="

RUN --mount=type=cache,target=/root/.npm \
  NODE_ENV=production npm run build \
  && echo "=== Verifying build artifacts ===" \
  && ls -la dist/ \
  && echo "=== Checking if env vars are embedded in bundle ===" \
  && grep -r "WEBCHAT_CHANNEL_UUID" dist/assets/*.js || echo "WARNING: WEBCHAT_CHANNEL_UUID not found in bundle!" \
  && grep -r "ELEVENLABS" dist/assets/*.js || echo "WARNING: ELEVENLABS config not found in bundle!" \
  && echo "===============================" \
  && touch /headers \
  && chmod +r /headers \
  && chmod -wx /headers

# Production stage
FROM nginxinc/nginx-unprivileged:1-alpine

COPY --chown=nginx:nginx docker/nginx.conf /etc/nginx/nginx.conf

# Copy built assets
COPY --from=build --chown=nginx:nginx /app/dist /usr/share/nginx/html
COPY --from=build --chown=nginx:nginx /headers /usr/share/nginx/html/
COPY docker/entrypoint.sh /

USER root:root

RUN mv /usr/share/nginx/html/index.html /usr/share/nginx/html/index.html.tmpl \
  && cd /usr/share/nginx/html/ \
  && ln -s /tmp/index.html

USER nginx:nginx

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget -q --spider http://localhost:8080 || exit 1

ENTRYPOINT ["/entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"]
