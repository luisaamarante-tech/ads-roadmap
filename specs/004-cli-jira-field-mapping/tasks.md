# Tasks: CLI JIRA Field Mapping Enhancement - Auto-Matching & Project-Scope

**Feature**: 004-cli-jira-field-mapping (Enhancement)
**Type**: Enhancement to existing feature
**Input**: Enhancement plan from `ENHANCEMENT_AUTO_MAPPING.md`

**Enhancement Summary**: Add automatic field name matching using fuzzy string matching and project-scope field filtering to the existing `map-fields` command. This reduces manual selection time from 2-3 minutes to ~1 minute by auto-detecting ~70% of field mappings.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2)
- Include exact file paths in descriptions

## Path Conventions

- Backend: `/Users/johncordeiro/workspaces/weni-ai/weni-roadmap/backend/`
- Tests: `/Users/johncordeiro/workspaces/weni-ai/weni-roadmap/backend/tests/`

---

## Phase 1: Setup (Preparation)

**Purpose**: Review existing implementation and prepare for enhancement

- [x] T001 Review existing `map-fields` command implementation in backend/app/cli/jira_setup.py
- [x] T002 Review existing test coverage in backend/tests/unit/test_jira_setup.py
- [x] T003 Document current command flow and identify insertion points for new features

---

## Phase 2: User Story 1 - Automatic Field Name Matching (Priority: P1) 🎯 MVP

**Goal**: Implement fuzzy string matching to automatically map configuration keys to JIRA custom fields based on name similarity, reducing manual selection by ~70%.

**Independent Test**: Run `flask jira map-fields PROJECT_KEY` and verify that fields with similar names are automatically matched with >80% confidence, displayed for review, and only unmatched fields require interactive selection.

### Implementation for User Story 1

- [x] T004 [P] [US1] Add `normalize_string()` helper function in backend/app/cli/jira_setup.py
- [x] T005 [P] [US1] Add `fuzzy_match_score()` helper function using difflib.SequenceMatcher in backend/app/cli/jira_setup.py
- [x] T006 [US1] Add `generate_expected_names()` helper function with field name mappings in backend/app/cli/jira_setup.py
- [x] T007 [US1] Add `auto_match_field()` function that finds best matching field above 0.8 threshold in backend/app/cli/jira_setup.py
- [x] T008 [US1] Modify `map_fields()` command to add `--no-auto-match` CLI flag in backend/app/cli/jira_setup.py
- [x] T009 [US1] Implement auto-matching logic before interactive prompts in `map_fields()` in backend/app/cli/jira_setup.py
- [x] T010 [US1] Add display of auto-matched fields with confidence scores in backend/app/cli/jira_setup.py
- [x] T011 [US1] Add optional review prompt for auto-matched fields in backend/app/cli/jira_setup.py
- [x] T012 [US1] Update interactive prompt flow to skip auto-matched fields in backend/app/cli/jira_setup.py

### Tests for User Story 1

- [x] T013 [P] [US1] Unit test for `normalize_string()` with various inputs in backend/tests/unit/test_jira_setup.py
- [x] T014 [P] [US1] Unit test for `fuzzy_match_score()` with known similarity cases in backend/tests/unit/test_jira_setup.py
- [x] T015 [P] [US1] Unit test for `generate_expected_names()` covering all 13 config keys in backend/tests/unit/test_jira_setup.py
- [x] T016 [US1] Unit test for `auto_match_field()` with exact matches in backend/tests/unit/test_jira_setup.py
- [x] T017 [US1] Unit test for `auto_match_field()` with close matches (>80% similarity) in backend/tests/unit/test_jira_setup.py
- [x] T018 [US1] Unit test for `auto_match_field()` with no matches (<80% similarity) in backend/tests/unit/test_jira_setup.py
- [x] T019 [US1] Unit test for `auto_match_field()` with special characters and spacing in backend/tests/unit/test_jira_setup.py
- [x] T020 [US1] CLI integration test for auto-matching workflow with mocked fields in backend/tests/unit/test_jira_setup.py
- [x] T021 [US1] CLI integration test for `--no-auto-match` flag (disables auto-matching) in backend/tests/unit/test_jira_setup.py
- [x] T022 [US1] CLI integration test for review and override flow in backend/tests/unit/test_jira_setup.py

**Checkpoint**: Auto-matching should work end-to-end with 80%+ test coverage

---

## Phase 3: User Story 2 - Project-Scope Field Filtering (Priority: P2)

**Goal**: Filter custom fields to show only project-scoped fields (excluding global fields), reducing noise in field selection by ~30% in multi-project environments.

**Independent Test**: Run `flask jira map-fields PROJECT_KEY` and verify that only fields scoped to the specific project are displayed, with global fields excluded by default. Run with `--include-global` flag and verify all fields are shown.

### Implementation for User Story 2

- [x] T023 [P] [US2] Add `get_field_context()` helper function to query `/rest/api/3/field/{fieldId}/context` in backend/app/cli/jira_setup.py
- [x] T024 [US2] Add `is_project_scoped_field()` function to check field scope in backend/app/cli/jira_setup.py
- [x] T025 [US2] Add `filter_project_scoped_fields()` function to filter field list in backend/app/cli/jira_setup.py
- [x] T026 [US2] Modify `map_fields()` command to add `--include-global` CLI flag in backend/app/cli/jira_setup.py
- [x] T027 [US2] Implement project-scope filtering after field retrieval in `map_fields()` in backend/app/cli/jira_setup.py
- [x] T028 [US2] Add progress indicator for field filtering operation in backend/app/cli/jira_setup.py
- [x] T029 [US2] Update field count display to show filtered vs total in backend/app/cli/jira_setup.py

### Tests for User Story 2

- [x] T030 [P] [US2] Unit test for `get_field_context()` with successful API response in backend/tests/unit/test_jira_setup.py
- [x] T031 [P] [US2] Unit test for `get_field_context()` with API error handling in backend/tests/unit/test_jira_setup.py
- [x] T032 [P] [US2] Unit test for `is_project_scoped_field()` with global context in backend/tests/unit/test_jira_setup.py
- [x] T033 [P] [US2] Unit test for `is_project_scoped_field()` with project-specific context in backend/tests/unit/test_jira_setup.py
- [x] T034 [P] [US2] Unit test for `is_project_scoped_field()` with missing context data in backend/tests/unit/test_jira_setup.py
- [x] T035 [US2] Unit test for `filter_project_scoped_fields()` with mixed field types in backend/tests/unit/test_jira_setup.py
- [x] T036 [US2] CLI integration test for default project-scope filtering in backend/tests/unit/test_jira_setup.py
- [x] T037 [US2] CLI integration test for `--include-global` flag (shows all fields) in backend/tests/unit/test_jira_setup.py

**Checkpoint**: Project-scope filtering should work independently with 80%+ test coverage

---

## Phase 4: Integration & Polish

**Purpose**: Integrate both features together and ensure they work harmoniously

### Integration Tasks

- [x] T038 [P] [US1+US2] Integration test for auto-matching with project-scoped fields in backend/tests/unit/test_jira_setup.py
- [x] T039 [US1+US2] Integration test for auto-matching with `--include-global` flag in backend/tests/unit/test_jira_setup.py
- [x] T040 [US1+US2] Integration test for `--no-auto-match` with project-scope filtering in backend/tests/unit/test_jira_setup.py
- [x] T041 [US1+US2] End-to-end test with real JIRA-like data simulating full workflow in backend/tests/unit/test_jira_setup.py

### Documentation & Polish

- [x] T042 [P] Update CLI command help text for new flags in backend/app/cli/jira_setup.py
- [x] T043 [P] Add docstrings to all new helper functions in backend/app/cli/jira_setup.py
- [x] T044 [P] Update quickstart.md with auto-matching and filtering examples in specs/004-cli-jira-field-mapping/quickstart.md
- [x] T045 Update README with new CLI flags and usage examples in README.md
- [x] T046 Add example output showing auto-matching flow to quickstart.md

### Code Quality

- [x] T047 Run linters (flake8, black, isort) on modified files in backend/app/cli/jira_setup.py
- [x] T048 Verify test coverage is >80% for enhanced command
- [x] T049 Run all existing tests to ensure no regressions
- [ ] T050 Manual testing with real JIRA instance (if available)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **User Story 1 (Phase 2)**: Depends on Setup completion
- **User Story 2 (Phase 3)**: Can run in parallel with US1 after Setup - Independent features
- **Integration (Phase 4)**: Depends on US1 and US2 completion

### User Story Dependencies

- **User Story 1 (Auto-Matching)**: No dependencies on US2 - Can implement independently
- **User Story 2 (Project-Scope Filtering)**: No dependencies on US1 - Can implement independently
- **Integration**: Both US1 and US2 must be complete

### Within Each User Story

- Helper functions before command modifications
- Command modifications before tests (but tests can be written first for TDD)
- Unit tests before integration tests

### Parallel Opportunities

- **Setup Phase**: All tasks can run sequentially (review tasks)
- **User Story 1**: Tasks T004, T005 can run in parallel (independent helpers)
- **User Story 1 Tests**: Tasks T013-T019 can run in parallel (independent unit tests)
- **User Story 2**: Tasks T023, T024, T025 can run in parallel (independent helpers)
- **User Story 2 Tests**: Tasks T030-T035 can run in parallel (independent unit tests)
- **User Stories 1 & 2**: Can be implemented in parallel by different developers
- **Documentation Tasks**: Tasks T042-T046 can run in parallel (different files)

---

## Parallel Example: User Story 1

```bash
# Launch all helper functions in parallel:
Task T004: "Add normalize_string() helper function in backend/app/cli/jira_setup.py"
Task T005: "Add fuzzy_match_score() helper function in backend/app/cli/jira_setup.py"

# Launch all unit tests in parallel after helpers are done:
Task T013: "Unit test for normalize_string()"
Task T014: "Unit test for fuzzy_match_score()"
Task T015: "Unit test for generate_expected_names()"
Task T016: "Unit test for auto_match_field() - exact matches"
Task T017: "Unit test for auto_match_field() - close matches"
Task T018: "Unit test for auto_match_field() - no matches"
Task T019: "Unit test for auto_match_field() - special characters"
```

---

## Parallel Example: User Story 2

```bash
# Launch all helper functions in parallel:
Task T023: "Add get_field_context() helper function"
Task T024: "Add is_project_scoped_field() function"
Task T025: "Add filter_project_scoped_fields() function"

# Launch all unit tests in parallel:
Task T030: "Unit test for get_field_context() - success"
Task T031: "Unit test for get_field_context() - error handling"
Task T032: "Unit test for is_project_scoped_field() - global"
Task T033: "Unit test for is_project_scoped_field() - project-specific"
Task T034: "Unit test for is_project_scoped_field() - missing data"
```

---

## Implementation Strategy

### Option 1: Sequential by Priority (Recommended for Single Developer)

1. Complete Phase 1: Setup (Review existing code)
2. Complete Phase 2: User Story 1 (Auto-Matching) - **MVP Enhancement**
3. **STOP and VALIDATE**: Test US1 independently, verify 70%+ auto-match rate
4. Complete Phase 3: User Story 2 (Project-Scope Filtering)
5. **STOP and VALIDATE**: Test US2 independently, verify filtering works
6. Complete Phase 4: Integration & Polish
7. **STOP and VALIDATE**: Full end-to-end testing

### Option 2: Parallel by User Story (Recommended for Multiple Developers)

1. Complete Phase 1: Setup together
2. Split work:
   - **Developer A**: Phase 2 (User Story 1 - Auto-Matching)
   - **Developer B**: Phase 3 (User Story 2 - Project-Scope Filtering)
3. Both developers validate their features independently
4. Merge and complete Phase 4 together

### Option 3: TDD Approach (Test-First)

1. Phase 1: Setup
2. Write all tests first (T013-T022 for US1, T030-T037 for US2)
3. Verify tests FAIL
4. Implement helpers and command modifications (T004-T012, T023-T029)
5. Verify tests PASS
6. Integration & Polish

---

## Success Criteria Checklist

Each checkbox represents a measurable outcome from the enhancement plan:

- [ ] Auto-matching correctly identifies >70% of fields in typical JIRA setup
- [ ] User can complete mapping in <1 minute (vs 2-3 minutes currently)
- [ ] Project-scoped filtering reduces field list by >30% in multi-project environments
- [ ] Zero breaking changes to existing functionality (all existing tests pass)
- [ ] Test coverage remains >80% overall
- [ ] All new CLI flags documented in help text and quickstart.md
- [ ] Manual testing with real JIRA confirms functionality

---

## Risk Mitigation

| Risk | Mitigation Tasks |
|------|-----------------|
| Fuzzy matching false positives | T016-T019 (comprehensive unit tests), T011 (review prompt) |
| API overhead for scope checking | T028 (progress indicator), make it optional via flag |
| Breaking existing workflows | T049 (regression testing), all new features are opt-in |
| Test coverage drops below 80% | T048 (coverage verification), comprehensive test tasks |

---

## Task Summary

- **Total Tasks**: 50
- **Setup**: 3 tasks
- **User Story 1 (Auto-Matching)**: 19 tasks (9 implementation + 10 tests)
- **User Story 2 (Project-Scope)**: 15 tasks (7 implementation + 8 tests)
- **Integration & Polish**: 13 tasks

**Estimated Time**: 4-6 hours total
- User Story 1: 2-3 hours
- User Story 2: 1-2 hours
- Integration & Polish: 1 hour

---

## Notes

- [P] tasks = different files or independent functions, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story (US1, US2) is independently implementable and testable
- Commit after each task or logical group of [P] tasks
- Stop at checkpoints to validate independently
- All new features are opt-in via flags (backward compatible)
- Existing `map-fields` command behavior is preserved by default (enhanced, not changed)

---

## Next Steps After Task Completion

1. Run full test suite: `cd backend && pytest tests/ --cov=app/cli --cov-report=html`
2. Verify coverage >80%: Check `coverage_html/index.html`
3. Manual testing: `flask jira map-fields <PROJECT_KEY>` with real JIRA
4. Test with various field naming patterns to verify auto-matching
5. Test with `--no-auto-match` and `--include-global` flags
6. Update feature status in `ENHANCEMENT_AUTO_MAPPING.md`
7. Commit with message: `feat: add auto-matching and project-scope filtering to map-fields command`
