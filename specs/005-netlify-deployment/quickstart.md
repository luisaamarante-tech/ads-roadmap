# Quickstart: Deploy to Netlify

**Feature**: 005-netlify-deployment
**Date**: December 29, 2025

## Overview

This guide walks through deploying the Weni Roadmap application (frontend + backend) to Netlify from scratch. By the end, you'll have:

- ✅ Frontend deployed as static site with SPA routing
- ✅ Backend deployed as serverless functions
- ✅ Automated deployments from git pushes
- ✅ Preview deployments for pull requests
- ✅ Environment variables configured
- ✅ Scheduled JIRA sync running

**Time estimate**: 30-45 minutes for complete setup

---

## Prerequisites

Before starting, ensure you have:

- [ ] Netlify account (sign up at [netlify.com](https://netlify.com))
- [ ] Git repository hosted on GitHub, GitLab, or Bitbucket
- [ ] JIRA API credentials (base URL, email, API token)
- [ ] Netlify CLI installed: `npm install -g netlify-cli`
- [ ] Repository cloned locally

---

## Part 1: Frontend Deployment (15 minutes)

### Step 1.1: Copy Configuration Files

```bash
# From repository root
cd frontend

# Copy the netlify.toml from contracts
cp ../specs/005-netlify-deployment/contracts/netlify.frontend.toml netlify.toml

# Create _redirects file for SPA routing
cat > public/_redirects << 'EOF'
# SPA fallback - all routes served by index.html
/*    /index.html   200
EOF
```

### Step 1.2: Update Configuration for Your Environment

Edit `frontend/netlify.toml`:

```toml
[context.production.environment]
  # Update with your backend URL (will be determined in Part 2)
  VITE_API_BASE_URL = "https://your-backend.netlify.app"
  VITE_APP_NAME = "Weni Public Roadmap"
```

**Note**: You can update `VITE_API_BASE_URL` later after deploying the backend.

### Step 1.3: Test Build Locally

```bash
# Install dependencies
npm ci

# Test production build
npm run build

# Verify dist/ directory created
ls -la dist/

# Test with Netlify dev (optional)
netlify dev
```

Expected output: Build completes successfully, `dist/` contains index.html and assets.

### Step 1.4: Deploy to Netlify

**Option A: Deploy via Netlify UI** (Recommended for first-time setup)

1. Log in to [app.netlify.com](https://app.netlify.com)
2. Click **Add new site > Import an existing project**
3. Connect your Git provider (GitHub/GitLab/Bitbucket)
4. Select the `weni-roadmap` repository
5. Configure build settings:
   - **Base directory**: `frontend`
   - **Build command**: `npm ci && npm run build`
   - **Publish directory**: `frontend/dist`
   - **Netlify.toml**: Detected automatically ✓
6. Click **Deploy site**

**Option B: Deploy via Netlify CLI**

```bash
# Login to Netlify
netlify login

# Initialize site
netlify init

# Follow prompts:
# - Create & configure a new site
# - Team: Select your team
# - Site name: weni-roadmap-frontend (or auto-generated)
# - Build settings: Detected from netlify.toml

# Deploy to production
netlify deploy --prod
```

### Step 1.5: Verify Frontend Deployment

1. Visit the deployment URL (e.g., `https://weni-roadmap-frontend.netlify.app`)
2. Check that the page loads without errors
3. Open browser console - you may see API errors (expected, backend not yet deployed)
4. Verify routing works: navigate to different paths, refresh page (should not 404)

**Troubleshooting**:
- **Build fails**: Check build logs in Netlify UI, verify `npm run build` works locally
- **White screen**: Check browser console for errors, verify assets loaded (Network tab)
- **404 on refresh**: Ensure `_redirects` file exists or redirects configured in `netlify.toml`

---

## Part 2: Backend Deployment (20 minutes)

### Step 2.1: Copy Configuration Files

```bash
# From repository root
cd backend

# Copy netlify.toml from contracts
cp ../specs/005-netlify-deployment/contracts/netlify.backend.toml netlify.toml

# Create Python version file
echo "3.11" > runtime.txt
```

### Step 2.2: Create Serverless Function Wrappers

Create the functions directory structure:

```bash
mkdir -p netlify/functions
cd netlify/functions
```

Create function wrapper for health endpoint (`api-health.py`):

```python
"""Netlify Function: Health Check Endpoint"""
import json
import sys
import os

# Add parent directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

def handler(event, context):
    """Handle GET /api/v1/health"""
    from app import create_app
    
    app = create_app()
    
    with app.test_client() as client:
        response = client.get('/api/v1/health')
        
        return {
            'statusCode': response.status_code,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
            },
            'body': response.get_data(as_text=True)
        }
```

**Repeat for other endpoints**:
- `api-roadmap-items.py` → GET /api/v1/roadmap/items
- `api-roadmap-item.py` → GET /api/v1/roadmap/items/{id}
- `api-roadmap-modules.py` → GET /api/v1/roadmap/modules
- `api-roadmap-stats.py` → GET /api/v1/roadmap/stats

**Template for other functions**:

```python
"""Netlify Function: [Description]"""
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

def handler(event, context):
    """Handle [METHOD] [PATH]"""
    from app import create_app
    
    app = create_app()
    
    # Extract request details
    method = event.get('httpMethod', 'GET')
    path = event.get('path', '/')
    query_params = event.get('queryStringParameters') or {}
    
    with app.test_client() as client:
        # Make request to Flask route
        if method == 'GET':
            response = client.get(path, query_string=query_params)
        # Add other methods as needed
        
        return {
            'statusCode': response.status_code,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
            },
            'body': response.get_data(as_text=True)
        }
```

### Step 2.3: Configure Environment Variables

**In Netlify UI**:

1. Go to **Site Settings > Environment Variables**
2. Add the following variables:

**Required (All Contexts)**:
- `JIRA_BASE_URL` = `https://your-company.atlassian.net`
- `JIRA_EMAIL` = `roadmap-sync@company.com`
- `JIRA_API_TOKEN` = `your-api-token` (mark as **Secret**)

**Optional**:
- `FLASK_ENV` = `production` (production context only)
- `LOG_LEVEL` = `INFO`
- `SYNC_INTERVAL_MINUTES` = `5` (production), `60` (deploy-preview)

**Context Selection**:
- ✓ Production
- ✓ Deploy previews
- ✓ Branch deploys

### Step 2.4: Test Locally with Netlify Dev

```bash
# From backend/ directory
cd backend

# Create local .env file (DO NOT COMMIT)
cat > .env << 'EOF'
JIRA_BASE_URL=https://your-company.atlassian.net
JIRA_EMAIL=roadmap-sync@company.com
JIRA_API_TOKEN=your-api-token
FLASK_ENV=development
EOF

# Install Netlify CLI if not already installed
npm install -g netlify-cli

# Start local Netlify dev environment
netlify dev
```

Expected output:
```
◈ Netlify Dev ◈
◈ Functions server is listening on 9999
◈ Setting up local development server
```

Test functions locally:
```bash
# Test health endpoint
curl http://localhost:8888/.netlify/functions/api-health

# Expected: {"status": "healthy", ...}
```

### Step 2.5: Deploy Backend to Netlify

**Option A: Deploy via Netlify UI**

1. In Netlify dashboard, click **Add new site**
2. Import your repository
3. Configure:
   - **Base directory**: `backend`
   - **Build command**: `pip install -r requirements.txt -t ./python_modules`
   - **Publish directory**: `backend`
   - **Functions directory**: `backend/netlify/functions`
4. Deploy!

**Option B: Deploy via CLI**

```bash
# From backend/ directory
netlify init

# Deploy
netlify deploy --prod
```

### Step 2.6: Verify Backend Deployment

```bash
# Replace with your actual backend URL
BACKEND_URL="https://weni-roadmap-backend.netlify.app"

# Test health endpoint
curl $BACKEND_URL/.netlify/functions/api-health

# Test roadmap items
curl "$BACKEND_URL/.netlify/functions/api-roadmap-items"

# Check function logs in Netlify UI
# Site > Functions > Select function > View logs
```

**Expected**: JSON responses with roadmap data.

**Troubleshooting**:
- **500 Error**: Check function logs for Python errors, verify environment variables set
- **Import errors**: Ensure `sys.path` modification in function wrappers
- **JIRA auth error**: Verify JIRA credentials in environment variables

---

## Part 3: Connect Frontend to Backend (5 minutes)

### Step 3.1: Update Frontend Environment Variable

1. Go to frontend site in Netlify UI
2. **Site Settings > Environment Variables**
3. Update `VITE_API_BASE_URL`:
   - Context: Production
   - Value: `https://your-backend.netlify.app` (from Part 2)
4. Click **Save**

### Step 3.2: Redeploy Frontend

```bash
# Trigger redeploy to pick up new environment variable
# Option 1: Push a commit to trigger auto-deploy
git commit --allow-empty -m "fix(config): update API endpoint"
git push origin main

# Option 2: Manual redeploy via UI
# Site > Deploys > Trigger deploy > Deploy site
```

### Step 3.3: Verify End-to-End

1. Visit frontend URL
2. Open browser DevTools > Network tab
3. Refresh page
4. Verify API requests succeed (status 200):
   - `/api/v1/roadmap/items`
   - `/api/v1/roadmap/modules`
5. Check roadmap items display correctly
6. Test filters (year, quarter, module, status)

---

## Part 4: Setup Scheduled Sync (10 minutes)

### Step 4.1: Create Scheduled Function

Create `backend/netlify/functions/scheduled-sync.js`:

```javascript
const { schedule } = require('@netlify/functions');

const handler = async (event) => {
  console.log('Running scheduled JIRA sync...');
  
  try {
    // Call internal sync function
    const response = await fetch(`${process.env.URL}/.netlify/functions/sync-roadmap`, {
      method: 'POST',
      headers: {
        'X-Internal-Request': 'true',
        'Content-Type': 'application/json'
      }
    });
    
    const result = await response.json();
    
    console.log('Sync completed:', result);
    
    return {
      statusCode: 200,
      body: JSON.stringify({
        message: 'Sync completed',
        result
      })
    };
  } catch (error) {
    console.error('Sync failed:', error);
    
    return {
      statusCode: 500,
      body: JSON.stringify({
        message: 'Sync failed',
        error: error.message
      })
    };
  }
};

// Run every 5 minutes in production, hourly in other contexts
const schedule_expression = process.env.CONTEXT === 'production' 
  ? '*/5 * * * *'   // Every 5 minutes
  : '0 * * * *';     // Every hour

exports.handler = schedule(schedule_expression, handler);
```

### Step 4.2: Create Internal Sync Function

Create `backend/netlify/functions/sync-roadmap.py`:

```python
"""Internal function to sync roadmap from JIRA"""
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

def handler(event, context):
    """Sync roadmap items from JIRA"""
    # Verify internal request (basic security)
    headers = event.get('headers', {})
    if headers.get('x-internal-request') != 'true':
        return {
            'statusCode': 403,
            'body': json.dumps({'error': 'Forbidden'})
        }
    
    from app.services.sync_service import sync_roadmap_items
    
    try:
        result = sync_roadmap_items()
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': True,
                'items_synced': len(result) if result else 0
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': False,
                'error': str(e)
            })
        }
```

### Step 4.3: Deploy and Verify Scheduled Function

```bash
# Deploy updated backend with scheduled function
cd backend
netlify deploy --prod

# Verify scheduled function appears in Netlify UI
# Site > Functions > Check for "scheduled-sync"

# Manually trigger sync to test (use Netlify CLI or curl)
curl -X POST https://your-backend.netlify.app/.netlify/functions/sync-roadmap \
  -H "X-Internal-Request: true"

# Check function logs for sync activity
```

---

## Part 5: Enable Preview Deployments (5 minutes)

### Step 5.1: Configure Branch Deploys

In Netlify UI for **both sites**:

1. **Site Settings > Build & deploy > Deploy contexts**
2. **Deploy previews**: Set to **Any pull request against your production branch**
3. **Branch deploys**: Set to **Let me add individual branches**
4. Add `develop` branch (if you have one)
5. Save settings

### Step 5.2: Test Preview Deployment

```bash
# Create a test feature branch
git checkout -b test-netlify-preview

# Make a trivial change
echo "# Test preview" >> README.md
git add README.md
git commit -m "test: netlify preview deployment"

# Push branch
git push origin test-netlify-preview

# Create pull request on GitHub/GitLab/Bitbucket

# Check Netlify for deploy preview
# Should see comment on PR with preview URL
```

### Step 5.3: Verify Preview Features

1. Click preview URL in PR comment
2. Verify application loads
3. Check that preview uses staging environment variables
4. Confirm independent from production (can test breaking changes safely)

---

## Part 6: Post-Deployment Checklist

### Verification

- [ ] Frontend loads at production URL
- [ ] Backend functions respond correctly
- [ ] API calls from frontend to backend succeed
- [ ] Roadmap items display correctly
- [ ] Filters work (year, quarter, module, status)
- [ ] Scheduled sync runs every 5 minutes (check logs)
- [ ] Preview deployments work for pull requests
- [ ] Branch deployments work for feature branches
- [ ] Environment variables set correctly for all contexts
- [ ] No secrets exposed in frontend bundle (check devtools > Sources)

### Performance

- [ ] Frontend Lighthouse score > 90
- [ ] API responses < 2 seconds (cold start)
- [ ] API responses < 200ms (warm start)
- [ ] Build time < 5 minutes
- [ ] Deployment time < 2 minutes

### Security

- [ ] HTTPS enabled (automatic with Netlify)
- [ ] Security headers configured (X-Frame-Options, CSP, etc.)
- [ ] CORS configured correctly
- [ ] API tokens marked as secrets in Netlify UI
- [ ] No credentials in git history

---

## Part 7: Rollback Procedure

If you need to rollback a deployment:

### Via Netlify UI

1. Go to **Site > Deploys**
2. Find the previous working deploy
3. Click **Publish deploy** button
4. Confirm rollback

**Time**: ~1-2 minutes

### Via Netlify CLI

```bash
# List recent deployments
netlify deploy:list

# Publish a specific deploy
netlify deploy:publish <deploy-id>

# Or use the rollback command
netlify rollback
```

---

## Part 8: Monitoring & Maintenance

### Daily Monitoring

Check Netlify dashboard for:
- Deploy success rate (should be >95%)
- Function error rate (should be <1%)
- Build duration (should be <5 minutes)

### Weekly Tasks

- Review function logs for errors
- Check JIRA sync success rate
- Monitor Lighthouse scores
- Review preview deployment usage

### Monthly Tasks

- Rotate JIRA API token (security best practice)
- Review and optimize function cold start times
- Clean up old branch deployments
- Update dependencies (frontend + backend)

---

## Troubleshooting Guide

### Problem: Build Fails

**Symptoms**: Deployment shows "Build failed" in Netlify UI

**Solutions**:
1. Check build logs in Netlify UI
2. Verify `npm run build` (frontend) or `pip install` (backend) works locally
3. Check for missing environment variables
4. Verify `netlify.toml` syntax (validate with schema)

### Problem: Functions Return 500 Error

**Symptoms**: API calls fail with 500 Internal Server Error

**Solutions**:
1. Check function logs in Netlify UI (Site > Functions > [function-name] > Logs)
2. Verify environment variables set for backend
3. Test JIRA credentials manually
4. Check Python import paths in function wrappers
5. Verify `app/` directory included in function bundle

### Problem: Frontend Shows API Errors

**Symptoms**: Console shows "Network Error" or "CORS Error"

**Solutions**:
1. Verify `VITE_API_BASE_URL` set correctly in frontend env vars
2. Check backend is deployed and accessible
3. Verify CORS headers in backend `netlify.toml`
4. Test API endpoint directly with curl
5. Check browser network tab for exact error

### Problem: Scheduled Sync Not Running

**Symptoms**: Data not updating from JIRA

**Solutions**:
1. Check scheduled function logs
2. Verify function listed in Netlify UI under Functions
3. Test manual sync: `curl -X POST [backend-url]/.netlify/functions/sync-roadmap`
4. Check JIRA credentials valid
5. Verify `schedule` expression in function code

---

## Additional Resources

- [Netlify Documentation](https://docs.netlify.com/)
- [Netlify Functions](https://docs.netlify.com/functions/overview/)
- [Netlify CLI Reference](https://cli.netlify.com/)
- [Vite Environment Variables](https://vitejs.dev/guide/env-and-mode.html)
- [JIRA Cloud REST API](https://developer.atlassian.com/cloud/jira/platform/rest/v3/)

---

## Success!

If all verification steps pass, your application is successfully deployed to Netlify! 🎉

**Next steps**:
- Set up custom domain (if needed)
- Configure monitoring and alerts
- Document deployment process for your team
- Create runbook for common issues

**Need help?** Check the troubleshooting guide above or consult:
- [spec.md](spec.md) - Feature requirements
- [research.md](research.md) - Technical decisions
- [data-model.md](data-model.md) - Configuration schemas
- [environment-variables.md](contracts/environment-variables.md) - Environment variable reference

