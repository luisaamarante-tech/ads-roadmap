# Tasks: JIRA Text Formatting Preservation

**Input**: Design documents from `/specs/009-jira-text-formatting/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verify project structure and prepare for implementation

- [X] T001 Verify backend Python 3.11+ environment and Flask dependencies
- [X] T002 Verify frontend Vue 3.4 + TypeScript 5.3 environment
- [X] T003 [P] Review existing jira_client.py _adf_to_text() method in backend/app/services/jira_client.py
- [X] T004 [P] Review existing RoadmapCard.vue description rendering in frontend/src/components/RoadmapCard.vue

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core HTML sanitization infrastructure that ALL user stories depend on for security

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 Create HTMLSanitizer class with allowlist-based sanitization in backend/app/services/html_sanitizer.py
- [X] T006 Implement safe tag allowlist (p, br, strong, em, u, s, ul, ol, li, h1-h6, a) in backend/app/services/html_sanitizer.py
- [X] T007 Implement safe attribute allowlist (href, rel, target for links) in backend/app/services/html_sanitizer.py
- [X] T008 Implement URL validation (http/https only, block javascript:, data:) in backend/app/services/html_sanitizer.py
- [X] T009 Add security headers to links (rel="noopener noreferrer", target="_blank") in backend/app/services/html_sanitizer.py
- [X] T010 [P] Unit test: XSS prevention - script tag removal in backend/tests/unit/test_html_sanitizer.py
- [X] T011 [P] Unit test: XSS prevention - event handler removal in backend/tests/unit/test_html_sanitizer.py
- [X] T012 [P] Unit test: XSS prevention - javascript: URL blocking in backend/tests/unit/test_html_sanitizer.py
- [X] T013 [P] Unit test: Safe HTML tags pass through in backend/tests/unit/test_html_sanitizer.py
- [X] T014 [P] Unit test: Link security attributes added in backend/tests/unit/test_html_sanitizer.py

**Checkpoint**: Sanitization framework ready - user story implementation can now begin

---

## Phase 3: User Story 1 - View Formatted Epic Descriptions (Priority: P1) 🎯 MVP

**Goal**: Enable rendering of basic JIRA text formatting (bold, italic, underline, lists, links, headings) on the public roadmap

**Independent Test**: Create a JIRA epic with bold text, italic text, bullet list, and a link. Mark it as public and sync. Verify all formatting displays correctly on the roadmap.

### Backend Implementation for User Story 1

- [X] T015 [US1] Replace _adf_to_text() with _adf_to_html() method in backend/app/services/jira_client.py
- [X] T016 [US1] Implement ADF text node converter (plain text extraction) in backend/app/services/jira_client.py
- [X] T017 [US1] Implement ADF paragraph node converter (<p> tags) in backend/app/services/jira_client.py
- [X] T018 [US1] Implement ADF strong mark converter (<strong> tags) in backend/app/services/jira_client.py
- [X] T019 [US1] Implement ADF em mark converter (<em> tags) in backend/app/services/jira_client.py
- [X] T020 [US1] Implement ADF underline mark converter (<u> tags) in backend/app/services/jira_client.py
- [X] T021 [US1] Implement ADF link mark converter (<a> tags with href) in backend/app/services/jira_client.py
- [X] T022 [US1] Implement ADF bulletList node converter (<ul> tags) in backend/app/services/jira_client.py
- [X] T023 [US1] Implement ADF orderedList node converter (<ol> tags) in backend/app/services/jira_client.py
- [X] T024 [US1] Implement ADF listItem node converter (<li> tags) in backend/app/services/jira_client.py
- [X] T025 [US1] Implement ADF heading node converter (<h1>-<h6> tags with level attr) in backend/app/services/jira_client.py
- [X] T026 [US1] Implement ADF hardBreak node converter (<br> tags) in backend/app/services/jira_client.py
- [X] T027 [US1] Integrate HTMLSanitizer into _extract_description() method in backend/app/services/jira_client.py
- [X] T028 [US1] Add error handling for malformed ADF (graceful fallback to empty string) in backend/app/services/jira_client.py

### Backend Tests for User Story 1

- [X] T029 [P] [US1] Unit test: Empty ADF document returns empty string in backend/tests/unit/test_jira_client.py
- [X] T030 [P] [US1] Unit test: Simple paragraph conversion in backend/tests/unit/test_jira_client.py
- [X] T031 [P] [US1] Unit test: Bold text (strong mark) conversion in backend/tests/unit/test_jira_client.py
- [X] T032 [P] [US1] Unit test: Italic text (em mark) conversion in backend/tests/unit/test_jira_client.py
- [X] T033 [P] [US1] Unit test: Underline text conversion in backend/tests/unit/test_jira_client.py
- [X] T034 [P] [US1] Unit test: Bullet list conversion in backend/tests/unit/test_jira_client.py
- [X] T035 [P] [US1] Unit test: Ordered list conversion in backend/tests/unit/test_jira_client.py
- [X] T036 [P] [US1] Unit test: Link with href conversion in backend/tests/unit/test_jira_client.py
- [X] T037 [P] [US1] Unit test: Heading (h1-h6) conversion in backend/tests/unit/test_jira_client.py
- [X] T038 [P] [US1] Unit test: Hard break (<br>) conversion in backend/tests/unit/test_jira_client.py
- [X] T039 [P] [US1] Unit test: Unknown node type graceful handling in backend/tests/unit/test_jira_client.py
- [X] T040 [P] [US1] Unit test: Malformed ADF graceful fallback in backend/tests/unit/test_jira_client.py
- [X] T041 [P] [US1] Unit test: Sanitization integration (HTML output is safe) in backend/tests/unit/test_jira_client.py

### Frontend Implementation for User Story 1

- [X] T042 [US1] Replace plain text rendering with v-html directive in frontend/src/components/RoadmapCard.vue
- [X] T043 [US1] Add scoped CSS for strong tags using :deep() selector in frontend/src/components/RoadmapCard.vue
- [X] T044 [US1] Add scoped CSS for em tags using :deep() selector in frontend/src/components/RoadmapCard.vue
- [X] T045 [US1] Add scoped CSS for u tags using :deep() selector in frontend/src/components/RoadmapCard.vue
- [X] T046 [US1] Add scoped CSS for ul/ol lists using :deep() selector in frontend/src/components/RoadmapCard.vue
- [X] T047 [US1] Add scoped CSS for li items using :deep() selector in frontend/src/components/RoadmapCard.vue
- [X] T048 [US1] Add scoped CSS for a (links) using :deep() selector with Unnnic colors in frontend/src/components/RoadmapCard.vue
- [X] T049 [US1] Add scoped CSS for h1-h6 headings using :deep() selector in frontend/src/components/RoadmapCard.vue
- [X] T050 [US1] Ensure mobile responsive styles (viewport ≥375px) in frontend/src/components/RoadmapCard.vue

### Frontend Tests for User Story 1

- [X] T051 [P] [US1] Unit test: Formatted HTML description renders correctly in frontend/tests/components/RoadmapCard.spec.ts
- [X] T052 [P] [US1] Unit test: Bold text displays with <strong> tag in frontend/tests/components/RoadmapCard.spec.ts
- [X] T053 [P] [US1] Unit test: Italic text displays with <em> tag in frontend/tests/components/RoadmapCard.spec.ts
- [X] T054 [P] [US1] Unit test: Links render with security attributes in frontend/tests/components/RoadmapCard.spec.ts
- [X] T055 [P] [US1] Unit test: Lists render with proper structure in frontend/tests/components/RoadmapCard.spec.ts
- [X] T056 [P] [US1] Unit test: Backward compatibility - plain text still displays in frontend/tests/components/RoadmapCard.spec.ts

**Checkpoint**: User Story 1 (basic formatting) is fully functional and testable independently. MVP is complete!

---

## Phase 4: User Story 3 - Handle Mixed Formatting (Priority: P1)

**Goal**: Enable rendering of combined formatting types (bold + italic, formatted lists with links, nested structures)

**Independent Test**: Create a JIRA epic with bold italic text, a list with bold items and links, and nested lists. Verify all formatting renders correctly together.

### Backend Implementation for User Story 3

- [X] T057 [US3] Implement multiple mark handling (combine strong + em, etc.) in backend/app/services/jira_client.py
- [X] T058 [US3] Implement nested list support (lists within lists) in backend/app/services/jira_client.py
- [X] T059 [US3] Implement strike mark converter (<s> tags for strikethrough) in backend/app/services/jira_client.py
- [X] T060 [US3] Add complex ADF structure handling (deep nesting) in backend/app/services/jira_client.py

### Backend Tests for User Story 3

- [X] T061 [P] [US3] Unit test: Combined marks (bold + italic) conversion in backend/tests/unit/test_jira_client.py
- [X] T062 [P] [US3] Unit test: List with formatted items (bold, italic, links) in backend/tests/unit/test_jira_client.py
- [X] T063 [P] [US3] Unit test: Nested lists (3+ levels) conversion in backend/tests/unit/test_jira_client.py
- [X] T064 [P] [US3] Unit test: Strikethrough text conversion in backend/tests/unit/test_jira_client.py

### Frontend Implementation for User Story 3

- [X] T065 [US3] Add scoped CSS for s (strikethrough) tags using :deep() selector in frontend/src/components/RoadmapCard.vue
- [X] T066 [US3] Add scoped CSS for nested list indentation in frontend/src/components/RoadmapCard.vue

### Frontend Tests for User Story 3

- [X] T067 [P] [US3] Unit test: Combined formatting (bold + italic) displays correctly in frontend/tests/components/RoadmapCard.spec.ts
- [X] T068 [P] [US3] Unit test: Formatted list items (bold, links) render correctly in frontend/tests/components/RoadmapCard.spec.ts
- [X] T069 [P] [US3] Unit test: Nested lists display with proper hierarchy in frontend/tests/components/RoadmapCard.spec.ts

**Checkpoint**: User Stories 1 AND 3 are both functional. All P1 requirements complete!

---

## Phase 5: User Story 2 - Preserve Code Blocks and Preformatted Text (Priority: P2)

**Goal**: Enable rendering of code blocks and inline code with monospace font and preserved whitespace

**Independent Test**: Create a JIRA epic with a code block (Python code) and inline code. Verify monospace font, preserved indentation, and distinct styling.

### Backend Implementation for User Story 2

- [X] T070 [US2] Implement ADF codeBlock node converter (<pre><code> tags) in backend/app/services/jira_client.py
- [X] T071 [US2] Implement ADF code mark converter (<code> tags for inline) in backend/app/services/jira_client.py
- [X] T072 [US2] Add language class support for code blocks (language-python, etc.) in backend/app/services/jira_client.py
- [X] T073 [US2] Implement ADF blockquote node converter (<blockquote> tags) in backend/app/services/jira_client.py
- [X] T074 [US2] Update HTMLSanitizer to allow code, pre, blockquote tags in backend/app/services/html_sanitizer.py

### Backend Tests for User Story 2

- [X] T075 [P] [US2] Unit test: Code block conversion with language class in backend/tests/unit/test_jira_client.py
- [X] T076 [P] [US2] Unit test: Inline code conversion in backend/tests/unit/test_jira_client.py
- [X] T077 [P] [US2] Unit test: Blockquote conversion in backend/tests/unit/test_jira_client.py
- [X] T078 [P] [US2] Unit test: Whitespace preservation in code blocks in backend/tests/unit/test_jira_client.py

### Frontend Implementation for User Story 2

- [X] T079 [US2] Add scoped CSS for code (inline) tags with monospace font in frontend/src/components/RoadmapCard.vue
- [X] T080 [US2] Add scoped CSS for pre (code block) tags with monospace font in frontend/src/components/RoadmapCard.vue
- [X] T081 [US2] Add scoped CSS for blockquote tags using :deep() selector in frontend/src/components/RoadmapCard.vue
- [X] T082 [US2] Ensure code blocks are horizontally scrollable on mobile in frontend/src/components/RoadmapCard.vue

### Frontend Tests for User Story 2

- [X] T083 [P] [US2] Unit test: Code block renders with monospace font in frontend/tests/components/RoadmapCard.spec.ts
- [X] T084 [P] [US2] Unit test: Inline code displays distinctly from text in frontend/tests/components/RoadmapCard.spec.ts
- [X] T085 [P] [US2] Unit test: Blockquote renders with proper styling in frontend/tests/components/RoadmapCard.spec.ts
- [X] T086 [P] [US2] Unit test: Code block whitespace preserved in frontend/tests/components/RoadmapCard.spec.ts

**Checkpoint**: All user stories (P1 + P2) are complete and independently functional!

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final validation

- [X] T087 [P] Run backend linters (black, isort, flake8) on modified files
- [X] T088 [P] Run frontend linters (prettier, eslint) on modified files
- [X] T089 [P] Verify backend test coverage ≥80% for all metrics (statements, branches, functions, lines)
- [X] T090 [P] Verify frontend test coverage ≥80% for all metrics
- [X] T091 Run full backend test suite with pytest
- [X] T092 Run full frontend test suite with vitest
- [X] T093 [P] Manual accessibility test: Screen reader compatibility with formatted content
- [X] T094 [P] Manual test: Mobile responsive display (viewport 375px, 768px, 1024px)
- [X] T095 [P] Manual test: Cross-browser compatibility (Chrome, Firefox, Safari)
- [X] T096 Create JIRA epic with all formatting types and verify end-to-end display
- [X] T097 Verify backward compatibility with existing plain text descriptions
- [X] T098 [P] Update quickstart.md with any findings from implementation
- [X] T099 Run pre-commit hooks on all modified files
- [X] T100 Final validation: Compare output with contracts/adf-conversion-spec.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational phase - No dependencies on other stories
- **User Story 3 (Phase 4)**: Depends on Foundational phase - Extends US1 but independently testable
- **User Story 2 (Phase 5)**: Depends on Foundational phase - No dependencies on other stories
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - MVP scope
- **User Story 3 (P1)**: Can start after Foundational (Phase 2) - Extends US1 but independently testable
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Independent enhancement

**Note**: US1 and US3 are both P1, but US3 builds on US1's basic formatting. Recommend completing US1 first for logical flow, though US3 can technically run in parallel.

### Within Each User Story

- Backend implementation before frontend (backend provides data)
- Tests can run in parallel with implementation (TDD) if marked [P]
- Core conversion logic before integration with sanitizer
- Component modification before styling
- Styling before component tests

### Parallel Opportunities

**Within Foundational Phase (Phase 2)**:
- All unit tests for sanitizer (T010-T014) can run in parallel

**Within User Story 1 (Phase 3)**:
- Backend tests (T029-T041) can run in parallel after T028 completes
- Frontend styling tasks (T043-T049) can run in parallel after T042 completes
- Frontend tests (T051-T056) can run in parallel after T050 completes

**Within User Story 3 (Phase 4)**:
- Backend tests (T061-T064) can run in parallel after T060 completes
- Frontend tests (T067-T069) can run in parallel after T066 completes

**Within User Story 2 (Phase 5)**:
- Backend tests (T075-T078) can run in parallel after T074 completes
- Frontend styling tasks (T079-T082) can run in parallel
- Frontend tests (T083-T086) can run in parallel after T082 completes

**Within Polish Phase (Phase 6)**:
- Linting tasks (T087-T088) can run in parallel
- Coverage verification (T089-T090) can run in parallel
- Manual tests (T093-T095) can run in parallel
- Documentation update (T098) can run in parallel with manual tests

---

## Parallel Example: User Story 1 Backend Tests

```bash
# After T028 completes, launch all backend tests for User Story 1 together:
T029: "Unit test: Empty ADF document returns empty string"
T030: "Unit test: Simple paragraph conversion"
T031: "Unit test: Bold text (strong mark) conversion"
T032: "Unit test: Italic text (em mark) conversion"
T033: "Unit test: Underline text conversion"
T034: "Unit test: Bullet list conversion"
T035: "Unit test: Ordered list conversion"
T036: "Unit test: Link with href conversion"
T037: "Unit test: Heading (h1-h6) conversion"
T038: "Unit test: Hard break (<br>) conversion"
T039: "Unit test: Unknown node type graceful handling"
T040: "Unit test: Malformed ADF graceful fallback"
T041: "Unit test: Sanitization integration"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T004)
2. Complete Phase 2: Foundational (T005-T014) - **CRITICAL BLOCKER**
3. Complete Phase 3: User Story 1 (T015-T056)
4. **STOP and VALIDATE**: Test US1 independently with real JIRA epic
5. Deploy/demo if ready - basic formatting works!

**Estimated Tasks for MVP**: 56 tasks (Setup + Foundational + US1)

### Incremental Delivery

1. **Foundation** (Phases 1-2): Setup + Sanitization → Security ready
2. **MVP** (Phase 3): User Story 1 → Basic formatting works → Deploy/Demo
3. **P1 Complete** (Phase 4): User Story 3 → Complex formatting works → Deploy/Demo
4. **Full Feature** (Phase 5): User Story 2 → Code blocks work → Deploy/Demo
5. **Production Ready** (Phase 6): Polish → All quality gates passed → Production release

### Parallel Team Strategy

With multiple developers:

1. **Together**: Complete Setup (Phase 1) + Foundational (Phase 2)
2. **After Foundational**:
   - Developer A: User Story 1 (T015-T056)
   - Developer B: User Story 2 (T070-T086) - can start in parallel
   - Developer C: User Story 3 (T057-T069) - ideally waits for US1 backend completion
3. Stories complete and integrate independently

---

## Task Count Summary

- **Phase 1 (Setup)**: 4 tasks
- **Phase 2 (Foundational)**: 10 tasks (9 implementation + 5 tests = 14 total, but test tasks counted in sequence)
- **Phase 3 (User Story 1)**: 42 tasks (14 backend + 13 backend tests + 9 frontend + 6 frontend tests)
- **Phase 4 (User Story 3)**: 13 tasks (4 backend + 4 backend tests + 2 frontend + 3 frontend tests)
- **Phase 5 (User Story 2)**: 17 tasks (5 backend + 4 backend tests + 4 frontend + 4 frontend tests)
- **Phase 6 (Polish)**: 14 tasks

**Total**: 100 tasks

**Parallel Opportunities**: 50+ tasks marked [P] for parallel execution

**MVP Scope**: 56 tasks (Phases 1-3)

---

## Notes

- [P] tasks = different files, no dependencies within phase
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Constitution requires ≥80% coverage - unit tests are mandatory
- Commit after each logical group of tasks
- Stop at any checkpoint to validate story independently
- US3 extends US1 but should still be independently testable
- All sanitization happens in backend - frontend just renders
- Use :deep() selector for styling v-html content in Vue
- Run linters frequently to catch issues early
