# Tasks: Weni Public Roadmap

**Input**: Design documents from `/specs/001-public-roadmap/`
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, contracts/openapi.yaml ✓

**Tests**: Optional - not explicitly requested in specification

**Organization**: Tasks grouped by user story for independent implementation and testing

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Exact file paths included in all descriptions

## Path Conventions

- **Backend**: `backend/` at repository root (Flask/Python)
- **Frontend**: `frontend/` at repository root (Vue.js/TypeScript)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize both backend and frontend project structures

### Backend Setup

- [x] T001 Create backend directory structure per plan in `backend/`
- [x] T002 [P] Create `backend/requirements.txt` with Flask dependencies (flask, flask-cors, flask-caching, flask-limiter, apscheduler, requests, python-dotenv, gunicorn)
- [x] T003 [P] Create `backend/.env.example` with JIRA configuration template
- [x] T004 [P] Create `backend/run.py` entry point script

### Frontend Setup

- [x] T005 Initialize Vue.js 3 project with TypeScript in `frontend/`
- [x] T006 [P] Configure `frontend/package.json` with dependencies (vue, vue-router, axios, @weni/unnnic-system)
- [x] T007 [P] Create `frontend/.env.example` with API URL template
- [x] T008 [P] Configure `frontend/vite.config.ts` with Vite settings
- [x] T009 [P] Configure `frontend/tsconfig.json` for TypeScript
- [x] T010 Setup Unnnic Design System in `frontend/src/main.ts`

---

## Phase 2: Foundational (Backend Core - BLOCKING)

**Purpose**: Complete backend infrastructure that MUST be ready before ANY frontend user story

**⚠️ CRITICAL**: No frontend implementation can begin until this phase is complete (frontend needs API data)

### Configuration & App Factory

- [x] T011 Create Flask app factory in `backend/app/__init__.py` with extensions (CORS, Cache, Limiter)
- [x] T012 [P] Create configuration management in `backend/app/config.py` with environment variable loading
- [x] T013 [P] Create `backend/app/routes/__init__.py` blueprint registry

### Data Models

- [x] T014 [P] Create RoadmapItem dataclass in `backend/app/models/roadmap.py`
- [x] T015 [P] Create Module dataclass in `backend/app/models/roadmap.py`
- [x] T016 [P] Create SyncMetadata dataclass in `backend/app/models/roadmap.py`
- [x] T017 Create `backend/app/models/__init__.py` with exports

### JIRA Integration (US4 Backend Implementation)

- [x] T018 Create JIRA API client with authentication in `backend/app/services/jira_client.py`
- [x] T019 Implement JQL query builder for public epics in `backend/app/services/jira_client.py`
- [x] T020 Implement field extraction with allowlist security in `backend/app/services/jira_client.py`
- [x] T021 Implement ADF-to-HTML description conversion in `backend/app/services/jira_client.py`

### Sync Service

- [x] T022 Create sync service with APScheduler in `backend/app/services/sync_service.py`
- [x] T023 Implement RoadmapItem validation logic in `backend/app/services/sync_service.py`
- [x] T024 Implement image URL extraction and validation in `backend/app/services/sync_service.py`
- [x] T025 Implement module extraction and counting in `backend/app/services/sync_service.py`

### Cache Service

- [x] T026 Create cache service wrapper in `backend/app/services/cache_service.py`
- [x] T027 Implement file-based fallback cache in `backend/app/services/cache_service.py`
- [x] T028 Create `backend/app/services/__init__.py` with exports

### API Routes

- [x] T029 Create health check endpoint in `backend/app/routes/health.py` (GET /api/v1/health)
- [x] T030 Create GET /api/v1/roadmap/items endpoint in `backend/app/routes/roadmap.py`
- [x] T031 [P] Create GET /api/v1/roadmap/items/{id} endpoint in `backend/app/routes/roadmap.py`
- [x] T032 [P] Create GET /api/v1/roadmap/modules endpoint in `backend/app/routes/roadmap.py`
- [x] T033 [P] Create GET /api/v1/roadmap/stats endpoint in `backend/app/routes/roadmap.py`
- [x] T034 Implement query parameter filtering (status, year, quarter, module) in `backend/app/routes/roadmap.py`

**Checkpoint**: Backend is fully functional - can sync from JIRA and serve data via API

---

## Phase 3: User Story 1 - Browse Roadmap by Status (Priority: P1) 🎯 MVP

**Goal**: Display roadmap items organized by status tabs (Delivered/Now/Next/Future) with item counts

**Independent Test**: Load roadmap page → See status tabs → Click tab → See items for that status with count

### Frontend Foundation

- [x] T035 [US1] Create TypeScript interfaces in `frontend/src/types/roadmap.ts` (RoadmapItem, Module, RoadmapFilters)
- [x] T036 [US1] Create API service in `frontend/src/services/roadmapService.ts` with getRoadmapItems, getStats, getModules
- [x] T037 [US1] Configure Vue Router in `frontend/src/router/index.ts` with /roadmap route

### Core Components

- [x] T038 [US1] Create RoadmapTabs component in `frontend/src/components/RoadmapTabs.vue` using unnnic-tabs
- [x] T039 [US1] Implement tab change event handler with status filter in `frontend/src/components/RoadmapTabs.vue`
- [x] T040 [US1] Create RoadmapCard component (collapsed state only) in `frontend/src/components/RoadmapCard.vue` using unnnic-card and unnnic-tag
- [x] T041 [US1] Create RoadmapCardList component in `frontend/src/components/RoadmapCardList.vue` with item count display
- [x] T042 [US1] Create RoadmapView page in `frontend/src/views/RoadmapView.vue` composing tabs and card list

### Integration

- [x] T043 [US1] Wire up API calls in RoadmapView to fetch items on tab change in `frontend/src/views/RoadmapView.vue`
- [x] T044 [US1] Display item count per status tab in `frontend/src/components/RoadmapTabs.vue`
- [x] T045 [US1] Add loading state during API calls in `frontend/src/views/RoadmapView.vue`
- [x] T046 [US1] Update `frontend/src/App.vue` with router-view and basic layout

**Checkpoint**: User Story 1 complete - Status tabs work with item counts, cards show title + module badge

---

## Phase 4: User Story 2 - View Feature Details (Priority: P1)

**Goal**: Expand roadmap cards to show full description, images (gallery), and documentation link

**Independent Test**: Click any card → Expands with description → See images in carousel → Click "Read More" → Opens docs

### Card Expansion

- [x] T047 [US2] Add expand/collapse functionality to `frontend/src/components/RoadmapCard.vue` using unnnic-accordion
- [x] T048 [US2] Display full description in expanded state in `frontend/src/components/RoadmapCard.vue`
- [x] T049 [US2] Add "Read More" button with conditional render in `frontend/src/components/RoadmapCard.vue`

### Image Gallery

- [x] T050 [US2] Create RoadmapImageGallery component in `frontend/src/components/RoadmapImageGallery.vue` using unnnic-carousel
- [x] T051 [US2] Handle 0-4 images with graceful empty state in `frontend/src/components/RoadmapImageGallery.vue`
- [x] T052 [US2] Integrate image gallery into expanded card in `frontend/src/components/RoadmapCard.vue`

### Polish

- [x] T053 [US2] Add smooth expand/collapse animation in `frontend/src/components/RoadmapCard.vue`
- [x] T054 [US2] Handle missing images gracefully (placeholder/hide) in `frontend/src/components/RoadmapImageGallery.vue`

**Checkpoint**: User Story 2 complete - Cards expand with full details, images show in carousel

---

## Phase 5: User Story 3 - Filter by Module/Product (Priority: P2)

**Goal**: Add year, quarter, and module filters to narrow down roadmap items

**Independent Test**: Select module from dropdown → Only items from that module shown → Clear filter → All items return

### Filter Components

- [x] T055 [US3] Create RoadmapFilters component in `frontend/src/components/RoadmapFilters.vue`
- [x] T056 [US3] Add year dropdown using unnnic-select-smart in `frontend/src/components/RoadmapFilters.vue`
- [x] T057 [US3] Add quarter buttons using unnnic-segmented-control in `frontend/src/components/RoadmapFilters.vue`
- [x] T058 [US3] Add module dropdown using unnnic-select-smart in `frontend/src/components/RoadmapFilters.vue`
- [x] T059 [US3] Implement filter reset/clear functionality in `frontend/src/components/RoadmapFilters.vue`

### Integration

- [x] T060 [US3] Integrate RoadmapFilters into RoadmapView in `frontend/src/views/RoadmapView.vue`
- [x] T061 [US3] Fetch modules list for dropdown on page load in `frontend/src/views/RoadmapView.vue`
- [x] T062 [US3] Update API calls with filter parameters in `frontend/src/views/RoadmapView.vue`
- [x] T063 [US3] Preserve filter state when switching status tabs in `frontend/src/views/RoadmapView.vue`

**Checkpoint**: User Story 3 complete - All filters work, module dropdown populated from API

---

## Phase 6: Polish & Production Readiness

**Purpose**: Cross-cutting concerns, UX improvements, and deployment preparation

### Empty & Loading States

- [x] T064 [P] Create RoadmapEmptyState component in `frontend/src/components/RoadmapEmptyState.vue` using unnnic-alert
- [x] T065 [P] Add skeleton loading state in `frontend/src/components/RoadmapEmptyState.vue` using unnnic-skeleton
- [x] T066 Integrate empty/loading states in `frontend/src/views/RoadmapView.vue`

### Mobile & Responsive

- [x] T067 [P] Add responsive styles to RoadmapTabs in `frontend/src/components/RoadmapTabs.vue`
- [x] T068 [P] Add responsive styles to RoadmapFilters in `frontend/src/components/RoadmapFilters.vue`
- [x] T069 [P] Add responsive grid layout to RoadmapCardList in `frontend/src/components/RoadmapCardList.vue`

### Backend Security & Operations

- [x] T070 [P] Configure rate limiting (100 req/min) in `backend/app/__init__.py`
- [x] T071 [P] Configure CORS with allowed origins in `backend/app/__init__.py`
- [x] T072 [P] Add audit logging for sync operations in `backend/app/services/sync_service.py`
- [x] T073 Add stale data indicator (>10 min since sync) to health response in `backend/app/routes/health.py`

### Containerization

- [x] T074 [P] Create `backend/Dockerfile` for Flask app
- [x] T075 [P] Create `frontend/Dockerfile` for Vue.js build
- [x] T076 Create `docker-compose.yml` at repository root for local development

### Documentation

- [x] T077 [P] Update `backend/.env.example` with all required variables
- [x] T078 [P] Update `frontend/.env.example` with API URL
- [x] T079 Create `README.md` at repository root with setup instructions

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup) ─────────────────────────────────────────┐
     │                                                    │
     ▼                                                    │
Phase 2 (Foundational/Backend) ◀── BLOCKS ALL ──────────┤
     │                                                    │
     ├─────────────────┬─────────────────┐                │
     ▼                 ▼                 ▼                │
Phase 3 (US1)    Phase 4 (US2)    Phase 5 (US3)          │
     │                 │                 │                │
     │ (depends on     │ (depends on     │                │
     │  basic card)    │  T040-T046)     │                │
     └─────────────────┴─────────────────┘                │
                       │                                  │
                       ▼                                  │
               Phase 6 (Polish)                           │
```

### User Story Dependencies

| Story | Depends On | Can Start After |
|-------|------------|-----------------|
| US1 (Browse by Status) | Phase 2 complete | T034 (API routes done) |
| US2 (View Details) | US1 T040-T046 | Cards exist to expand |
| US3 (Filter by Module) | Phase 2 + US1 base | API + Tabs working |

### Within Each Story

1. TypeScript types first
2. API service methods
3. Components (parent → child)
4. Integration and state management
5. Polish and edge cases

### Parallel Opportunities

**Setup Phase (All [P] tasks):**
```
T002, T003, T004 (backend) | T006, T007, T008, T009 (frontend)
```

**Foundational Phase (Model tasks):**
```
T014, T015, T016 (all models in parallel)
```

**Foundational Phase (Route tasks):**
```
T031, T032, T033 (item detail, modules, stats - after T030)
```

**Polish Phase:**
```
T064, T065 | T067, T068, T069 | T070, T071, T072 | T074, T075 | T077, T078
```

---

## Parallel Example: Phase 2 Foundational

```bash
# After T013 (blueprint registry), these can run in parallel:
Task T014: "Create RoadmapItem dataclass in backend/app/models/roadmap.py"
Task T015: "Create Module dataclass in backend/app/models/roadmap.py"
Task T016: "Create SyncMetadata dataclass in backend/app/models/roadmap.py"

# After T030 (items endpoint), these can run in parallel:
Task T031: "Create GET /api/v1/roadmap/items/{id} endpoint"
Task T032: "Create GET /api/v1/roadmap/modules endpoint"
Task T033: "Create GET /api/v1/roadmap/stats endpoint"
```

## Parallel Example: User Story 1

```bash
# After T037 (router), these can run in parallel:
Task T038: "Create RoadmapTabs component in frontend/src/components/RoadmapTabs.vue"
Task T040: "Create RoadmapCard component in frontend/src/components/RoadmapCard.vue"
Task T041: "Create RoadmapCardList component in frontend/src/components/RoadmapCardList.vue"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. ✅ Complete Phase 1: Setup (T001-T010)
2. ✅ Complete Phase 2: Foundational (T011-T034) - **CRITICAL GATE**
3. ✅ Complete Phase 3: User Story 1 (T035-T046)
4. **STOP and VALIDATE**: Status tabs work, cards show, counts display
5. Deploy/demo to stakeholders → Immediate value delivered!

### Incremental Delivery

| Increment | Delivers | Value |
|-----------|----------|-------|
| MVP (US1) | Status tabs + card list | "What's delivered? What's next?" |
| +US2 | Expandable cards + images | Full feature details |
| +US3 | Module filtering | Focused product view |
| +Polish | Mobile + empty states | Production-ready |

### Team Parallelization

```
Developer A (Backend):     Phase 1 backend → Phase 2 all → Phase 6 backend
Developer B (Frontend):    Phase 1 frontend → (wait for Phase 2) → US1 → US2 → US3 → Phase 6 frontend
```

---

## Summary

| Metric | Count |
|--------|-------|
| **Total Tasks** | 79 |
| **Phase 1 (Setup)** | 10 tasks |
| **Phase 2 (Foundational)** | 24 tasks |
| **Phase 3 (US1 - MVP)** | 12 tasks |
| **Phase 4 (US2)** | 8 tasks |
| **Phase 5 (US3)** | 9 tasks |
| **Phase 6 (Polish)** | 16 tasks |
| **Parallel Opportunities** | 28 tasks marked [P] |

### MVP Scope

**Minimum Viable Product = Phase 1 + Phase 2 + Phase 3 (46 tasks)**

After completing MVP:
- ✅ Backend syncs from JIRA and serves public items
- ✅ Frontend shows status tabs (Delivered/Now/Next/Future)
- ✅ Each tab shows items as cards with title + module badge
- ✅ Item counts displayed per status
- ✅ Core value proposition delivered to stakeholders

---

## Notes

- [P] tasks = different files, no blocking dependencies
- [US#] label = maps task to specific user story
- Backend Phase 2 MUST complete before frontend can show real data
- Each user story is independently testable after completion
- Commit after each task or logical group
- Stop at any checkpoint to demo/validate independently
