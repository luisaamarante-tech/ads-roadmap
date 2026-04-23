# Tasks: Epic Viewer Enhancements

**Input**: Design documents from `/specs/008-epic-viewer-enhancements/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Tests are INCLUDED based on 80% coverage requirement from constitution

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `frontend/src/`, `frontend/tests/`
- All paths relative to repository root

---

## Phase 1: Setup (Shared Infrastructure) ✅ COMPLETE

**Purpose**: Project initialization and basic structure

- [x] T001 Review plan.md and verify Vue 3.4, TypeScript 5.3, Vitest configuration in frontend/package.json
- [x] T002 [P] Create composables directory if not exists: frontend/src/composables/
- [x] T003 [P] Create tests/composables directory: frontend/tests/composables/

---

## Phase 2: Foundational (Blocking Prerequisites) ✅ COMPLETE

**Purpose**: Core composables that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Tests for Foundational Composables

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T004 [P] Create test file for useClipboard composable: frontend/tests/composables/useClipboard.spec.ts
- [x] T005 [P] Create test file for useKeyboardNavigation composable: frontend/tests/composables/useKeyboardNavigation.spec.ts
- [x] T006 [P] Write tests for useClipboard: successful copy, API not supported, timeout reset, callbacks
- [x] T007 [P] Write tests for useKeyboardNavigation: ESC, arrow keys, isActive flag, event cleanup

### Implementation of Foundational Composables

- [x] T008 [P] Implement useClipboard composable in frontend/src/composables/useClipboard.ts
- [x] T009 [P] Implement useKeyboardNavigation composable in frontend/src/composables/useKeyboardNavigation.ts
- [x] T010 Run tests for composables and verify 80% coverage: `npm test tests/composables/`
- [x] T011 Fix any failing tests and achieve green test suite for composables

**Checkpoint**: ✅ Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - View Enlarged Epic Images (Priority: P1) ✅ COMPLETE 🎯 MVP

**Goal**: Users can click on epic images to view them in an enlarged modal with basic navigation

**Independent Test**: ✅ Click any epic image → Modal opens with enlarged view → Close with ESC/X/backdrop → Modal closes

**Note**: This phase includes US2 (Navigate Between Images) as the navigation is built into the same ImageCarouselModal component

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T012 [US1] Create test file for ImageCarouselModal: frontend/tests/components/ImageCarouselModal.spec.ts
- [ ] T013 [US1] Write test: should render modal when show=true
- [ ] T014 [US1] Write test: should not render modal when show=false
- [ ] T015 [US1] Write test: should display image at currentIndex
- [ ] T016 [US1] Write test: should emit close on ESC key
- [ ] T017 [US1] Write test: should emit close on backdrop click
- [ ] T018 [US1] Write test: should emit close on close button click
- [ ] T019 [US1] Write test: should navigate to next image on arrow click
- [ ] T020 [US1] Write test: should navigate to previous image on arrow click
- [ ] T021 [US1] Write test: should wrap navigation at boundaries
- [ ] T022 [US1] Write test: should navigate with keyboard arrow keys
- [ ] T023 [US1] Write test: should hide navigation arrows for single image
- [ ] T024 [US1] Write test: should show loading state while image loads
- [ ] T025 [US1] Write test: should show error placeholder for broken images
- [ ] T026 [US1] Write test: should have correct ARIA attributes

### Implementation for User Story 1

- [ ] T027 [US1] Create ImageCarouselModal component: frontend/src/components/ImageCarouselModal.vue
- [ ] T028 [US1] Implement component props interface (images, currentIndex, epicTitle, show)
- [ ] T029 [US1] Implement component emits (close, indexChange)
- [ ] T030 [US1] Implement local state (localIndex, imageLoadingStates)
- [ ] T031 [US1] Implement computed properties (currentImage, positionLabel, showNavigation, currentImageState)
- [ ] T032 [US1] Implement navigation functions (navigateNext, navigatePrev, onClose)
- [ ] T033 [US1] Implement image load/error handlers (onImageLoad, onImageError)
- [ ] T034 [US1] Integrate useKeyboardNavigation composable for ESC and arrow keys
- [ ] T035 [US1] Implement modal template with Teleport to body
- [ ] T036 [US1] Add backdrop with click handler
- [ ] T037 [US1] Add close button with ARIA label
- [ ] T038 [US1] Add image display with loading/error states
- [ ] T039 [US1] Add navigation arrows with position indicator (US2 requirement)
- [ ] T040 [US1] Style modal with BEM methodology and Unnnic CSS variables
- [ ] T041 [US1] Add fade in/out transitions for modal

### Integration with RoadmapCard

- [ ] T042 [US1] Add imports to RoadmapCard.vue: ImageCarouselModal component
- [ ] T043 [US1] Add new state to RoadmapCard: showImageModal, clickedImageIndex
- [ ] T044 [US1] Implement onImageClick handler in RoadmapCard
- [ ] T045 [US1] Implement onModalClose handler in RoadmapCard
- [ ] T046 [US1] Make images clickable in template: add @click="onImageClick(index)"
- [ ] T047 [US1] Add hover styles for clickable images: cursor pointer, scale transform
- [ ] T048 [US1] Add ImageCarouselModal to RoadmapCard template with proper props binding
- [ ] T049 [US1] Expose isExpanded in defineExpose for URL navigation (needed for US3)

### Tests for RoadmapCard Integration

- [ ] T050 [US1] Update RoadmapCard tests: add test for image click opens modal
- [ ] T051 [US1] Update RoadmapCard tests: verify modal receives correct props
- [ ] T052 [US1] Update RoadmapCard tests: verify modal close handler works

### Validation

- [ ] T053 [US1] Run tests for ImageCarouselModal: `npm test tests/components/ImageCarouselModal.spec.ts`
- [ ] T054 [US1] Run tests for RoadmapCard: `npm test tests/components/RoadmapCard.spec.ts`
- [ ] T055 [US1] Verify 80% coverage for ImageCarouselModal and RoadmapCard
- [ ] T056 [US1] Manual test: Click image in browser → Modal opens → Navigate with arrows → Close with ESC
- [ ] T057 [US1] Manual test: Verify modal works with single image (no navigation arrows)
- [ ] T058 [US1] Manual test: Test with broken image URL shows error placeholder

**Checkpoint**: At this point, Users can view and navigate epic images in enlarged modal (US1 + US2 complete)

---

## Phase 4: User Story 3 - Share Epic from Card View (Priority: P1) ✅ COMPLETE 🎯 MVP

**Goal**: Users can share a direct link to a specific epic that automatically opens when visited

**Independent Test**: ✅ Click share button → Link copied → Open link in new tab → Epic automatically expands with filters cleared

**Note**: This phase includes shared epic link handling (URL parameters) as it's required for the share feature to work

### Tests for User Story 3

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T059 [US3] Create test file for ShareButton: frontend/tests/components/ShareButton.spec.ts
- [ ] T060 [US3] Write test: should render button with default props
- [ ] T061 [US3] Write test: should generate correct share URL
- [ ] T062 [US3] Write test: should copy URL to clipboard on click
- [ ] T063 [US3] Write test: should emit copied event on success
- [ ] T064 [US3] Write test: should show "Copied!" state after successful copy
- [ ] T065 [US3] Write test: should show fallback input if clipboard API unavailable
- [ ] T066 [US3] Write test: should handle clipboard permission denied error
- [ ] T067 [US3] Write test: should disable button when epicId is empty
- [ ] T068 [US3] Write test: should have correct ARIA attributes

### Implementation for User Story 3 - ShareButton

- [ ] T069 [US3] Create ShareButton component: frontend/src/components/ShareButton.vue
- [ ] T070 [US3] Implement component props interface (epicId, size, variant, customClass)
- [ ] T071 [US3] Implement component emits (copied, copyError)
- [ ] T072 [US3] Integrate useClipboard composable
- [ ] T073 [US3] Implement local state (showFallback, fallbackInputRef)
- [ ] T074 [US3] Implement computed properties (shareUrl, buttonLabel, buttonIcon, isDisabled)
- [ ] T075 [US3] Implement onShareClick handler with clipboard copy
- [ ] T076 [US3] Implement onFallbackClose handler
- [ ] T077 [US3] Implement button template with dynamic classes and ARIA attributes
- [ ] T078 [US3] Add SVG icons for share, check, and alert states
- [ ] T079 [US3] Add fallback input dialog with manual copy instructions
- [ ] T080 [US3] Style button with BEM methodology and Unnnic CSS variables
- [ ] T081 [US3] Add size variants (small, medium, large) styles
- [ ] T082 [US3] Add visual variants (primary, secondary, outlined, ghost) styles
- [ ] T083 [US3] Add state modifiers (loading, copied, error) styles

### Integration with RoadmapCard

- [ ] T084 [US3] Add import to RoadmapCard.vue: ShareButton component
- [ ] T085 [US3] Add ShareButton to RoadmapCard header with size="small" variant="ghost"
- [ ] T086 [US3] Add @click.stop to ShareButton to prevent card expansion
- [ ] T087 [US3] Update RoadmapCard tests: verify ShareButton renders in header

### Implementation for User Story 3 - URL Parameters

- [ ] T088 [US3] Add types to frontend/src/types/roadmap.ts: ImageLoadingState, ShareButtonSize, ShareButtonVariant
- [ ] T089 [US3] Add new state to RoadmapView: sharedEpicId, isProcessingSharedEpic
- [ ] T090 [US3] Implement handleSharedEpicLink function in RoadmapView
- [ ] T091 [US3] Implement clearSharedEpicState function in RoadmapView
- [ ] T092 [US3] Add computed property hasSharedEpicParam in RoadmapView
- [ ] T093 [US3] Modify onMounted in RoadmapView to check for epic parameter first
- [ ] T094 [US3] Implement logic to clear filters when epic parameter exists
- [ ] T095 [US3] Implement logic to fetch all items without filters for shared link
- [ ] T096 [US3] Implement expandEpicById function to find and expand epic programmatically
- [ ] T097 [US3] Add watch for route.query.epic to handle navigation to shared links
- [ ] T098 [US3] Implement error handling for invalid/not found epic IDs
- [ ] T099 [US3] Implement URL cleanup to remove epic parameter after processing

### Tests for URL Parameters

- [ ] T100 [US3] Update RoadmapView tests: detect epic parameter in URL on mount
- [ ] T101 [US3] Update RoadmapView tests: clear filters when epic parameter present
- [ ] T102 [US3] Update RoadmapView tests: fetch all items without filters
- [ ] T103 [US3] Update RoadmapView tests: expand epic when found in items
- [ ] T104 [US3] Update RoadmapView tests: show error when epic not found
- [ ] T105 [US3] Update RoadmapView tests: remove epic parameter after processing
- [ ] T106 [US3] Update RoadmapView tests: handle malformed epic parameter gracefully

### Validation

- [ ] T107 [US3] Run tests for ShareButton: `npm test tests/components/ShareButton.spec.ts`
- [ ] T108 [US3] Run tests for RoadmapView: `npm test tests/views/RoadmapView.spec.ts`
- [ ] T109 [US3] Verify 80% coverage for ShareButton and RoadmapView
- [ ] T110 [US3] Manual test: Click share button → "Copied!" appears → Paste in browser
- [ ] T111 [US3] Manual test: Open shared link → Epic expands automatically → Filters cleared
- [ ] T112 [US3] Manual test: Test invalid epic ID shows error message
- [ ] T113 [US3] Manual test: Test clipboard permission denied shows fallback

**Checkpoint**: At this point, Users can share epic links from card view and shared links work (US3 complete)

---

## Phase 5: User Story 4 - Share Epic from Expanded View (Priority: P2) ✅ COMPLETE

**Goal**: Users can share epic link from expanded view for convenience

**Independent Test**: ✅ Expand epic → Click share button in expanded content → Link copied → Same behavior as card view sharing

### Implementation for User Story 4

- [ ] T114 [US4] Add ShareButton to RoadmapCard expanded content section
- [ ] T115 [US4] Use size="medium" variant="outlined" for expanded view ShareButton
- [ ] T116 [US4] Position ShareButton appropriately in expanded content layout
- [ ] T117 [US4] Add CSS for ShareButton in expanded view if needed

### Tests for User Story 4

- [ ] T118 [US4] Update RoadmapCard tests: verify ShareButton renders in expanded view
- [ ] T119 [US4] Update RoadmapCard tests: verify share from expanded view works identically

### Validation

- [ ] T120 [US4] Manual test: Expand epic → Click share in expanded view → Verify copy works
- [ ] T121 [US4] Manual test: Verify shared link from expanded view opens correctly

**Checkpoint**: All user stories complete (US1, US2, US3, US4) - feature fully functional

---

## Phase 6: Polish & Cross-Cutting Concerns ✅ COMPLETE

**Purpose**: Improvements that affect multiple user stories

- [x] T122 [P] Run full test suite: `npm test`
- [x] T123 [P] Generate coverage report: `npm run test:coverage`
- [x] T124 Verify 80% coverage across all metrics (statements, branches, functions, lines)
- [x] T125 Fix any coverage gaps by adding missing tests
- [x] T126 [P] Run linting: `npm run lint -- --fix`
- [x] T127 [P] Run formatting: `npm run format`
- [x] T128 [P] Run style linting: `npm run stylelint:check`
- [x] T129 Fix any linting or styling errors
- [ ] T130 [P] Test all acceptance scenarios from spec.md manually
- [ ] T131 [P] Test all edge cases from spec.md manually
- [ ] T132 Verify modal animations complete in <300ms
- [ ] T133 Verify clipboard copy completes in <100ms
- [ ] T134 [P] Review code for accessibility (ARIA labels, keyboard navigation, focus management)
- [ ] T135 [P] Review code for Unnnic Design System compliance
- [ ] T136 [P] Verify no trailing whitespace in any files
- [ ] T137 Update documentation if needed (README, comments)
- [ ] T138 Final manual testing in browser with all features
- [ ] T139 Run pre-commit checks: formatters, linters, tests
- [ ] T140 Prepare for commit: stage all changes

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User Story 1 (Phase 3): Can start after Foundational - No dependencies on other stories
  - User Story 3 (Phase 4): Can start after Foundational - No dependencies on other stories
  - User Story 4 (Phase 5): Depends on User Story 3 (ShareButton must exist)
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1) - View Enlarged Images**: Independent - requires only Foundational composables
- **User Story 2 (P2) - Navigate Between Images**: Built into User Story 1 (same component)
- **User Story 3 (P1) - Share from Card View**: Independent - requires only Foundational composables
- **User Story 4 (P2) - Share from Expanded View**: Depends on User Story 3 (reuses ShareButton component)

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Composables before components
- Components before integration
- Integration before validation
- Story complete before moving to next priority

### Parallel Opportunities

- **Phase 1 (Setup)**: All 3 tasks can run in parallel
- **Phase 2 (Foundational)**: 
  - Tests (T004-T007) can run in parallel
  - Implementations (T008-T009) can run in parallel after tests are written
- **User Stories**:
  - After Foundational completes, User Story 1 and User Story 3 can be implemented in parallel (different components, no dependencies)
  - User Story 4 must wait for User Story 3 to complete
- **Within Each Story**:
  - All tests for a story can be written in parallel
  - Component implementation tasks that affect different files can run in parallel

---

## Parallel Example: Foundational Phase

```bash
# Launch all composable tests together:
Task T004: "Create test file for useClipboard composable"
Task T005: "Create test file for useKeyboardNavigation composable"
Task T006: "Write tests for useClipboard"
Task T007: "Write tests for useKeyboardNavigation"

# Launch both composable implementations together (after tests written):
Task T008: "Implement useClipboard composable"
Task T009: "Implement useKeyboardNavigation composable"
```

## Parallel Example: User Stories 1 & 3

```bash
# After Foundational complete, these can start simultaneously:
Story 1 (Team Member A): "Implement ImageCarouselModal and integrate with RoadmapCard"
Story 3 (Team Member B): "Implement ShareButton and URL parameter handling"

# User Story 4 waits for Story 3:
Story 4 (Team Member B): "Add ShareButton to expanded view (after Story 3 done)"
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 3 Only)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational (T004-T011) - CRITICAL, blocks everything
3. Complete Phase 3: User Story 1 (T012-T058)
4. Complete Phase 4: User Story 3 (T059-T113)
5. **STOP and VALIDATE**: Test both stories independently
6. Skip User Story 4 if needed for faster MVP
7. Complete Phase 6: Polish (T122-T140)
8. Ready for deployment

### Incremental Delivery

1. **Foundation**: Complete Setup + Foundational → Composables ready
2. **Release 1 (MVP)**: Add US1 + US3 → Test → Deploy
   - Users can view images in modal AND share epics
3. **Release 2**: Add US4 → Test → Deploy
   - Users can also share from expanded view (convenience feature)
4. Each release adds value without breaking previous functionality

### Parallel Team Strategy

With 2 developers after Foundational phase:

1. **Team completes Setup + Foundational together** (T001-T011)
2. **Once Foundational is done:**
   - Developer A: User Story 1 (T012-T058) - ImageCarouselModal
   - Developer B: User Story 3 (T059-T113) - ShareButton + URL parameters
3. **After both complete:**
   - Developer B: User Story 4 (T114-T121) - Add ShareButton to expanded view
4. **Polish together** (T122-T140)

---

## Task Summary

**Total Tasks**: 140
**Parallelizable Tasks**: 49 (marked with [P])

### Tasks by Phase

- **Phase 1 (Setup)**: 3 tasks
- **Phase 2 (Foundational)**: 8 tasks (CRITICAL - blocks all stories)
- **Phase 3 (User Story 1 - P1)**: 47 tasks (includes US2 navigation)
- **Phase 4 (User Story 3 - P1)**: 55 tasks (includes URL parameters)
- **Phase 5 (User Story 4 - P2)**: 8 tasks
- **Phase 6 (Polish)**: 19 tasks

### Tasks by Story

- **Setup**: 3 tasks
- **Foundational**: 8 tasks
- **[US1] View Enlarged Images**: 47 tasks
- **[US3] Share from Card View**: 55 tasks
- **[US4] Share from Expanded View**: 8 tasks
- **Polish**: 19 tasks

### Coverage Requirements

- All tests must pass before implementation
- Minimum 80% coverage for: Statements, Branches, Functions, Lines
- Tests included for: Composables, Components, Views
- Manual testing checklist included in tasks

---

## Notes

- [P] tasks = different files, no dependencies, can run in parallel
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Tests MUST be written first and MUST fail before implementation
- Commit after each completed user story phase
- Stop at any checkpoint to validate story independently
- US2 (Navigate Between Images) is built into US1's ImageCarouselModal component
- US4 depends on US3 (reuses ShareButton component)
