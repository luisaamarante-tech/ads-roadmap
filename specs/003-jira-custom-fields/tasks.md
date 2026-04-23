---
description: "Task list for JIRA Custom Fields Configuration implementation"
---

# Tasks: JIRA Custom Fields Configuration

**Input**: Design documents from `/specs/003-jira-custom-fields/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Included - Constitution requires 80%+ test coverage

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app structure**: `backend/` for API, `frontend/` for UI
- This feature: Backend-only changes
- Config files: `backend/config/`
- Source code: `backend/app/`
- Tests: `backend/tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and configuration structure

- [x] T001 Create backend/config/ directory for JSON configuration files
- [x] T002 Add jsonschema dependency to backend/requirements.txt
- [x] T003 [P] Create JSON schema file at backend/config/jira_projects.schema.json (copy from specs/003-jira-custom-fields/contracts/config-schema.json)
- [x] T004 [P] Create example configuration file at backend/config/jira_projects.example.json (copy from specs/003-jira-custom-fields/contracts/example-config.json)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T005 Create backend/app/cli/ directory for Flask CLI commands
- [x] T006 Add CLI imports to backend/app/__init__.py to enable Flask command discovery

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Configure Custom Fields for JIRA Projects (Priority: P1) 🎯 MVP

**Goal**: Enable JSON-based configuration mapping JIRA project keys to custom field IDs with validation

**Independent Test**: Create a valid JSON config file, start the application, verify it loads without errors and can retrieve project configurations

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T007 [P] [US1] Create unit test file backend/tests/unit/test_config_loader.py with test structure
- [x] T008 [P] [US1] Write test_load_valid_config - verifies loading valid JSON config
- [x] T009 [P] [US1] Write test_load_invalid_json_syntax - verifies handling of malformed JSON
- [x] T010 [P] [US1] Write test_schema_validation - verifies schema violations are caught
- [x] T011 [P] [US1] Write test_missing_config_file - verifies fallback behavior
- [x] T012 [P] [US1] Write test_get_project_config - verifies project-specific lookup
- [x] T013 [P] [US1] Write test_invalid_field_id_format - verifies field ID validation
- [x] T014 [P] [US1] Write test_multiple_projects - verifies multi-project configuration

### Implementation for User Story 1

- [x] T015 [P] [US1] Create backend/app/services/config_loader.py with ProjectConfig and ProjectFieldMapping dataclasses
- [x] T016 [US1] Implement load_config() function in config_loader.py to read and parse JSON file
- [x] T017 [US1] Implement validate_config() function in config_loader.py using jsonschema library
- [x] T018 [US1] Implement get_project_config() function in config_loader.py for project-specific lookup
- [x] T019 [US1] Add error handling and logging for config loading failures in config_loader.py
- [x] T020 [US1] Update backend/app/config.py to call config_loader on startup
- [x] T021 [US1] Add get_project_custom_fields() method to Config class in config.py
- [x] T022 [US1] Ensure backward compatibility with environment variable config in config.py (fallback if JSON missing)
- [x] T023 [US1] Run unit tests for User Story 1 and verify all pass

**Checkpoint**: At this point, User Story 1 should be fully functional - application can load and validate project configurations

---

## Phase 4: User Story 2 - Create Custom Fields via CLI Command (Priority: P2)

**Goal**: Provide CLI command to automatically create JIRA custom fields and update configuration file

**Independent Test**: Run `flask jira setup-fields TEST` against a test JIRA project, verify fields are created and config file is updated

### Tests for User Story 2 ⚠️

- [x] T024 [P] [US2] Create unit test file backend/tests/unit/test_jira_setup.py with test structure
- [x] T025 [P] [US2] Write test_setup_command_success - verifies successful field creation with mocked JIRA API
- [x] T026 [P] [US2] Write test_setup_command_auth_failure - verifies authentication error handling
- [x] T027 [P] [US2] Write test_setup_command_invalid_project - verifies invalid project key handling
- [x] T028 [P] [US2] Write test_detect_existing_fields - verifies duplicate detection logic
- [x] T029 [P] [US2] Write test_get_epic_issue_type_id - verifies Epic issue type retrieval
- [x] T030 [P] [US2] Write test_create_custom_field - verifies field creation API call
- [x] T031 [P] [US2] Write test_update_config_file - verifies config file updates correctly

### Implementation for User Story 2

- [x] T032 [P] [US2] Create backend/app/cli/jira_setup.py with Flask CLI command structure
- [x] T033 [US2] Define CUSTOM_FIELDS constant in jira_setup.py with 6 field configurations
- [x] T034 [US2] Implement get_epic_issue_type_id() function in jira_setup.py using JIRA API
- [x] T035 [US2] Implement detect_existing_fields() function in jira_setup.py to check for duplicates
- [x] T036 [US2] Implement create_custom_field() function in jira_setup.py using POST /rest/api/3/field
- [x] T037 [US2] Implement setup_fields command in jira_setup.py with Click decorators and arguments
- [x] T038 [US2] Add progress indicators using click.progressbar() in setup_fields command
- [x] T039 [US2] Implement config file update logic in jira_setup.py to add/update project entry
- [x] T040 [US2] Add authentication validation before field creation in setup_fields command
- [x] T041 [US2] Add error handling for JIRA API failures in jira_setup.py
- [x] T042 [US2] Add summary output showing created fields and updated config in setup_fields command
- [x] T043 [US2] Register CLI command in backend/run.py to make it available via flask command
- [x] T044 [US2] Run unit tests for User Story 2 and verify all pass

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - administrators can configure projects via CLI

---

## Phase 5: User Story 3 - Extract Roadmap Data from Custom Fields (Priority: P3)

**Goal**: Extract custom field values from JIRA epics with fallback to default fields, including image URLs

**Independent Test**: Create a JIRA epic with custom fields populated, run sync, verify API response includes custom title/description/images

### Tests for User Story 3 ⚠️

- [ ] T045 [P] [US3] Update backend/tests/unit/test_jira_client.py with custom field extraction tests
- [ ] T046 [P] [US3] Write test_extract_custom_title - verifies custom title extraction
- [ ] T047 [P] [US3] Write test_extract_custom_description - verifies custom description extraction
- [ ] T048 [P] [US3] Write test_extract_image_urls - verifies image URL extraction (0-4 URLs)
- [ ] T049 [P] [US3] Write test_fallback_to_default_title - verifies fallback when custom field empty
- [ ] T050 [P] [US3] Write test_fallback_to_default_description - verifies fallback when custom field empty
- [ ] T051 [P] [US3] Write test_invalid_image_url - verifies URL validation and filtering
- [ ] T052 [P] [US3] Write test_project_not_in_config - verifies default field usage for unconfigured projects
- [ ] T053 [P] [US3] Write test_empty_image_urls_filtered - verifies empty URLs are excluded

### Implementation for User Story 3

- [ ] T054 [P] [US3] Update RoadmapItem dataclass in backend/app/models/roadmap.py to ensure images field properly handles 0-4 URLs
- [ ] T055 [US3] Update to_dict() method in roadmap.py to include images array in serialization
- [ ] T056 [US3] Add _extract_custom_field_value() helper method to JiraClient in backend/app/services/jira_client.py
- [ ] T057 [US3] Add _extract_image_urls() method to JiraClient in jira_client.py to extract and validate image URLs
- [ ] T058 [US3] Add _validate_url() helper method to JiraClient in jira_client.py for URL format checking
- [ ] T059 [US3] Update extract_roadmap_item() in jira_client.py to get project config from Config class
- [ ] T060 [US3] Update extract_roadmap_item() to extract custom title field with fallback to epic summary
- [ ] T061 [US3] Update extract_roadmap_item() to extract custom description field with fallback to epic description
- [ ] T062 [US3] Update extract_roadmap_item() to extract image URLs from 4 custom fields
- [ ] T063 [US3] Update ALLOWED_FIELDS in JiraClient to dynamically include custom field IDs from config
- [ ] T064 [US3] Add error handling for missing project config in extract_roadmap_item()
- [ ] T065 [US3] Run unit tests for User Story 3 and verify all pass

**Checkpoint**: All user stories should now be independently functional - full feature ready for integration testing

---

## Phase 6: Integration & Polish

**Purpose**: Integration testing across user stories and cross-cutting improvements

### Integration Tests

- [ ] T066 [P] Update backend/tests/integration/test_routes.py to verify roadmap API returns custom field data
- [ ] T067 [P] Write integration test for end-to-end flow: CLI setup → JIRA sync → API response with custom fields
- [ ] T068 [P] Write integration test for multi-project scenario with different custom field mappings
- [ ] T069 Test backward compatibility: verify application works without JSON config file (uses env vars)

### Cross-Cutting Concerns

- [ ] T070 [P] Update backend/app/config.py docstrings to document new configuration methods
- [ ] T071 [P] Add logging statements for config loading in config.py and config_loader.py
- [ ] T072 [P] Update backend/README.md with CLI command usage and configuration instructions
- [ ] T073 [P] Create backend/config/jira_projects.json.example with placeholder values
- [ ] T074 Run full test suite and verify 80%+ coverage is maintained
- [ ] T075 Run linters (Black, Flake8) and fix any style violations
- [ ] T076 Validate quickstart.md guide by following all steps manually
- [ ] T077 Update .env.example with note about JSON configuration option

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User Story 1 (Configuration) can start immediately after Foundational
  - User Story 2 (CLI) can start immediately after Foundational (works independently)
  - User Story 3 (Extraction) can start immediately after Foundational BUT benefits from US1 being done first for easier testing
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational - Works independently, updates config that US1 reads
- **User Story 3 (P3)**: Can start after Foundational - Ideally after US1 (to test with real configs) but technically independent

**Recommended sequence**: US1 → US2 → US3 (aligns with priorities and natural flow)

**Parallel option**: US1 and US2 can be developed in parallel by different developers

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Models/dataclasses before services
- Services before CLI/extraction logic
- Core implementation before error handling
- Story complete and tested before moving to next priority

### Parallel Opportunities

**Phase 1 (Setup)**:
- T003 and T004 can run in parallel (different files)

**Phase 2 (Foundational)**:
- T005 and T006 are sequential (directory before imports)

**User Story 1 (Configuration)**:
- T007-T014: All test tasks can run in parallel (different test functions)
- T015 can start once tests are written
- T016-T019: Sequential (building up config_loader.py)
- T020-T022: Sequential (modifying config.py)

**User Story 2 (CLI)**:
- T024-T031: All test tasks can run in parallel (different test functions)
- T032-T033: Sequential (file creation then constants)
- T034-T036: Can run in parallel (different functions in jira_setup.py)
- T037-T042: Sequential (building up the command)
- T043: Final integration

**User Story 3 (Extraction)**:
- T045-T053: All test tasks can run in parallel (different test functions)
- T054-T055: Sequential (model changes)
- T056-T058: Can run in parallel (different helper methods)
- T059-T064: Sequential (modifying extraction logic)

**Phase 6 (Integration & Polish)**:
- T066-T069: Integration tests can run in parallel (different test files)
- T070-T077: Polish tasks mostly independent, can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task T007: "Create unit test file backend/tests/unit/test_config_loader.py"
Task T008: "Write test_load_valid_config"
Task T009: "Write test_load_invalid_json_syntax"
Task T010: "Write test_schema_validation"
Task T011: "Write test_missing_config_file"
Task T012: "Write test_get_project_config"
Task T013: "Write test_invalid_field_id_format"
Task T014: "Write test_multiple_projects"

# After T015 creates the file, launch helper functions in parallel:
Task T016: "Implement load_config() function"
Task T017: "Implement validate_config() function"
Task T018: "Implement get_project_config() function"
Task T019: "Add error handling and logging"
```

---

## Parallel Example: User Story 2

```bash
# Launch all tests for User Story 2 together:
Task T024: "Create unit test file backend/tests/unit/test_jira_setup.py"
Task T025: "Write test_setup_command_success"
Task T026: "Write test_setup_command_auth_failure"
Task T027: "Write test_setup_command_invalid_project"
Task T028: "Write test_detect_existing_fields"
Task T029: "Write test_get_epic_issue_type_id"
Task T030: "Write test_create_custom_field"
Task T031: "Write test_update_config_file"

# After T032-T033, launch these helper functions in parallel:
Task T034: "Implement get_epic_issue_type_id()"
Task T035: "Implement detect_existing_fields()"
Task T036: "Implement create_custom_field()"
```

---

## Parallel Example: User Story 3

```bash
# Launch all tests for User Story 3 together:
Task T045: "Update backend/tests/unit/test_jira_client.py with custom field tests"
Task T046: "Write test_extract_custom_title"
Task T047: "Write test_extract_custom_description"
Task T048: "Write test_extract_image_urls"
Task T049: "Write test_fallback_to_default_title"
Task T050: "Write test_fallback_to_default_description"
Task T051: "Write test_invalid_image_url"
Task T052: "Write test_project_not_in_config"
Task T053: "Write test_empty_image_urls_filtered"

# After T055, launch these helper methods in parallel:
Task T056: "Add _extract_custom_field_value() helper method"
Task T057: "Add _extract_image_urls() method"
Task T058: "Add _validate_url() helper method"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (4 tasks)
2. Complete Phase 2: Foundational (2 tasks) - CRITICAL
3. Complete Phase 3: User Story 1 (17 tasks)
4. **STOP and VALIDATE**: Test configuration loading independently
5. Deploy/demo if ready

**MVP Scope**: Application can load and validate JSON-based project configurations
**Estimated Time**: ~6-8 hours

### Incremental Delivery

1. **Foundation** (Phases 1-2): Setup + Foundational → 6 tasks → ~2 hours
2. **+ User Story 1** (Phase 3): Configuration management → 17 tasks → ~6 hours → **Deploy MVP!**
3. **+ User Story 2** (Phase 4): CLI automation → 21 tasks → ~8 hours → **Deploy v2!**
4. **+ User Story 3** (Phase 5): Custom field extraction → 21 tasks → ~8 hours → **Deploy v3!**
5. **Polish** (Phase 6): Integration tests & docs → 12 tasks → ~4 hours → **Production ready!**

**Total**: 77 tasks, estimated ~28-32 hours

### Parallel Team Strategy

With 2-3 developers:

1. **All together**: Complete Setup + Foundational (Phases 1-2)
2. **Split after Foundational**:
   - Developer A: User Story 1 (Configuration)
   - Developer B: User Story 2 (CLI) - can work in parallel with A
3. **Developer A or B**: User Story 3 (Extraction) - after US1 done for easier testing
4. **All together**: Integration & Polish (Phase 6)

**Timeline**: ~2-3 days with 2 developers working in parallel

---

## Task Summary

### Total Task Count

- **Phase 1 (Setup)**: 4 tasks
- **Phase 2 (Foundational)**: 2 tasks
- **Phase 3 (User Story 1)**: 17 tasks (8 tests + 9 implementation)
- **Phase 4 (User Story 2)**: 21 tasks (8 tests + 13 implementation)
- **Phase 5 (User Story 3)**: 21 tasks (9 tests + 12 implementation)
- **Phase 6 (Integration & Polish)**: 12 tasks

**Total**: 77 tasks

### Task Count Per User Story

- **US1**: 17 tasks → Configuration loading and validation
- **US2**: 21 tasks → CLI command for field creation
- **US3**: 21 tasks → Custom field data extraction

### Parallel Opportunities Identified

- **Setup**: 2 tasks parallelizable (50%)
- **User Story 1**: 8 test tasks + 3 implementation tasks parallelizable (65%)
- **User Story 2**: 8 test tasks + 3 implementation tasks parallelizable (52%)
- **User Story 3**: 9 test tasks + 3 implementation tasks parallelizable (57%)
- **Polish**: 8 tasks parallelizable (67%)

**Overall**: ~40-45% of tasks can run in parallel with proper coordination

### Independent Test Criteria

**User Story 1**:
- ✅ Application starts without errors
- ✅ Can load valid JSON config file
- ✅ Invalid configs show warnings but don't crash
- ✅ Can retrieve project-specific custom field mappings
- ✅ Fallback to env vars works when JSON missing

**User Story 2**:
- ✅ `flask jira setup-fields PROJECT` creates 6 custom fields in JIRA
- ✅ Fields appear only on Epic issue type
- ✅ Config file automatically updated with field IDs
- ✅ Running command again detects existing fields
- ✅ Authentication errors are clearly reported

**User Story 3**:
- ✅ Epics with custom fields show custom title/description in API
- ✅ Epics without custom fields show default title/description
- ✅ Image URLs (0-4) appear in API response
- ✅ Invalid URLs are filtered out
- ✅ Multiple projects work with different field mappings

### Suggested MVP Scope

**MVP = User Story 1 Only** (Configuration Management)

**Rationale**:
- Provides foundation for multi-project support
- Can be tested independently without JIRA changes
- Enables gradual migration from env vars to JSON config
- Lower risk, faster to market

**MVP Deliverables**:
- JSON configuration file support
- Schema validation
- Project-specific field mapping
- Backward compatibility with env vars

**Post-MVP Additions**:
- Phase 2: Add CLI automation (User Story 2)
- Phase 3: Add custom field extraction (User Story 3)
- Phase 4: Integration testing and polish

---

## Format Validation

✅ **All 77 tasks follow the checklist format:**
- [x] All tasks start with `- [ ]` checkbox
- [x] All tasks have Task ID (T001-T077)
- [x] Parallelizable tasks marked with [P]
- [x] User story tasks marked with [US1], [US2], or [US3]
- [x] All tasks include specific file paths in descriptions
- [x] Setup and Foundational phases have no story labels (correct)
- [x] User Story phases have appropriate story labels (correct)
- [x] Polish phase has no story labels (correct)

---

## Notes

- [P] tasks = different files, no dependencies within phase
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing (TDD approach)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Constitution requires 80%+ test coverage - achieved with comprehensive test tasks
- Backward compatibility maintained throughout - env var fallback preserved
- All file paths use backend/ prefix for web application structure
