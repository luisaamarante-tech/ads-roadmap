# Deployment Onboarding Checklist

**Purpose**: Guide new team members through the Netlify deployment setup and familiarize them with deployment workflows.

**Time**: ~1 hour for complete onboarding

## Prerequisites

Before starting, ensure you have:
- [ ] Netlify account access (join team)
- [ ] Repository access (GitHub/GitLab/Bitbucket)
- [ ] JIRA credentials (for testing backend)
- [ ] Netlify CLI installed: `npm install -g netlify-cli`

## Phase 1: Understanding the Setup (15 minutes)

### Read Documentation

- [ ] **Main guide**: [`specs/005-netlify-deployment/quickstart.md`](../specs/005-netlify-deployment/quickstart.md)
  - Understand deployment process
  - Note manual steps required
  - Review configuration files

- [ ] **Architecture overview**: [`specs/005-netlify-deployment/plan.md`](../specs/005-netlify-deployment/plan.md)
  - Understand frontend (static site) vs backend (serverless functions)
  - Review tech stack and dependencies
  - Note: Backend is broken into small standalone functions (api-health, api-roadmap-items, etc.)

- [ ] **Configuration files**:
  - `frontend/netlify.toml` - Frontend build and deploy config
  - `backend/netlify.toml` - Backend functions config
  - `.env.example` files - Environment variable templates

## Phase 2: Local Setup (15 minutes)

### Install and Configure

1. **Clone repository** (if not already done):
   ```bash
   git clone <repository-url>
   cd weni-roadmap
   ```

2. **Install Netlify CLI**:
   ```bash
   npm install -g netlify-cli
   netlify login
   ```
   - [ ] CLI installed
   - [ ] Authenticated with Netlify

3. **Review project structure**:
   ```bash
   # Check frontend config
   cat frontend/netlify.toml

   # Check backend config
   cat backend/netlify.toml

   # Check serverless functions
   ls backend/netlify/functions/
   ```
   - [ ] Understand monorepo structure
   - [ ] Located configuration files
   - [ ] Found serverless function wrappers

## Phase 3: Test Local Development (15 minutes)

### Frontend Local Testing

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev

# In browser: http://localhost:5173
# Expected: App loads (may show API errors if backend not running)
```
- [ ] Frontend dev server runs
- [ ] App loads in browser
- [ ] No build errors

### Backend Local Testing

```bash
cd backend

# Create local .env (DO NOT COMMIT)
cp .env.example .env
# Edit .env with actual JIRA credentials

# Start Netlify dev (simulates serverless functions locally)
netlify dev

# In new terminal: Test function
curl http://localhost:8888/.netlify/functions/api-health
# Expected: {"status": "healthy", ...}
```
- [ ] Backend dev server runs
- [ ] Functions accessible locally
- [ ] Health check returns 200 OK

## Phase 4: Understand Deployment Workflow (10 minutes)

### Deployment Triggers

Study how deployments are triggered:

| Action | Result | Environment |
|--------|--------|-------------|
| Push to `main` | Production deploy | Production vars |
| Create PR to `main` | Deploy preview | Preview vars |
| Push to feature branch | Branch deploy | Dev vars |

**Exercise**: Understand what happens when you:
1. Make a change in `frontend/` only
2. Make a change in `backend/` only
3. Create a pull request

**Answer**:
1. Only frontend rebuilds (build ignore rules)
2. Only backend rebuilds (build ignore rules)
3. Both get deploy previews with unique URLs

- [ ] Understand deployment contexts
- [ ] Understand build ignore rules
- [ ] Know where environment variables are set (Netlify UI)

## Phase 5: Practice Deployment (15 minutes)

### Test Deployment Process

**Note**: Only if you have permission to create test deployments

1. **Create test branch**:
   ```bash
   git checkout -b onboarding/test-deploy-$(whoami)
   ```

2. **Make a small change**:
   ```bash
   echo "# Onboarding test" >> specs/005-netlify-deployment/README.md
   git add specs/005-netlify-deployment/README.md
   git commit -m "docs: onboarding deployment test"
   git push origin onboarding/test-deploy-$(whoami)
   ```

3. **Monitor deployment**:
   - Go to Netlify dashboard
   - Find your branch deploy
   - Watch build logs
   - Note deployment URL

4. **Cleanup**:
   ```bash
   git checkout main
   git branch -D onboarding/test-deploy-$(whoami)
   git push origin --delete onboarding/test-deploy-$(whoami)
   ```

- [ ] Created test deployment
- [ ] Monitored build logs
- [ ] Accessed deployed site
- [ ] Cleaned up test branch

## Phase 6: Learn Troubleshooting (10 minutes)

### Common Issues

Review troubleshooting guide: [`specs/005-netlify-deployment/TROUBLESHOOTING.md`](../specs/005-netlify-deployment/TROUBLESHOOTING.md)

**Key scenarios to understand**:
1. Build fails - where to check logs
2. Environment variables missing - how to set them
3. CORS errors - where configuration lives
4. Functions not found - debugging paths

**Practice**:
- [ ] Know how to access Netlify build logs
- [ ] Know how to view function logs
- [ ] Know where to set environment variables
- [ ] Know how to test functions locally

## Phase 7: Understand Rollback (5 minutes)

### Rollback Procedures

Review: [`specs/005-netlify-deployment/ROLLBACK_RUNBOOK.md`](../specs/005-netlify-deployment/ROLLBACK_RUNBOOK.md)

**Key points**:
- When to rollback (critical failures)
- How to rollback (Netlify UI, CLI, or API)
- Target: < 2 minutes rollback time

**Mental exercise**: If you discovered a critical bug in production right now:
1. How would you rollback? (Netlify UI > Deploys > Previous deploy > Publish)
2. Who would you notify? (Team lead, stakeholders)
3. What would you document? (Incident log, root cause)

- [ ] Know how to find previous deployments
- [ ] Know how to publish old deployment
- [ ] Understand when rollback is appropriate

## Phase 8: Review Documentation (5 minutes)

### Key Resources

Bookmark these for quick reference:

- [x] **Quickstart Guide**: `specs/005-netlify-deployment/quickstart.md`
  - Step-by-step deployment instructions

- [x] **Deployment URLs**: `specs/005-netlify-deployment/DEPLOYMENT_URLS.md`
  - Manual deployment steps and URLs

- [x] **CI/CD Setup**: `specs/005-netlify-deployment/CI_CD_SETUP.md`
  - Automated deployment configuration

- [x] **Environment Variables**: `specs/005-netlify-deployment/ENV_VARIABLES_CHECKLIST.md`
  - Complete list of required variables

- [x] **Rollback Runbook**: `specs/005-netlify-deployment/ROLLBACK_RUNBOOK.md`
  - Emergency rollback procedures

- [x] **Troubleshooting**: `specs/005-netlify-deployment/TROUBLESHOOTING.md`
  - Common issues and solutions

- [x] **Performance**: `specs/005-netlify-deployment/PERFORMANCE.md`
  - Metrics and monitoring

## Onboarding Complete! ✅

You should now understand:
- ✅ Project structure (monorepo with frontend/backend)
- ✅ How to run locally (with Netlify Dev)
- ✅ Deployment triggers and contexts
- ✅ Where configuration lives (netlify.toml files)
- ✅ How to monitor deployments
- ✅ How to troubleshoot common issues
- ✅ When and how to rollback

## Next Steps

1. **Join team channels**:
   - Slack: #deployments
   - Get notifications for failed builds

2. **Review team conventions**:
   - Commit message format
   - PR review process
   - Deployment approval workflow (if any)

3. **Ask questions**:
   - Unclear about anything? Ask the team!
   - Suggest documentation improvements

## Quiz (Optional)

Test your knowledge:

1. What triggers a production deployment?
   <details><summary>Answer</summary>Push to main branch</details>

2. Where are environment variables configured?
   <details><summary>Answer</summary>Netlify UI > Site Settings > Environment Variables</details>

3. How long should a rollback take?
   <details><summary>Answer</summary>Under 2 minutes (Success Criteria SC-005)</details>

4. Where are backend API routes defined?
   <details><summary>Answer</summary>backend/netlify/functions/ (one file per endpoint)</details>

5. What command tests functions locally?
   <details><summary>Answer</summary>netlify dev</details>

6. If frontend build fails, where do you check logs?
   <details><summary>Answer</summary>Netlify UI > Site > Deploys > [deployment] > Deploy log</details>

Congratulations on completing the deployment onboarding! 🎉
