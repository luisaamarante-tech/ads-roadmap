---
description: "Task list for Epic Likes and Multi-Module Selection feature"
---

# Tasks: Epic Likes and Multi-Module Selection

**Input**: Design documents from `/specs/006-epic-likes-multi-select/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Tests**: Tests are included to meet the 80% coverage requirement specified in the constitution.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

This is a web application with:
- **Backend**: `backend/app/` for source, `backend/tests/` for tests
- **Frontend**: `frontend/src/` for source, `frontend/tests/` for tests
- **Configuration**: `backend/config/` for JIRA field mappings

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: JIRA field configuration and schema updates

- [X] T001 Update JIRA projects schema to require roadmap_likes field in backend/config/jira_projects.schema.json
- [X] T002 [P] Add roadmap_likes custom field IDs for all 6 projects in backend/config/jira_projects.json
- [X] T003 [P] Validate configuration JSON against schema using validation script

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core data model and service infrastructure that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Update ProjectFieldConfiguration dataclass to include roadmap_likes field in backend/app/models/custom_field.py
- [X] T005 Update ProjectFieldMapping dataclass to include roadmap_likes field in backend/app/services/config_loader.py
- [X] T006 Update RoadmapItem dataclass to include likes field with default 0 in backend/app/models/roadmap.py
- [X] T007 Update RoadmapItem.to_dict() method to serialize likes field in backend/app/models/roadmap.py
- [X] T008 Update RoadmapItem.matches_filters() to accept module as List[str] in backend/app/models/roadmap.py
- [X] T009 [P] Update RoadmapItem interface to include likes: number field in frontend/src/types/roadmap.ts
- [X] T010 [P] Update RoadmapFilters interface to support module?: string | string[] in frontend/src/types/roadmap.ts
- [X] T011 [P] Create LikeResponse interface in frontend/src/types/roadmap.ts

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - View Like Count on Epics (Priority: P1) 🎯 MVP

**Goal**: Users can see how many likes each roadmap epic has received, with counts retrieved from JIRA during sync

**Independent Test**: Load the roadmap page and verify that like counts from JIRA are displayed on each epic card (even if all counts are 0)

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T012 [P] [US1] Unit test RoadmapItem includes likes field in backend/tests/unit/test_roadmap_model.py
- [X] T013 [P] [US1] Unit test RoadmapItem.to_dict() serializes likes field in backend/tests/unit/test_roadmap_model.py
- [X] T014 [P] [US1] Unit test JiraClient extracts likes field from JIRA response in backend/tests/unit/test_jira_client.py
- [X] T015 [P] [US1] Unit test JiraClient defaults to 0 when likes field missing in backend/tests/unit/test_jira_client.py
- [X] T016 [P] [US1] Integration test sync includes likes in cached data in backend/tests/unit/test_sync_service.py
- [X] T017 [P] [US1] Component test RoadmapCard displays like count in frontend/tests/components/RoadmapCard.spec.ts

### Implementation for User Story 1

**Backend - JIRA Sync**:

- [X] T018 [US1] Update JiraClient._extract_roadmap_item() to extract likes from JIRA custom field in backend/app/services/jira_client.py
- [X] T019 [US1] Add error handling for missing roadmap_likes field mapping (default to 0) in backend/app/services/jira_client.py
- [X] T020 [US1] Verify SyncService includes likes in sync cycle (no changes needed, validates existing flow) in backend/app/services/sync_service.py
- [X] T021 [US1] Update GET /api/v1/roadmap/items endpoint to return likes in response in backend/app/routes/roadmap.py

**Frontend - Display**:

- [X] T022 [P] [US1] Update RoadmapCard.vue to display like count in card header in frontend/src/components/RoadmapCard.vue
- [X] T023 [P] [US1] Add like icon (heart) and count styling using BEM and Unnnic tokens in frontend/src/components/RoadmapCard.vue
- [X] T024 [P] [US1] Handle likes: undefined gracefully (show 0) in frontend/src/components/RoadmapCard.vue

**Verification**:

- [X] T025 [US1] Manual test: Start backend, trigger sync, verify likes appear in API response
- [X] T026 [US1] Manual test: Load frontend, verify like counts display on all epic cards

**Checkpoint**: At this point, User Story 1 should be fully functional - like counts are visible on all epics

---

## Phase 4: User Story 2 - Like an Epic (Priority: P2)

**Goal**: Users can click a like button to increment the like count, which updates both the UI and the JIRA custom field

**Independent Test**: Click the like button on an epic, verify the count increments in the UI, and confirm the JIRA custom field is updated

### Tests for User Story 2

- [X] T027 [P] [US2] Unit test JiraClient.update_epic_likes() method in backend/tests/unit/test_jira_client.py
- [X] T028 [P] [US2] Unit test JiraClient.update_epic_likes() handles missing field config in backend/tests/unit/test_jira_client.py
- [X] T029 [P] [US2] API test POST /api/v1/roadmap/items/{id}/like success case in backend/tests/unit/test_roadmap_routes.py
- [X] T030 [P] [US2] API test POST /api/v1/roadmap/items/{id}/like with invalid item ID in backend/tests/unit/test_roadmap_routes.py
- [X] T031 [P] [US2] API test POST /api/v1/roadmap/items/{id}/like with JIRA API error in backend/tests/unit/test_roadmap_routes.py
- [ ] T032 [P] [US2] Component test like button click triggers API call in frontend/tests/components/RoadmapCard.test.ts
- [ ] T033 [P] [US2] Component test like button shows loading state in frontend/tests/components/RoadmapCard.test.ts
- [ ] T034 [P] [US2] Component test like button handles errors gracefully in frontend/tests/components/RoadmapCard.test.ts
- [X] T035 [P] [US2] Service test likeEpic() calls correct endpoint in frontend/tests/services/roadmapService.test.ts

### Implementation for User Story 2

**Backend - Like Endpoint**:

- [X] T036 [US2] Implement JiraClient.update_epic_likes(issue_key, new_count) method in backend/app/services/jira_client.py
- [X] T037 [US2] Add validation for project field configuration in update_epic_likes method in backend/app/services/jira_client.py
- [X] T038 [US2] Add error handling for JIRA API failures in update_epic_likes method in backend/app/services/jira_client.py
- [X] T039 [US2] Create POST /api/v1/roadmap/items/{item_id}/like endpoint in backend/app/routes/roadmap.py
- [X] T040 [US2] Implement like endpoint logic: get item, update JIRA, invalidate cache in backend/app/routes/roadmap.py
- [X] T041 [US2] Add error handling for 404 (item not found) and 500 (JIRA error) in backend/app/routes/roadmap.py
- [X] T042 [US2] Return LikeResponse JSON with id, likes, success fields in backend/app/routes/roadmap.py

**Frontend - Like Button**:

- [X] T043 [P] [US2] Add likeEpic(itemId: string) method to roadmapService.ts in frontend/src/services/roadmapService.ts
- [X] T044 [US2] Add like button with click handler to RoadmapCard.vue in frontend/src/components/RoadmapCard.vue
- [X] T045 [US2] Implement optimistic update: increment count immediately on click in frontend/src/components/RoadmapCard.vue
- [X] T046 [US2] Add debouncing (500ms) to prevent rapid clicks in frontend/src/components/RoadmapCard.vue
- [X] T047 [US2] Implement server reconciliation: update count from API response in frontend/src/components/RoadmapCard.vue
- [X] T048 [US2] Add rollback logic: revert count on API error in frontend/src/components/RoadmapCard.vue
- [X] T049 [US2] Add loading state (disable button) while request pending in frontend/src/components/RoadmapCard.vue
- [X] T050 [US2] Add error message display below card on failure in frontend/src/components/RoadmapCard.vue
- [X] T051 [US2] Add ARIA labels for accessibility: "Like this epic (X likes)" in frontend/src/components/RoadmapCard.vue
- [X] T052 [US2] Style like button using Unnnic tokens and BEM methodology in frontend/src/components/RoadmapCard.vue

**Verification**:

- [ ] T053 [US2] Manual test: Click like button, verify UI increments immediately (optimistic)
- [ ] T054 [US2] Manual test: Verify JIRA field updates in JIRA UI
- [ ] T055 [US2] Manual test: Refresh page, verify like count persists from JIRA
- [ ] T056 [US2] Manual test: Simulate JIRA API error, verify rollback and error message

**Checkpoint**: At this point, User Stories 1 AND 2 should both work - users can view and like epics

---

## Phase 5: User Story 3 - Filter by Multiple Modules (Priority: P3)

**Goal**: Users can select multiple product modules simultaneously to filter epics across different product areas

**Independent Test**: Select multiple modules in the filter, verify epics from all selected modules are displayed, and verify the URL updates with multiple module parameters

### Tests for User Story 3

- [X] T057 [P] [US3] Unit test RoadmapItem.matches_filters() with module list in backend/tests/unit/test_roadmap_model.py
- [X] T058 [P] [US3] Unit test RoadmapItem.matches_filters() with empty module list in backend/tests/unit/test_roadmap_model.py
- [X] T059 [P] [US3] API test GET /roadmap/items with single module (backward compatible) in backend/tests/unit/test_roadmap_routes.py
- [X] T060 [P] [US3] API test GET /roadmap/items with multiple module params in backend/tests/unit/test_roadmap_routes.py
- [X] T061 [P] [US3] API test GET /roadmap/items with no module params (show all) in backend/tests/unit/test_roadmap_routes.py
- [X] T062 [P] [US3] Component test multi-select allows selecting multiple modules in frontend/tests/components/RoadmapFilters.test.ts
- [X] T063 [P] [US3] Component test multi-select deselecting modules in frontend/tests/components/RoadmapFilters.test.ts
- [X] T064 [P] [US3] Component test URL updates with multiple module params in frontend/tests/components/RoadmapFilters.test.ts

### Implementation for User Story 3

**Backend - Multi-Module Filtering**:

- [X] T065 [US3] Update GET /api/v1/roadmap/items to accept module as List[str] using Query in backend/app/routes/roadmap.py
- [X] T066 [US3] Update filtering logic to pass module list to matches_filters in backend/app/routes/roadmap.py
- [X] T067 [US3] Add validation: maximum 10 modules per request in backend/app/routes/roadmap.py
- [X] T068 [US3] Verify backward compatibility: single module string still works in backend/app/routes/roadmap.py

**Frontend - Multi-Select UI**:

- [X] T069 [P] [US3] Update RoadmapFilters.vue to support multiple module selection in frontend/src/components/RoadmapFilters.vue
- [X] T070 [P] [US3] Replace single-select dropdown with checkbox list for modules in frontend/src/components/RoadmapFilters.vue
- [X] T071 [P] [US3] Add selectedModules computed property (get/set) in frontend/src/components/RoadmapFilters.vue
- [X] T072 [P] [US3] Implement onModuleToggle handler to add/remove modules from selection in frontend/src/components/RoadmapFilters.vue
- [X] T073 [P] [US3] Style module checkboxes using BEM and Unnnic tokens in frontend/src/components/RoadmapFilters.vue
- [X] T074 [P] [US3] Update RoadmapView.vue to handle module as string or array in filters state in frontend/src/views/RoadmapView.vue
- [X] T075 [US3] Update getRoadmapItems in roadmapService.ts to serialize module array as repeated params in frontend/src/services/roadmapService.ts
- [X] T076 [US3] Update URL serialization to use ?module=X&module=Y format in frontend/src/views/RoadmapView.vue
- [X] T077 [US3] Add URL parsing to restore multi-module selection from query params in frontend/src/views/RoadmapView.vue

**Verification**:

- [ ] T078 [US3] Manual test: Select 2 modules, verify filtered results include both
- [ ] T079 [US3] Manual test: Verify URL shows ?module=flows&module=integrations
- [ ] T080 [US3] Manual test: Copy URL, open in new tab, verify same filters applied
- [ ] T081 [US3] Manual test: Deselect one module, verify results update
- [ ] T082 [US3] Manual test: Select no modules, verify all epics shown

**Checkpoint**: All user stories should now be independently functional - like counts, like actions, and multi-module filtering all work

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final validation

- [X] T083 [P] Run all backend tests and verify 80%+ coverage with pytest --cov in backend/
- [X] T084 [P] Run all frontend tests and verify coverage with npm test:coverage in frontend/
- [X] T085 [P] Run backend linters: black, flake8, mypy in backend/
- [X] T086 [P] Run frontend linters: eslint, prettier, stylelint in frontend/
- [X] T087 [P] Update API documentation (if exists) with new like endpoint in docs/
- [X] T088 [P] Add inline code documentation for complex logic (debouncing, optimistic updates) in frontend/src/components/RoadmapCard.vue
- [X] T089 Verify no trailing whitespace in any files (constitution requirement)
- [X] T090 [P] Test accessibility: like button keyboard navigation and ARIA labels in frontend/
- [X] T091 [P] Test accessibility: multi-select keyboard navigation in frontend/
- [X] T092 Performance test: Verify multi-module filtering < 1s for 500 epics in frontend/
- [X] T093 [P] Create migration guide for adding roadmap_likes field in JIRA in docs/
- [ ] T094 Run complete quickstart.md workflow to validate all steps
- [ ] T095 Smoke test in staging: Like an epic, verify JIRA field updates
- [ ] T096 Smoke test in staging: Filter by multiple modules, share URL

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup (Phase 1) completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational (Phase 2) completion
  - User stories can proceed in parallel (if staffed)
  - Or sequentially in priority order: US1 (P1) → US2 (P2) → US3 (P3)
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
  - **Delivers**: View like counts on epics
  - **Can deploy independently**: Yes - provides immediate value
  
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Builds on US1 but independently testable
  - **Delivers**: Interactive like button
  - **Can deploy independently**: Yes (though best deployed after US1 for coherent UX)
  - **Note**: Integrates with US1's display logic but doesn't break if US1 is incomplete
  
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Completely independent of US1 and US2
  - **Delivers**: Multi-module filtering
  - **Can deploy independently**: Yes - separate feature from likes
  - **Note**: No technical dependency on likes feature, can be developed in parallel

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Backend model updates before service updates
- Backend services before API endpoints
- Frontend types before components
- Frontend services before component integration
- Core implementation before error handling and polish
- Manual verification tests after implementation

### Parallel Opportunities

**Setup Phase (Phase 1)**:
- T002 and T003 can run in parallel (different files)

**Foundational Phase (Phase 2)**:
- T009, T010, T011 (frontend types) can run in parallel with backend tasks
- All frontend type updates (T009-T011) can run in parallel with each other

**User Story 1 - Tests**:
- All test tasks (T012-T017) can run in parallel (different test files)

**User Story 1 - Implementation**:
- T022, T023, T024 (frontend display) can run in parallel with each other

**User Story 2 - Tests**:
- All test tasks (T027-T035) can run in parallel (different test files)

**User Story 2 - Implementation**:
- T043 (service) can run in parallel with backend tasks T036-T042

**User Story 3 - Tests**:
- All test tasks (T057-T064) can run in parallel (different test files)

**User Story 3 - Implementation**:
- All frontend tasks (T069-T073) marked [P] can run in parallel
- T069-T073 can run while backend is being implemented

**Polish Phase (Phase 6)**:
- All tasks marked [P] (T083-T088, T090-T093) can run in parallel

**Cross-Story Parallelization**:
- Once Foundational (Phase 2) completes:
  - Developer A: User Story 1 (T012-T026)
  - Developer B: User Story 2 (T027-T056)
  - Developer C: User Story 3 (T057-T082)
- All three stories can be developed simultaneously by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
T012: "Unit test RoadmapItem includes likes field in backend/tests/unit/test_roadmap_model.py"
T013: "Unit test RoadmapItem.to_dict() serializes likes field in backend/tests/unit/test_roadmap_model.py"
T014: "Unit test JiraClient extracts likes field in backend/tests/unit/test_jira_client.py"
T015: "Unit test JiraClient defaults to 0 when likes field missing in backend/tests/unit/test_jira_client.py"
T016: "Integration test sync includes likes in backend/tests/integration/test_sync_service.py"
T017: "Component test RoadmapCard displays like count in frontend/tests/components/RoadmapCard.test.ts"

# Launch all frontend display tasks together:
T022: "Update RoadmapCard.vue to display like count in frontend/src/components/RoadmapCard.vue"
T023: "Add like icon and styling in frontend/src/components/RoadmapCard.vue"
T024: "Handle likes: undefined gracefully in frontend/src/components/RoadmapCard.vue"
```

## Parallel Example: User Story 2

```bash
# Launch all tests for User Story 2 together:
T027-T035: All test tasks can run in parallel (9 different test files/cases)

# Launch service layer in parallel with backend:
T043: "Add likeEpic() method to roadmapService.ts" (can run while T036-T042 are being done)
```

## Parallel Example: User Story 3

```bash
# Launch all tests for User Story 3 together:
T057-T064: All test tasks can run in parallel (8 different test files/cases)

# Launch all frontend UI tasks together:
T069: "Update RoadmapFilters.vue to support multiple module selection"
T070: "Replace single-select with checkbox list"
T071: "Add selectedModules computed property"
T072: "Implement onModuleToggle handler"
T073: "Style module checkboxes"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

**Goal**: Get like counts visible on roadmap as quickly as possible

1. Complete Phase 1: Setup (T001-T003) - ~1 hour
2. Complete Phase 2: Foundational (T004-T011) - ~2-3 hours
3. Complete Phase 3: User Story 1 (T012-T026) - ~4-6 hours
4. **STOP and VALIDATE**: 
   - Run all US1 tests
   - Load roadmap and verify like counts display
   - Check JIRA fields are being read correctly
5. Deploy to staging/production if ready

**Total MVP Time**: ~1 day (8-10 hours) for a single developer

**MVP Delivers**: Users can see how popular each epic is based on historical like data

### Incremental Delivery (Recommended)

**Sprint 1: Foundation + MVP**
1. Complete Setup (Phase 1) → Configuration ready
2. Complete Foundational (Phase 2) → Data models updated
3. Complete User Story 1 (Phase 3) → Test independently → **Deploy/Demo (MVP!)**

**Sprint 2: Interactive Likes**
4. Complete User Story 2 (Phase 4) → Test independently → **Deploy/Demo**
   - Now users can actually like epics, not just view counts

**Sprint 3: Enhanced Filtering**
5. Complete User Story 3 (Phase 5) → Test independently → **Deploy/Demo**
   - Multi-module filtering adds powerful filtering capability

**Sprint 4: Polish**
6. Complete Polish (Phase 6) → Final validation → **Production ready**

**Benefits**:
- Each sprint delivers working, testable value
- Can stop at any point with a functional feature
- Feedback from US1 can inform US2 and US3
- Lower risk - failures are contained to one story

### Parallel Team Strategy (3 Developers)

With multiple developers, maximize parallelization after Foundational phase:

**Week 1 - Foundation (All Developers)**:
- Day 1: Everyone works on Setup + Foundational together (T001-T011)
- **Checkpoint**: Foundation complete, stories can proceed independently

**Week 2 - User Stories (Parallel Development)**:
- Developer A: User Story 1 (T012-T026) - Like count display
- Developer B: User Story 2 (T027-T056) - Like button interaction
- Developer C: User Story 3 (T057-T082) - Multi-module filtering
- **Checkpoint**: All three stories complete and tested independently

**Week 3 - Integration & Polish**:
- All developers: Integration testing, polish tasks (T083-T096)
- Resolve any conflicts or integration issues
- Deploy all features together

**Total Time**: ~3 weeks for full feature with 3 developers

**Benefits**:
- Fastest time to complete all features
- Requires good planning to avoid merge conflicts
- Each developer owns a complete user story

### Sequential Solo Developer Strategy

If working alone, recommended order:

1. **Days 1-2**: Setup + Foundational + User Story 1 (T001-T026)
   - Deploy MVP after US1
2. **Days 3-4**: User Story 2 (T027-T056)
   - Deploy like button feature
3. **Days 5-6**: User Story 3 (T057-T082)
   - Deploy multi-module filtering
4. **Day 7**: Polish (T083-T096)
   - Final testing and documentation

**Total Time**: ~1.5-2 weeks for solo developer

---

## Task Count Summary

- **Setup (Phase 1)**: 3 tasks
- **Foundational (Phase 2)**: 8 tasks (BLOCKING)
- **User Story 1 (Phase 3)**: 15 tasks (6 tests + 9 implementation)
- **User Story 2 (Phase 4)**: 30 tasks (9 tests + 21 implementation)
- **User Story 3 (Phase 5)**: 26 tasks (8 tests + 18 implementation)
- **Polish (Phase 6)**: 14 tasks

**Total**: 96 tasks

**Test Coverage**: 23 test tasks (24% of total) ensuring 80%+ code coverage

**Parallelizable**: 41 tasks marked [P] (43% can run in parallel with proper staffing)

---

## Validation Checklist

Before marking this feature complete, verify:

- [ ] All 96 tasks completed
- [ ] All tests passing (80%+ coverage achieved)
- [ ] All linters passing (no trailing whitespace, PEP 8, ESLint)
- [ ] Each user story independently tested and verified:
  - [ ] US1: Like counts display correctly from JIRA
  - [ ] US2: Like button increments count and updates JIRA
  - [ ] US3: Multi-module filtering works with URL sharing
- [ ] Constitution compliance:
  - [ ] Code follows BEM methodology (frontend)
  - [ ] Code follows PEP 8 (backend)
  - [ ] Semantic HTML used (buttons, proper ARIA)
  - [ ] No trailing whitespace
  - [ ] Self-documenting code with minimal comments
- [ ] Accessibility:
  - [ ] Like button keyboard accessible
  - [ ] ARIA labels present
  - [ ] Color contrast meets WCAG AA
- [ ] Performance:
  - [ ] Like count load < 2s
  - [ ] Like action < 3s
  - [ ] Multi-module filter < 1s
- [ ] JIRA configuration:
  - [ ] "Roadmap Likes" field created in all projects
  - [ ] Field IDs added to jira_projects.json
  - [ ] Configuration validated
- [ ] Documentation:
  - [ ] quickstart.md validated (all steps work)
  - [ ] Migration guide created for JIRA field setup
  - [ ] Code comments explain "why" for complex logic
- [ ] Deployment:
  - [ ] Staging smoke tests passed
  - [ ] Production deployment plan reviewed
  - [ ] Rollback plan documented

---

## Notes

- [P] tasks = different files, no shared state, can run in parallel
- [Story] label maps task to specific user story for traceability and parallel development
- Each user story is independently completable and testable
- Tests must FAIL before implementing (TDD approach)
- Commit after each task or logical group for clean git history
- Stop at any checkpoint to validate story independently before proceeding
- **Key Architecture Decision**: No local database - JIRA is the single source of truth for likes
- **Key UX Decision**: Optimistic updates for like button (instant feedback, server reconciliation)
- **Key Compatibility Decision**: Multi-module uses repeated query params (standard, backward compatible)
