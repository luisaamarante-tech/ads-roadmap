# Known Issues and Limitations

**Feature**: 005-netlify-deployment
**Last Updated**: December 29, 2025

## Current Limitations

### 1. Manual Deployment Steps Required

**Issue**: Initial deployment requires manual steps in Netlify UI

**Impact**: Cannot fully automate first-time setup

**Affected Tasks**: T016-T020 (frontend), T029-T038 (backend)

**Workaround**: Follow step-by-step instructions in:
- [`DEPLOYMENT_URLS.md`](DEPLOYMENT_URLS.md)
- [`quickstart.md`](quickstart.md)

**Future Solution**: Consider infrastructure-as-code (Terraform, Pulumi) for automated provisioning

---

### 2. APScheduler Not Compatible with Serverless

**Issue**: Background job scheduler (APScheduler) doesn't work in serverless environment

**Impact**: Must use Netlify Scheduled Functions instead

**Resolution**: ✅ Implemented
- Created `scheduled-sync.js` (replaces APScheduler)
- Created `sync-roadmap.py` (internal sync function)
- Schedule: Every 5 min (production), hourly (preview)

**Migration Note**: Existing `app/services/sync_service.py` reused with minimal changes

---

### 3. Large Bundle Size Warning

**Issue**: Frontend bundle exceeds 500 KB (Vite warning during build)

**Current Size**:
- JS: 1,961 KB uncompressed (574 KB gzipped)
- CSS: 10,489 KB uncompressed (5,596 KB gzipped)

**Impact**: Potential performance impact on slow connections

**Mitigation**: Assets are gzipped, caching configured

**Future Optimization**:
- Implement code splitting with dynamic imports
- Review Unnnic design system CSS (very large)
- Lazy load non-critical components
- Consider bundle analyzer: `npm run build -- --analyze`

---

### 4. Production Requirements.txt vs Development

**Issue**: `requirements.txt` includes dev/test dependencies

**Resolution**: ✅ Created `requirements-prod.txt`
- Excludes: pytest, black, flake8, etc.
- Reduces function cold start time
- Updated `backend/netlify.toml` to use production requirements

**Note**: Development still uses full `requirements.txt` for local testing

---

### 5. Environment Variable Management

**Issue**: No automated sync of environment variables between contexts

**Impact**: Must manually set variables in Netlify UI for each context

**Workaround**: Use [`ENV_VARIABLES_CHECKLIST.md`](ENV_VARIABLES_CHECKLIST.md) to ensure all variables set

**Future Solution**: Consider using Netlify API or CLI to script variable setup

---

### 6. CORS Configuration for Production

**Issue**: Backend `netlify.toml` currently allows CORS from any origin (`*`)

**Security Consideration**: Should be restricted to specific frontend domain in production

**Current Config**:
```toml
Access-Control-Allow-Origin = "*"  # TODO: Update to specific origin
```

**Recommended Fix**:
```toml
Access-Control-Allow-Origin = "https://roadmap.weni.ai"
```

**Action Required**: Update after frontend domain configured

---

### 7. No Automated Testing in CI/CD Pipeline

**Issue**: Deployment happens without running tests automatically

**Impact**: Could deploy broken code if tests not run locally

**Current Process**: Manual test execution before pushing

**Mitigation**: Pre-commit hooks run linters and tests locally

**Future Solution**: Add GitHub Actions / GitLab CI workflow:
- Run tests on PR creation
- Block merge if tests fail
- Run smoke tests after deployment

---

### 8. Function Cold Starts

**Issue**: First request to function (after 5+ min idle) is slow

**Expected Performance**:
- Cold start: 1.5-2.0s
- Warm start: 100-200ms

**Mitigation Implemented**:
- Lazy imports in function wrappers
- Minimal dependencies per function
- Connection pooling for JIRA client

**Future Optimization**: Function warming (if needed):
- Scheduled "ping" requests to keep functions warm
- Only for critical user-facing endpoints
- Trade-off: Increased function invocation cost

---

### 9. Build Ignore Rules May Skip Important Changes

**Issue**: Build ignore rules check only specific directory for changes

**Current Logic**:
```toml
ignore = "git diff --quiet $CACHED_COMMIT_REF $COMMIT_REF -- ."
```

**Limitation**: Changes in root directory might not trigger builds

**Example**: Updating `README.md` won't trigger frontend or backend rebuild

**Workaround**: If both need to redeploy, make a trivial change in each directory

**Considered Trade-off**: Reduces unnecessary builds vs. potential missed deployments

---

### 10. Scheduled Sync Interval Not Configurable Per Deployment

**Issue**: Sync interval hardcoded in `scheduled-sync.js`

**Current**: Production=5min, Other=60min (code-level decision)

**Limitation**: Changing interval requires code change and redeploy

**Future Enhancement**: Read interval from environment variable:
```javascript
const interval = process.env.SYNC_INTERVAL_MINUTES || 5;
```

Then configure per context in Netlify UI

---

## Edge Cases

### Concurrent Deployments

**Scenario**: Multiple commits pushed rapidly or multiple PRs created simultaneously

**Behavior**: Netlify queues deployments, processes sequentially

**Impact**: Later deployments may take longer (queued behind others)

**Mitigation**: Wait for previous deployment to complete before pushing next change

---

### Large Dataset from JIRA

**Scenario**: JIRA returns very large number of roadmap items (>1000)

**Potential Issue**: Function timeout (26s max), large response size

**Current Mitigation**: Caching reduces frequency of large fetches

**Future Enhancement**: Implement pagination in JIRA queries

---

### Deployment During Active User Session

**Scenario**: User browsing roadmap when new deployment goes live

**Behavior**: May see mixed state (old cached data + new UI)

**Mitigation**: Browser refresh loads new version completely

**Future Enhancement**: Implement service worker for cache invalidation

---

## Out of Scope (Documented in spec.md)

These items are explicitly not part of this feature:

- ❌ Custom domain configuration and DNS management
- ❌ Cost optimization strategies for Netlify plan selection
- ❌ Monitoring and alerting configuration beyond Netlify built-in
- ❌ Database setup and migration automation
- ❌ Performance optimization of application code
- ❌ Security hardening beyond Netlify's built-in features

See [`spec.md` - Scope Boundaries](spec.md#scope-boundaries) for complete list

---

## Reporting New Issues

If you discover a new issue or limitation:

1. **Document in this file**:
   - Issue description
   - Impact and workaround
   - Future solution (if known)

2. **Create ticket** (if action needed):
   - Reference this document
   - Assign priority
   - Link to related PRs

3. **Update team**:
   - Share in team chat
   - Add to sprint planning (if urgent)

---

## Related Documentation

- [spec.md](spec.md) - Original specification and requirements
- [plan.md](plan.md) - Technical approach and decisions
- [research.md](research.md) - Design decisions and alternatives considered
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Solutions for common problems

