# Implementation Plan: Update README with JIRA Configuration Documentation

**Branch**: `011-readme-jira-docs` | **Date**: 2026-01-29 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/011-readme-jira-docs/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Update the main README.md to provide comprehensive JIRA configuration documentation while removing obsolete Netlify deployment references. This documentation update will guide new developers through JIRA authentication setup, custom field configuration, CLI command usage, and troubleshooting procedures.

**Primary Requirement**: Create a dedicated JIRA Configuration section in README.md that explains authentication, permissions, custom field requirements (14 fields), CLI mapping commands, and validation procedures.

**Technical Approach**: This is a documentation-only feature requiring no code changes. The implementation involves restructuring README.md content, documenting existing CLI commands from `backend/app/cli/jira_setup.py`, and referencing existing configuration patterns in `backend/config/jira_projects.json`.

## Technical Context

**Language/Version**: Markdown documentation
**Primary Dependencies**: N/A (documentation only)
**Storage**: N/A (no data storage changes)
**Testing**: N/A (documentation validation through manual review)
**Target Platform**: README.md file in repository root
**Project Type**: Web application (existing backend + frontend structure)
**Performance Goals**: N/A (documentation)
**Constraints**: Documentation must be complete enough that 90% of JIRA configuration questions can be answered without consulting additional sources (SC-005)
**Scale/Scope**: Single README.md file update affecting onboarding of all new developers and system administrators

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Assessment: ✅ PASS (Documentation-Only Feature)

This feature involves only documentation updates to README.md with no code changes, therefore most constitution principles do not apply:

**Applicable Principles**:
- ✅ **Universal Standards (Section II)**: Documentation must not contain trailing whitespace
- ✅ **Clean Code & Readability (Section I)**: Documentation must be clear, well-organized, and self-explanatory
- ✅ **Pre-Commit Compliance (Section VI)**: Markdown files must pass pre-commit hooks (trailing-whitespace, end-of-file-fixer)

**Non-Applicable Principles**:
- N/A **Code Style Standards**: No Python or TypeScript code changes
- N/A **Testing & Quality Assurance**: No code to test (documentation validation through manual review)
- N/A **Naming Conventions**: No variables, functions, or components being created
- N/A **Semantic HTML**: Markdown documentation, not HTML/Vue components

**Violation**: None

**Justification**: Documentation-only features inherently comply with constitution as they don't introduce code complexity, bypass testing requirements, or violate style standards.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
/ (repository root)
├── README.md                              # PRIMARY UPDATE TARGET
├── backend/
│   ├── app/
│   │   └── cli/
│   │       └── jira_setup.py             # CLI commands to document
│   └── config/
│       └── jira_projects.json            # Field mapping config format to document
├── docs/
│   ├── JIRA_LIKES_FIELD_MIGRATION.md     # Referenced for additional detail
│   └── DEPLOYMENT_ONBOARDING.md          # Keep Docker deployment references
└── specs/
    ├── 004-cli-jira-field-mapping/       # CLI quickstart to reference
    │   └── quickstart.md
    └── 011-readme-jira-docs/             # This feature documentation
        ├── spec.md
        ├── plan.md                        # This file
        ├── research.md                    # Phase 0 output
        ├── data-model.md                  # Phase 1 output
        ├── quickstart.md                  # Phase 1 output
        └── contracts/                     # Phase 1 output (empty for docs-only)
```

**Structure Decision**: Web application structure (backend + frontend). This feature only modifies README.md at repository root and references existing backend CLI commands and configuration files. No source code changes are required—all work is documentation updates.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**N/A** - No constitution violations. This is a documentation-only feature with no code complexity concerns.

---

## Phase 0: Research (Completed)

**Deliverable**: `research.md` ✅

**Key Findings**:
- 17 Netlify references identified for removal
- 4 CLI commands documented: `list-fields`, `map-fields`, `validate-config`, `test-create-issue`
- 14 custom field requirements analyzed with types and purposes
- JIRA authentication flow documented (3 environment variables, token generation process)
- Documentation structure best practices researched

**All unknowns resolved**: No "NEEDS CLARIFICATION" items remaining

---

## Phase 1: Design & Contracts (Completed)

**Deliverables**:
- `data-model.md` ✅ - Documents 5 entities: JIRA Config Section, Environment Variables, Custom Field Mappings, CLI Commands, Netlify References
- `contracts/` ✅ - Empty directory (no API contracts for documentation-only feature)
- `quickstart.md` ✅ - Implementation checklist with 4 phases, 85-minute timeline
- Agent context updated ✅ - Cursor rules updated with "Markdown documentation" language

**Constitution Re-Check**: ✅ PASS

**Rationale**: Documentation-only feature continues to comply with all applicable constitution principles:
- ✅ No trailing whitespace will be introduced (verified via pre-commit hooks)
- ✅ Documentation follows clear, self-explanatory structure
- ✅ Cross-references are accurate and helpful
- ✅ No code complexity introduced

---

## Implementation Readiness

**Status**: ✅ READY FOR IMPLEMENTATION

**Next Steps** (to be executed by `/speckit.implement` or manual implementation):
1. Remove 17 Netlify references from README.md
2. Create new "JIRA Configuration" section with 4 subsections
3. Document 3 environment variables with examples
4. Document 14 custom fields with comprehensive table
5. Document 4 CLI commands with usage examples
6. Add validation and troubleshooting guidance
7. Update cross-references throughout README
8. Verify no trailing whitespace
9. Test documentation with new developer simulation

**Estimated Implementation Time**: 85 minutes

**Testing Approach**: Manual review, new developer simulation, CLI command execution verification

---

## Branch & Artifacts

- **Branch**: `011-readme-jira-docs`
- **Spec**: [spec.md](./spec.md)
- **Plan**: [plan.md](./plan.md) (this file)
- **Research**: [research.md](./research.md)
- **Data Model**: [data-model.md](./data-model.md)
- **Quickstart**: [quickstart.md](./quickstart.md)
- **Contracts**: [contracts/](./contracts/) (empty - N/A for docs)

**Ready for**: Task generation via `/speckit.tasks` command
