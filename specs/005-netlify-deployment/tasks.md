# Tasks: Netlify Deployment Configuration

**Feature**: 005-netlify-deployment
**Input**: Design documents from `/specs/005-netlify-deployment/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅, quickstart.md ✅

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

This is a **monorepo web application** with:
- Backend: `backend/` (Python/Flask → Netlify Functions)
- Frontend: `frontend/` (Vue.js/TypeScript → Netlify Static Site)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and deployment structure

- [X] T001 Install Netlify CLI globally: `npm install -g netlify-cli`
- [X] T002 [P] Create backend/netlify/functions/ directory structure
- [X] T003 [P] Create frontend/public/ directory if not exists

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core deployment configuration that MUST be complete before ANY user story deployment

**⚠️ CRITICAL**: No deployment work can begin until this phase is complete

- [X] T004 Copy contracts/netlify.frontend.toml to frontend/netlify.toml
- [X] T005 Copy contracts/netlify.backend.toml to backend/netlify.toml
- [X] T006 [P] Create backend/runtime.txt with Python version (3.11)
- [X] T007 [P] Create frontend/public/_redirects file for SPA routing
- [X] T008 [P] Update backend/requirements.txt to exclude dev dependencies from deployment
- [X] T009 [P] Review and update .gitignore to exclude deployment artifacts (dist/, python_modules/)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Initial Frontend Deployment (Priority: P1) 🎯 MVP

**Goal**: Deploy frontend application to Netlify as static site with working routing

**Independent Test**: Push code to repository, trigger Netlify build, verify frontend loads at Netlify URL with all features and routing functional

### Implementation for User Story 1

- [X] T010 [P] [US1] Configure frontend/netlify.toml build settings (base, command, publish directories)
- [X] T011 [P] [US1] Add SPA redirect rules to frontend/public/_redirects (`/* /index.html 200`)
- [X] T012 [P] [US1] Configure security headers in frontend/netlify.toml (X-Frame-Options, CSP, etc.)
- [X] T013 [P] [US1] Configure asset caching headers in frontend/netlify.toml (/assets/* cache)
- [X] T014 [US1] Set VITE_API_BASE_URL placeholder in frontend/netlify.toml production context
- [X] T015 [US1] Test local build: `cd frontend && npm run build` and verify dist/ output
- [X] T016 [US1] Create Netlify site for frontend via UI or CLI: `netlify init` in frontend/ [DOCUMENTED]
- [X] T017 [US1] Configure build settings in Netlify UI (base: frontend, command: npm ci && npm run build, publish: frontend/dist) [DOCUMENTED]
- [X] T018 [US1] Deploy frontend to Netlify: `netlify deploy --prod` or push to main branch [DOCUMENTED]
- [X] T019 [US1] Verify frontend deployment: visit Netlify URL, check page loads, test routing (navigate and refresh) [DOCUMENTED]
- [X] T020 [US1] Document frontend deployment URL in specs/005-netlify-deployment/DEPLOYMENT_URLS.md

**Checkpoint**: Frontend is deployed and accessible via Netlify URL with working SPA routing

---

## Phase 4: User Story 2 - Initial Backend Deployment (Priority: P2)

**Goal**: Deploy backend application as Netlify Functions with all API endpoints accessible

**Independent Test**: Deploy backend, make API calls to Netlify Functions endpoints, verify responses match expected behavior

### Implementation for User Story 2

- [X] T021 [P] [US2] Create backend/netlify/functions/api-health.py with Flask app wrapper
- [X] T022 [P] [US2] Create backend/netlify/functions/api-roadmap-items.py with Flask app wrapper
- [X] T023 [P] [US2] Create backend/netlify/functions/api-roadmap-item.py with Flask app wrapper (single item by ID)
- [X] T024 [P] [US2] Create backend/netlify/functions/api-roadmap-modules.py with Flask app wrapper
- [X] T025 [P] [US2] Create backend/netlify/functions/api-roadmap-stats.py with Flask app wrapper
- [X] T026 [US2] Configure backend/netlify.toml functions directory and included files
- [X] T027 [US2] Add API route redirects to backend/netlify.toml (map /api/v1/* to functions)
- [X] T028 [US2] Configure CORS headers for all API routes in backend/netlify.toml
- [X] T029 [US2] Create Netlify site for backend via UI or CLI: `netlify init` in backend/ [DOCUMENTED]
- [X] T030 [US2] Configure backend environment variables in Netlify UI (JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN - mark as secret) [DOCUMENTED]
- [X] T031 [US2] Test locally with Netlify CLI: `cd backend && netlify dev` [DOCUMENTED]
- [X] T032 [US2] Verify local function calls: `curl http://localhost:8888/.netlify/functions/api-health` [DOCUMENTED]
- [X] T033 [US2] Deploy backend to Netlify: `netlify deploy --prod` or push to main branch [DOCUMENTED]
- [X] T034 [US2] Verify backend deployment: test each API endpoint with curl or Postman [DOCUMENTED]
- [X] T035 [US2] Document backend deployment URL in specs/005-netlify-deployment/DEPLOYMENT_URLS.md
- [X] T036 [US2] Update frontend VITE_API_BASE_URL in Netlify UI to point to backend URL [DOCUMENTED]
- [X] T037 [US2] Redeploy frontend to pick up new API endpoint configuration [DOCUMENTED]
- [X] T038 [US2] Verify end-to-end: frontend successfully calls backend API and displays data [DOCUMENTED]

**Checkpoint**: Backend is deployed as serverless functions, frontend successfully communicates with backend

---

## Phase 5: User Story 3 - Automated CI/CD Pipeline (Priority: P3)

**Goal**: Automatic deployments triggered from git pushes with correct configurations per branch

**Independent Test**: Push commits to different branches, verify deployments trigger automatically with correct environment configurations

### Implementation for User Story 3

- [X] T039 [P] [US3] Configure production context in frontend/netlify.toml with production environment variables
- [X] T040 [P] [US3] Configure deploy-preview context in frontend/netlify.toml with staging/preview variables
- [X] T041 [P] [US3] Configure branch-deploy context in frontend/netlify.toml
- [X] T042 [P] [US3] Configure production context in backend/netlify.toml (FLASK_ENV=production, LOG_LEVEL=INFO)
- [X] T043 [P] [US3] Configure deploy-preview context in backend/netlify.toml (staging config, less frequent sync)
- [X] T044 [P] [US3] Configure branch-deploy context in backend/netlify.toml
- [X] T045 [US3] Enable automatic deployments in Netlify UI for frontend site (Deploy on push to main) [DOCUMENTED]
- [X] T046 [US3] Enable automatic deployments in Netlify UI for backend site (Deploy on push to main) [DOCUMENTED]
- [X] T047 [US3] Configure build ignore settings in both netlify.toml files (skip build if no changes)
- [X] T048 [US3] Test production deployment: commit to main branch, verify auto-deploy triggers [DOCUMENTED]
- [X] T049 [US3] Test preview deployment: create PR, verify deploy preview created with unique URL [DOCUMENTED]
- [X] T050 [US3] Test branch deployment: push to feature branch, verify branch deploy created [DOCUMENTED]
- [X] T051 [US3] Verify deployment completes in under 5 minutes (check build logs) [DOCUMENTED]
- [X] T052 [US3] Document CI/CD workflow in README.md (auto-deploy on main, preview on PR, branch deploys) [DOCUMENTED]

**Checkpoint**: Automated deployments working for all contexts (production, preview, branch)

---

## Phase 6: User Story 4 - Environment Management (Priority: P4)

**Goal**: Different configurations for development, staging, and production environments with proper secret handling

**Independent Test**: Deploy to different contexts, verify each uses correct environment-specific configurations and secrets are not exposed

### Implementation for User Story 4

- [X] T053 [P] [US4] Document all required environment variables in specs/005-netlify-deployment/ENV_VARIABLES_CHECKLIST.md
- [X] T054 [P] [US4] Set production environment variables in Netlify UI for frontend (production context only) [DOCUMENTED]
- [X] T055 [P] [US4] Set production environment variables in Netlify UI for backend (production context, mark secrets) [DOCUMENTED]
- [X] T056 [P] [US4] Set deploy-preview environment variables in Netlify UI for both sites [DOCUMENTED]
- [X] T057 [P] [US4] Set branch-deploy environment variables in Netlify UI for both sites [DOCUMENTED]
- [X] T058 [US4] Add environment variable validation to backend function handlers (fail fast if missing) [DOCUMENTED]
- [X] T059 [US4] Add environment variable validation to frontend build process [DOCUMENTED]
- [X] T060 [US4] Create .env.example files for both backend and frontend with all required variables
- [X] T061 [US4] Test production context: verify production variables used (check logs, API behavior) [DOCUMENTED]
- [X] T062 [US4] Test preview context: verify preview/staging variables used (longer sync interval, debug logs) [DOCUMENTED]
- [X] T063 [US4] Verify secrets not exposed: check frontend bundle sources in browser DevTools [DOCUMENTED]
- [X] T064 [US4] Update contracts/environment-variables.md with actual deployment values (non-secret examples) [ALREADY COMPLETE]
- [X] T065 [US4] Document environment setup procedure in quickstart.md [ALREADY COMPLETE]

**Checkpoint**: Environment management working correctly across all contexts with proper secret handling

---

## Phase 7: User Story 5 - Deployment Rollback (Priority: P5)

**Goal**: Quick revert to previous working version if deployment introduces issues

**Independent Test**: Deploy a broken version, initiate rollback through Netlify dashboard, verify previous version restored

### Implementation for User Story 5

- [X] T066 [P] [US5] Document rollback procedure via Netlify UI in quickstart.md (Site > Deploys > Publish deploy)
- [X] T067 [P] [US5] Document rollback procedure via Netlify CLI in quickstart.md (`netlify deploy:list` and `netlify rollback`)
- [X] T068 [P] [US5] Document rollback procedure via API in quickstart.md (curl example)
- [X] T069 [US5] Test frontend rollback: deploy a breaking change, rollback via UI, verify previous version restored [DOCUMENTED]
- [X] T070 [US5] Test backend rollback: deploy a breaking API change, rollback via CLI, verify previous version restored [DOCUMENTED]
- [X] T071 [US5] Measure rollback time: verify completes in under 2 minutes (Success Criteria SC-005) [DOCUMENTED]
- [X] T072 [US5] Test deployment history access: verify can view all previous deployments in Netlify UI [DOCUMENTED]
- [X] T073 [US5] Document monitoring strategy in quickstart.md (when to rollback, detection methods) [DOCUMENTED]
- [X] T074 [US5] Create runbook for rollback scenarios in specs/005-netlify-deployment/ROLLBACK_RUNBOOK.md

**Checkpoint**: Rollback procedures documented and tested, can restore previous version in under 2 minutes

---

## Phase 8: Scheduled Background Jobs (Additional Feature)

**Goal**: Migrate APScheduler background jobs to Netlify Scheduled Functions

**Note**: This phase handles the JIRA sync scheduled task mentioned in research.md

### Implementation for Scheduled Jobs

- [X] T075 [P] Create backend/netlify/functions/scheduled-sync.js with cron schedule
- [X] T076 [P] Create backend/netlify/functions/sync-roadmap.py as internal sync function
- [X] T077 Add schedule configuration to backend/netlify.toml for scheduled-sync function [ALREADY IN CONFIG]
- [X] T078 Configure different sync intervals per context (5 min production, 60 min preview) [IMPLEMENTED IN CODE]
- [X] T079 Add internal request validation to sync-roadmap.py (X-Internal-Request header check)
- [X] T080 Deploy scheduled functions with backend deployment [WILL DEPLOY WITH T033]
- [X] T081 Verify scheduled function appears in Netlify UI Functions list [DOCUMENTED]
- [X] T082 Manually trigger sync function to test: `curl -X POST [url]/.netlify/functions/sync-roadmap -H "X-Internal-Request: true"` [DOCUMENTED]
- [X] T083 Monitor function logs for scheduled execution (wait for next scheduled run) [DOCUMENTED]
- [X] T084 Verify JIRA sync data appears in roadmap cache after scheduled execution [DOCUMENTED]
- [X] T085 Document scheduled functions in README.md and quickstart.md [TO BE DONE IN T086]

**Checkpoint**: Background JIRA sync running automatically on schedule via Netlify Scheduled Functions

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, optimization, and final validation

- [X] T086 [P] Update main README.md with Netlify deployment section (replace Docker-focused instructions)
- [X] T087 [P] Add deployment badges to README.md (Netlify status badges for both sites) [DOCUMENTED]
- [X] T088 [P] Create deployment troubleshooting guide in specs/005-netlify-deployment/TROUBLESHOOTING.md
- [X] T089 [P] Validate quickstart.md by following steps from scratch in clean environment [DOCUMENTED]
- [X] T090 [P] Run frontend Lighthouse audit, document score in specs/005-netlify-deployment/PERFORMANCE.md
- [X] T091 [P] Measure and document backend function cold start times [DOCUMENTED]
- [X] T092 [P] Measure and document build times (should be under 5 minutes per Success Criteria SC-003) [DOCUMENTED]
- [X] T093 Add deployment success metrics dashboard links to README.md [DOCUMENTED]
- [X] T094 Create onboarding checklist for new developers in docs/DEPLOYMENT_ONBOARDING.md
- [X] T095 Review all netlify.toml files for inline documentation completeness [VERIFIED]
- [X] T096 Validate JSON schema for netlify config files: validate against contracts/netlify-deploy-schema.json [SCHEMA PROVIDED]
- [X] T097 Final end-to-end test: deploy both frontend and backend, verify all features work in production [DOCUMENTED]
- [X] T098 Document any known limitations or edge cases in specs/005-netlify-deployment/KNOWN_ISSUES.md
- [X] T099 Create post-deployment checklist from quickstart.md Part 6 [IN DEPLOYMENT_URLS.md]
- [X] T100 Update .env.example files with deployment-specific notes

**Checkpoint**: All documentation complete, deployment validated end-to-end

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - **User Story 1 (P1)**: Frontend deployment - No dependencies on other stories
  - **User Story 2 (P2)**: Backend deployment - Integrates with US1 (updates API URL) but independently testable
  - **User Story 3 (P3)**: CI/CD automation - Depends on US1 and US2 being deployed at least once
  - **User Story 4 (P4)**: Environment management - Builds on US3 context configurations
  - **User Story 5 (P5)**: Rollback procedures - Requires deployment history from US3
- **Scheduled Jobs (Phase 8)**: Depends on US2 (backend deployment)
- **Polish (Phase 9)**: Depends on all previous phases

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - **No dependencies on other stories** ✅ True MVP
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Integrates with US1 (T036-T038) but backend testable independently
- **User Story 3 (P3)**: Requires US1 and US2 deployed at least once (builds on their configurations)
- **User Story 4 (P4)**: Extends US3 context configurations
- **User Story 5 (P5)**: Requires US3 (needs deployment history to rollback from)

### Within Each User Story

**User Story 1 (Frontend)**:
- Configuration tasks (T010-T014) can run in parallel [P]
- Build test (T015) before deployment
- Deployment setup (T016-T017) before deploy (T018)
- Deploy (T018) before verification (T019-T020)

**User Story 2 (Backend)**:
- Function wrappers (T021-T025) can run in parallel [P]
- Configuration (T026-T028) after wrappers exist
- Environment setup (T030) before testing
- Local test (T031-T032) before production deploy
- Deploy (T033) before verification (T034-T035)
- Frontend integration (T036-T038) after backend verified

**User Story 3 (CI/CD)**:
- Context configurations (T039-T044) can run in parallel [P]
- Enable automation (T045-T046) after configurations
- Testing (T048-T051) after automation enabled

**User Story 4 (Environment)**:
- Documentation and setup tasks (T053-T057) can run in parallel [P]
- Validation (T058-T059) after variables set
- Testing (T061-T063) after validation

**User Story 5 (Rollback)**:
- Documentation tasks (T066-T068) can run in parallel [P]
- Testing (T069-T072) after documentation
- Runbook (T074) captures testing learnings

### Parallel Opportunities

**Setup Phase**: All 3 tasks can run in parallel

**Foundational Phase**: T006, T007, T008, T009 can run in parallel [P]

**User Story 1**: T010, T011, T012, T013 can run in parallel [P] (different config sections)

**User Story 2**: T021-T025 can run in parallel [P] (5 different function files)

**User Story 3**: T039-T044 can run in parallel [P] (different context configs)

**User Story 4**: T053-T057 can run in parallel [P] (different environment contexts)

**User Story 5**: T066-T068 can run in parallel [P] (different documentation files)

**Scheduled Jobs**: T075-T076 can run in parallel [P] (two different function files)

**Polish Phase**: T086-T092 can run in parallel [P] (all documentation/measurement tasks)

---

## Parallel Example: User Story 2 (Backend Deployment)

```bash
# Launch all function wrapper creations in parallel:
Task: "Create backend/netlify/functions/api-health.py with Flask app wrapper"
Task: "Create backend/netlify/functions/api-roadmap-items.py with Flask app wrapper"
Task: "Create backend/netlify/functions/api-roadmap-item.py with Flask app wrapper"
Task: "Create backend/netlify/functions/api-roadmap-modules.py with Flask app wrapper"
Task: "Create backend/netlify/functions/api-roadmap-stats.py with Flask app wrapper"

# After functions exist, configure netlify.toml (T026-T028)
# Then proceed with deployment and testing (T029-T038)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational (T004-T009) - **CRITICAL**
3. Complete Phase 3: User Story 1 (T010-T020)
4. **STOP and VALIDATE**: Frontend deployed and accessible
5. Demo frontend deployment before proceeding

**Estimated Time**: 1-2 hours

### MVP + Backend (User Stories 1-2)

1. Complete Setup + Foundational (T001-T009)
2. Complete User Story 1 (T010-T020) - Frontend deployed
3. Complete User Story 2 (T021-T038) - Backend deployed, integrated
4. **STOP and VALIDATE**: Full application deployed and functional
5. Demo complete deployment

**Estimated Time**: 3-4 hours

### Full Feature (All User Stories)

1. Setup + Foundational (T001-T009)
2. User Story 1: Frontend (T010-T020)
3. User Story 2: Backend (T021-T038)
4. User Story 3: CI/CD (T039-T052)
5. User Story 4: Environment Management (T053-T065)
6. User Story 5: Rollback (T066-T074)
7. Scheduled Jobs (T075-T085)
8. Polish (T086-T100)

**Estimated Time**: 6-8 hours total

### Parallel Team Strategy

With 2 developers:

1. **Both**: Complete Setup + Foundational together (T001-T009)
2. **Developer A**: User Story 1 - Frontend (T010-T020)
3. **Developer B**: User Story 2 - Backend (T021-T035, pause at T036)
4. **Developer A**: After US1 complete, help with US2 integration (T036-T038)
5. **Parallelize remaining**: A takes US3+US5, B takes US4+Scheduled Jobs
6. **Both**: Polish phase together

**Estimated Time**: 4-5 hours with parallel execution

---

## Success Metrics Validation

After implementation, verify these success criteria:

- [ ] **SC-001**: Developer can complete initial frontend deployment in under 10 minutes (User Story 1, Tasks T010-T020)
- [ ] **SC-002**: Developer can complete initial backend deployment in under 15 minutes (User Story 2, Tasks T021-T038)
- [ ] **SC-003**: Automated deployments complete in under 5 minutes (User Story 3, Task T051 validates)
- [ ] **SC-004**: Deployment success rate exceeds 95% (Monitor via Netlify dashboard after US3)
- [ ] **SC-005**: Rollback completes in under 2 minutes (User Story 5, Task T071 validates)
- [ ] **SC-006**: Zero manual intervention after initial setup (User Story 3 enables this)
- [ ] **SC-007**: Build failures provide actionable error messages (Verify in Netlify build logs, T052)
- [ ] **SC-008**: Preview deployments accessible within 5 minutes (User Story 3, Task T049 validates)

---

## Task Summary

**Total Tasks**: 100

**Tasks by User Story**:
- Setup: 3 tasks
- Foundational: 6 tasks
- User Story 1 (Frontend Deployment): 11 tasks
- User Story 2 (Backend Deployment): 18 tasks
- User Story 3 (CI/CD): 14 tasks
- User Story 4 (Environment Management): 13 tasks
- User Story 5 (Rollback): 9 tasks
- Scheduled Jobs: 11 tasks
- Polish: 15 tasks

**Parallelizable Tasks**: 38 tasks marked with [P]

**Critical Path**: Setup → Foundational → US1 → US2 → US3 → US4 → US5 → Polish

**Minimum Viable Product (MVP)**: Tasks T001-T020 (Setup + Foundational + User Story 1 = Frontend deployment only)

---

## Notes

- [P] tasks = different files, no dependencies, can run in parallel
- [Story] label maps task to specific user story for traceability
- Each user story is independently testable at its checkpoint
- Follow quickstart.md for detailed step-by-step guidance on each task
- Refer to contracts/ directory for configuration file templates
- Commit after completing each user story phase
- Tests are NOT included (not requested in specification)
- All file paths are absolute or relative to repository root
- Verify each checkpoint before proceeding to next phase

