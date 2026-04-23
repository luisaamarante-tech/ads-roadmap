# Deployment Rollback Runbook

**Feature**: 005-netlify-deployment
**Last Updated**: December 29, 2025
**Success Criteria**: Rollback completes in under 2 minutes (SC-005)

## Overview

This runbook provides step-by-step procedures for rolling back deployments when issues are detected in production.

## When to Rollback

### Immediate Rollback Scenarios

Roll back immediately if you observe:
- ❌ **Critical API failures**: 5xx errors > 5% of requests
- ❌ **Frontend load failures**: White screen, bundle errors, blank page
- ❌ **Data corruption**: Incorrect data displayed to users
- ❌ **Security vulnerabilities**: Exposed secrets, authentication bypass
- ❌ **Complete service outage**: Site inaccessible or functions timing out

### Investigate Before Rollback

Consider investigating first (don't rollback immediately) if:
- ⚠️ Minor UI glitches that don't affect core functionality
- ⚠️ Non-critical feature broken but main features work
- ⚠️ Slow performance but site is functional
- ⚠️ Single user reports issue (may be user-specific)

## Rollback Methods

### Method 1: Netlify UI (Recommended for Non-Technical Users)

**Time**: ~1-2 minutes

**Steps**:

1. **Navigate to Deployment History**:
   - Log in to [Netlify Dashboard](https://app.netlify.com)
   - Select the affected site (Frontend or Backend)
   - Click **Deploys** tab

2. **Identify Target Deployment**:
   - Review deployment list (newest at top)
   - Find the last known working deployment
   - Check deploy timestamp and commit message
   - Verify deploy status shows "Published" (green checkmark)

3. **Execute Rollback**:
   - Click on the target deployment
   - Click the **Publish deploy** button
   - Confirm the action when prompted
   - Wait for "Publishing..." to complete (~30-60 seconds)

4. **Verify Rollback**:
   - Visit the site URL
   - Test critical functionality
   - Check error rates in monitoring dashboard
   - Confirm issue is resolved

**Time Checkpoint**: Rollback should complete in under 2 minutes ✓

### Method 2: Netlify CLI (Recommended for Developers)

**Time**: ~1-2 minutes

**Prerequisites**:
- Netlify CLI installed: `npm install -g netlify-cli`
- Authenticated: `netlify login`

**Steps**:

1. **List Recent Deployments**:
   ```bash
   # Navigate to project directory
   cd /path/to/weni-roadmap/frontend  # or backend
   
   # List deployments
   netlify deploy:list
   
   # Output shows:
   # Deploy ID | Created | Status | URL
   # abc123... | 2h ago  | ready  | https://...
   # def456... | 1d ago  | ready  | https://...
   ```

2. **Identify Target Deployment ID**:
   - Find the last working deployment
   - Copy the Deploy ID (e.g., `def456...`)

3. **Execute Rollback**:
   ```bash
   # Publish the previous deployment
   netlify deploy:publish def456...
   
   # Or use interactive rollback
   netlify rollback
   ```

4. **Verify Rollback**:
   ```bash
   # Check current live deploy
   netlify status
   
   # Test the site
   curl https://your-site.netlify.app/api/v1/health
   ```

**Time Checkpoint**: Rollback should complete in under 2 minutes ✓

### Method 3: Netlify API (For Automation/Scripts)

**Time**: ~30-60 seconds

**Prerequisites**:
- Netlify Personal Access Token
- Site ID and Deploy ID

**Steps**:

1. **Get Netlify Personal Access Token**:
   - Navigate to [User Settings > Applications](https://app.netlify.com/user/applications)
   - Click **New access token**
   - Copy token (save securely)

2. **Get Site ID**:
   ```bash
   # Via Netlify CLI
   netlify sites:list
   
   # Or from Netlify UI: Site Settings > General > Site details
   ```

3. **Execute Rollback via API**:
   ```bash
   # Set variables
   SITE_ID="your-site-id"
   DEPLOY_ID="target-deploy-id"
   TOKEN="your-access-token"
   
   # Restore deployment
   curl -X POST \
     "https://api.netlify.com/api/v1/sites/${SITE_ID}/deploys/${DEPLOY_ID}/restore" \
     -H "Authorization: Bearer ${TOKEN}"
   ```

4. **Verify Rollback**:
   ```bash
   # Check current production deploy
   curl "https://api.netlify.com/api/v1/sites/${SITE_ID}" \
     -H "Authorization: Bearer ${TOKEN}" \
     | jq '.published_deploy.id'
   
   # Should match DEPLOY_ID
   ```

## Rollback Decision Matrix

| Issue Severity | Affected Users | Action | Method |
|----------------|----------------|--------|--------|
| Critical | All users | Immediate rollback | Netlify UI or CLI |
| High | >50% users | Rollback within 5 min | Netlify UI or CLI |
| Medium | <50% users | Investigate first | Hold, monitor |
| Low | Few users | Fix forward | Deploy hotfix |

## Post-Rollback Actions

### Immediate (Within 5 Minutes)

1. **Notify Stakeholders**:
   - [ ] Post in team Slack/chat: "Production rolled back to previous version"
   - [ ] Include: What was rolled back, why, when normal service resumed
   - [ ] Example: "Frontend rolled back to 2h ago deploy due to API errors. Service restored."

2. **Verify Service Health**:
   - [ ] Frontend loads correctly
   - [ ] Backend API responds correctly
   - [ ] Error rates returned to normal
   - [ ] Monitor for 10 minutes to ensure stability

3. **Document Incident**:
   - [ ] Create incident log entry
   - [ ] Note: What failed, when detected, rollback time, current status

### Short Term (Within 1 Hour)

1. **Root Cause Analysis**:
   - [ ] Review deployment diff between failed and working versions
   - [ ] Check deployment logs for errors
   - [ ] Identify specific commit/change that caused issue
   - [ ] Test failed deployment in staging/preview environment

2. **Create Fix**:
   - [ ] Open bug ticket with root cause details
   - [ ] Create hotfix branch if urgent
   - [ ] Implement fix with tests
   - [ ] Deploy to preview environment first

### Long Term (Within 1 Day)

1. **Prevention**:
   - [ ] Add automated tests to catch similar issues
   - [ ] Update deployment checklist
   - [ ] Review monitoring and alerting setup
   - [ ] Document lessons learned

2. **Communication**:
   - [ ] Post-mortem document (if critical incident)
   - [ ] Share learnings with team
   - [ ] Update runbooks if needed

## Rollback Testing Procedures

### T069: Test Frontend Rollback

**Objective**: Verify frontend rollback completes in under 2 minutes

**Steps**:

1. **Deploy Breaking Change**:
   ```bash
   cd frontend/src
   # Introduce syntax error
   echo "INTENTIONAL_ERROR!!!" >> App.vue
   git add App.vue
   git commit -m "test: intentional error for rollback testing"
   git push origin main
   ```

2. **Wait for Deployment**:
   - Monitor Netlify dashboard
   - Deployment will likely fail or site will be broken

3. **Execute Rollback**:
   - Start timer ⏱️
   - Use Netlify UI rollback method (Method 1 above)
   - Stop timer when site is restored

4. **Verify**:
   - [ ] Site loads correctly
   - [ ] Rollback completed in under 2 minutes ✓
   - [ ] No errors in console

5. **Cleanup**:
   ```bash
   git revert HEAD
   git push origin main
   ```

### T070: Test Backend Rollback

**Objective**: Verify backend rollback completes in under 2 minutes

**Steps**:

1. **Deploy Breaking Change**:
   ```bash
   cd backend/netlify/functions
   # Introduce API error
   echo "raise Exception('Test rollback')" >> api-health.py
   git add api-health.py
   git commit -m "test: intentional error for rollback testing"
   git push origin main
   ```

2. **Wait for Deployment & Test**:
   ```bash
   # Test API (will fail)
   curl https://your-backend.netlify.app/.netlify/functions/api-health
   # Expected: 500 error
   ```

3. **Execute Rollback**:
   - Start timer ⏱️
   - Use Netlify CLI rollback method (Method 2 above)
   - Stop timer when API is restored

4. **Verify**:
   ```bash
   curl https://your-backend.netlify.app/.netlify/functions/api-health
   # Expected: 200 OK, {"status": "healthy"}
   ```
   - [ ] API responds correctly
   - [ ] Rollback completed in under 2 minutes ✓

5. **Cleanup**:
   ```bash
   git revert HEAD
   git push origin main
   ```

### T071: Measure Rollback Time

**Objective**: Verify Success Criteria SC-005

**Method**:
1. Execute T069 and T070 rollback tests
2. Record actual rollback times
3. Calculate average: (Frontend time + Backend time) / 2
4. Success Criteria: Average < 2 minutes

**Results Template**:
```
Frontend Rollback Time: _____ seconds
Backend Rollback Time: _____ seconds
Average: _____ seconds
Success Criteria (< 120 seconds): [PASS/FAIL]
```

### T072: Test Deployment History Access

**Objective**: Verify deployment history is accessible and complete

**Steps**:

1. **Via Netlify UI**:
   - [ ] Navigate to Site > Deploys
   - [ ] Verify can see list of all deployments
   - [ ] Verify can click on any deployment to see details
   - [ ] Verify can access deployment logs

2. **Via Netlify CLI**:
   ```bash
   netlify deploy:list
   # Verify output shows deployment history
   ```

3. **Verify Retention**:
   - [ ] Can access deployments from > 1 month ago
   - [ ] Can access failed deployments
   - [ ] Can access branch and preview deployments

## Monitoring for Rollback Triggers

### Automated Monitoring (Recommended)

Set up external monitoring to detect issues:

**Uptime Monitoring**:
- **Service**: UptimeRobot, Better Uptime, Pingdom
- **Check interval**: Every 1-5 minutes
- **Endpoints to monitor**:
  - Frontend: `https://your-frontend.netlify.app`
  - Backend Health: `https://your-backend.netlify.app/.netlify/functions/api-health`
  - Backend API: `https://your-backend.netlify.app/.netlify/functions/api-roadmap-items`

**Error Tracking**:
- **Service**: Sentry, LogRocket, Rollbar
- **Frontend**: Track JavaScript errors
- **Backend**: Track function exceptions
- **Alert threshold**: > 5% error rate

**Performance Monitoring**:
- **Service**: Netlify Analytics (built-in)
- **Metrics**: Load time, function execution time
- **Alert threshold**: > 2x normal response time

### Manual Monitoring

**Post-Deployment Checklist** (run after every production deploy):

1. **Immediate (0-5 minutes)**:
   - [ ] Visit homepage - loads without errors
   - [ ] Test main user flow (view roadmap items)
   - [ ] Check browser console - no critical errors
   - [ ] Test API health endpoint

2. **Short Term (5-30 minutes)**:
   - [ ] Monitor error rates in Netlify function logs
   - [ ] Check user reports/support channels
   - [ ] Review deployment logs for warnings

## Rollback Communication Template

### Internal Team Notification

```
🚨 ROLLBACK EXECUTED

Site: [Frontend/Backend]
Rollback Time: [timestamp]
Rolled back to: Deploy [deploy-id] from [time ago]
Reason: [brief description]
Impact: [user-facing impact]
Status: Service restored ✅

Next steps:
1. Root cause analysis in progress
2. Fix being developed
3. Will redeploy after testing in preview

Questions? Contact [incident lead]
```

### Stakeholder Notification (If Needed)

```
Subject: Service Issue Resolved

The Weni Public Roadmap experienced a brief service disruption at [time].
Our team immediately rolled back to a stable version and service was 
restored within [X] minutes.

Impact: [describe user impact]
Resolution: Previous stable version restored
Prevention: [brief description of fix in progress]

We apologize for any inconvenience. The issue is fully resolved and 
we're implementing additional safeguards to prevent recurrence.
```

## References

- [Netlify Deployment Management](https://docs.netlify.com/site-deploys/manage-deploys/)
- [Netlify API - Deploy Restore](https://open-api.netlify.com/#tag/deploy/operation/restoreSiteDeploy)
- Success Criteria SC-005: Rollback to previous version completes in under 2 minutes

