# Tasks: Constitution Compliance Refactor

**Input**: Design documents from `/specs/002-constitution-refactor/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Tests**: Required - Constitution mandates 80% test coverage (FR-002, FR-007)

**Organization**: Tasks grouped by user story for independent implementation and testing

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/` (Python/Flask)
- **Frontend**: `frontend/` (Vue 3/TypeScript)
- **Root**: Repository root for shared configs

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dev dependency installation

- [x] T001 [P] Install Python dev dependencies (black, flake8, isort, pytest-cov) in backend/requirements.txt
- [x] T002 [P] Install Node.js dev dependencies (eslint, prettier, stylelint, vitest) in frontend/package.json
- [x] T003 [P] Create backend test directory structure: backend/tests/__init__.py, backend/tests/unit/, backend/tests/integration/
- [x] T004 [P] Create frontend test directory structure: frontend/tests/, frontend/tests/components/, frontend/tests/services/
- [x] T005 [P] Create frontend mocks directory: frontend/mocks/roadmapData.ts

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core configuration that MUST be complete before user story implementation

**⚠️ CRITICAL**: Pre-commit and linting configs must exist before tests can validate code

- [x] T006 Create backend pyproject.toml with Black, Flake8, isort, pytest config in backend/pyproject.toml
- [x] T007 Create backend setup.cfg for Flake8 configuration in backend/setup.cfg
- [x] T008 [P] Create ESLint flat config with Vue 3 + TypeScript rules in frontend/eslint.config.js
- [x] T009 [P] Create Prettier config with constitution requirements in frontend/prettier.config.js
- [x] T010 [P] Create Stylelint config with BEM plugin in frontend/stylelint.config.js
- [x] T011 Create Vitest config with 80% coverage thresholds in frontend/vitest.config.ts
- [x] T012 Create test setup file with Vue Test Utils config in frontend/tests/setup.ts
- [x] T013 Update frontend package.json with lint, format, test scripts

**Checkpoint**: Foundation ready - linting and test infrastructure configured

---

## Phase 3: User Story 1 - Developer Contributes Clean, Tested Code (Priority: P1) 🎯 MVP

**Goal**: Pre-commit hooks validate all code changes, backend + frontend achieve 80%+ test coverage

**Independent Test**: Run `git commit` and verify linters + tests execute automatically

### Backend Testing for US1

- [x] T014 [P] [US1] Create pytest fixtures and mocks in backend/tests/conftest.py
- [x] T015 [P] [US1] Create JIRA client mock factory in backend/tests/conftest.py
- [x] T016 [P] [US1] Create Flask app fixture for route testing in backend/tests/conftest.py
- [x] T017 [P] [US1] Write unit tests for RoadmapItem model in backend/tests/unit/test_models.py
- [x] T018 [P] [US1] Write unit tests for CacheService in backend/tests/unit/test_cache_service.py
- [x] T019 [P] [US1] Write unit tests for JiraClient in backend/tests/unit/test_jira_client.py
- [x] T020 [P] [US1] Write unit tests for SyncService in backend/tests/unit/test_sync_service.py
- [x] T021 [US1] Write integration tests for roadmap routes in backend/tests/integration/test_routes.py
- [x] T022 [US1] Verify backend test coverage reaches 80% with pytest --cov

### Frontend Testing for US1

- [x] T023 [P] [US1] Write component test for RoadmapCard in frontend/tests/components/RoadmapCard.spec.ts
- [x] T024 [P] [US1] Write component test for RoadmapCardList in frontend/tests/components/RoadmapCardList.spec.ts
- [x] T025 [P] [US1] Write component test for RoadmapFilters in frontend/tests/components/RoadmapFilters.spec.ts
- [x] T026 [P] [US1] Write component test for RoadmapTabs in frontend/tests/components/RoadmapTabs.spec.ts
- [x] T027 [P] [US1] Write component test for RoadmapEmptyState in frontend/tests/components/RoadmapEmptyState.spec.ts
- [x] T028 [P] [US1] Write service test for roadmapService in frontend/tests/services/roadmapService.spec.ts
- [x] T029 [US1] Verify frontend test coverage reaches 80% with npm run test:coverage

### Pre-commit Configuration for US1

- [x] T030 [US1] Create pre-commit config with Black, Flake8, isort hooks in .pre-commit-config.yaml
- [x] T031 [US1] Add ESLint, Prettier, Stylelint hooks to .pre-commit-config.yaml
- [x] T032 [US1] Add conventional commits hook to .pre-commit-config.yaml
- [ ] T033 [US1] Install pre-commit hooks with `pre-commit install`
- [ ] T034 [US1] Run `pre-commit run --all-files` to verify all hooks pass

### CI Pipeline for US1

- [x] T035 [US1] Create .github/workflows/ directory structure
- [x] T036 [US1] Create CI workflow with backend job in .github/workflows/ci.yml
- [x] T037 [US1] Add frontend job to CI workflow in .github/workflows/ci.yml
- [x] T038 [US1] Add commitlint job to CI workflow in .github/workflows/ci.yml
- [x] T039 [US1] Add build check job to CI workflow in .github/workflows/ci.yml

**Checkpoint**: US1 complete - pre-commit validates code, tests pass with 80%+ coverage, CI runs all checks

---

## Phase 4: User Story 2 - Codebase Follows Naming Conventions (Priority: P2)

**Goal**: All CSS follows BEM methodology, event handlers use on*/handle* prefixes

**Independent Test**: Run static analysis tools, verify BEM pattern matching

### BEM Refactoring for US2

- [x] T040 [P] [US2] Refactor RoadmapCard.vue CSS classes to BEM in frontend/src/components/RoadmapCard.vue
- [x] T041 [P] [US2] Refactor RoadmapCardList.vue CSS classes to BEM in frontend/src/components/RoadmapCardList.vue
- [x] T042 [P] [US2] Refactor RoadmapFilters.vue CSS classes to BEM in frontend/src/components/RoadmapFilters.vue
- [x] T043 [P] [US2] Refactor RoadmapTabs.vue CSS classes to BEM in frontend/src/components/RoadmapTabs.vue
- [x] T044 [P] [US2] Refactor RoadmapEmptyState.vue CSS classes to BEM in frontend/src/components/RoadmapEmptyState.vue
- [x] T045 [P] [US2] Refactor RoadmapView.vue CSS classes to BEM in frontend/src/views/RoadmapView.vue
- [x] T046 [P] [US2] Refactor App.vue global styles to BEM in frontend/src/App.vue

### Event Handler Naming for US2

- [x] T047 [P] [US2] Rename event handlers to on* prefix in frontend/src/components/RoadmapCard.vue
- [x] T048 [P] [US2] Rename event handlers to on* prefix in frontend/src/components/RoadmapFilters.vue
- [x] T049 [P] [US2] Rename event handlers to on* prefix in frontend/src/components/RoadmapTabs.vue
- [x] T050 [P] [US2] Rename state methods to handle* prefix in frontend/src/views/RoadmapView.vue

### Backend Import Organization for US2

- [x] T051 [P] [US2] Organize imports (stdlib, third-party, local) in backend/app/services/jira_client.py
- [x] T052 [P] [US2] Organize imports (stdlib, third-party, local) in backend/app/services/cache_service.py
- [x] T053 [P] [US2] Organize imports (stdlib, third-party, local) in backend/app/services/sync_service.py
- [x] T054 [P] [US2] Organize imports (stdlib, third-party, local) in backend/app/routes/roadmap.py
- [x] T055 [US2] Run `isort --check-only backend/` to verify import ordering

**Checkpoint**: US2 complete - all CSS follows BEM, naming conventions enforced, Stylelint passes

---

## Phase 5: User Story 3 - Frontend Uses Unnnic Design System (Priority: P3)

**Goal**: All UI components use Unnnic Design System, custom components replaced

**Independent Test**: Visual comparison against unnnic.stg.cloud.weni.ai

### Unnnic Setup for US3

- [x] T056 [US3] Import Unnnic CSS in main.ts: frontend/src/main.ts
- [x] T057 [US3] Register Unnnic components globally or create component imports pattern

### Component Migration for US3

- [x] T058 [P] [US3] Replace custom buttons with UnnnicButton in frontend/src/components/RoadmapCard.vue
- [x] T059 [P] [US3] Replace custom buttons with UnnnicButton in frontend/src/views/RoadmapView.vue
- [x] T060 [P] [US3] Replace custom select with UnnnicSelectSmart in frontend/src/components/RoadmapFilters.vue
- [x] T061 [P] [US3] Replace custom tabs with UnnnicTab in frontend/src/components/RoadmapTabs.vue
- [x] T062 [P] [US3] Replace loading skeleton with UnnnicSkeletonLoading in frontend/src/components/RoadmapCardList.vue
- [x] T063 [P] [US3] Replace loading skeleton with UnnnicSkeletonLoading in frontend/src/components/RoadmapEmptyState.vue

### Design Token Migration for US3

- [x] T064 [P] [US3] Replace hardcoded colors with Unnnic tokens in frontend/src/components/RoadmapCard.vue
- [x] T065 [P] [US3] Replace hardcoded colors with Unnnic tokens in frontend/src/components/RoadmapCardList.vue
- [x] T066 [P] [US3] Replace hardcoded colors with Unnnic tokens in frontend/src/components/RoadmapFilters.vue
- [x] T067 [P] [US3] Replace hardcoded colors with Unnnic tokens in frontend/src/components/RoadmapTabs.vue
- [x] T068 [P] [US3] Replace hardcoded colors with Unnnic tokens in frontend/src/views/RoadmapView.vue

### Update Tests for US3

- [x] T069 [US3] Update component tests for Unnnic component stubs in frontend/tests/setup.ts
- [x] T070 [US3] Verify all component tests still pass after Unnnic migration

**Checkpoint**: US3 complete - all components use Unnnic, design tokens applied, visual consistency achieved

---

## Phase 6: User Story 4 - HTML is Semantic and Accessible (Priority: P3)

**Goal**: Semantic HTML structure, proper heading hierarchy, Lighthouse score 90+

**Independent Test**: Run Lighthouse accessibility audit, verify no critical issues

### Semantic HTML for US4

- [x] T071 [P] [US4] Audit and improve semantic HTML in frontend/src/views/RoadmapView.vue
- [x] T072 [P] [US4] Add semantic structure (article, section) to frontend/src/components/RoadmapCard.vue
- [x] T073 [P] [US4] Add semantic structure to frontend/src/components/RoadmapCardList.vue
- [x] T074 [P] [US4] Verify heading hierarchy (h1 → h2 → h3) in frontend/src/views/RoadmapView.vue

### Accessibility Improvements for US4

- [x] T075 [P] [US4] Add ARIA labels to interactive elements in frontend/src/components/RoadmapCard.vue
- [x] T076 [P] [US4] Add ARIA labels to filter controls in frontend/src/components/RoadmapFilters.vue
- [x] T077 [P] [US4] Add ARIA labels to tab navigation in frontend/src/components/RoadmapTabs.vue
- [x] T078 [P] [US4] Ensure keyboard navigation works for all interactive elements

### Accessibility Validation for US4

- [x] T079 [US4] Run Lighthouse accessibility audit on roadmap page
- [x] T080 [US4] Fix any issues to achieve Lighthouse accessibility score 90+

**Checkpoint**: US4 complete - semantic HTML structure, accessible navigation, Lighthouse 90+

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, cleanup, and final validation

- [x] T081 [P] Create commitlint config for conventional commits in commitlint.config.js
- [x] T082 [P] Update README.md with contribution guidelines and setup instructions
- [x] T083 [P] Add .editorconfig for consistent editor settings
- [x] T084 Run full pre-commit suite: `pre-commit run --all-files`
- [x] T085 Verify all tests pass: backend and frontend with 80%+ coverage
- [x] T086 Create test commit to verify pre-commit hooks work end-to-end
- [x] T087 Validate quickstart.md instructions by following them in clean environment

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup)
    │
    ▼
Phase 2 (Foundational) ──────────────────────────────────────┐
    │                                                         │
    │ BLOCKS all user stories until complete                  │
    ▼                                                         │
Phase 3 (US1: Dev Tooling + Testing) ◄────────────────────────┤
    │                                                         │
    │ Can start US2, US3, US4 in parallel after US1 complete  │
    ▼                                                         │
Phase 4 (US2: Naming Conventions) ◄───────────────────────────┤
    │                                                         │
    │ Can run in parallel with US3, US4                       │
Phase 5 (US3: Unnnic Design System) ◄─────────────────────────┤
    │                                                         │
    │ Can run in parallel with US2, US4                       │
Phase 6 (US4: Accessibility) ◄────────────────────────────────┘
    │
    ▼
Phase 7 (Polish) ── Depends on all user stories complete
```

### User Story Dependencies

| Story | Depends On | Can Run In Parallel With |
|-------|------------|--------------------------|
| US1 (P1) | Phase 2 Foundational | None - MVP, complete first |
| US2 (P2) | US1 (for Stylelint BEM validation) | US3, US4 |
| US3 (P3) | US1 (for test infrastructure) | US2, US4 |
| US4 (P3) | US1 (for Lighthouse in CI) | US2, US3 |

### Within Each User Story

1. Tests first (if applicable) - should fail initially
2. Configuration files
3. Implementation
4. Validation (tests pass, coverage met)

---

## Parallel Opportunities

### Phase 1 (All parallel)
```bash
# Launch all setup tasks together:
T001: Install Python dev dependencies
T002: Install Node.js dev dependencies
T003: Create backend test directories
T004: Create frontend test directories
T005: Create frontend mocks
```

### Phase 2 (Parallel after T006-T007)
```bash
# After pyproject.toml created, launch frontend configs:
T008: ESLint config
T009: Prettier config
T010: Stylelint config
```

### Phase 3 - US1 Backend Tests (All parallel)
```bash
# Launch all backend tests together:
T017: test_models.py
T018: test_cache_service.py
T019: test_jira_client.py
T020: test_sync_service.py
```

### Phase 3 - US1 Frontend Tests (All parallel)
```bash
# Launch all component tests together:
T023-T028: All component and service tests
```

### Phase 4 - US2 BEM Refactoring (All parallel)
```bash
# Different files, can refactor simultaneously:
T040-T046: All component BEM refactoring
```

### Phase 5 - US3 Unnnic Migration (All parallel)
```bash
# Component migrations can happen simultaneously:
T058-T063: All component replacements
T064-T068: All design token replacements
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational configs
3. Complete Phase 3: US1 (Testing + Pre-commit + CI)
4. **STOP and VALIDATE**:
   - `pre-commit run --all-files` passes
   - `pytest --cov` shows 80%+ backend coverage
   - `npm run test:coverage` shows 80%+ frontend coverage
5. **MVP DELIVERED**: Development workflow is protected

### Incremental Delivery

| Increment | Delivered Value |
|-----------|-----------------|
| US1 Complete | Dev workflow protected, tests catch regressions |
| US2 Complete | Consistent codebase, easier onboarding |
| US3 Complete | Brand consistency, reduced maintenance |
| US4 Complete | Accessibility compliance, better UX |

### Parallel Team Strategy

With multiple developers after US1:
- Developer A: US2 (BEM refactoring)
- Developer B: US3 (Unnnic migration)
- Developer C: US4 (Accessibility)

All can proceed simultaneously since they touch different aspects of the same components.

---

## Summary

| Metric | Count |
|--------|-------|
| **Total Tasks** | 87 |
| **Setup Phase** | 5 tasks |
| **Foundational Phase** | 8 tasks |
| **US1 (Dev Tooling + Testing)** | 26 tasks |
| **US2 (Naming Conventions)** | 16 tasks |
| **US3 (Unnnic Design System)** | 15 tasks |
| **US4 (Accessibility)** | 10 tasks |
| **Polish Phase** | 7 tasks |
| **Parallel Opportunities** | 65 tasks marked [P] |

### Suggested MVP Scope

**MVP = Phase 1 + Phase 2 + Phase 3 (US1)**

Total: 39 tasks to get protected development workflow with:
- Pre-commit hooks validating all changes
- 80%+ test coverage on backend and frontend
- CI pipeline running all checks on PR

This is the critical foundation - once US1 is complete, the remaining stories can be implemented with confidence that quality is enforced.
