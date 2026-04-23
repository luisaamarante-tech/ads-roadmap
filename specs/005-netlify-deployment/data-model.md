# Data Model: Netlify Deployment Configuration

**Feature**: 005-netlify-deployment
**Date**: December 29, 2025
**Status**: Complete

## Overview

This document defines the data structures and configuration schemas for Netlify deployment. While this feature primarily involves configuration files rather than traditional data models, these schemas ensure consistent and valid deployment configurations.

---

## 1. Netlify Configuration Schema

### Entity: NetlifyConfig

Represents the complete deployment configuration for a single deployable unit (frontend or backend).

**Attributes**:

| Attribute | Type | Required | Description | Validation Rules |
|-----------|------|----------|-------------|-----------------|
| `build.base` | string | Yes | Base directory for build | Must be valid directory path |
| `build.command` | string | Yes | Command to execute build | Non-empty string |
| `build.publish` | string | Yes | Directory to publish | Relative path from base |
| `build.environment` | object | No | Build-time environment variables | Key-value pairs |
| `functions.directory` | string | Conditional | Directory containing functions | Required for backend |
| `functions.node_bundler` | string | No | Node bundler (esbuild/zisi) | Enum: esbuild, zisi |
| `context.production` | object | No | Production-specific overrides | ContextConfig schema |
| `context.deploy-preview` | object | No | Preview deployment overrides | ContextConfig schema |
| `context.branch-deploy` | object | No | Branch deployment overrides | ContextConfig schema |
| `redirects` | array | No | Redirect/rewrite rules | Array of RedirectRule |
| `headers` | array | No | Custom HTTP headers | Array of HeaderRule |

**Relationships**:
- Contains multiple `ContextConfig` objects (production, preview, branch deploys)
- Contains multiple `RedirectRule` objects
- Contains multiple `HeaderRule` objects

**State Transitions**:
- Draft → Validated → Deployed → Active
- Active → Rollback-Target (when newer deploy exists)

**Validation Rules**:
1. `build.command` must be executable in target environment
2. `build.publish` directory must be created by `build.command`
3. If `functions.directory` specified, directory must contain valid function files
4. All environment variable keys must be uppercase with underscores
5. Redirect rules must have valid HTTP status codes (200, 301, 302, 404, etc.)

---

### Entity: ContextConfig

Represents environment-specific configuration overrides.

**Attributes**:

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `command` | string | No | Override build command |
| `environment` | object | No | Context-specific env vars |
| `publish` | string | No | Override publish directory |
| `functions` | object | No | Override function settings |

**Context Types**:
- `production`: Main branch deployments
- `deploy-preview`: Pull request deployments
- `branch-deploy`: Feature branch deployments
- `{branch-name}`: Specific branch overrides

---

### Entity: RedirectRule

Represents a URL redirect or rewrite rule.

**Attributes**:

| Attribute | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| `from` | string | Yes | Source path pattern | - |
| `to` | string | Yes | Destination path or URL | - |
| `status` | integer | No | HTTP status code | 301 |
| `force` | boolean | No | Force redirect even if file exists | false |
| `query` | object | No | Query parameter conditions | {} |
| `conditions` | object | No | Advanced conditions | {} |

**Validation Rules**:
1. `status` must be valid HTTP code (200, 301, 302, 303, 404, 410, 451)
2. `from` supports wildcard (`*`) and splat (`:splat`) patterns
3. `to` can reference captured splats with `:splat`
4. SPA fallback typically uses: `from="/*"`, `to="/index.html"`, `status=200`

---

### Entity: HeaderRule

Represents custom HTTP headers for specific paths.

**Attributes**:

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `for` | string | Yes | Path pattern to apply headers |
| `values` | object | Yes | Header key-value pairs |

**Common Headers**:
- `Cache-Control`: Cache behavior for assets
- `X-Frame-Options`: Clickjacking protection
- `X-Content-Type-Options`: MIME sniffing protection
- `Content-Security-Policy`: XSS protection
- `Referrer-Policy`: Referrer information control

---

## 2. Environment Variable Schema

### Entity: EnvironmentVariable

Represents a single environment variable configuration.

**Attributes**:

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `key` | string | Yes | Variable name (UPPER_SNAKE_CASE) |
| `value` | string | Yes | Variable value |
| `context` | array | No | Contexts where variable applies |
| `scope` | enum | Yes | build-time or runtime |
| `secret` | boolean | No | Whether value should be masked in logs |

**Scopes**:

**Build-time** (Frontend):
- Embedded into compiled bundle
- Accessible via `import.meta.env.VITE_*` in code
- Safe for non-sensitive configuration
- Examples: API URLs, feature flags, app version

**Runtime** (Backend):
- Accessed via `os.getenv()` at function execution
- Not embedded in any bundle
- Required for sensitive data
- Examples: API keys, database credentials, secrets

**Validation Rules**:
1. Build-time frontend vars must be prefixed with `VITE_`
2. Secret variables must be runtime scope only
3. Context must be one of: `production`, `deploy-preview`, `branch-deploy`, `all`
4. Keys must match regex: `^[A-Z][A-Z0-9_]*$`

---

### Variable Groups

**Backend Runtime Variables**:

| Variable | Required | Secret | Default | Description |
|----------|----------|--------|---------|-------------|
| `JIRA_BASE_URL` | Yes | No | - | JIRA instance URL |
| `JIRA_EMAIL` | Yes | No | - | Service account email |
| `JIRA_API_TOKEN` | Yes | Yes | - | JIRA API authentication token |
| `SYNC_INTERVAL_MINUTES` | No | No | 5 | Roadmap sync frequency |
| `CACHE_TYPE` | No | No | simple | Cache backend (simple/redis) |
| `REDIS_URL` | Conditional | Yes | - | Redis connection string (if CACHE_TYPE=redis) |
| `FLASK_ENV` | No | No | production | Flask environment |
| `LOG_LEVEL` | No | No | INFO | Logging verbosity |

**Frontend Build-time Variables**:

| Variable | Required | Secret | Default | Description |
|----------|----------|--------|---------|-------------|
| `VITE_API_BASE_URL` | Yes | No | - | Backend API endpoint |
| `VITE_APP_NAME` | No | No | Weni Roadmap | Application title |
| `VITE_APP_VERSION` | No | No | 1.0.0 | Version string |

---

## 3. Function Configuration Schema

### Entity: ServerlessFunction

Represents a single Netlify Function endpoint.

**Attributes**:

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | Yes | Function name (becomes URL path) |
| `handler` | string | Yes | Path to handler file |
| `runtime` | string | Yes | Runtime environment (python3.11, nodejs20) |
| `schedule` | string | No | Cron expression for scheduled functions |
| `timeout` | integer | No | Max execution time in seconds (default: 10, max: 26) |
| `memorySize` | integer | No | Memory allocation in MB (1024, 2048, 3008) |

**File Naming Convention**:
- File name becomes URL path: `api-health.py` → `/.netlify/functions/api-health`
- Use hyphens for multi-word names: `api-roadmap-items.py`
- Prefix API functions with `api-` for clarity

**Handler Signature**:
```python
def handler(event: dict, context: dict) -> dict:
    """
    Args:
        event: Request metadata (httpMethod, path, queryStringParameters, headers, body)
        context: Execution context (requestId, functionName, remainingTimeInMillis)
    
    Returns:
        dict with statusCode, headers, body
    """
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({'message': 'Success'})
    }
```

---

### Entity: ScheduledFunction

Represents a cron-scheduled background task.

**Attributes**:

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | Yes | Function identifier |
| `schedule` | string | Yes | Cron expression |
| `handler` | string | Yes | Path to handler function |
| `timezone` | string | No | Timezone for schedule (default: UTC) |

**Schedule Examples**:

| Cron Expression | Description | Use Case |
|----------------|-------------|----------|
| `*/5 * * * *` | Every 5 minutes | Production JIRA sync |
| `*/30 * * * *` | Every 30 minutes | Staging JIRA sync |
| `0 * * * *` | Every hour at :00 | Hourly cache cleanup |
| `0 0 * * *` | Daily at midnight | Daily reports |
| `0 0 * * 0` | Weekly on Sunday | Weekly analytics |

**Validation Rules**:
1. Schedule must be valid cron expression
2. Minimum interval is 1 minute
3. Timezone must be valid IANA timezone name
4. Handler must exist in functions directory

---

## 4. Deployment Metadata Schema

### Entity: Deployment

Represents a single deployment instance.

**Attributes**:

| Attribute | Type | Description |
|-----------|------|-------------|
| `id` | string | Unique deployment identifier (Netlify-generated) |
| `site_id` | string | Site identifier |
| `context` | string | Deployment context (production/deploy-preview/branch-deploy) |
| `branch` | string | Git branch name |
| `commit_ref` | string | Git commit SHA |
| `commit_message` | string | Git commit message |
| `deploy_url` | string | Unique URL for this deployment |
| `deploy_ssl_url` | string | HTTPS URL for this deployment |
| `created_at` | datetime | Deployment creation timestamp |
| `updated_at` | datetime | Last update timestamp |
| `published_at` | datetime | When deployment went live (null if not published) |
| `state` | enum | Deployment state |
| `build_id` | string | Associated build identifier |
| `error_message` | string | Error details if failed |

**State Values**:
- `new`: Deployment created, not yet building
- `building`: Build in progress
- `enqueued`: Waiting for build slot
- `processing`: Post-build processing
- `ready`: Build succeeded, awaiting publish
- `published`: Live deployment
- `error`: Build or deploy failed
- `retrying`: Automatic retry in progress

**State Transitions**:
```
new → enqueued → building → processing → ready → published
                     ↓           ↓          ↓
                   error      error      error
                     ↓
                 retrying → building
```

---

### Entity: BuildLog

Represents build execution logs.

**Attributes**:

| Attribute | Type | Description |
|-----------|------|-------------|
| `deployment_id` | string | Associated deployment ID |
| `timestamp` | datetime | Log entry timestamp |
| `level` | enum | Log level (info/warning/error) |
| `message` | string | Log message content |
| `step` | string | Build step identifier |

**Build Steps**:
1. `install`: Install dependencies
2. `build`: Execute build command
3. `package`: Package artifacts
4. `deploy`: Upload to CDN
5. `post_deploy`: Post-processing

---

## 5. Configuration File Locations

### File Structure

```text
weni-roadmap/
├── backend/
│   ├── netlify.toml                    # Backend deployment config
│   ├── runtime.txt                     # Python version (3.11)
│   └── netlify/
│       └── functions/                  # Serverless function handlers
│           ├── api-health.py
│           ├── api-roadmap-items.py
│           ├── api-roadmap-item.py
│           ├── api-roadmap-modules.py
│           ├── api-roadmap-stats.py
│           ├── sync-roadmap.py         # Internal sync function
│           └── scheduled-sync.js       # Cron scheduler
│
└── frontend/
    ├── netlify.toml                    # Frontend deployment config
    ├── _redirects                      # SPA routing rules (alternative to redirects in .toml)
    └── dist/                           # Build output (gitignored)
```

---

## 6. Validation Schema (JSON Schema)

### NetlifyConfig JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Netlify Configuration",
  "type": "object",
  "required": ["build"],
  "properties": {
    "build": {
      "type": "object",
      "required": ["command", "publish"],
      "properties": {
        "base": { "type": "string" },
        "command": { "type": "string", "minLength": 1 },
        "publish": { "type": "string", "minLength": 1 },
        "environment": {
          "type": "object",
          "patternProperties": {
            "^[A-Z][A-Z0-9_]*$": { "type": "string" }
          }
        }
      }
    },
    "functions": {
      "type": "object",
      "properties": {
        "directory": { "type": "string" },
        "node_bundler": { "enum": ["esbuild", "zisi"] }
      }
    },
    "redirects": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["from", "to"],
        "properties": {
          "from": { "type": "string" },
          "to": { "type": "string" },
          "status": { "type": "integer", "enum": [200, 301, 302, 303, 404, 410, 451] },
          "force": { "type": "boolean" }
        }
      }
    },
    "headers": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["for", "values"],
        "properties": {
          "for": { "type": "string" },
          "values": {
            "type": "object",
            "patternProperties": {
              ".*": { "type": "string" }
            }
          }
        }
      }
    }
  }
}
```

---

## Summary

This data model defines:

1. **Configuration Entities**: NetlifyConfig, ContextConfig, RedirectRule, HeaderRule
2. **Environment Variables**: Scoping rules, naming conventions, secret handling
3. **Serverless Functions**: Handler signatures, naming conventions, scheduling
4. **Deployment Metadata**: Lifecycle states, build logs, rollback targets
5. **Validation Schemas**: JSON Schema for configuration validation

All schemas support the functional requirements defined in [spec.md](spec.md) and implementation patterns from [research.md](research.md).

**Next**: See [contracts/](contracts/) for concrete configuration examples and [quickstart.md](quickstart.md) for implementation guide.

