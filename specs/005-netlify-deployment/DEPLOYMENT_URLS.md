# Deployment URLs

**Feature**: 005-netlify-deployment
**Last Updated**: December 29, 2025

## Frontend Deployment

**Status**: ⏳ Awaiting Manual Deployment

**Configuration Ready**: ✅
- `frontend/netlify.toml` configured with build settings
- `frontend/public/_redirects` configured for SPA routing
- Build tested successfully (T015 ✅)

**Manual Steps Required** (T016-T020):

### T016: Create Netlify Site for Frontend

```bash
cd frontend
netlify login
netlify init

# Follow prompts:
# - Create & configure a new site
# - Team: Select your team
# - Site name: weni-roadmap-frontend (or custom name)
# - Build settings: Auto-detected from netlify.toml
```

### T017: Configure Build Settings in Netlify UI

Navigate to: **Site Settings > Build & deploy > Build settings**

Verify the following settings are correct:
- **Base directory**: `frontend`
- **Build command**: `npm ci && npm run build`
- **Publish directory**: `frontend/dist`
- **Production branch**: `main`

### T018: Deploy Frontend to Netlify

```bash
# Option 1: Manual deployment
cd frontend
netlify deploy --prod

# Option 2: Git-based deployment (recommended)
git add .
git commit -m "feat(deploy): add Netlify frontend configuration"
git push origin main
```

### T019: Verify Frontend Deployment

After deployment completes:

1. **Visit Netlify URL**: Check that page loads without errors
2. **Test SPA Routing**: 
   - Navigate to different routes in the app
   - Refresh the page on a non-root route
   - Verify no 404 errors occur
3. **Check Browser Console**: Ensure no critical errors
4. **Verify Assets**: Check that all images, fonts, and styles load correctly

### T020: Document Deployment URL

Once deployed, record the URL below:

**Frontend URL**: `_________________________` (to be filled after deployment)

**Example**: `https://weni-roadmap-frontend.netlify.app`

---

## Backend Deployment

**Status**: ⏳ Awaiting Manual Deployment

**Configuration Ready**: ✅
- `backend/netlify.toml` configured with functions and redirects
- `backend/runtime.txt` created (Python 3.11)
- `backend/requirements-prod.txt` created (production dependencies only)
- Serverless function wrappers created:
  - `api-health.py` ✅
  - `api-roadmap-items.py` ✅
  - `api-roadmap-item.py` ✅
  - `api-roadmap-modules.py` ✅
  - `api-roadmap-stats.py` ✅

**Manual Steps Required** (T029-T038):

### T029: Create Netlify Site for Backend

```bash
cd backend
netlify login
netlify init

# Follow prompts:
# - Create & configure a new site
# - Team: Select your team
# - Site name: weni-roadmap-backend (or custom name)
# - Build settings: Auto-detected from netlify.toml
```

### T030: Configure Backend Environment Variables in Netlify UI

Navigate to: **Site Settings > Environment Variables**

Add the following variables for **all contexts** (Production, Deploy Previews, Branch deploys):

**Required Variables**:
- `JIRA_BASE_URL` = `https://your-company.atlassian.net`
- `JIRA_EMAIL` = `roadmap-sync@company.com`
- `JIRA_API_TOKEN` = `your-api-token` ✓ **Mark as Secret**

**Optional Variables** (context-specific):
- `FLASK_ENV` = `production` (production only)
- `LOG_LEVEL` = `INFO` (production), `DEBUG` (preview/branch)
- `SYNC_INTERVAL_MINUTES` = `5` (production), `60` (preview/branch)
- `CACHE_TYPE` = `simple`

### T031: Test Locally with Netlify CLI

```bash
cd backend

# Create local .env file (DO NOT COMMIT)
cat > .env << 'EOF'
JIRA_BASE_URL=https://your-company.atlassian.net
JIRA_EMAIL=roadmap-sync@company.com
JIRA_API_TOKEN=your-api-token
FLASK_ENV=development
EOF

# Start local Netlify dev environment
netlify dev
```

### T032: Verify Local Function Calls

Test each function locally:

```bash
# Health check
curl http://localhost:8888/.netlify/functions/api-health

# Expected: {"status": "healthy", ...}

# Roadmap items
curl http://localhost:8888/.netlify/functions/api-roadmap-items

# Expected: {"items": [...], ...}

# Single item (replace with actual ID)
curl http://localhost:8888/.netlify/functions/api-roadmap-item?id=ITEM-123

# Modules
curl http://localhost:8888/.netlify/functions/api-roadmap-modules

# Stats
curl http://localhost:8888/.netlify/functions/api-roadmap-stats
```

### T033: Deploy Backend to Netlify

```bash
# Option 1: Manual deployment
cd backend
netlify deploy --prod

# Option 2: Git-based deployment (recommended)
git add .
git commit -m "feat(deploy): add Netlify backend serverless functions"
git push origin main
```

### T034: Verify Backend Deployment

After deployment completes, test each API endpoint:

```bash
# Replace with your actual backend URL
BACKEND_URL="https://your-backend.netlify.app"

# Test health endpoint
curl $BACKEND_URL/.netlify/functions/api-health

# Test roadmap items
curl "$BACKEND_URL/.netlify/functions/api-roadmap-items"

# Test with filters
curl "$BACKEND_URL/.netlify/functions/api-roadmap-items?status=NOW"

# Check function logs in Netlify UI
# Navigate to: Site > Functions > Select function > View logs
```

### T035: Document Backend Deployment URL

Once deployed, record the URL below:

**Backend API URL**: `_________________________` (to be filled after deployment)

**Example**: `https://weni-roadmap-backend.netlify.app`

### T036: Update Frontend VITE_API_BASE_URL

Navigate to frontend site in Netlify UI:
1. **Site Settings > Environment Variables**
2. Find or add `VITE_API_BASE_URL`
3. Update value to your backend URL (from T035)
4. Context: **Production**
5. Save changes

### T037: Redeploy Frontend

Trigger frontend redeploy to pick up new API endpoint:

```bash
# Option 1: Trigger via Netlify UI
# Site > Deploys > Trigger deploy > Deploy site

# Option 2: Push empty commit
git commit --allow-empty -m "chore(config): update API endpoint"
git push origin main
```

### T038: Verify End-to-End Integration

1. **Visit Frontend URL** (from T020)
2. **Open Browser DevTools** > Network tab
3. **Refresh Page**
4. **Verify API Calls**:
   - Requests to `/api/v1/roadmap/items` succeed (status 200)
   - Requests to `/api/v1/roadmap/modules` succeed
   - Response data displayed correctly in UI
5. **Test Filters**: Apply different filters and verify data updates
6. **Check Console**: No critical errors

---

## Environment URLs

Once both frontend and backend are deployed, the application will be accessible at:

### Production
- **Frontend**: `https://[your-frontend-site].netlify.app`
- **Backend API**: `https://[your-backend-site].netlify.app`

### Deploy Preview (Pull Requests)
- **Frontend**: `https://deploy-preview-[PR-number]--[site-name].netlify.app`
- **Backend API**: `https://deploy-preview-[PR-number]--[backend-site].netlify.app`

### Branch Deploys
- **Frontend**: `https://[branch-name]--[site-name].netlify.app`
- **Backend API**: `https://[branch-name]--[backend-site].netlify.app`

---

## Post-Deployment Checklist

After completing manual deployment steps:

- [ ] Frontend URL accessible and functional
- [ ] Backend API URL accessible (once deployed)
- [ ] Frontend successfully connects to backend
- [ ] SPA routing works correctly (no 404 on refresh)
- [ ] All environment variables configured
- [ ] Security headers present (check with browser DevTools)
- [ ] Caching headers configured for assets

---

## Notes

- Frontend is ready for deployment (all configuration complete)
- Backend deployment will begin in Phase 4 (User Story 2)
- After backend deployment, update frontend `VITE_API_BASE_URL` environment variable in Netlify UI
- Redeploy frontend to pick up new API endpoint configuration

