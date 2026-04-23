# Environment Variables Checklist

**Feature**: 005-netlify-deployment
**Last Updated**: December 29, 2025
**Reference**: See [contracts/environment-variables.md](contracts/environment-variables.md) for detailed documentation

## Purpose

This checklist ensures all required environment variables are configured correctly across all deployment contexts.

## Backend Environment Variables

### ✅ Production Context

Navigate to: **Backend Site > Site Settings > Environment Variables**

**Required Variables** (mark context: Production):
- [ ] `JIRA_BASE_URL` = `https://your-company.atlassian.net`
- [ ] `JIRA_EMAIL` = `roadmap-sync@company.com`
- [ ] `JIRA_API_TOKEN` = `***` ✓ Mark as Secret
- [ ] `FLASK_ENV` = `production`
- [ ] `LOG_LEVEL` = `INFO`

**Optional Variables** (production):
- [ ] `SYNC_INTERVAL_MINUTES` = `5`
- [ ] `CACHE_TYPE` = `simple` (or `redis`)
- [ ] `REDIS_URL` = `***` (if using Redis) ✓ Mark as Secret

### ✅ Deploy Preview Context

**Required Variables** (mark context: Deploy previews):
- [ ] `JIRA_BASE_URL` = `https://your-company.atlassian.net`
- [ ] `JIRA_EMAIL` = `roadmap-sync@company.com`  
- [ ] `JIRA_API_TOKEN` = `***` ✓ Mark as Secret
- [ ] `FLASK_ENV` = `staging`
- [ ] `LOG_LEVEL` = `DEBUG`
- [ ] `SYNC_INTERVAL_MINUTES` = `60`
- [ ] `CACHE_TYPE` = `simple`

### ✅ Branch Deploy Context

**Required Variables** (mark context: Branch deploys):
- [ ] `JIRA_BASE_URL` = `https://your-company.atlassian.net`
- [ ] `JIRA_EMAIL` = `roadmap-sync@company.com`
- [ ] `JIRA_API_TOKEN` = `***` ✓ Mark as Secret
- [ ] `FLASK_ENV` = `development`
- [ ] `LOG_LEVEL` = `DEBUG`
- [ ] `SYNC_INTERVAL_MINUTES` = `60`
- [ ] `CACHE_TYPE` = `simple`

## Frontend Environment Variables

### ✅ Production Context

Navigate to: **Frontend Site > Site Settings > Environment Variables**

**Required Variables** (mark context: Production):
- [ ] `VITE_API_BASE_URL` = `https://your-backend.netlify.app`
- [ ] `VITE_WEBCHAT_CHANNEL_UUID` = `your-webchat-channel-uuid`
- [ ] `VITE_APP_NAME` = `Weni Public Roadmap`
- [ ] `VITE_APP_VERSION` = `1.0.0`
- [ ] `NODE_ENV` = `production`

**Optional Variables** (mark context: Production):
- [ ] `VITE_WEBCHAT_SOCKET_URL` = `https://websocket.weni.ai`
- [ ] `VITE_WEBCHAT_HOST` = `https://flows.weni.ai`

### ✅ Deploy Preview Context

**Required Variables** (mark context: Deploy previews):
- [ ] `VITE_API_BASE_URL` = `https://deploy-preview-XX--your-backend.netlify.app` (or staging backend)
- [ ] `VITE_WEBCHAT_CHANNEL_UUID` = `your-webchat-channel-uuid`
- [ ] `VITE_APP_NAME` = `Weni Roadmap (Preview)`
- [ ] `NODE_ENV` = `staging`

**Optional Variables** (mark context: Deploy previews):
- [ ] `VITE_WEBCHAT_SOCKET_URL` = `https://websocket.weni.ai`
- [ ] `VITE_WEBCHAT_HOST` = `https://flows.weni.ai`

### ✅ Branch Deploy Context

**Required Variables** (mark context: Branch deploys):
- [ ] `VITE_API_BASE_URL` = `https://roadmap-api-staging.netlify.app`
- [ ] `VITE_WEBCHAT_CHANNEL_UUID` = `your-webchat-channel-uuid`
- [ ] `VITE_APP_NAME` = `Weni Roadmap (Staging)`
- [ ] `NODE_ENV` = `development`

**Optional Variables** (mark context: Branch deploys):
- [ ] `VITE_WEBCHAT_SOCKET_URL` = `https://websocket.weni.ai`
- [ ] `VITE_WEBCHAT_HOST` = `https://flows.weni.ai`

## Validation Steps

### Backend Variable Validation (T058)

Test that backend functions validate required variables on startup:

```bash
# Test with missing variable (should fail with clear error)
curl https://your-backend.netlify.app/.netlify/functions/api-health

# Expected if variables missing:
# {"error": "Missing required environment variable: JIRA_BASE_URL"}

# Test with all variables set (should succeed)
# Expected: {"status": "healthy", ...}
```

### Frontend Variable Validation (T059)

Check frontend build fails if required variables missing:

```bash
cd frontend

# Test build without VITE_API_BASE_URL
unset VITE_API_BASE_URL
npm run build

# Expected: Build should fail or warn about missing variable
```

### Production Context Validation (T061)

After setting production variables:

```bash
# Deploy to production
git push origin main

# Wait for deployment
# Check function logs in Netlify UI

# Verify production config in logs:
# - FLASK_ENV=production
# - LOG_LEVEL=INFO
# - SYNC_INTERVAL_MINUTES=5
```

### Preview Context Validation (T062)

After setting preview variables:

```bash
# Create a PR
# Wait for preview deployment

# Check preview function logs
# Verify staging config:
# - FLASK_ENV=staging
# - LOG_LEVEL=DEBUG
# - SYNC_INTERVAL_MINUTES=60
```

### Secret Exposure Check (T063)

**Critical Security Check**:

1. **Frontend Bundle Inspection**:
   ```bash
   # Visit frontend site
   # Open DevTools > Sources tab
   # Navigate to /assets/index-*.js
   # Search for "JIRA_API_TOKEN"
   # Expected: NOT FOUND
   ```

2. **Backend Function Inspection**:
   ```bash
   # Check function response
   curl https://your-backend.netlify.app/.netlify/functions/api-health
   # Expected: No JIRA credentials in response body or headers
   ```

3. **Build Logs Inspection**:
   ```bash
   # In Netlify UI: Site > Deploys > [deployment] > Deploy log
   # Search for "JIRA_API_TOKEN"
   # Expected: Should be masked as ***
   ```

## Troubleshooting

### Variables Not Applied

**Symptom**: Deployment uses old or default values

**Solutions**:
1. Verify variables saved in Netlify UI
2. Check correct context is selected (Production/Deploy Preview/Branch Deploy)
3. Trigger new deployment after setting variables
4. Clear build cache: Site Settings > Build & deploy > Clear cache

### Secrets Exposed

**Symptom**: Secret values visible in logs or frontend

**Solutions**:
1. Immediately rotate exposed secrets (generate new JIRA API token)
2. Verify "Secret" checkbox is checked for sensitive variables
3. Ensure backend secrets are NOT prefixed with `VITE_`
4. Redeploy after fixing configuration

### Build Failures

**Symptom**: Build fails with "environment variable not found"

**Solutions**:
1. Check variable name spelling (case-sensitive)
2. Verify variable set for correct deployment context
3. Check netlify.toml [context.*] configuration
4. Review build logs for specific missing variable

## Post-Configuration Checklist

After completing all variable setup:

- [ ] All backend production variables configured and tested
- [ ] All backend preview variables configured and tested
- [ ] All backend branch deploy variables configured and tested
- [ ] All frontend production variables configured and tested
- [ ] All frontend preview variables configured and tested
- [ ] All frontend branch deploy variables configured and tested
- [ ] Secret variables marked as "Secret" in Netlify UI
- [ ] No secrets exposed in frontend bundle (verified)
- [ ] No secrets exposed in backend responses (verified)
- [ ] All deployment contexts tested and working
- [ ] .env.example files created for local development
- [ ] Documentation updated with actual (non-secret) values

## References

- [Netlify Environment Variables Documentation](https://docs.netlify.com/environment-variables/overview/)
- [Vite Environment Variables Guide](https://vitejs.dev/guide/env-and-mode.html)
- [contracts/environment-variables.md](contracts/environment-variables.md) - Comprehensive variable reference

