# Tasks: Design System Update & Brand Rename

**Input**: Design documents from `/specs/012-design-system-rebrand/`
**Prerequisites**: plan.md ✅ | spec.md ✅ | research.md ✅ | quickstart.md ✅
**Branch**: `012-design-system-rebrand`

**Tests**: No test tasks generated — the spec contains no test-generation requirements and the changes are CSS/text only (no logic changes that reduce coverage).

**Organization**: Tasks grouped by user story. US2 and US3 can begin in parallel with US1 after Phase 1 completes — they touch different files.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: US1, US2, US3 maps to user stories in spec.md

## Color Token Reference (used across Phase 3 tasks)

| CSS variable | Replace old fallback | With new fallback |
|---|---|---|
| `--unnnic-color-weni-50` | `#e6f8f8` | `#e9faf8` |
| `--unnnic-color-weni-500` | `#00bfbf` or `#009e96` or `#00a8a8` | `#10b6af` |
| `--unnnic-color-weni-600` | `#00a8a8` or `#009e96` | `#01a29b` |
| `--unnnic-color-weni-700` | `#008f8f` | `#017873` |

> Only replace the fallback hex inside `var(--unnnic-color-weni-NNN, <hex>)`. Leave the CSS variable name unchanged.

---

## Phase 1: Setup

**Purpose**: Upgrade the design system package so all subsequent tasks use the correct dist CSS.

- [x] T001 Run `npm install` in `frontend/` to resolve `@weni/unnnic-system@latest` to `3.25.3`
- [x] T002 Verify upgrade succeeded: `node -e "console.log(require('./frontend/node_modules/@weni/unnnic-system/package.json').version)"` must output `3.25.3`

**Checkpoint**: Package at 3.25.3 — user story work can now begin.

---

## Phase 2: Foundational (Blocking Prerequisite for US1)

**Purpose**: Update the global font stack. This is the only application-level typography change; all other typography improvements come from the upgraded package dist automatically.

**⚠️ CRITICAL**: Must complete before Phase 3 visual verification is meaningful.

- [x] T003 Update font-family fallback from `'Lato'` to `'Inter'` inside `.app { font-family: ... }` in `frontend/src/App.vue`

**Checkpoint**: Global font now falls back to Inter — typography portion of US1 is unblocked.

---

## Phase 3: User Story 1 — Updated Visual Identity (Priority: P1) 🎯 MVP

**Goal**: The roadmap page renders with the new Inter typography, updated teal color palette (#01a29b as primary brand accent), and "VTEX Agentic CX" in both the hero heading and the footer.

**Independent Test**: Load http://localhost:5173, verify Inter font in devtools Computed panel, inspect interactive elements for `#01a29b` teal, confirm hero reads "Roadmap of VTEX Agentic CX" and footer reads "© [year] VTEX Agentic CX. All rights reserved."

### Implementation for User Story 1

All color tasks are [P] — they touch different files and have no inter-task dependencies.

- [x] T004 [P] [US1] Update 14 `--unnnic-color-weni-*` fallback hex values in `frontend/src/components/RoadmapCard.vue` using the Color Token Reference above
- [x] T005 [P] [US1] Update 9 `--unnnic-color-weni-*` fallback hex values in `frontend/src/components/ShareButton.vue` using the Color Token Reference above
- [x] T006 [P] [US1] Update 9 `--unnnic-color-weni-*` fallback hex values in `frontend/src/components/RoadmapFilters.vue` using the Color Token Reference above
- [x] T007 [P] [US1] Update 4 `--unnnic-color-weni-*` fallback hex values in `frontend/src/components/RoadmapTabs.vue` using the Color Token Reference above
- [x] T008 [P] [US1] Update 3 `--unnnic-color-weni-*` fallback hex values in `frontend/src/components/RoadmapEmptyState.vue` using the Color Token Reference above
- [x] T009 [P] [US1] Update 2 `--unnnic-color-weni-*` fallback hex values in `frontend/src/components/MagicSearchBar.vue` using the Color Token Reference above
- [x] T010 [P] [US1] Update 2 `--unnnic-color-weni-*` fallback hex values in `frontend/src/components/ImageCarouselModal.vue` using the Color Token Reference above
- [x] T011 [P] [US1] Update 1 `--unnnic-color-weni-*` fallback hex value in `frontend/src/components/RoadmapCardList.vue` using the Color Token Reference above
- [x] T012 [P] [US1] Update 1 `--unnnic-color-weni-*` fallback hex value in `frontend/src/components/CanvasMode/CanvasEmptyState.vue` using the Color Token Reference above
- [x] T013 [P] [US1] Update 1 `--unnnic-color-weni-*` fallback hex value in `frontend/src/components/CanvasMode/CanvasExitButton.vue` using the Color Token Reference above
- [x] T014 [US1] In `frontend/src/views/RoadmapView.vue`: (a) update 1 `--unnnic-color-weni-*` fallback hex value; (b) change hero span from `Weni` to `VTEX Agentic CX`; (c) change footer from `© {{ new Date().getFullYear() }} Weni. All rights reserved.` to `© {{ new Date().getFullYear() }} VTEX Agentic CX. All rights reserved.`

**Checkpoint**: User Story 1 fully functional. Roadmap page shows new typography, colors, and brand name. Test independently before proceeding to US2/US3.

---

## Phase 4: User Story 2 — Feature Request Form Brand Name (Priority: P2)

**Goal**: The feature request modal introductory text references "VTEX Agentic CX Roadmap" instead of "Weni Roadmap".

**Independent Test**: Open the feature request modal and confirm zero occurrences of "Weni" in all visible text.

### Implementation for User Story 2

- [x] T015 [US2] Replace `Weni Roadmap` with `VTEX Agentic CX Roadmap` in the help text of `frontend/src/components/RoadmapFeatureRequestForm.vue`

**Checkpoint**: Feature request modal shows updated brand name.

---

## Phase 5: User Story 3 — Browser Tab Title (Priority: P3)

**Goal**: The browser tab and page bookmarks display "VTEX Agentic CX Roadmap".

**Independent Test**: Load the page and read the browser tab title — it must read "VTEX Agentic CX Roadmap".

### Implementation for User Story 3

- [x] T016 [US3] Update `<title>Weni Roadmap</title>` to `<title>VTEX Agentic CX Roadmap</title>` in `frontend/index.html`

**Checkpoint**: Browser tab shows correct brand name.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Quality gates, code style enforcement, and final verification across all user stories.

- [x] T017 Run `npm run format` in `frontend/` (Prettier — auto-fixes whitespace and formatting)
- [x] T018 Run `npm run lint -- --fix` then `npm run lint:check` in `frontend/` (ESLint — verify zero errors)
- [x] T019 Run `npm run stylelint:check` in `frontend/` (CSS lint — verify no modern color-function or vendor-prefix violations)
- [x] T020 Run `npm test` in `frontend/` and confirm all tests pass with ≥80% coverage on statements, branches, functions, and lines
- [x] T021 [P] Start `npm run dev` in `frontend/` and complete the visual verification checklist in `specs/012-design-system-rebrand/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 — BLOCKS US1 visual verification
- **Phase 3 (US1)**: Depends on Phase 1 + 2 — T004–T013 can run in parallel; T014 depends only on Phase 1
- **Phase 4 (US2)**: Depends only on Phase 1 — can run in parallel with Phase 3
- **Phase 5 (US3)**: Depends only on Phase 1 — can run in parallel with Phases 3 and 4
- **Phase 6 (Polish)**: Depends on all phases being complete

### User Story Dependencies

- **US1 (P1)**: Requires Phase 1 + 2 (package + App.vue font)
- **US2 (P2)**: Requires only Phase 1 — no dependency on US1
- **US3 (P3)**: Requires only Phase 1 — no dependency on US1 or US2

### Within Phase 3 (US1)

- T004–T013: All parallel (different files, same replacement rule)
- T014 (`RoadmapView.vue`): Parallel with T004–T013 (different file); combines color + brand rename for that file

---

## Parallel Opportunities

### After Phase 1 + 2 complete, all three stories can run simultaneously

```
After T001, T002, T003:

  Developer / Agent A:  T004, T005, T006, T007, T008, T009, T010, T011, T012, T013, T014  (US1 - 11 files)
  Developer / Agent B:  T015                                                                (US2 - 1 file)
  Developer / Agent C:  T016                                                                (US3 - 1 file)
```

### Within US1 — all color tasks are parallel

```
Parallel batch (T004–T014 are all different files):
  T004  frontend/src/components/RoadmapCard.vue
  T005  frontend/src/components/ShareButton.vue
  T006  frontend/src/components/RoadmapFilters.vue
  T007  frontend/src/components/RoadmapTabs.vue
  T008  frontend/src/components/RoadmapEmptyState.vue
  T009  frontend/src/components/MagicSearchBar.vue
  T010  frontend/src/components/ImageCarouselModal.vue
  T011  frontend/src/components/RoadmapCardList.vue
  T012  frontend/src/components/CanvasMode/CanvasEmptyState.vue
  T013  frontend/src/components/CanvasMode/CanvasExitButton.vue
  T014  frontend/src/views/RoadmapView.vue
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 (T001–T002): Upgrade package
2. Complete Phase 2 (T003): Font family
3. Complete Phase 3 (T004–T014): Colors + brand in main page
4. **STOP and VALIDATE**: Run `npm test` and open dev server, verify visually
5. Ship US1 if deadline requires it — US2 and US3 are additive

### Full Delivery (all stories)

1. Phase 1 + 2 (T001–T003)
2. Phase 3 + 4 + 5 in parallel (T004–T016)
3. Phase 6 quality gates (T017–T021)
4. Commit and open PR

### Single-developer sequence (no parallelism)

```
T001 → T002 → T003 → T004 → T005 → T006 → T007 → T008 →
T009 → T010 → T011 → T012 → T013 → T014 → T015 → T016 →
T017 → T018 → T019 → T020 → T021
```

---

## Notes

- Total tasks: **21**
- Tasks per story: US1 = 12 (T003–T014), US2 = 1 (T015), US3 = 1 (T016)
- Parallel opportunities: 11 tasks in US1 are fully parallel (T004–T014)
- Never modify `weni-roadmap-liked-items` localStorage key (data loss risk)
- Never rename internal CSS selectors prefixed with `.weni-` (webchat widget integration)
- Commit after completing each phase or when a logical group of [P] tasks finishes
