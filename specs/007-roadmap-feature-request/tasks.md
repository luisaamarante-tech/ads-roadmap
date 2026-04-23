---

description: "Task list for Roadmap Feature Request implementation"
---

# Tasks: Roadmap Feature Request

**Input**: Design documents from `/specs/007-roadmap-feature-request/`  
**Prerequisites**: `plan.md` (required), `spec.md` (required), `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `- [ ] T### [P?] [US#?] Description with file path`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[US#]**: Which user story this task belongs to (US1, US2, US3). Setup/Foundational/Polish tasks have no story label.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create required configuration scaffolding and wire environment for local runs.

- [x] T001 Create routing schema in `backend/config/feature_request_routing.schema.json`
- [x] T002 Create initial routing config in `backend/config/feature_request_routing.json`
- [x] T003 Update backend container env wiring for Slack webhook in `docker-compose.yml`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core backend building blocks required before user story implementation.

**⚠️ CRITICAL**: No user story work should begin until this phase is complete.

- [x] T004 Create feature request DTO models in `backend/app/models/feature_request.py`
- [x] T005 Implement routing config loader + schema validation in `backend/app/services/feature_request_routing_loader.py`
- [x] T006 Update configuration to expose routing + Slack webhook settings in `backend/app/config.py`
- [x] T007 Initialize Flask-Limiter in `backend/app/__init__.py`
- [x] T008 Add idempotency helpers (get/set with TTL) in `backend/app/services/cache_service.py`
- [x] T009 Add Jira issue creation support (create issue + ADF builder) in `backend/app/services/jira_client.py`

**Checkpoint**: Backend foundation ready (routing loadable, limiter available, idempotency storage available, Jira create-issue callable).

---

## Phase 3: User Story 1 - Submit a feature request from the roadmap (Priority: P1) 🎯 MVP

**Goal**: Provide a “Request Feature” form on the roadmap page and create a Jira issue in the correct backlog with `[FEATURE-REQUEST]` title prefix.

**Independent Test**: From the roadmap page, open the form, select a Module, submit Title/Description/Email, and receive a success confirmation containing the created Jira issue key (and link when available).

### Backend (US1)

- [x] T010 [US1] Add GET requestable modules endpoint in `backend/app/routes/roadmap.py` (`/feature-request/modules`)
- [x] T011 [US1] Add POST feature requests endpoint skeleton in `backend/app/routes/roadmap.py` (`/feature-requests`)
- [x] T012 [US1] Implement payload validation (required fields, lengths, email format, honeypot) in `backend/app/routes/roadmap.py`
- [x] T013 [US1] Implement moduleId → Jira destination lookup using `backend/app/services/feature_request_routing_loader.py`
- [x] T014 [US1] Create Jira issue with `[FEATURE-REQUEST]` prefix and full details in `backend/app/services/jira_client.py`
- [x] T015 [US1] Add Idempotency-Key handling (return previous response on retry) in `backend/app/routes/roadmap.py`
- [x] T016 [US1] Apply per-route rate limits for feature request endpoints in `backend/app/routes/roadmap.py`

### Frontend (US1)

- [x] T017 [P] [US1] Add feature request types in `frontend/src/types/roadmap.ts`
- [x] T018 [P] [US1] Add API methods in `frontend/src/services/roadmapService.ts` (`getFeatureRequestModules`, `createFeatureRequest`)
- [x] T019 [US1] Create request form component in `frontend/src/components/RoadmapFeatureRequestForm.vue`
- [x] T020 [US1] Add “Request Feature” entry point + modal wiring in `frontend/src/views/RoadmapView.vue`
- [x] T021 [US1] Implement module loading and submit flow in `frontend/src/components/RoadmapFeatureRequestForm.vue`
- [x] T022 [US1] Add success UI with returned Jira issue key/link in `frontend/src/components/RoadmapFeatureRequestForm.vue`

### Tests (US1)

> Note: While tests are not explicitly requested in `spec.md`, this repository’s constitution and CI require coverage; include these to keep the feature shippable.

- [x] T023 [P] [US1] Add routing loader unit tests in `backend/tests/unit/test_feature_request_routing.py`
- [x] T024 [P] [US1] Add feature request route integration tests (mock Jira) in `backend/tests/integration/test_feature_request_routes.py`
- [x] T025 [P] [US1] Extend service tests for new endpoints in `frontend/tests/services/roadmapService.spec.ts`
- [x] T026 [P] [US1] Add component tests for basic submit flow in `frontend/tests/components/RoadmapFeatureRequestForm.spec.ts`

**Checkpoint**: US1 complete when a Jira issue is created and the user sees confirmation (Slack notification not required yet).

---

## Phase 4: User Story 2 - Get clear validation and failure feedback (Priority: P2)

**Goal**: Prevent invalid submissions and provide clear, actionable errors without creating duplicate Jira issues.

**Independent Test**: Attempt to submit without Module/Title/Description/Email and confirm client + server feedback blocks submission; simulate a retry/double-submit and confirm only one Jira issue is created and the same response is returned.

### Backend (US2)

- [x] T027 [US2] Standardize error responses for validation failures in `backend/app/routes/roadmap.py`
- [x] T028 [US2] Harden idempotency semantics (TTL, response reuse, safe fallbacks) in `backend/app/services/cache_service.py`
- [x] T029 [P] [US2] Add idempotency unit tests in `backend/tests/unit/test_feature_request_idempotency.py`

### Frontend (US2)

- [x] T030 [US2] Add per-field client-side validation in `frontend/src/components/RoadmapFeatureRequestForm.vue`
- [x] T031 [US2] Add clear server error rendering and retry guidance in `frontend/src/components/RoadmapFeatureRequestForm.vue`
- [x] T032 [P] [US2] Extend component tests for validation/error states in `frontend/tests/components/RoadmapFeatureRequestForm.spec.ts`

**Checkpoint**: US2 complete when invalid requests never create Jira issues and users always get clear corrective feedback.

---

## Phase 5: User Story 3 - Notify product/tech leaders in Slack (Priority: P3)

**Goal**: Notify `#weni-product-tech-squad-leaders` in Slack after successful feature request submission, including a Jira issue reference/link.

**Independent Test**: Submit a request successfully and confirm a single Slack notification appears with module, title, short excerpt, and Jira issue link.

### Backend (US3)

- [x] T033 [P] [US3] Implement Slack webhook client in `backend/app/services/slack_service.py`
- [x] T034 [US3] Send Slack notification after Jira issue creation in `backend/app/routes/roadmap.py`
- [x] T035 [US3] Add bounded retries/backoff and status reporting in `backend/app/services/slack_service.py`
- [x] T036 [P] [US3] Add Slack service unit tests (mock HTTP) in `backend/tests/unit/test_slack_service.py`

### Frontend (US3)

- [x] T037 [US3] Display leader notification status (when present) in `frontend/src/components/RoadmapFeatureRequestForm.vue`
- [x] T038 [P] [US3] Extend service tests for notification status field in `frontend/tests/services/roadmapService.spec.ts`

**Checkpoint**: US3 complete when the Slack channel receives exactly one message per successful request (with sensible handling on Slack failures).

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Align docs/contracts with implementation, improve UX/accessibility, and add observability.

- [x] T039 [P] Sync contract details with implementation in `specs/007-roadmap-feature-request/contracts/openapi.yaml`
- [x] T040 Improve accessibility (labels, focus management, keyboard navigation) in `frontend/src/components/RoadmapFeatureRequestForm.vue`
- [x] T041 Add safe operational logging (no sensitive payload logging) in `backend/app/routes/roadmap.py` and `backend/app/services/jira_client.py`
- [x] T042 Validate quickstart smoke test and update if needed in `specs/007-roadmap-feature-request/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)** → required before Foundational
- **Phase 2 (Foundational)** → blocks all user stories
- **Phase 3 (US1)** → MVP; required before US2/US3
- **Phase 4 (US2)** → builds on US1 UX + endpoint behavior
- **Phase 5 (US3)** → builds on US1 Jira creation
- **Phase 6 (Polish)** → after desired stories complete

### User Story Dependencies

- **US1 (P1)**: Depends on Phase 2
- **US2 (P2)**: Depends on US1
- **US3 (P3)**: Depends on US1

### Parallel Opportunities

- In **US1**, frontend work can proceed in parallel with backend work once Phase 2 is complete.
- Tasks marked **[P]** can be assigned to different engineers/agents concurrently.

---

## Parallel Example: User Story 1

```bash
# Backend tasks in parallel (different files):
Task: "Add feature request types in frontend/src/types/roadmap.ts"
Task: "Add API methods in frontend/src/services/roadmapService.ts"

# Frontend tasks in parallel once service/types exist:
Task: "Create request form component in frontend/src/components/RoadmapFeatureRequestForm.vue"
Task: "Add Request Feature entry point in frontend/src/views/RoadmapView.vue"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

Complete Phases 1–3, then validate the independent test for US1. This delivers the core business value (feature request → Jira issue) and can be demoed immediately.

### Incremental Delivery

After MVP:

- Add US2 for robust validation and clear feedback
- Add US3 for Slack leader notifications
- Finish with Polish for accessibility, logging, and contract/doc alignment

