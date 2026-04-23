# Performance Metrics

**Feature**: 005-netlify-deployment
**Last Updated**: December 29, 2025

## Deployment Performance Targets

Based on Success Criteria from [spec.md](spec.md):

| Metric | Target | Success Criteria |
|--------|--------|------------------|
| Frontend initial deployment | < 10 minutes | SC-001 |
| Backend initial deployment | < 15 minutes | SC-002 |
| Automated deployment | < 5 minutes (95%) | SC-003 |
| Deployment success rate | > 95% | SC-004 |
| Rollback time | < 2 minutes | SC-005 |
| Preview deployment | < 5 minutes | SC-008 |

## Frontend Performance

### Build Metrics

**Measured during T015**:
```
Build Time: 2.29s ✅
Bundle Size:
  - index.html: 0.46 kB
  - CSS: 10,488.70 kB (gzipped: 5,595.82 kB)
  - JS: 1,961.10 kB (gzipped: 573.78 kB)
  - Images: 4,403.59 kB (apple logo)

Total: ~16.9 MB uncompressed, ~10.6 MB gzipped
```

**Optimization Opportunities**:
- ⚠️ Large JS bundle (>500 kB warning from Vite)
- Consider code splitting with dynamic imports
- Evaluate need for large design system CSS

### Runtime Performance (Lighthouse)

**Targets**:
- Performance score: > 90
- First Contentful Paint (FCP): < 1.8s
- Largest Contentful Paint (LCP): < 2.5s
- Time to Interactive (TTI): < 3.8s
- Cumulative Layout Shift (CLS): < 0.1

**To Measure** (T090):
```bash
# Run Lighthouse audit
npx lighthouse https://your-frontend.netlify.app --view

# Or use Netlify Analytics (built-in)
# Site > Analytics > Performance
```

## Backend Performance

### Function Cold Start Times

**Target** (from research.md):
- Cold start: < 2 seconds
- Warm start: < 200ms

**Measurement Method** (T091):
```bash
# Cold start: Wait 5 minutes for function to cool down
# Then measure first request
time curl https://your-backend.netlify.app/.netlify/functions/api-health

# Warm start: Immediate follow-up request
time curl https://your-backend.netlify.app/.netlify/functions/api-health
```

**Expected Results**:
```
Cold Start: ~1.5-2.0s
Warm Start: ~100-200ms
```

### Function Execution Times

**By Endpoint**:

| Endpoint | Expected | Maximum |
|----------|----------|---------|
| `/api/v1/health` | < 100ms | 500ms |
| `/api/v1/roadmap/items` | < 1s | 5s |
| `/api/v1/roadmap/items/{id}` | < 200ms | 1s |
| `/api/v1/roadmap/modules` | < 200ms | 1s |
| `/api/v1/roadmap/stats` | < 500ms | 2s |
| `sync-roadmap` (internal) | < 10s | 26s (Netlify limit) |

**Monitoring**:
- Check Netlify Functions > View logs > Duration column
- Set up alerts for execution time > 5s

## Build Performance

### Deployment Time Breakdown (T092)

**Typical Deployment Timeline**:

**Frontend**:
```
1. Build trigger: 0s
2. Install dependencies (npm ci): 30-60s
3. Build (npm run build): 2-3s
4. Deploy assets: 10-20s
5. Post-processing: 5-10s
Total: ~50-95s ✅
```

**Backend**:
```
1. Build trigger: 0s
2. Install dependencies (pip install): 60-90s
3. Package functions: 10-20s
4. Deploy functions: 20-30s
5. Post-processing: 10-20s
Total: ~100-160s ✅
```

Both well under 5-minute target ✅

### Build Optimization Strategies

**Implemented**:
- ✅ `npm ci` instead of `npm install` (uses package-lock.json)
- ✅ Production dependencies only (`requirements-prod.txt`)
- ✅ Build ignore rules (skip build if no changes)
- ✅ Dependency caching (Netlify automatic)

**Future Optimizations**:
- Consider asset optimization plugins
- Implement incremental builds if available
- Monitor and reduce bundle size over time

## Resource Usage

### Netlify Plan Limits

**Free Tier**:
- Build minutes: 300/month
- Bandwidth: 100 GB/month
- Functions: 125K invocations, 100 hours runtime/month

**Pro Tier** (recommended):
- Build minutes: 25,000/month
- Bandwidth: 1 TB/month
- Functions: Unlimited invocations, 100 hours runtime/month
- Function timeout: Up to 26 seconds (vs 10s free tier)

### Estimated Usage

**Build Minutes**:
- Frontend: ~1.5 min/deploy
- Backend: ~2.5 min/deploy
- Total: ~4 min/deploy
- Estimated deploys: 50/month
- Usage: ~200 build minutes/month ✅ (within free tier)

**Bandwidth**:
- Average page load: ~11 MB (uncompressed)
- Estimated users: 100/month
- Usage: ~1.1 GB/month ✅ (well within free tier)

**Function Invocations**:
- API calls per user session: ~5
- Users: 100/month
- Scheduled sync: 8,640/month (every 5 min)
- Total: ~9,140/month ✅ (within free tier)

**Function Runtime**:
- API call duration: 0.5s average
- Scheduled sync: 5s average
- Monthly: (500×0.5s + 8640×5s) = ~12.25 hours ✅ (within free tier)

## Performance Monitoring

### Automated Monitoring Setup

**Recommended Services**:

1. **Netlify Analytics** (built-in):
   - Page views, bandwidth, function invocations
   - Performance metrics per page
   - Enable: Site Settings > Analytics

2. **Uptime Monitoring**:
   - Service: UptimeRobot, Better Uptime
   - Check frequency: Every 5 minutes
   - Endpoints:
     - Frontend: `https://your-frontend.netlify.app`
     - Backend health: `https://your-backend.netlify.app/.netlify/functions/api-health`

3. **Error Tracking**:
   - Frontend: Sentry, LogRocket
   - Backend: Check Netlify Function logs
   - Alert on error rate > 1%

### Performance Dashboard

**Key Metrics to Track**:
- Deployment success rate (target: >95%)
- Average deployment time (target: <5 min)
- Average API response time (target: <1s)
- Function cold start percentage (target: <10% of requests)
- Error rate (target: <1%)

**Monthly Review**:
- Review performance trends
- Identify optimization opportunities
- Check resource usage vs plan limits
- Adjust monitoring thresholds

## Performance Checklist

Post-deployment performance validation:

- [ ] Frontend Lighthouse score > 90
- [ ] Backend function cold start < 2s
- [ ] Backend function warm start < 200ms
- [ ] API response times within targets
- [ ] Build times < 5 minutes
- [ ] Deployment success rate > 95%
- [ ] Rollback tested and < 2 minutes
- [ ] Preview deployments < 5 minutes
- [ ] Resource usage within plan limits
- [ ] Monitoring and alerts configured

## References

- Success Criteria: [spec.md](spec.md) (SC-001 through SC-008)
- Research findings: [research.md](research.md) (Cold start optimization section)
- Build configuration: `frontend/netlify.toml`, `backend/netlify.toml`

