# Research: Netlify Deployment for Flask & Vue Applications

**Feature**: 005-netlify-deployment
**Date**: December 29, 2025
**Status**: Complete

## Overview

This document consolidates research findings for deploying a monorepo containing a Flask backend and Vue.js frontend to Netlify. The primary challenge is adapting Flask's WSGI application model to Netlify's serverless function architecture while maintaining existing API contracts.

---

## 1. Netlify Functions Adapter Patterns for Flask

### Research Question
How do we deploy a Flask application as Netlify Functions while maintaining existing route structure and API contracts?

### Decision
**Use function-per-endpoint wrapper pattern with shared Flask app context**

### Rationale
1. **Maintains API contracts**: Existing routes remain unchanged from client perspective
2. **Minimal code changes**: Flask application code stays intact; only add serverless wrappers
3. **Cold start optimization**: Each function imports only necessary dependencies
4. **Debugging simplicity**: Individual functions can be tested locally with Netlify CLI

### Implementation Pattern

**Architecture**:
```text
netlify/functions/
├── api-health.py          # Wraps GET /api/v1/health
├── api-roadmap-items.py   # Wraps GET /api/v1/roadmap/items
├── api-roadmap-item.py    # Wraps GET /api/v1/roadmap/items/{id}
├── api-roadmap-modules.py # Wraps GET /api/v1/roadmap/modules
└── api-roadmap-stats.py   # Wraps GET /api/v1/roadmap/stats
```

**Function wrapper template**:
```python
# netlify/functions/api-health.py
from app import create_app

def handler(event, context):
    """Netlify Function wrapper for Flask route"""
    app = create_app()
    
    # Extract HTTP details from event
    http_method = event.get('httpMethod', 'GET')
    path = event.get('path', '/')
    query_params = event.get('queryStringParameters', {})
    headers = event.get('headers', {})
    body = event.get('body', '')
    
    # Create Flask test client and make request
    with app.test_client() as client:
        if http_method == 'GET':
            response = client.get(path, query_string=query_params, headers=headers)
        # ... handle other methods
        
        return {
            'statusCode': response.status_code,
            'headers': dict(response.headers),
            'body': response.get_data(as_text=True)
        }
```

### Alternatives Considered

**Alternative 1: Single function with route dispatching**
- **Pros**: One deployment unit, simpler configuration
- **Cons**: Slower cold starts (loads entire Flask app), harder to debug individual endpoints
- **Rejected**: Cold start performance critical for user experience

**Alternative 2: Complete Flask rewrite to native functions**
- **Pros**: Optimal serverless performance
- **Cons**: Massive code changes, breaks existing abstractions, high risk
- **Rejected**: Violates "minimal code changes" principle

**Alternative 3: Use third-party adapter (e.g., Zappa, Mangum)**
- **Pros**: Off-the-shelf solution
- **Cons**: Adds dependency, may not support Netlify Functions format, opaque behavior
- **Rejected**: Custom wrapper is lightweight and maintainable

### References
- [Netlify Functions Documentation](https://docs.netlify.com/functions/overview/)
- [AWS Lambda Python Handler](https://docs.aws.amazon.com/lambda/latest/dg/python-handler.html)
- [Flask Application Factories Pattern](https://flask.palletsprojects.com/patterns/appfactories/)

---

## 2. Netlify Build Configuration for Vue + Vite

### Research Question
What build settings optimize Vue/Vite application deployment to Netlify with SPA routing support?

### Decision
**Use Vite production build with Netlify's SPA redirect rules**

### Rationale
1. **Vite optimizations**: Built-in code splitting, tree shaking, and asset optimization
2. **SPA routing**: `_redirects` file handles client-side routing without server config
3. **Build performance**: Vite's fast builds meet 5-minute deployment goal
4. **Asset handling**: Automatic chunking and lazy loading for optimal performance

### Implementation Configuration

**netlify.toml** (frontend):
```toml
[build]
  base = "frontend"
  command = "npm run build"
  publish = "dist"

[build.environment]
  NODE_VERSION = "20"
  NPM_FLAGS = "--prefix frontend"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
  force = false

[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "DENY"
    X-Content-Type-Options = "nosniff"
    Referrer-Policy = "strict-origin-when-cross-origin"

[[headers]]
  for = "/assets/*"
  [headers.values]
    Cache-Control = "public, max-age=31536000, immutable"
```

**_redirects** file (alternative to redirects in netlify.toml):
```text
# SPA fallback
/*    /index.html   200

# API proxy (if needed for local preview)
/api/*  https://backend-subdomain.netlify.app/api/:splat  200
```

### Alternatives Considered

**Alternative 1: Server-side rendering (SSR)**
- **Pros**: Better SEO, faster initial load
- **Cons**: Requires Node.js functions, complexity increase, not needed for authenticated app
- **Rejected**: Roadmap is public but SEO not critical; simplicity preferred

**Alternative 2: Static site generation (SSG)**
- **Pros**: Pre-rendered HTML, optimal performance
- **Cons**: Dynamic data from JIRA requires rebuild on every content change
- **Rejected**: Content updates frequently; runtime data fetching required

### References
- [Netlify SPA Routing](https://docs.netlify.com/routing/redirects/rewrites-proxies/#history-pushstate-and-single-page-apps)
- [Vite Production Build](https://vitejs.dev/guide/build.html)
- [Netlify Build Configuration](https://docs.netlify.com/configure-builds/file-based-configuration/)

---

## 3. Environment Variable Management

### Research Question
How should environment variables be managed across development, preview, and production deployments?

### Decision
**Use Netlify's environment variable scoping with context-based configuration**

### Rationale
1. **Security**: Secrets never committed to repository
2. **Flexibility**: Different values per deployment context (production, deploy-preview, branch-deploy)
3. **Build-time vs Runtime**: Clear separation prevents frontend secret exposure
4. **Team access**: Netlify UI provides controlled access to production secrets

### Environment Variable Strategy

**Backend (runtime, serverless functions)**:
```text
# Required for all contexts
JIRA_BASE_URL=https://company.atlassian.net
JIRA_EMAIL=roadmap-sync@company.com
JIRA_API_TOKEN=ATATT3x...  # Secret, Netlify env var only

# Context-specific
SYNC_INTERVAL_MINUTES=5  # Production: 5, Preview: 60
CACHE_TYPE=simple        # Production: redis, Preview: simple
REDIS_URL=redis://...    # Production only

# Flask config
FLASK_ENV=production
```

**Frontend (build-time, embedded in bundle)**:
```text
# API endpoint (injected at build time)
VITE_API_BASE_URL=https://backend.netlify.app  # Production
VITE_API_BASE_URL=https://deploy-preview-123.netlify.app  # Preview

# Public config (safe to embed)
VITE_APP_NAME=Weni Public Roadmap
```

**Netlify Configuration**:
- **Production context**: Full configuration with production endpoints
- **Deploy Preview context**: Testing configuration with longer sync intervals
- **Branch deploys**: Development configuration with mock data support

### Security Considerations
1. **Never prefix backend secrets with `VITE_`**: These get embedded in frontend bundle
2. **Use Netlify Functions for API keys**: Backend secrets stay server-side
3. **Validate environment on startup**: Fail fast if required vars missing
4. **Audit access**: Use Netlify teams to control who can view production secrets

### Alternatives Considered

**Alternative 1: .env files in repository**
- **Pros**: Simple, works locally
- **Cons**: Secrets exposed in git history, no per-context variation
- **Rejected**: Security risk unacceptable

**Alternative 2: External secret management (AWS Secrets Manager, Vault)**
- **Pros**: Enterprise-grade security, rotation support
- **Cons**: Additional complexity, cost, latency for function cold starts
- **Rejected**: Netlify built-in solution sufficient for current needs

### References
- [Netlify Environment Variables](https://docs.netlify.com/environment-variables/overview/)
- [Vite Environment Variables](https://vitejs.dev/guide/env-and-mode.html)
- [12-Factor App Config](https://12factor.net/config)

---

## 4. Serverless Function Cold Start Optimization

### Research Question
How do we minimize cold start latency for Python-based Netlify Functions?

### Decision
**Implement lazy imports, connection pooling, and optional function warming**

### Rationale
1. **User experience**: First request should complete in under 2 seconds including cold start
2. **Cost efficiency**: Warming functions has cost implications; optimize before warming
3. **Pragmatic approach**: Start with optimization, add warming only if needed

### Optimization Strategies

**1. Lazy Import Pattern**
```python
# ❌ BAD: Import at module level
from app import create_app
from app.services.jira_client import JiraClient

def handler(event, context):
    app = create_app()
    # Heavy imports loaded on every cold start

# ✅ GOOD: Import inside handler
def handler(event, context):
    # Import only when function executes
    from app import create_app
    app = create_app()
```

**2. Dependency Optimization**
- Use `requirements.txt` with minimal dependencies per function
- Exclude dev dependencies (pytest, black, flake8) from deployment
- Pin versions for reproducible builds

**3. Connection Reuse**
```python
# Reuse connections across warm invocations
import os
from functools import lru_cache

@lru_cache(maxsize=1)
def get_jira_client():
    """Cached JIRA client reused across warm invocations"""
    from app.services.jira_client import JiraClient
    return JiraClient(
        base_url=os.getenv('JIRA_BASE_URL'),
        email=os.getenv('JIRA_EMAIL'),
        token=os.getenv('JIRA_API_TOKEN')
    )

def handler(event, context):
    client = get_jira_client()  # Reuses existing connection if warm
    # ... handle request
```

**4. Optional Function Warming** (if cold starts >2s)
```javascript
// netlify/functions/warmer.js
// Scheduled function to keep critical functions warm
export async function handler(event, context) {
  const functions = [
    'api-roadmap-items',
    'api-roadmap-modules'
  ];
  
  await Promise.all(
    functions.map(fn => 
      fetch(`/.netlify/functions/${fn}?warmup=true`)
    )
  );
  
  return { statusCode: 200 };
}
```

### Measured Performance Targets
- **Cold start**: <2 seconds (first invocation)
- **Warm start**: <200ms (subsequent invocations within 5 minutes)
- **Acceptable**: 90% of requests complete within warm start time

### Alternatives Considered

**Alternative 1: Keep functions perpetually warm**
- **Pros**: Consistent performance
- **Cons**: High cost (constant invocations), wasteful for low-traffic periods
- **Rejected**: Optimize first, warm only if needed

**Alternative 2: Reduce Python runtime overhead**
- **Pros**: Faster cold starts
- **Cons**: Would require rewrite in Node.js/Go, massive effort
- **Rejected**: Python cold starts acceptable with optimization

### References
- [AWS Lambda Cold Starts](https://docs.aws.amazon.com/lambda/latest/dg/lambda-runtime-environment.html)
- [Python Import Optimization](https://realpython.com/python-import/)
- [Netlify Function Performance](https://www.netlify.com/blog/improve-your-serverless-performance/)

---

## 5. Background Jobs and Scheduled Tasks

### Research Question
How do we handle Flask-APScheduler background jobs in a serverless environment?

### Decision
**Migrate APScheduler jobs to Netlify Scheduled Functions**

### Rationale
1. **Serverless compatibility**: Functions are stateless; long-running processes not supported
2. **Native scheduling**: Netlify provides cron-based scheduling
3. **Reliability**: Netlify handles retries and monitoring
4. **Cost efficiency**: Only pay for scheduled execution time

### Migration Strategy

**Current Architecture** (local/Docker):
```python
# app/services/sync_service.py
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
scheduler.add_job(
    func=sync_roadmap_items,
    trigger="interval",
    minutes=int(os.getenv('SYNC_INTERVAL_MINUTES', 5))
)
scheduler.start()
```

**New Architecture** (Netlify):
```javascript
// netlify/functions/scheduled-sync.js
const { schedule } = require('@netlify/functions');

const handler = async (event) => {
  // Call Python sync function
  const response = await fetch('/.netlify/functions/sync-roadmap', {
    method: 'POST',
    headers: { 'X-Internal-Request': 'true' }
  });
  
  return {
    statusCode: 200,
    body: JSON.stringify({ synced: true })
  };
};

// Run every 5 minutes
exports.handler = schedule("*/5 * * * *", handler);
```

**Sync function** (Python):
```python
# netlify/functions/sync-roadmap.py
def handler(event, context):
    """Internal function called by scheduled sync"""
    # Verify internal request
    if event.get('headers', {}).get('x-internal-request') != 'true':
        return {'statusCode': 403, 'body': 'Forbidden'}
    
    from app.services.sync_service import sync_roadmap_items
    result = sync_roadmap_items()
    
    return {
        'statusCode': 200,
        'body': json.dumps({'items_synced': result})
    }
```

### Scheduling Configuration

**netlify.toml**:
```toml
[functions]
  directory = "netlify/functions"
  
[functions.scheduled-sync]
  schedule = "*/5 * * * *"  # Every 5 minutes (production)
```

**Environment-based scheduling**:
- **Production**: Every 5 minutes (`*/5 * * * *`)
- **Staging**: Every 30 minutes (`*/30 * * * *`)
- **Preview**: Manual trigger only (no schedule)

### Alternatives Considered

**Alternative 1: External cron service (Cronitor, EasyCron)**
- **Pros**: More flexible scheduling options
- **Cons**: Additional service dependency, auth complexity, cost
- **Rejected**: Netlify Scheduled Functions sufficient

**Alternative 2: Keep APScheduler in single long-running function**
- **Pros**: Minimal code changes
- **Cons**: Not supported by Netlify Functions (10s execution limit), defeats serverless purpose
- **Rejected**: Fundamentally incompatible with serverless

**Alternative 3: Client-side scheduling (frontend triggers sync)**
- **Pros**: No backend scheduling needed
- **Cons**: Unreliable (requires active users), security risk (exposed endpoint)
- **Rejected**: Data sync must be server-driven

### References
- [Netlify Scheduled Functions](https://docs.netlify.com/functions/scheduled-functions/)
- [Cron Expression Syntax](https://crontab.guru/)
- [Serverless Background Jobs Patterns](https://www.serverless.com/blog/serverless-scheduled-tasks)

---

## 6. Preview Deployments and Branch Configuration

### Research Question
How should preview deployments work for feature branches to enable safe testing before production?

### Decision
**Enable automatic deploy previews for all branches with production-like configuration**

### Rationale
1. **Test before merge**: Every PR gets a live preview environment
2. **Isolated testing**: Each branch has unique URL, no collision with production
3. **Stakeholder review**: Product managers can review features before merge
4. **Regression prevention**: Catch deployment issues before production

### Configuration

**netlify.toml** (applies to both frontend and backend):
```toml
[build]
  command = "npm run build"  # or python equivalent
  publish = "dist"

# Production branch (auto-deploys to main domain)
[context.production]
  environment = { ENVIRONMENT = "production" }

# Deploy previews (PRs and merge requests)
[context.deploy-preview]
  environment = { ENVIRONMENT = "preview" }
  command = "npm run build"

# Branch deploys (non-PR branches)
[context.branch-deploy]
  environment = { ENVIRONMENT = "staging" }
  command = "npm run build"

# Specific branch override (e.g., develop branch)
[context.develop]
  environment = { ENVIRONMENT = "staging" }
```

### Deployment Workflow

**Feature branch** (`005-netlify-deployment`):
1. Push commit → Netlify builds branch deploy
2. URL: `https://005-netlify-deployment--weni-roadmap.netlify.app`
3. Environment: staging (longer sync intervals, test data OK)

**Pull request** (from feature to main):
1. Create PR → Netlify builds deploy preview
2. URL: `https://deploy-preview-42--weni-roadmap.netlify.app`
3. Comment on PR with preview link
4. Environment: preview (isolated test environment)

**Main branch** (after merge):
1. Merge PR → Netlify builds production deploy
2. URL: `https://roadmap.weni.ai` (custom domain)
3. Environment: production (real JIRA data, optimized settings)

### Branch Strategy

| Branch | Deployment Type | URL Pattern | Environment |
|--------|----------------|-------------|-------------|
| `main` | Production | `roadmap.weni.ai` | production |
| `develop` | Branch Deploy | `develop--weni-roadmap.netlify.app` | staging |
| `###-feature` | Branch Deploy | `###-feature--weni-roadmap.netlify.app` | staging |
| PR to main | Deploy Preview | `deploy-preview-##--weni-roadmap.netlify.app` | preview |

### Alternatives Considered

**Alternative 1: Manual preview deploys only**
- **Pros**: Lower build minute usage, explicit control
- **Cons**: Slows down review process, requires manual triggers
- **Rejected**: Automation saves time, build minutes sufficient in Pro plan

**Alternative 2: Preview deploys for PRs only (no branch deploys)**
- **Pros**: Fewer deploys, lower cost
- **Cons**: Can't test branches before creating PR
- **Rejected**: Developers need to validate before PR creation

### References
- [Netlify Deploy Contexts](https://docs.netlify.com/site-deploys/overview/#deploy-contexts)
- [Branch Deploy Controls](https://docs.netlify.com/site-deploys/overview/#branch-deploy-controls)

---

## 7. Rollback Mechanisms and Deployment History

### Research Question
How do we quickly rollback to a previous version if a deployment introduces issues?

### Decision
**Use Netlify's built-in deployment history with one-click rollback**

### Rationale
1. **Speed**: Rollback completes in under 2 minutes (meets SC-005)
2. **Reliability**: No custom scripting required, proven Netlify feature
3. **Auditability**: Full deployment history with git commit linkage
4. **Simplicity**: Web UI and CLI both support rollback

### Rollback Procedures

**Method 1: Netlify Web UI** (recommended for non-technical users)
1. Navigate to site dashboard
2. Click "Deploys" tab
3. Find previous successful deploy
4. Click "Publish deploy" button
5. Confirm rollback

**Method 2: Netlify CLI** (recommended for developers)
```bash
# List recent deployments
netlify deploy:list

# Rollback to specific deploy ID
netlify deploy:publish --prod <deploy-id>

# Or rollback to previous deploy
netlify rollback
```

**Method 3: API** (for automated rollback scripts)
```bash
# Get site ID and auth token from Netlify dashboard
curl -X POST https://api.netlify.com/api/v1/sites/{site-id}/deploys/{deploy-id}/restore \
  -H "Authorization: Bearer {token}"
```

### Deployment History Retention

**Netlify retains**:
- All successful deploys (unlimited retention)
- Failed deploys (30 days)
- Deployment logs (90 days for Pro plan)

**Git integration**:
- Each deploy linked to git commit SHA
- Can redeploy any historical commit
- Branch and PR information preserved

### Monitoring and Alerts

**Detection strategies**:
1. **Automated monitoring**: Uptime monitoring with external service (e.g., UptimeRobot, Better Uptime)
2. **Error tracking**: Frontend error logging (Sentry, LogRocket)
3. **Manual verification**: Post-deployment smoke tests

**Rollback triggers**:
- Critical API endpoint failures (5xx errors >5% of requests)
- Frontend load failures (white screen, bundle errors)
- User reports of broken functionality
- Failed post-deployment smoke tests

### Alternatives Considered

**Alternative 1: Blue-green deployment with manual switching**
- **Pros**: Test new version before making live, instant rollback
- **Cons**: Requires custom infrastructure, complexity increase
- **Rejected**: Netlify atomic deploys provide similar safety without complexity

**Alternative 2: Git revert + redeploy**
- **Pros**: Source control driven, explicit in git history
- **Cons**: Slower (requires rebuild), creates revert commits
- **Rejected**: Netlify rollback faster and cleaner

**Alternative 3: Keep multiple versions running simultaneously**
- **Pros**: Can gradually migrate traffic
- **Cons**: State synchronization complexity, cost
- **Rejected**: Overkill for current scale

### References
- [Netlify Deployment Management](https://docs.netlify.com/site-deploys/manage-deploys/)
- [Netlify API - Deploy Restore](https://open-api.netlify.com/#tag/deploy/operation/restoreSiteDeploy)
- [Atomic Deploys](https://www.netlify.com/blog/2016/09/29/atomic-deploys-for-your-website/)

---

## 8. Testing Strategy for Deployments

### Research Question
How do we validate that deployments work correctly without manual testing?

### Decision
**Implement automated smoke tests in CI/CD pipeline post-deployment**

### Rationale
1. **Early detection**: Catch deployment issues before users do
2. **Confidence**: Automated validation for every deploy
3. **Fast feedback**: Test results within 1-2 minutes of deployment
4. **Repeatability**: Same tests for production and preview deploys

### Testing Approach

**Level 1: Build Validation** (CI phase, before deployment)
- Unit tests pass (80% coverage minimum)
- Linting passes (Black, Flake8, ESLint, Prettier)
- Type checking passes (mypy, vue-tsc)
- Bundle builds successfully

**Level 2: Deployment Validation** (post-deployment, smoke tests)
```javascript
// tests/smoke/deployment.spec.js
import { test, expect } from '@playwright/test';

test('Frontend loads successfully', async ({ page }) => {
  await page.goto(process.env.DEPLOY_URL);
  await expect(page).toHaveTitle(/Weni.*Roadmap/);
  await expect(page.locator('main')).toBeVisible();
});

test('API health endpoint responds', async ({ request }) => {
  const response = await request.get(`${process.env.API_URL}/api/v1/health`);
  expect(response.status()).toBe(200);
  const data = await response.json();
  expect(data.status).toBe('healthy');
});

test('Roadmap items load', async ({ request }) => {
  const response = await request.get(`${process.env.API_URL}/api/v1/roadmap/items`);
  expect(response.status()).toBe(200);
  const data = await response.json();
  expect(data.items).toBeInstanceOf(Array);
});
```

**Level 3: Integration Testing** (preview deployments)
- Full E2E tests with Playwright/Cypress
- Test user flows (filter roadmap, expand cards, click documentation links)
- Visual regression testing (optional)

### CI/CD Pipeline Integration

```yaml
# .github/workflows/deploy.yml (example)
name: Deploy to Netlify

on:
  push:
    branches: [main, develop]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run unit tests
        run: |
          cd backend && pytest
          cd frontend && npm test
      - name: Run linters
        run: |
          cd backend && flake8
          cd frontend && npm run lint:check

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: netlify/actions/cli@master
        with:
          args: deploy --prod
      
      - name: Run smoke tests
        env:
          DEPLOY_URL: ${{ steps.deploy.outputs.url }}
        run: npm run test:smoke
```

### References
- [Netlify Build Plugins](https://docs.netlify.com/integrations/build-plugins/)
- [Playwright Testing](https://playwright.dev/)
- [Deployment Testing Best Practices](https://martinfowler.com/articles/practical-test-pyramid.html)

---

## Summary of Key Decisions

| Area | Decision | Rationale |
|------|----------|-----------|
| **Backend Architecture** | Function-per-endpoint wrappers | Maintains API contracts, optimizes cold starts |
| **Frontend Build** | Vite production build with SPA redirects | Fast builds, optimal asset optimization |
| **Environment Management** | Netlify context-based env vars | Security, flexibility, no secrets in repo |
| **Cold Starts** | Lazy imports + connection pooling | <2s cold start without function warming |
| **Background Jobs** | Netlify Scheduled Functions | Serverless-compatible, reliable scheduling |
| **Preview Deploys** | Automatic for all branches + PRs | Enable safe testing before production |
| **Rollback** | Netlify built-in deployment history | <2min rollback, simple UI/CLI |
| **Testing** | Automated smoke tests post-deploy | Fast feedback, catch issues early |

---

## Next Phase

Proceed to **Phase 1: Design & Contracts** to create:
1. `data-model.md` - Deployment configuration schemas
2. `contracts/` - Example netlify.toml files and environment variable documentation
3. `quickstart.md` - Step-by-step deployment guide

All research findings will inform the design artifacts.

