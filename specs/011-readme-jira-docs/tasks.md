# Tasks: Update README with JIRA Configuration Documentation

**Feature**: 011-readme-jira-docs
**Branch**: `011-readme-jira-docs`
**Input**: Design documents from `/specs/011-readme-jira-docs/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, quickstart.md ✅

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story increment.

**Tests**: Not applicable - documentation-only feature validated through manual review and new developer simulation.

---

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: Prepare environment and create backup before documentation updates

- [x] T001 Create backup of current README.md as README.md.backup
- [x] T002 Verify README.md exists at repository root (/Users/johncordeiro/workspaces/weni-ai/weni-roadmap/README.md)
- [x] T003 Read research.md to understand 17 Netlify references and documentation structure
- [x] T004 Read data-model.md to understand the 5 documentation entities

---

## Phase 2: Foundational - Remove Obsolete Content

**Purpose**: Clean up deprecated Netlify references (serves User Story 4)

**⚠️ CRITICAL**: Complete Netlify removal before adding new JIRA documentation to prevent conflicts

- [x] T005 [US4] Search README.md for all Netlify references using grep -i "netlify" (expect 17 matches)
- [x] T006 [US4] Remove Netlify deployment instructions section from README.md
- [x] T007 [US4] Remove Netlify environment variable tables from README.md
- [x] T008 [US4] Remove Netlify build command examples from README.md
- [x] T009 [US4] Remove references to netlify.toml configuration file from README.md
- [x] T010 [US4] Remove automated Netlify deployment workflow descriptions from README.md
- [x] T011 [US4] Verify Docker deployment section is preserved in README.md (lines ~280-320)
- [x] T012 [US4] Verify no Netlify references remain: grep -i "netlify" README.md should return 0 matches

**Checkpoint**: Netlify content removed, Docker deployment preserved - README.md ready for JIRA documentation addition

---

## Phase 3: User Story 1 - New Developer Onboarding (Priority: P1) 🎯 MVP

**Goal**: Enable new developers to set up JIRA authentication and field mappings following only README instructions

**Independent Test**: New developer with no prior project knowledge can follow README to set up JIRA authentication, configure field mappings, and successfully sync roadmap data from JIRA in under 20 minutes

### Create JIRA Configuration Section Structure

- [x] T013 [US1] Insert "## JIRA Configuration" section heading after "Quick Start" section in README.md
- [x] T014 [US1] Add brief introduction paragraph explaining JIRA integration purpose in README.md
- [x] T015 [US1] Create subsection "### Authentication Setup" in JIRA Configuration section of README.md

### Document Environment Variables (FR-002, FR-003)

- [x] T016 [US1] Create environment variables table in Authentication Setup subsection with 3 rows in README.md
- [x] T017 [US1] Document JIRA_BASE_URL variable with format "https://DOMAIN.atlassian.net" and example in README.md
- [x] T018 [US1] Document JIRA_EMAIL variable with format "email@domain.com" and service account note in README.md
- [x] T019 [US1] Document JIRA_API_TOKEN variable with security warning in README.md
- [x] T020 [US1] Add "Obtaining API Token" subsection with 5-step instructions in README.md
- [x] T021 [US1] Include URL https://id.atlassian.com/manage-profile/security/api-tokens in token generation steps in README.md
- [x] T022 [US1] Add security best practices subsection (never commit tokens, rotate every 90 days) in README.md

### Document Required Permissions (FR-010)

- [x] T023 [US1] Add "Required Permissions" subsection in Authentication Setup of README.md
- [x] T024 [US1] Document minimum permission: read access to projects in README.md
- [x] T025 [US1] Document recommended permission: read/write access to Epic custom fields in README.md

### Document CLI Mapping Commands (FR-006, FR-007)

- [x] T026 [US1] Create subsection "### Field Mapping with CLI" after Authentication Setup in README.md
- [x] T027 [US1] Add initial setup workflow (3-command sequence) with examples in README.md
- [x] T028 [US1] Document "flask jira list-fields PROJECT_KEY" command with purpose in README.md
- [x] T029 [US1] Document "flask jira map-fields PROJECT_KEY" command with interactive wizard description in README.md
- [x] T030 [US1] Document --all flag for mapping multiple projects sequentially in README.md
- [x] T031 [US1] Document --no-auto-match flag for disabling fuzzy matching in README.md
- [x] T032 [US1] Document --include-global flag for showing globally-scoped fields in README.md
- [x] T033 [US1] Document --show-all-types flag for displaying all field types in README.md
- [x] T034 [US1] Document --dry-run flag for previewing changes without saving in README.md

### Document Validation Commands (FR-008, FR-009)

- [x] T035 [US1] Add "Validation" subsection in Field Mapping with CLI section of README.md
- [x] T036 [US1] Document "flask jira validate-config [PROJECT_KEY]" command with purpose in README.md
- [x] T037 [US1] Document --verbose flag for detailed validation checks in README.md
- [x] T038 [US1] Document --fix flag for auto-fixing issues in README.md
- [x] T039 [US1] Document "flask sync run --once" command for testing data sync in README.md
- [x] T040 [US1] Add code block example showing complete validation workflow in README.md

**Checkpoint**: User Story 1 complete - New developers can now set up JIRA authentication and field mappings using README only

---

## Phase 4: User Story 2 - System Administrator Project Setup (Priority: P2)

**Goal**: Enable system administrators to understand custom field requirements and create JIRA fields with correct types and associations

**Independent Test**: System administrator with JIRA admin access can create all 14 required custom fields, associate with Epic issue type, and complete field mapping without external help

### Document Custom Field Requirements (FR-004, FR-005)

- [x] T041 [US2] Create subsection "### Custom Field Requirements" after Authentication Setup in README.md
- [x] T042 [US2] Add introductory paragraph explaining 14 custom field mappings in README.md
- [x] T043 [US2] Create comprehensive custom fields table with 14 rows in README.md
- [x] T044 [US2] Document public_roadmap field (checkbox type, required) with purpose in README.md
- [x] T045 [US2] Document roadmap_status field (select list, required, values: Delivered/Now/Next/Future) in README.md
- [x] T046 [US2] Document module field (select list, required) with purpose in README.md
- [x] T047 [US2] Document release_year field (number, required, YYYY format) in README.md
- [x] T048 [US2] Document release_quarter field (select list, required, Q1-Q4 values) in README.md
- [x] T049 [US2] Document release_month field (number, required, 1-12 range) in README.md
- [x] T050 [US2] Document documentation_url field (URL, required) in README.md
- [x] T051 [US2] Document roadmap_title field (text 255 chars, required) in README.md
- [x] T052 [US2] Document roadmap_description field (paragraph/rich text, required) in README.md
- [x] T053 [US2] Document roadmap_image_url_1 field (URL, optional) in README.md
- [x] T054 [US2] Document roadmap_image_url_2 field (URL, optional) in README.md
- [x] T055 [US2] Document roadmap_image_url_3 field (URL, optional) in README.md
- [x] T056 [US2] Document roadmap_image_url_4 field (URL, optional) in README.md
- [x] T057 [US2] Document roadmap_likes field (number, required) in README.md
- [x] T058 [US2] Mark which fields are required (10) vs optional (4) in the table in README.md

### Document JIRA Setup Requirements (FR-005)

- [x] T059 [US2] Add "JIRA Setup Notes" subsection after custom fields table in README.md
- [x] T060 [US2] Document requirement: fields must be associated with Epic issue type in README.md
- [x] T061 [US2] Document requirement: fields must appear on Epic Edit screen in README.md
- [x] T062 [US2] Document requirement: fields must appear on Epic View screen in README.md
- [x] T063 [US2] Document custom field ID format pattern: customfield_NNNNN in README.md
- [x] T064 [US2] Add note that field IDs differ across JIRA instances (dev/staging/prod) in README.md

**Checkpoint**: User Story 2 complete - System administrators can create and configure all required JIRA custom fields

---

## Phase 5: User Story 3 - Troubleshooting Configuration Issues (Priority: P3)

**Goal**: Enable developers to diagnose and fix JIRA configuration issues (authentication, permissions, field mappings) using README guidance

**Independent Test**: Developer with intentionally misconfigured JIRA credentials or field mappings can use README instructions to identify and fix issues using validation commands

### Document Troubleshooting Guidance (FR-013)

- [x] T065 [US3] Create subsection "### Validation & Troubleshooting" after Field Mapping with CLI in README.md
- [x] T066 [US3] Add introductory paragraph about using validation commands for diagnosis in README.md
- [x] T067 [US3] Create "Common Issues" subsection with 5 common problems in README.md
- [x] T068 [US3] Document Issue 1: Authentication failures → Solution: Check environment variables in README.md
- [x] T069 [US3] Document Issue 2: Missing fields → Solution: Re-run map-fields command in README.md
- [x] T070 [US3] Document Issue 3: Invalid field IDs → Solution: Verify field exists in JIRA in README.md
- [x] T071 [US3] Document Issue 4: Permission errors → Solution: Check API token permissions in README.md
- [x] T072 [US3] Document Issue 5: Sync failures → Solution: Run test-create-issue command in README.md
- [x] T073 [US3] Add code block example showing troubleshooting workflow with validation command in README.md

### Document test-create-issue Command (Supporting FR-009)

- [x] T074 [US3] Document "flask jira test-create-issue PROJECT_KEY" command with purpose in README.md
- [x] T075 [US3] Document --summary flag for custom issue summary in README.md
- [x] T076 [US3] Document --type flag for issue type selection in README.md
- [x] T077 [US3] Add note that test-create-issue verifies write permissions in README.md

### Add Cross-References (FR-014)

- [x] T078 [US3] Add "Additional Resources" subsection in Troubleshooting section of README.md
- [x] T079 [US3] Link to docs/JIRA_LIKES_FIELD_MIGRATION.md for likes field details in README.md
- [x] T080 [US3] Link to specs/004-cli-jira-field-mapping/quickstart.md for CLI deep dive in README.md

**Checkpoint**: User Story 3 complete - Developers can troubleshoot and resolve JIRA configuration issues independently

---

## Phase 6: User Story 4 - Understanding Deployment Configuration (Priority: P2)

**Goal**: Ensure README provides accurate deployment documentation without obsolete Netlify references

**Independent Test**: Reader unfamiliar with project can identify current deployment approach (Docker/Render) without confusion from Netlify references

**Note**: Netlify removal already completed in Phase 2 (Foundational). This phase ensures deployment documentation is complete.

### Verify Deployment Documentation (FR-011, FR-012)

- [x] T081 [US4] Verify Docker deployment section exists and is accurate in README.md
- [x] T082 [US4] Verify docker-compose instructions are present in README.md
- [x] T083 [US4] Verify no conflicting deployment information exists in README.md
- [x] T084 [US4] Add reference to docs/DEPLOYMENT_ONBOARDING.md for detailed deployment guidance in README.md

### Update Quick Start Section

- [x] T085 [US4] Verify Quick Start section flows into JIRA Configuration section in README.md
- [x] T086 [US4] Update line 47 reference "See 'JIRA Configuration' section below" with anchor link in README.md

**Checkpoint**: User Story 4 complete - Deployment documentation is accurate and Netlify-free

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements that affect multiple user stories and overall README quality

### Update Cross-References Throughout README (FR-014)

- [x] T087 Update Table of Contents (if present) to include JIRA Configuration section in README.md
- [x] T088 Verify all internal anchor links navigate correctly in README.md
- [x] T089 Update "Project Structure" section to reflect current backend services (FR-015) in README.md

### Validate Documentation Completeness (All Success Criteria)

- [x] T090 Verify all 14 custom fields documented with types and purposes (SC-002, SC-006) in README.md
- [x] T091 Verify all 4 CLI commands documented with examples (SC-007) in README.md
- [x] T092 Verify 3 environment variables documented with format examples (SC-001) in README.md
- [x] T093 Verify troubleshooting section addresses top 5 common issues (SC-008) in README.md
- [x] T094 Verify cross-references to detailed docs are accurate (SC-009) in README.md
- [x] T095 Verify README structure flows logically (SC-010) in README.md

### Pre-Commit Validation

- [x] T096 Run git diff --check to verify no trailing whitespace in README.md
- [x] T097 Verify no Netlify references remain: grep -i "netlify" README.md returns 0 matches (SC-003)
- [x] T098 Verify JIRA Configuration section exists: grep "## JIRA Configuration" README.md returns 1 match
- [x] T099 Run pre-commit hooks on README.md: pre-commit run --files README.md
- [x] T100 Fix any pre-commit errors (trailing-whitespace, end-of-file-fixer) in README.md

### Manual Testing

- [x] T101 Conduct new developer simulation: time setup following only README instructions (target: <20 min, SC-001)
- [x] T102 Verify all CLI command examples are executable (SC-007)
- [x] T103 Test all cross-reference links resolve correctly (SC-009)
- [x] T104 Verify 90% of JIRA configuration questions answerable in README (SC-005)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup (T001-T004) - MUST complete before user story work
- **User Story 1 (Phase 3)**: Depends on Foundational (T005-T012) completion
- **User Story 2 (Phase 4)**: Depends on Foundational (T005-T012) completion AND User Story 1 (T013-T040) completion (builds on JIRA Configuration section structure)
- **User Story 3 (Phase 5)**: Depends on User Story 1 and 2 completion (adds to existing JIRA Configuration section)
- **User Story 4 (Phase 6)**: Depends on Foundational completion (Netlify removal), can run in parallel with US1-3
- **Polish (Phase 7)**: Depends on all user stories (T001-T086) completion

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - Creates JIRA Configuration section structure
- **User Story 2 (P2)**: Can start after User Story 1 - Adds custom field documentation to existing section
- **User Story 3 (P3)**: Can start after User Story 1 and 2 - Adds troubleshooting to existing section
- **User Story 4 (P2)**: Can start after Foundational (Phase 2) - Independent verification/cleanup

**Note**: Since all tasks modify README.md sequentially, parallelization is limited. However, User Story 4 verification (T081-T086) can be done in parallel with User Story 1-3 work if using branch/merge strategy.

### Within Each User Story

- Authentication documentation (T016-T025) before CLI commands (T026-T040)
- Custom field table (T043-T058) before JIRA setup notes (T059-T064)
- Troubleshooting content (T065-T077) before cross-references (T078-T080)
- All content addition before validation (Phase 7)

### Sequential Constraints (Same File)

⚠️ **CRITICAL**: All tasks modify README.md and must be executed sequentially within each phase. No true parallel opportunities exist due to single-file editing.

**Recommended Workflow**:
1. Complete Setup → Foundational → User Story 1 → User Story 2 → User Story 3 → User Story 4 → Polish
2. Commit after each phase completion for rollback safety
3. Create draft checkpoints after each user story for incremental review

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T004)
2. Complete Phase 2: Foundational - Remove Netlify (T005-T012)
3. Complete Phase 3: User Story 1 - New Developer Onboarding (T013-T040)
4. **STOP and VALIDATE**: Test User Story 1 with new developer simulation
5. If successful, proceed to User Story 2

**Rationale**: User Story 1 (P1) is most critical - enables all new developers to set up JIRA integration. Delivers immediate value.

### Incremental Delivery

1. Setup + Foundational → Clean slate ready for JIRA documentation
2. Add User Story 1 → Test independently → Commit (MVP! New developer onboarding works)
3. Add User Story 2 → Test independently → Commit (Administrators can create fields)
4. Add User Story 3 → Test independently → Commit (Troubleshooting guidance available)
5. Add User Story 4 → Test independently → Commit (Deployment documentation accurate)
6. Polish → Final validation → Commit

**Checkpoint Strategy**: After each user story, test that specific story's acceptance scenarios independently before proceeding.

### Single-Developer Sequential Strategy

**Recommended for documentation-only features:**

1. Day 1 Morning: Setup + Foundational (2 hours)
   - T001-T012: Remove Netlify, create backup
2. Day 1 Afternoon: User Story 1 (3 hours)
   - T013-T040: Authentication, CLI commands, validation
   - Checkpoint: Test new developer setup
3. Day 2 Morning: User Story 2 (2 hours)
   - T041-T064: Custom fields, JIRA setup requirements
   - Checkpoint: Test administrator field creation
4. Day 2 Afternoon: User Story 3 (2 hours)
   - T065-T080: Troubleshooting, cross-references
   - Checkpoint: Test intentional misconfiguration resolution
5. Day 3 Morning: User Story 4 + Polish (2 hours)
   - T081-T104: Deployment verification, validation, testing
   - Final checkpoint: New developer simulation

**Total Estimated Time**: 11 hours across 3 days (aligns with quickstart.md 85-minute per-phase estimate × 7 phases)

---

## Validation Checklist

Before considering feature complete:

**Functional Requirements Coverage**:
- [ ] FR-001: JIRA Configuration section with 4 subsections exists
- [ ] FR-002: 3 environment variables documented with examples
- [ ] FR-003: Token generation steps included (5 steps)
- [ ] FR-004: 14 custom fields listed with types and purposes
- [ ] FR-005: Epic association requirements explained
- [ ] FR-006: CLI command examples provided
- [ ] FR-007: CLI flags documented with use cases
- [ ] FR-008: validate-config command instructions included
- [ ] FR-009: Sync testing command explained
- [ ] FR-010: Required permissions described
- [ ] FR-011: All Netlify content removed (0 matches)
- [ ] FR-012: Docker deployment preserved
- [ ] FR-013: Troubleshooting guidance for 5 common issues
- [ ] FR-014: Cross-references to detailed docs accurate
- [ ] FR-015: Project Structure section accurate

**Success Criteria Coverage**:
- [ ] SC-001: New developer setup time < 20 minutes (test with simulation)
- [ ] SC-002: Required vs optional fields clearly marked
- [ ] SC-003: 0 Netlify references remain (verified with grep)
- [ ] SC-004: Validation commands detect misconfigurations < 2 minutes
- [ ] SC-005: 90% of questions answerable in README
- [ ] SC-006: Administrators can create fields from README
- [ ] SC-007: CLI examples are executable
- [ ] SC-008: Top 5 issues addressed in troubleshooting
- [ ] SC-009: Cross-references accurate and helpful
- [ ] SC-010: README structure flows logically

**Constitution Compliance**:
- [ ] No trailing whitespace (git diff --check)
- [ ] File ends with newline (pre-commit check)
- [ ] Markdown properly formatted
- [ ] Clear, self-explanatory documentation
- [ ] Pre-commit hooks pass

---

## Task Summary

**Total Tasks**: 104
- Setup (Phase 1): 4 tasks
- Foundational (Phase 2): 8 tasks
- User Story 1 (Phase 3): 28 tasks
- User Story 2 (Phase 4): 24 tasks
- User Story 3 (Phase 5): 16 tasks
- User Story 4 (Phase 6): 6 tasks
- Polish (Phase 7): 18 tasks

**Tasks by User Story**:
- US1 (New Developer Onboarding): 28 tasks
- US2 (System Administrator Setup): 24 tasks
- US3 (Troubleshooting): 16 tasks
- US4 (Deployment Documentation): 14 tasks (8 in Phase 2 + 6 in Phase 6)

**Parallel Opportunities**: None (all tasks modify single file README.md sequentially)

**Estimated Timeline**: 11 hours (85 minutes per phase × 7 phases + validation time)

**Suggested MVP Scope**: Phase 1 + Phase 2 + Phase 3 (User Story 1 only) = 40 tasks, ~5 hours

**Format Validation**: ✅ All 104 tasks follow checklist format: `- [ ] [ID] [Story?] Description with file path`

---

## Notes

- All tasks modify README.md and must be executed sequentially
- Commit after each phase for rollback safety
- Each user story should be independently testable via acceptance scenarios
- Use checkpoints after each phase to validate before proceeding
- Pre-commit hooks MUST pass before final commit
- New developer simulation is final acceptance test
