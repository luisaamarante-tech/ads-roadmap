# Environment Variables Reference

**Feature**: 005-netlify-deployment
**Last Updated**: December 29, 2025

## Overview

This document lists all environment variables required for deploying the Weni Roadmap application to Netlify. Variables are organized by scope (build-time vs runtime) and component (frontend vs backend).

---

## Backend Runtime Variables

These variables are accessed by serverless functions at **runtime** and must be configured in the Netlify UI under **Site Settings > Environment Variables**.

### Required Variables

| Variable | Description | Example | Secret? | Context |
|----------|-------------|---------|---------|---------|
| `JIRA_BASE_URL` | JIRA instance base URL | `https://weni.atlassian.net` | No | All |
| `JIRA_EMAIL` | Service account email for JIRA API | `roadmap-sync@weni.ai` | No | All |
| `JIRA_API_TOKEN` | JIRA API authentication token | `ATATT3xFfG...` | **Yes** | All |

### Optional Variables

| Variable | Description | Default | Context | Notes |
|----------|-------------|---------|---------|-------|
| `SYNC_INTERVAL_MINUTES` | How often to sync from JIRA | `5` | production | Set to `60` for preview/staging |
| `CACHE_TYPE` | Cache backend type | `simple` | All | Options: `simple`, `redis` |
| `REDIS_URL` | Redis connection string | - | production | Required if `CACHE_TYPE=redis` |
| `FLASK_ENV` | Flask environment mode | `production` | All | Options: `production`, `staging`, `development` |
| `LOG_LEVEL` | Logging verbosity | `INFO` | All | Options: `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `MAX_CACHE_AGE_MINUTES` | Cache expiration time | `10` | All | Stale cache fallback duration |

### Configuration by Context

**Production** (`main` branch):
```bash
JIRA_BASE_URL=https://weni.atlassian.net
JIRA_EMAIL=roadmap-sync@weni.ai
JIRA_API_TOKEN=<secret-token>  # Set in Netlify UI
SYNC_INTERVAL_MINUTES=5
CACHE_TYPE=redis
REDIS_URL=<redis-connection-string>  # Set in Netlify UI
FLASK_ENV=production
LOG_LEVEL=INFO
```

**Deploy Preview** (pull requests):
```bash
JIRA_BASE_URL=https://weni.atlassian.net
JIRA_EMAIL=roadmap-sync@weni.ai
JIRA_API_TOKEN=<secret-token>  # Same as production
SYNC_INTERVAL_MINUTES=60  # Sync less frequently
CACHE_TYPE=simple
FLASK_ENV=staging
LOG_LEVEL=DEBUG
```

**Branch Deploy** (feature branches):
```bash
JIRA_BASE_URL=https://weni.atlassian.net
JIRA_EMAIL=roadmap-sync@weni.ai
JIRA_API_TOKEN=<secret-token>
SYNC_INTERVAL_MINUTES=60
CACHE_TYPE=simple
FLASK_ENV=development
LOG_LEVEL=DEBUG
```

---

## Frontend Build-time Variables

These variables are embedded into the frontend bundle during the **build process**. They are configured in `netlify.toml` or the Netlify UI.

⚠️ **Security Warning**: All frontend variables are **public** and visible in the compiled JavaScript. Never put secrets here.

### Required Variables

| Variable | Description | Example | Context |
|----------|-------------|---------|---------|
| `VITE_API_BASE_URL` | Backend API endpoint | `https://roadmap-api.weni.ai` | All |
| `VITE_WEBCHAT_CHANNEL_UUID` | WebChat channel UUID for Canvas Search | `a9687ddd-849c-44e2-8f81-da9a07de21b8` | All |

### Optional Variables

| Variable | Description | Default | Context |
|----------|-------------|---------|---------|
| `VITE_APP_NAME` | Application display name | `Weni Public Roadmap` | All |
| `VITE_APP_VERSION` | Version string | `1.0.0` | All |
| `VITE_WEBCHAT_SOCKET_URL` | WebChat WebSocket URL | `https://websocket.weni.ai` | All |
| `VITE_WEBCHAT_HOST` | WebChat host URL | `https://flows.weni.ai` | All |
| `NODE_ENV` | Build mode | `production` | All |

### Configuration by Context

**Production**:
```bash
VITE_API_BASE_URL=https://roadmap-api.weni.ai
VITE_WEBCHAT_CHANNEL_UUID=a9687ddd-849c-44e2-8f81-da9a07de21b8
VITE_WEBCHAT_SOCKET_URL=https://websocket.weni.ai
VITE_WEBCHAT_HOST=https://flows.weni.ai
VITE_APP_NAME=Weni Public Roadmap
VITE_APP_VERSION=1.0.0
NODE_ENV=production
```

**Deploy Preview**:
```bash
VITE_API_BASE_URL=https://roadmap-api-preview.netlify.app
VITE_WEBCHAT_CHANNEL_UUID=a9687ddd-849c-44e2-8f81-da9a07de21b8
VITE_WEBCHAT_SOCKET_URL=https://websocket.weni.ai
VITE_WEBCHAT_HOST=https://flows.weni.ai
VITE_APP_NAME=Weni Roadmap (Preview)
NODE_ENV=staging
```

**Branch Deploy**:
```bash
VITE_API_BASE_URL=https://roadmap-api-staging.netlify.app
VITE_WEBCHAT_CHANNEL_UUID=a9687ddd-849c-44e2-8f81-da9a07de21b8
VITE_WEBCHAT_SOCKET_URL=https://websocket.weni.ai
VITE_WEBCHAT_HOST=https://flows.weni.ai
VITE_APP_NAME=Weni Roadmap (Staging)
NODE_ENV=development
```

---

## Build Environment Variables

These variables control the build process itself.

### Backend Build

| Variable | Description | Default | Set In |
|----------|-------------|---------|--------|
| `PYTHON_VERSION` | Python version for functions | `3.11` | netlify.toml |
| `PIP_CACHE_DIR` | Pip cache directory | `.pip_cache` | netlify.toml |

### Frontend Build

| Variable | Description | Default | Set In |
|----------|-------------|---------|--------|
| `NODE_VERSION` | Node.js version | `20` | netlify.toml |
| `NPM_VERSION` | npm version | `10` | netlify.toml |

---

## Setting Environment Variables

### Option 1: Netlify UI (Recommended for Secrets)

1. Navigate to **Site Settings > Environment Variables**
2. Click **Add a variable**
3. Enter key, value, and select contexts (production, deploy-preview, branch-deploy)
4. Mark as **Secret** if sensitive (hides value in UI and logs)

**Example**: Setting JIRA_API_TOKEN
- Key: `JIRA_API_TOKEN`
- Value: `ATATT3xFfG...`
- Contexts: ✓ Production, ✓ Deploy previews, ✓ Branch deploys
- Secret: ✓ Yes

### Option 2: netlify.toml (Recommended for Non-Secrets)

Non-sensitive build-time variables can be set in `netlify.toml`:

```toml
[context.production.environment]
  VITE_API_BASE_URL = "https://roadmap-api.weni.ai"
  VITE_APP_NAME = "Weni Public Roadmap"
  NODE_ENV = "production"
```

### Option 3: Netlify CLI (Local Development)

For local testing with `netlify dev`:

```bash
# Create .env file (DO NOT commit to git)
cat > .env << EOF
JIRA_BASE_URL=https://weni.atlassian.net
JIRA_EMAIL=roadmap-sync@weni.ai
JIRA_API_TOKEN=your-token-here
VITE_API_BASE_URL=http://localhost:5000
EOF

# Run local development
netlify dev
```

---

## Validation

### Backend Function Startup Validation

All backend functions should validate required environment variables on startup:

```python
import os
from typing import List

def validate_env_vars(required: List[str]) -> None:
    """Validate required environment variables are set."""
    missing = [var for var in required if not os.getenv(var)]
    if missing:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing)}"
        )

def handler(event, context):
    # Validate on cold start
    validate_env_vars([
        'JIRA_BASE_URL',
        'JIRA_EMAIL',
        'JIRA_API_TOKEN'
    ])
    
    # Proceed with function logic
    # ...
```

### Frontend Build Validation

Vite will fail the build if required `VITE_*` variables are missing:

```typescript
// src/config.ts
const apiBaseUrl = import.meta.env.VITE_API_BASE_URL;

if (!apiBaseUrl) {
  throw new Error('VITE_API_BASE_URL is required');
}

export const config = {
  apiBaseUrl,
  appName: import.meta.env.VITE_APP_NAME || 'Weni Roadmap',
  version: import.meta.env.VITE_APP_VERSION || '1.0.0',
};
```

---

## Security Best Practices

### ✅ DO

- Store all secrets (API tokens, credentials) in Netlify UI environment variables
- Mark sensitive variables as "Secret" in Netlify UI
- Use different API tokens for production vs preview/staging (if possible)
- Validate required variables on function startup
- Rotate secrets periodically

### ❌ DON'T

- Commit `.env` files to git
- Use `VITE_*` prefix for backend secrets (they'll be exposed in frontend bundle)
- Hardcode credentials in code or config files
- Share production secrets in Slack/email
- Reuse personal JIRA credentials for service accounts

---

## Troubleshooting

### Problem: "Missing required environment variable"

**Cause**: Variable not set in Netlify UI for the deployment context.

**Solution**:
1. Check Site Settings > Environment Variables
2. Verify variable is set for the correct context (production/deploy-preview/branch-deploy)
3. Redeploy after adding variable

### Problem: Frontend can't reach backend API

**Cause**: `VITE_API_BASE_URL` pointing to wrong endpoint or CORS not configured.

**Solution**:
1. Check `VITE_API_BASE_URL` in build logs
2. Verify backend is deployed and accessible
3. Check CORS headers in backend netlify.toml

### Problem: JIRA sync not working

**Cause**: Invalid JIRA credentials or network issues.

**Solution**:
1. Test credentials: `curl -u email:token https://your-jira.atlassian.net/rest/api/3/myself`
2. Check JIRA_BASE_URL doesn't have trailing slash
3. Verify service account has read access to projects

### Problem: Build fails with "Module not found"

**Cause**: Environment variable used in build but not set.

**Solution**:
1. Check build logs for missing variable name
2. Add variable to netlify.toml or Netlify UI
3. Ensure variable has correct context (production/deploy-preview/branch-deploy)

---

## Migration from Docker Compose

If migrating from Docker Compose to Netlify, map environment variables as follows:

| Docker Compose (.env) | Netlify (Backend) | Netlify (Frontend) |
|----------------------|-------------------|-------------------|
| `JIRA_BASE_URL` | `JIRA_BASE_URL` | - |
| `JIRA_EMAIL` | `JIRA_EMAIL` | - |
| `JIRA_API_TOKEN` | `JIRA_API_TOKEN` (secret) | - |
| `FLASK_ENV` | `FLASK_ENV` | - |
| `SYNC_INTERVAL_MINUTES` | `SYNC_INTERVAL_MINUTES` | - |
| `VITE_API_BASE_URL` (build arg) | - | `VITE_API_BASE_URL` (build-time) |

---

## Reference Links

- [Netlify Environment Variables Documentation](https://docs.netlify.com/environment-variables/overview/)
- [Vite Environment Variables Guide](https://vitejs.dev/guide/env-and-mode.html)
- [JIRA Cloud API Authentication](https://developer.atlassian.com/cloud/jira/platform/basic-auth-for-rest-apis/)
- [12-Factor App: Config](https://12factor.net/config)

