# Troubleshooting Guide

**Feature**: 005-netlify-deployment
**Last Updated**: December 29, 2025

## Common Issues and Solutions

### Build Failures

#### Frontend Build Fails

**Symptom**: `npm run build` fails during Netlify deployment

**Common Causes**:
1. TypeScript type errors
2. Missing environment variables
3. Dependency installation failed
4. Out of memory during build

**Solutions**:
```bash
# Test build locally
cd frontend
npm ci
npm run build

# Check for errors
npm run type-check

# If build succeeds locally, check Netlify build logs for differences
```

#### Backend Build Fails

**Symptom**: `pip install` fails during Netlify deployment

**Common Causes**:
1. Incompatible Python version
2. Missing system dependencies
3. requirements.txt syntax error

**Solutions**:
- Verify `runtime.txt` specifies Python 3.11
- Check `requirements-prod.txt` for syntax errors
- Review Netlify build logs for specific error

### Deployment Failures

#### Functions Not Accessible

**Symptom**: 404 error when calling `/.netlify/functions/api-health`

**Causes & Solutions**:

1. **Function didn't deploy**: Check Netlify UI > Functions tab
2. **Path incorrect**: Functions are at `/.netlify/functions/{name}`, not `/api/v1/*`
3. **Redirects not working**: Check `netlify.toml` redirects configuration

**Test**:
```bash
# Direct function access (should always work if deployed)
curl https://your-site.netlify.app/.netlify/functions/api-health

# Via redirect (requires netlify.toml redirects)
curl https://your-site.netlify.app/api/v1/health
```

#### Environment Variables Not Applied

**Symptom**: Function errors about missing JIRA credentials

**Solutions**:
1. Verify variables set in Netlify UI for correct context
2. Check variable names match exactly (case-sensitive)
3. Redeploy after setting variables (variables apply to new deploys)
4. Clear build cache: Site Settings > Build & deploy > Clear cache

### Runtime Issues

#### CORS Errors

**Symptom**: Browser console shows CORS policy errors when calling API

**Causes**:
1. CORS headers not configured in `backend/netlify.toml`
2. Frontend calling wrong backend URL
3. OPTIONS preflight requests failing

**Solutions**:
```toml
# Verify in backend/netlify.toml:
[[headers]]
  for = "/api/*"
  [headers.values]
    Access-Control-Allow-Origin = "*"
    Access-Control-Allow-Methods = "GET, POST, OPTIONS"
    Access-Control-Allow-Headers = "Content-Type, Authorization"
```

#### Function Timeout

**Symptom**: Function execution exceeds 10 seconds (Netlify limit)

**Solutions**:
1. Optimize JIRA API calls (reduce data fetched)
2. Implement caching to reduce external API calls
3. Break large operations into smaller functions
4. Consider upgrading Netlify plan for longer timeout (up to 26s)

#### Cold Start Latency

**Symptom**: First request to function takes >2 seconds

**Solutions**:
1. Optimize imports (lazy load heavy dependencies)
2. Reduce function code size
3. Use connection pooling for external services
4. Consider function warming for critical endpoints

### Data Issues

#### Roadmap Data Not Updating

**Symptom**: Frontend shows stale data

**Causes & Solutions**:

1. **Scheduled sync not running**:
   - Check Netlify UI > Functions > scheduled-sync logs
   - Verify schedule configuration in code
   - Manually trigger sync to test

2. **JIRA credentials invalid**:
   - Test credentials: `curl -u email:token https://your-jira.atlassian.net/rest/api/3/myself`
   - Regenerate API token if expired
   - Update JIRA_API_TOKEN in Netlify UI

3. **Cache not cleared**:
   - Sync function updates cache
   - Frontend fetches from cache
   - Verify cache file location accessible to functions

#### Empty Roadmap Display

**Symptom**: Frontend loads but shows no items

**Causes**:
1. No items marked as public in JIRA
2. JIRA project configuration incorrect
3. Sync never ran successfully
4. Filter removing all items

**Debug**:
```bash
# Check API response
curl https://your-backend.netlify.app/.netlify/functions/api-roadmap-items

# Should return: {"items": [...], "count": N}
# If count is 0, check JIRA configuration
```

## Performance Issues

### Slow Page Load

**Causes & Solutions**:

1. **Large assets**: Check bundle size in build logs
   - Solution: Code splitting, lazy loading
   - Check: Frontend dist/ directory size

2. **API slow**: Check function execution time in logs
   - Solution: Implement caching, optimize queries
   - Check: Netlify Functions > View logs > Duration

3. **Too many API calls**: Check Network tab in DevTools
   - Solution: Batch requests, implement pagination
   - Check: Number of requests on page load

### Build Time Too Long

**Symptom**: Builds exceed 5 minutes (violates SC-003)

**Solutions**:
1. Enable dependency caching in Netlify
2. Use `npm ci` instead of `npm install`
3. Minimize dependencies in requirements-prod.txt
4. Use build ignore rules to skip unnecessary builds

## Security Issues

### Secrets Exposed

**Critical**: Immediately rotate any exposed secrets

**Prevention**:
1. Never prefix backend secrets with `VITE_` (frontend embeds these)
2. Always mark secrets as "Secret" in Netlify UI
3. Never commit .env files to git
4. Regularly audit frontend bundle (DevTools > Sources)

**Rotation Steps**:
1. Generate new JIRA API token
2. Update JIRA_API_TOKEN in Netlify UI
3. Redeploy both frontend and backend
4. Verify old token no longer works

## Monitoring and Debugging

### View Function Logs

```bash
# Via Netlify CLI
netlify functions:list
netlify functions:invoke api-health

# Via Netlify UI
Site > Functions > [function-name] > View logs
```

### Test Locally

```bash
# Backend with Netlify Dev
cd backend
netlify dev

# Test function
curl http://localhost:8888/.netlify/functions/api-health

# Frontend with Vite dev server
cd frontend
npm run dev
```

### Check Deployment Status

```bash
# Via Netlify CLI
netlify status
netlify deploy:list

# Via Netlify UI
Site > Deploys > [deployment] > Deploy log
```

## Getting Help

### Documentation References
- [specs/005-netlify-deployment/quickstart.md](quickstart.md) - Deployment guide
- [specs/005-netlify-deployment/DEPLOYMENT_URLS.md](DEPLOYMENT_URLS.md) - Manual steps
- [specs/005-netlify-deployment/ROLLBACK_RUNBOOK.md](ROLLBACK_RUNBOOK.md) - Rollback procedures
- [contracts/environment-variables.md](contracts/environment-variables.md) - Variable reference

### External Resources
- [Netlify Functions Documentation](https://docs.netlify.com/functions/overview/)
- [Netlify Build Documentation](https://docs.netlify.com/configure-builds/overview/)
- [Netlify Support Forum](https://answers.netlify.com/)

### Internal Support
- Check team documentation wiki
- Post in team Slack #deployments channel
- Contact DevOps team for infrastructure issues

