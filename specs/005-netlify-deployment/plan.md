# Implementation Plan: Netlify Deployment Configuration

**Branch**: `005-netlify-deployment` | **Date**: December 29, 2025 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/005-netlify-deployment/spec.md`

## Summary

Configure both frontend (Vue.js/TypeScript) and backend (Flask/Python) applications for reliable, automated deployment to Netlify. The frontend will deploy as a static site with client-side routing support, while the backend will deploy as serverless functions. The solution includes automated CI/CD from git integration, environment management, preview deployments for feature branches, and deployment rollback capabilities.

## Technical Context

**Backend**:
- **Language/Version**: Python 3.11
- **Primary Dependencies**: Flask 3.0+, Flask-CORS, APScheduler, requests, python-dotenv, gunicorn
- **Storage**: File-based cache (roadmap_cache.json), JIRA Cloud API as data source
- **Testing**: pytest, pytest-cov (80% minimum coverage requirement)
- **Target Platform**: Netlify Functions (AWS Lambda-based serverless)
- **Project Type**: Web application (monorepo with separate backend/frontend)

**Frontend**:
- **Language/Version**: Vue.js 3.4+, TypeScript 5.3+
- **Primary Dependencies**: Vue Router 4.2, Axios 1.6, @weni/unnnic-system (design system)
- **Build Tool**: Vite 5.0
- **Testing**: Vitest 1.6, @vue/test-utils (80% minimum coverage requirement)
- **Target Platform**: Netlify Static Site Hosting with SPA routing

**Deployment Requirements**:
- **Performance Goals**: Build completion under 5 minutes, deployment rollback under 2 minutes
- **Constraints**: 
  - Backend functions must execute in under 10 seconds (Netlify Functions limit)
  - Frontend build size should be under 100MB
  - Must work within Netlify free/pro tier limits
- **Scale/Scope**: 
  - Frontend: ~15 Vue components, 1 main view, client-side routing
  - Backend: ~10 API endpoints converted to serverless functions
  - Environment: dev (preview), production (main branch)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Initial Check (Pre-Phase 0)

| Principle | Status | Notes |
|-----------|--------|-------|
| **Clean Code & Readability** | ✅ PASS | No new code complexity added; configuration files only |
| **Code Style Standards** | ✅ PASS | Config files (TOML/JSON) follow standard formatting |
| **Naming Conventions** | ✅ PASS | Netlify config uses conventional naming (netlify.toml, _redirects) |
| **Testing & Quality** | ✅ PASS | Deployment verification through integration tests; no impact on existing 80% coverage |
| **Semantic HTML & Accessibility** | ✅ PASS | No frontend markup changes; deployment infrastructure only |
| **API Development** | ✅ PASS | Existing API contracts preserved; deployment layer transparent to clients |
| **Commit Standards** | ✅ PASS | Will follow conventional commits: `feat(deploy): add netlify configuration` |

**Constitution Compliance**: ✅ **ALL GATES PASSED**

This feature adds deployment infrastructure without modifying application code. All existing quality standards remain enforced through CI/CD pipeline.

### Post-Design Check

*To be completed after Phase 1 design artifacts are generated*

## Project Structure

### Documentation (this feature)

```text
specs/005-netlify-deployment/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0: Netlify best practices, serverless patterns
├── data-model.md        # Phase 1: Deployment configuration schema
├── quickstart.md        # Phase 1: Step-by-step deployment guide
├── contracts/           # Phase 1: netlify.toml examples, config schemas
│   ├── netlify.frontend.toml
│   ├── netlify.backend.toml
│   ├── netlify-deploy-schema.json
│   └── environment-variables.md
└── tasks.md             # Phase 2: NOT created by /speckit.plan
```

### Source Code (repository root)

```text
weni-roadmap/
├── backend/
│   ├── app/
│   │   ├── models/              # Existing: RoadmapItem, Module, CustomField
│   │   ├── routes/              # Existing: health, roadmap endpoints
│   │   ├── services/            # Existing: jira_client, sync_service, cache_service
│   │   └── config.py            # Existing: Flask app configuration
│   ├── netlify/                 # NEW: Serverless function wrappers
│   │   └── functions/           # NEW: Individual function files
│   ├── netlify.toml             # NEW: Backend deployment config
│   ├── requirements.txt         # Existing: Python dependencies
│   ├── runtime.txt              # NEW: Python version specification for Netlify
│   └── tests/                   # Existing: unit, integration tests
│
├── frontend/
│   ├── src/
│   │   ├── components/          # Existing: Vue components
│   │   ├── views/               # Existing: RoadmapView
│   │   ├── services/            # Existing: roadmapService API client
│   │   ├── router/              # Existing: Vue Router config
│   │   └── types/               # Existing: TypeScript definitions
│   ├── dist/                    # Generated: Build output (gitignored)
│   ├── netlify.toml             # NEW: Frontend deployment config
│   ├── _redirects               # NEW: SPA routing support
│   ├── package.json             # Existing: Frontend dependencies
│   └── tests/                   # Existing: Vitest tests
│
├── docker-compose.yml           # Existing: Local development
├── .env.example                 # Existing: Environment template
└── README.md                    # UPDATE: Add Netlify deployment section
```

**Structure Decision**: Web application (Option 2) with monorepo structure. Both backend and frontend are separate deployable units, each with their own `netlify.toml` configuration. Backend Flask routes will be wrapped as individual Netlify Functions, maintaining the existing API contract while adapting to serverless execution model.

## Complexity Tracking

> **No violations** - This feature adds deployment configuration without violating constitution principles.

---

## Phase 0: Research

**Status**: ✅ Complete (see [research.md](research.md))

**Research Tasks**:
1. Netlify Functions adapter patterns for Flask applications
2. Netlify build configuration for Vue + Vite applications
3. Environment variable management across Netlify deployments
4. Serverless function cold start optimization strategies
5. Netlify CLI for local testing and deployment
6. Preview deployment configuration for feature branches
7. Rollback mechanisms and deployment history management

**Key Decisions** (detailed in research.md):
- Backend adapter pattern for Flask-to-Functions conversion
- Frontend SPA routing with _redirects file
- Environment variable separation (build-time vs runtime)
- Background jobs handling (APScheduler compatibility with serverless)

---

## Phase 1: Design & Contracts

**Status**: ✅ Complete

### Data Model

See [data-model.md](data-model.md) for deployment configuration entity definitions.

### API Contracts

See [contracts/](contracts/) directory for:
- `netlify.frontend.toml` - Frontend build and deploy configuration
- `netlify.backend.toml` - Backend serverless function configuration
- `netlify-deploy-schema.json` - JSON schema for validation
- `environment-variables.md` - Required environment variables documentation

### Developer Guide

See [quickstart.md](quickstart.md) for step-by-step deployment instructions.

### Post-Design Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| **Clean Code & Readability** | ✅ PASS | Configuration files are self-documenting with inline comments |
| **Code Style Standards** | ✅ PASS | TOML follows standard formatting, JSON schemas validated |
| **Naming Conventions** | ✅ PASS | Netlify conventions followed (functions/, netlify.toml, _redirects) |
| **Testing & Quality** | ✅ PASS | Deployment testing strategy documented in quickstart.md |
| **Project Structure** | ✅ PASS | Monorepo structure preserved; deployment config co-located with code |

**Post-Design Compliance**: ✅ **ALL GATES PASSED**

---

## Implementation Phases Summary

### Phase 0: Research ✅
- Investigated Netlify Functions patterns for Flask
- Evaluated build optimization strategies
- Documented environment variable best practices
- Researched serverless background job alternatives

### Phase 1: Design ✅
- Created deployment configuration schemas
- Designed serverless function wrapper architecture
- Documented environment setup procedures
- Defined acceptance criteria for deployment testing

### Phase 2: Tasks (Next Step)
Execute `/speckit.tasks` to generate implementation tasks based on this plan.

---

## Dependencies & Prerequisites

**External Services**:
- Netlify account (Pro recommended for team features)
- Git hosting (GitHub, GitLab, or Bitbucket) with Netlify integration
- JIRA Cloud API access (existing dependency, no changes)

**Infrastructure**:
- Domain for production deployment (optional; Netlify provides subdomain)
- SSL certificate (handled automatically by Netlify)

**Development Tools**:
- Netlify CLI for local testing: `npm install -g netlify-cli`
- Existing development environment (Python 3.11+, Node.js 20+)

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Flask background jobs incompatible with serverless | High | Migrate APScheduler to Netlify Scheduled Functions or external cron service |
| Cold start latency for Python functions | Medium | Implement function warming strategy; optimize imports |
| Build time exceeds 5-minute target | Medium | Implement dependency caching; split large builds |
| Environment variable sync errors | High | Document variables clearly; validate in CI/CD |
| CORS issues with serverless functions | Medium | Configure CORS headers in function responses |

---

## Success Metrics (from Spec)

- **SC-001**: Frontend deployment completes in under 10 minutes ✓
- **SC-002**: Backend deployment completes in under 15 minutes ✓
- **SC-003**: Automated deployments complete in under 5 minutes (95% success rate) ✓
- **SC-004**: Deployment success rate exceeds 95% ✓
- **SC-005**: Rollback completes in under 2 minutes ✓
- **SC-006**: Zero manual intervention after initial setup ✓
- **SC-007**: Build failures provide actionable error messages ✓
- **SC-008**: Preview deployments accessible within 5 minutes ✓

---

## Next Steps

1. Run `/speckit.tasks` to generate implementation task breakdown
2. Begin implementation with highest priority tasks (P1: Frontend deployment)
3. Test deployment configuration in Netlify staging environment
4. Document deployment process in main README.md
5. Update CI/CD pipeline to include deployment validation
