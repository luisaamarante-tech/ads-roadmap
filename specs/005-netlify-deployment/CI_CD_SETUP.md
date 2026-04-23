# CI/CD Pipeline Setup Guide

**Feature**: 005-netlify-deployment
**Last Updated**: December 29, 2025

## Overview

This guide documents the automated CI/CD pipeline configuration for Netlify deployments. The pipeline supports:
- **Production deployments**: Automatic deployment from `main` branch
- **Preview deployments**: Automatic deployment for pull requests
- **Branch deployments**: Automatic deployment for feature branches

## Configuration Status

### ✅ Frontend Configuration (T039-T041)

**File**: `frontend/netlify.toml`

**Production Context** (T039):
```toml
[context.production]
  [context.production.environment]
    VITE_API_BASE_URL = "https://roadmap-api.weni.ai"
    VITE_APP_NAME = "Weni Public Roadmap"
    VITE_APP_VERSION = "1.0.0"
    NODE_ENV = "production"
```

**Deploy Preview Context** (T040):
```toml
[context.deploy-preview]
  [context.deploy-preview.environment]
    VITE_API_BASE_URL = "https://roadmap-api-preview.netlify.app"
    VITE_APP_NAME = "Weni Roadmap (Preview)"
    NODE_ENV = "staging"
```

**Branch Deploy Context** (T041):
```toml
[context.branch-deploy]
  [context.branch-deploy.environment]
    VITE_API_BASE_URL = "https://roadmap-api-staging.netlify.app"
    VITE_APP_NAME = "Weni Roadmap (Staging)"
    NODE_ENV = "development"
```

### ✅ Backend Configuration (T042-T044)

**File**: `backend/netlify.toml`

**Production Context** (T042):
```toml
[context.production]
  [context.production.environment]
    FLASK_ENV = "production"
    LOG_LEVEL = "INFO"
    # JIRA credentials set in Netlify UI (secrets)
```

**Deploy Preview Context** (T043):
```toml
[context.deploy-preview]
  [context.deploy-preview.environment]
    FLASK_ENV = "staging"
    LOG_LEVEL = "DEBUG"
    SYNC_INTERVAL_MINUTES = "60"  # Less frequent in preview
    CACHE_TYPE = "simple"
```

**Branch Deploy Context** (T044):
```toml
[context.branch-deploy]
  [context.branch-deploy.environment]
    FLASK_ENV = "development"
    LOG_LEVEL = "DEBUG"
    SYNC_INTERVAL_MINUTES = "60"
    CACHE_TYPE = "simple"
```

## Manual Netlify UI Configuration

### T045: Enable Automatic Deployments for Frontend

1. Navigate to **Frontend Site** in Netlify dashboard
2. Go to **Site Settings > Build & deploy > Continuous Deployment**
3. **Branch deploys**:
   - Production branch: `main` ✓ (auto-enabled)
   - Branch deploy branches: Select "Let me add individual branches"
   - Add: `develop` (if exists)
4. **Deploy previews**:
   - Set to: "Any pull request against your production branch" ✓
5. **Build settings**:
   - Verify Build command: `npm ci && npm run build`
   - Verify Publish directory: `frontend/dist`
   - Verify Base directory: `frontend`
6. **Save changes**

### T046: Enable Automatic Deployments for Backend

1. Navigate to **Backend Site** in Netlify dashboard
2. Go to **Site Settings > Build & deploy > Continuous Deployment**
3. **Branch deploys**:
   - Production branch: `main` ✓ (auto-enabled)
   - Branch deploy branches: Select "Let me add individual branches"
   - Add: `develop` (if exists)
4. **Deploy previews**:
   - Set to: "Any pull request against your production branch" ✓
5. **Build settings**:
   - Verify Build command: `pip install -r requirements-prod.txt -t ./python_modules`
   - Verify Publish directory: `backend`
   - Verify Base directory: `backend`
6. **Save changes**

### T047: Configure Build Ignore Settings

Both `netlify.toml` files already include build ignore settings:

```toml
[build]
  # Skip build if no changes in this directory
  ignore = "git diff --quiet $CACHED_COMMIT_REF $COMMIT_REF -- ."
```

This prevents unnecessary builds when changes are only in the other project.

**Verification**:
- Make a change in `backend/` only → Only backend should rebuild
- Make a change in `frontend/` only → Only frontend should rebuild
- Make changes in both → Both should rebuild

## Testing the CI/CD Pipeline

### T048: Test Production Deployment

```bash
# Create a small change
echo "# Test CI/CD" >> README.md

# Commit to main branch
git add README.md
git commit -m "test(ci): verify automatic production deployment"
git push origin main

# Monitor deployment:
# 1. Check Netlify dashboard for both sites
# 2. Verify both deployments trigger
# 3. Verify deployments complete successfully
# 4. Check deployment time is under 5 minutes
```

**Expected Results**:
- Both frontend and backend trigger deployments
- Deployments use production context configurations
- Deployments complete in under 5 minutes
- Sites are accessible at production URLs

### T049: Test Preview Deployment

```bash
# Create a feature branch
git checkout -b test/preview-deployment

# Make a change
echo "Test preview deployment" >> specs/005-netlify-deployment/README.md

# Commit and push
git add specs/005-netlify-deployment/README.md
git commit -m "test(ci): verify preview deployment"
git push origin test/preview-deployment

# Create pull request on GitHub/GitLab/Bitbucket
# Monitor Netlify dashboard for deploy previews
```

**Expected Results**:
- Netlify creates deploy previews for both frontend and backend
- Preview URLs are posted as comments on the PR
- Preview deployments use `deploy-preview` context configurations
- Preview sites are accessible at unique URLs
- Preview deployments complete in under 5 minutes

**Preview URL Format**:
- Frontend: `https://deploy-preview-[PR#]--[site-name].netlify.app`
- Backend: `https://deploy-preview-[PR#]--[backend-site].netlify.app`

### T050: Test Branch Deployment

```bash
# Push to a feature branch (not PR)
git checkout -b feature/test-branch-deploy

# Make a change
echo "Test branch deployment" >> specs/005-netlify-deployment/README.md

# Commit and push
git add specs/005-netlify-deployment/README.md
git commit -m "test(ci): verify branch deployment"
git push origin feature/test-branch-deploy

# Monitor Netlify dashboard for branch deploys
```

**Expected Results**:
- Netlify creates branch deployments for both sites
- Branch deployments use `branch-deploy` context configurations
- Branch sites are accessible at branch-specific URLs
- Branch deployments complete in under 5 minutes

**Branch URL Format**:
- Frontend: `https://feature-test-branch-deploy--[site-name].netlify.app`
- Backend: `https://feature-test-branch-deploy--[backend-site].netlify.app`

### T051: Verify Deployment Completes in Under 5 Minutes

**Measurement Method**:
1. Navigate to **Netlify Dashboard > Site > Deploys**
2. Click on a recent deployment
3. Check the deployment duration in the header
4. Verify: `Build time` + `Deploy time` < 5 minutes

**Success Criteria** (SC-003):
- 95% of deployments complete in under 5 minutes
- Monitor first 20 deployments after setup
- Calculate success rate: (successful deploys < 5 min) / (total deploys) × 100%

**If deployments exceed 5 minutes**:
- Check build logs for bottlenecks
- Consider dependency caching improvements
- Review asset optimization opportunities
- Check for network issues during deployment

### T052: Document CI/CD Workflow in README.md

The CI/CD workflow documentation will be added to the main README.md file covering:
- How automatic deployments work
- Branch strategy (main = production, PRs = previews, feature branches = branch deploys)
- How to trigger deployments
- How to view deployment status
- How to access preview/branch URLs
- Troubleshooting deployment failures

## CI/CD Workflow Summary

### Deployment Triggers

| Trigger | Action | Environment | URL Pattern |
|---------|--------|-------------|-------------|
| Push to `main` | Production deploy | Production | `https://[site].netlify.app` |
| Create PR to `main` | Preview deploy | Staging | `https://deploy-preview-[#]--[site].netlify.app` |
| Push to feature branch | Branch deploy | Development | `https://[branch]--[site].netlify.app` |

### Environment Variables by Context

| Variable | Production | Deploy Preview | Branch Deploy |
|----------|-----------|----------------|---------------|
| Frontend `VITE_API_BASE_URL` | Production API | Preview API | Staging API |
| Frontend `NODE_ENV` | `production` | `staging` | `development` |
| Backend `FLASK_ENV` | `production` | `staging` | `development` |
| Backend `LOG_LEVEL` | `INFO` | `DEBUG` | `DEBUG` |
| Backend `SYNC_INTERVAL_MINUTES` | `5` | `60` | `60` |

### Build Optimization

Both projects include build ignore rules to skip unnecessary builds:
- Changes in `backend/` only → Skip frontend build
- Changes in `frontend/` only → Skip backend build
- Changes in both → Build both

This reduces build minutes usage and deployment time.

## Troubleshooting

### Deployment Not Triggering

**Symptom**: Push to main/PR created but no deployment starts

**Solutions**:
1. Check **Site Settings > Build & deploy > Deploy contexts** is enabled
2. Verify production branch is set to `main`
3. Check build ignore rules aren't blocking the build
4. Verify repository is connected in **Site Settings > Build & deploy > Link repository**

### Deployment Fails

**Symptom**: Deployment triggers but fails during build

**Solutions**:
1. Check build logs in Netlify dashboard
2. Verify build command succeeds locally
3. Check environment variables are set correctly
4. Verify dependencies install successfully
5. Check for missing files or incorrect paths

### Wrong Context Used

**Symptom**: Deployment uses wrong environment configuration

**Solutions**:
1. Verify branch name matches expected pattern
2. Check `netlify.toml` context configuration syntax
3. Verify environment variables are set for correct context
4. Clear build cache and retry deployment

## Next Steps

After completing CI/CD setup:
- ✅ Phase 5 complete - Automated deployments configured
- → Phase 6: Environment Management - Verify variables across contexts
- → Phase 7: Deployment Rollback - Test rollback procedures
- → Phase 8: Scheduled Jobs - Configure JIRA sync scheduler
- → Phase 9: Polish - Final documentation and validation

