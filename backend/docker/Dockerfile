# syntax = docker/dockerfile:1
# Weni Public Roadmap - Backend

ARG PYTHON_VERSION="3.11"
ARG DEBIAN_VERSION="bookworm"

ARG BUILD_DEPS="\
  gcc bzip2 git curl libpq-dev gettext \
  libgdal-dev python3-cffi python3-gdal \
  python3-dev default-libmysqlclient-dev build-essential \
  cmake \
  autoconf pkg-config libtool automake \
  libmariadb-dev ccache"
# default-libmysqlclient-dev
ARG RUNTIME_DEPS="\
  git \
  tzdata \
  postgresql-client \
  netcat-traditional \
  curl \
  gosu \
  gdal-bin \
  npm"

FROM python:${PYTHON_VERSION}-slim-${DEBIAN_VERSION} AS base

ENV PYTHONUNBUFFERED=1 \
  PYTHONDONTWRITEBYTECODE=1 \
  DEBIAN_FRONTEND=noninteractive \
  APP_PATH=/app \
  APP_USER=app_user \
  APP_GROUP=app_group \
  PIP_DISABLE_PIP_VERSION_CHECK=1 \
  PATH="/opt/npm-globals/bin:/app/node_modules/.bin/:${PATH}:/install/bin"

WORKDIR "${APP_PATH}"

RUN addgroup --gid 1999 "${APP_GROUP}" \
  && useradd --system -m -d /app -u 1999 -g 1999 "${APP_USER}" \
  && rm -f /etc/apt/apt.conf.d/docker-clean; echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' > /etc/apt/apt.conf.d/keep-cache

FROM base AS build

ARG BUILD_DEPS

ENV CC="ccache gcc" CXX="ccache g++" PATH="/usr/lib/ccache:${PATH}"

# Install build dependencies
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
  --mount=type=cache,target=/var/lib/apt,sharing=locked \
  apt-get update \
  && apt-get install --no-install-recommends --no-install-suggests -y ${BUILD_DEPS}

# Install Python dependencies
COPY requirements.txt .

RUN --mount=type=cache,mode=0755,target=/pip_cache,id=pip \
  --mount=type=cache,mode=0755,target=/root/.cache/ccache,id=ccache \
  pip install --cache-dir /pip_cache --prefer-binary --prefix=/install -r requirements.txt

FROM base

ARG BUILD_DEPS
ARG RUNTIME_DEPS

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
  --mount=type=cache,target=/var/lib/apt,sharing=locked \
  apt-get update \
  && apt-get install -y --no-install-recommends ${RUNTIME_DEPS} \
  && rm -rf /usr/share/man /usr/share/doc

# Copy application code
COPY --from=build /install /usr/local
COPY . .

USER "${APP_USER}:${APP_GROUP}"

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/v1/health || exit 1

ENTRYPOINT ["/app/docker/entrypoint.sh"]
CMD ["start"]
