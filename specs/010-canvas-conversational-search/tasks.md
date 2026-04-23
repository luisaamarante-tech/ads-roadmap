# Tasks: Canvas Mode with Conversational Search

**Input**: Design documents from `/specs/010-canvas-conversational-search/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: Required per constitution (80% coverage threshold)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `frontend/src/`, `frontend/tests/`
- Paths follow existing project structure from plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and TypeScript types

- [X] T001 Create CanvasMode component directory at frontend/src/components/CanvasMode/
- [X] T002 [P] Create canvas TypeScript types in frontend/src/types/canvas.ts
- [X] T003 [P] Create utils directory structure at frontend/src/utils/ (if not exists)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core utilities and composables that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Implement searchResultParser utility in frontend/src/utils/searchResultParser.ts
- [X] T005 Write unit tests for searchResultParser in frontend/tests/utils/searchResultParser.spec.ts
- [X] T006 Implement useCanvasSearch composable in frontend/src/composables/useCanvasSearch.ts
- [X] T007 Write unit tests for useCanvasSearch in frontend/tests/composables/useCanvasSearch.spec.ts

**Checkpoint**: Foundation ready - parser and state management tested and working

---

## Phase 3: User Story 1 - Enter Canvas Search Mode (Priority: P1) 🎯 MVP

**Goal**: User can click a trigger to enter canvas mode with split-panel layout (WebChat left 40%, results right 60%)

**Independent Test**: Click search trigger → screen splits into two panels with WebChat on left and empty results on right

### Tests for User Story 1

- [X] T008 [P] [US1] Write unit tests for CanvasContainer in frontend/tests/components/CanvasContainer.spec.ts
- [X] T009 [P] [US1] Write unit tests for CanvasEmptyState in frontend/tests/components/CanvasEmptyState.spec.ts

### Implementation for User Story 1

- [X] T010 [P] [US1] Create CanvasEmptyState component in frontend/src/components/CanvasMode/CanvasEmptyState.vue
- [X] T011 [US1] Create CanvasContainer component in frontend/src/components/CanvasMode/CanvasContainer.vue
- [X] T012 [US1] Add canvas mode trigger button to RoadmapView navbar in frontend/src/views/RoadmapView.vue
- [X] T013 [US1] Integrate useCanvasSearch composable into RoadmapView in frontend/src/views/RoadmapView.vue
- [X] T014 [US1] Add CSS overrides for WebChat positioning in canvas mode in frontend/src/components/CanvasMode/CanvasContainer.vue
- [X] T015 [US1] Hide traditional filters when canvas mode is active in frontend/src/views/RoadmapView.vue

**Checkpoint**: User Story 1 complete - can enter canvas mode and see split panel with WebChat and empty state

---

## Phase 4: User Story 2 - Receive and Display Search Results (Priority: P1)

**Goal**: When agent sends [[SEARCH_RESULT]] block, roadmap items are filtered in real-time on right panel

**Independent Test**: Send message → agent responds with [[SEARCH_RESULT]] → right panel shows only matching items

### Tests for User Story 2

- [X] T016 [P] [US2] Write unit tests for CanvasSearchResults in frontend/tests/components/CanvasSearchResults.spec.ts

### Implementation for User Story 2

- [X] T017 [US2] Create CanvasSearchResults component in frontend/src/components/CanvasMode/CanvasSearchResults.vue
- [X] T018 [US2] Add WebChat message listener to useCanvasSearch composable in frontend/src/composables/useCanvasSearch.ts
- [X] T019 [US2] Implement message parsing and filter update logic in useCanvasSearch in frontend/src/composables/useCanvasSearch.ts
- [X] T020 [US2] Connect CanvasSearchResults to filtered items from composable in frontend/src/components/CanvasMode/CanvasContainer.vue
- [X] T021 [US2] Handle edge case: invalid IDs silently skipped in frontend/src/utils/searchResultParser.ts
- [X] T022 [US2] Handle edge case: zero results shows "no matching items" state in frontend/src/components/CanvasMode/CanvasSearchResults.vue

**Checkpoint**: User Story 2 complete - search results filter roadmap items in real-time

---

## Phase 5: User Story 3 - Maintain Search Context (Priority: P2)

**Goal**: Search results persist based on most recent [[SEARCH_RESULT]], even across conversation turns

**Independent Test**: Receive [[SEARCH_RESULT]] → send follow-up → previous results remain until new [[SEARCH_RESULT]]

### Implementation for User Story 3

- [X] T023 [US3] Implement result persistence logic in useCanvasSearch composable in frontend/src/composables/useCanvasSearch.ts
- [X] T024 [US3] Add history scanning for last [[SEARCH_RESULT]] on canvas mode enter in frontend/src/composables/useCanvasSearch.ts
- [X] T025 [US3] Update unit tests for context persistence in frontend/tests/composables/useCanvasSearch.spec.ts

**Checkpoint**: User Story 3 complete - search context persists correctly

---

## Phase 6: User Story 4 - Exit Canvas Mode (Priority: P2)

**Goal**: User can exit canvas mode and return to normal roadmap view with filters restored

**Independent Test**: Click exit button → returns to normal view with filters visible

### Tests for User Story 4

- [X] T026 [P] [US4] Write unit tests for CanvasExitButton in frontend/tests/components/CanvasExitButton.spec.ts

### Implementation for User Story 4

- [X] T027 [US4] Create CanvasExitButton component in frontend/src/components/CanvasMode/CanvasExitButton.vue
- [X] T028 [US4] Add exit button to CanvasContainer in frontend/src/components/CanvasMode/CanvasContainer.vue
- [X] T029 [US4] Implement exitCanvasMode action in useCanvasSearch composable in frontend/src/composables/useCanvasSearch.ts
- [X] T030 [US4] Restore filter UI visibility on exit in frontend/src/views/RoadmapView.vue
- [X] T031 [US4] Ensure WebChat conversation history preserved on mode switch in frontend/src/composables/useCanvasSearch.ts

**Checkpoint**: User Story 4 complete - can exit canvas mode and return to normal view

---

## Phase 7: User Story 5 - Visual Polish and Animations (Priority: P3)

**Goal**: Smooth, professional animations for mode transitions (300-400ms, ease-out)

**Independent Test**: Trigger mode transitions → animations are smooth, no visual glitches

### Implementation for User Story 5

- [X] T032 [US5] Add Vue Transition wrapper for canvas mode enter/exit in frontend/src/views/RoadmapView.vue
- [X] T033 [US5] Implement CSS animations for panel slide and fade in frontend/src/components/CanvasMode/CanvasContainer.vue
- [X] T034 [US5] Add stagger animation for search results appearance in frontend/src/components/CanvasMode/CanvasSearchResults.vue
- [X] T035 [US5] Add subtle pulse animation to empty state icon in frontend/src/components/CanvasMode/CanvasEmptyState.vue
- [X] T036 [US5] Add fade animation for filter panel hide/show in frontend/src/views/RoadmapView.vue

**Checkpoint**: User Story 5 complete - all animations smooth and professional

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, cleanup, and documentation

- [X] T037 [P] Run full test suite and verify 80% coverage threshold in frontend/
- [X] T038 [P] Run Prettier, ESLint, and Stylelint on all new files in frontend/
- [X] T039 Responsive design review for canvas mode on different screen sizes
- [X] T040 Cross-browser testing (Chrome, Firefox, Safari, Edge)
- [X] T041 Run quickstart.md validation scenarios
- [X] T042 Update any affected component documentation

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - US1 and US2 are both P1, but US2 needs CanvasContainer from US1
  - US3 and US4 are both P2, can run in parallel after US1/US2
  - US5 (P3) can start after basic functionality from US1-US4
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

```
Phase 1 (Setup)
     │
     ▼
Phase 2 (Foundational) ─────────────────────────────┐
     │                                               │
     ▼                                               │
Phase 3 (US1: Enter Canvas) ◀────────────────────────┤
     │                                               │
     ▼                                               │
Phase 4 (US2: Display Results) ◀─────────────────────┤
     │                                               │
     ├──────────────────┬───────────────────────────┘
     │                  │
     ▼                  ▼
Phase 5 (US3)     Phase 6 (US4)
     │                  │
     └──────────┬───────┘
                │
                ▼
         Phase 7 (US5: Polish)
                │
                ▼
         Phase 8 (Final)
```

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Models/Types before services/composables
- Composables before components
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

**Setup Phase (all parallel)**:
- T001, T002, T003 can run in parallel

**Foundational Phase**:
- T004 → T005 (parser then tests)
- T006 → T007 (composable then tests)

**Within User Stories**:
- T008 and T009 can run in parallel (US1 tests)
- T010 independent of T011 (US1 components)
- T016 independent (US2 tests)
- T026 independent (US4 tests)

---

## Parallel Example: User Story 1

```bash
# Launch tests for User Story 1 together:
Task: "T008 Write unit tests for CanvasContainer"
Task: "T009 Write unit tests for CanvasEmptyState"

# After tests pass (fail first), launch components:
Task: "T010 Create CanvasEmptyState component"
Task: "T011 Create CanvasContainer component"
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Enter Canvas Mode)
4. Complete Phase 4: User Story 2 (Display Results)
5. **STOP and VALIDATE**: Test US1 + US2 independently
6. Deploy/demo if ready - basic conversational search works!

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add US1 (Enter Canvas) → Test → Demo (can enter canvas mode)
3. Add US2 (Results) → Test → Demo (search works!) - **MVP COMPLETE**
4. Add US3 (Context) → Test → Demo (better UX)
5. Add US4 (Exit) → Test → Demo (complete flow)
6. Add US5 (Animations) → Test → Demo (polished)
7. Each story adds value without breaking previous stories

---

## Task Summary

| Phase | Tasks | Parallel Tasks | Files Modified |
|-------|-------|----------------|----------------|
| 1. Setup | 3 | 2 | 3 new directories/files |
| 2. Foundational | 4 | 0 | 4 files |
| 3. US1 (P1) | 8 | 2 | 5 files |
| 4. US2 (P1) | 7 | 1 | 4 files |
| 5. US3 (P2) | 3 | 0 | 2 files |
| 6. US4 (P2) | 6 | 1 | 4 files |
| 7. US5 (P3) | 5 | 0 | 4 files |
| 8. Polish | 6 | 2 | Various |

**Total**: 42 tasks | **MVP (US1+US2)**: 22 tasks

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing (TDD approach)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Constitution requires 80% coverage - tests are mandatory
- Follow BEM naming for CSS classes
- Use Unnnic components where applicable
