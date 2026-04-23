# Implementation Plan: JIRA Custom Fields Configuration

**Branch**: `003-jira-custom-fields` | **Date**: December 26, 2025 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-jira-custom-fields/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Enable multi-project JIRA custom field configuration through JSON-based mapping. Replace individual environment variables with a structured configuration file that maps each JIRA project to its custom field IDs. Provide a CLI command to automatically create the 6 required custom fields (Roadmap Title, Roadmap Description, and 4 Image URLs) for Epic issue types and auto-update the configuration file. Extend data extraction to use custom field values with fallback to default epic fields.

**Technical Approach**: Add JSON configuration loader with schema validation, extend JiraClient to support per-project field mappings, implement Flask CLI command using JIRA REST API v3 for custom field creation, and enhance RoadmapItem model to accommodate optional custom fields and image URLs.

## Technical Context

**Language/Version**: Python 3.14
**Primary Dependencies**: Flask, requests, python-dotenv, dataclasses
**Storage**: JSON configuration file (`backend/config/jira_projects.json`), in-memory cache
**Testing**: pytest with fixtures, unittest.mock for JIRA API mocking
**Target Platform**: Linux server (Docker container)
**Project Type**: Web (backend Flask API)
**Performance Goals**: CLI field creation < 30 seconds, configuration load < 100ms, no impact to existing sync performance
**Constraints**: Must maintain backward compatibility with existing field mappings, JSON validation must not block startup on warnings
**Scale/Scope**: Support 10+ JIRA projects, 6 custom fields per project, maintain 80%+ test coverage

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Clean Code & Readability ✅

- **Self-documenting code**: CLI commands, configuration loaders, and validators will use descriptive function names
- **Zen of Python**: Explicit JSON schema over implicit field discovery, simple file-based config over complex discovery
- **Single responsibility**: Separate concerns - ConfigLoader, FieldCreator, FieldValidator
- **File organization**: New modules stay within existing structure, no new top-level directories

### Code Style Standards ✅

**Backend (Python)**:
- Follow PEP 8 for all new modules
- Type annotations for all functions (e.g., `def load_config(path: str) -> ProjectConfig`)
- Black + Flake8 enforcement via pre-commit hooks
- SOLID principles: dependency injection for config, testable CLI commands

### Naming Conventions ✅

- `snake_case` for functions: `load_project_config()`, `create_custom_field()`
- `PascalCase` for new classes: `ProjectConfig`, `CustomFieldManager`
- Descriptive names: `jira_projects.json` not `config.json`

### Testing & Quality Assurance ✅

- **Unit tests required**: 80%+ coverage target
- Test CLI commands with mocked JIRA API calls
- Test JSON validation with valid/invalid/malformed configs
- Test field extraction with custom vs. default fallback scenarios
- Mock filesystem for configuration loading tests
- Pre-commit hooks run all tests before commit

### Accessibility N/A

- No frontend changes in this feature (backend-only)

## Constitution Compliance Summary

**Status**: ✅ **PASSED** - All applicable principles satisfied

**No violations** - Feature follows established patterns:
- Extends existing `Config` and `JiraClient` classes
- Adds new CLI command following Flask patterns
- Maintains test coverage requirements
- No complexity additions requiring justification

## Project Structure

### Documentation (this feature)

```text
specs/003-jira-custom-fields/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   └── config-schema.json
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── config.py                    # MODIFIED: Add JSON config loader
│   ├── models/
│   │   └── roadmap.py              # MODIFIED: Add image URLs support
│   ├── services/
│   │   ├── jira_client.py          # MODIFIED: Custom field extraction
│   │   └── config_loader.py        # NEW: JSON configuration management
│   └── cli/
│       └── jira_setup.py           # NEW: Flask CLI commands
├── config/
│   ├── jira_projects.json          # NEW: Project custom field mappings
│   └── jira_projects.schema.json  # NEW: JSON schema validation
├── tests/
│   ├── unit/
│   │   ├── test_config_loader.py   # NEW: Config loading tests
│   │   ├── test_jira_setup.py      # NEW: CLI command tests
│   │   └── test_jira_client.py     # MODIFIED: Add custom field tests
│   └── integration/
│       └── test_routes.py          # MODIFIED: Test image URLs in response
└── run.py                          # MODIFIED: Register CLI commands

frontend/
└── [No changes - backend only feature]
```

**Structure Decision**: Web application (backend + frontend separation). This feature only modifies the backend. New configuration management layer sits between Config class and JiraClient, maintaining separation of concerns. CLI commands follow Flask's click-based pattern for consistency with existing tooling.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**No violations to justify** - Feature maintains existing complexity levels and follows established patterns.

---

## Phase 0: Research & Discovery ✅

**Status**: Complete | **Date**: December 26, 2025

### Research Outputs

1. **Configuration Format**: JSON selected over YAML, environment variables, or database
   - Rationale: Balance of simplicity, validation, and version control friendliness
   - Schema-based validation with jsonschema library

2. **JIRA API Integration**: REST API v3 endpoints identified
   - Field creation: `POST /rest/api/3/field`
   - Field types: textfield for title/URLs, textarea for description
   - Context configuration for Epic-only fields

3. **Loading Strategy**: Startup validation with lazy project lookup
   - One-time load, in-memory cache
   - Warning-only errors for resilience
   - Fallback to defaults for missing projects

4. **CLI Framework**: Flask Click integration
   - Command syntax: `flask jira setup-fields <PROJECT_KEY>`
   - Progress bars and colored output
   - Dry-run support for testing

5. **Field Extraction Logic**: Custom field priority with fallback
   - Try custom fields first, fall back to epic defaults
   - URL validation for image fields
   - Filter empty values

### Key Decisions

| Decision Point | Selected Approach | Alternative Rejected |
|----------------|-------------------|---------------------|
| Config format | JSON with schema | YAML, env vars, database |
| Field type | Text fields | URL type (too strict) |
| Loading strategy | Startup with cache | On-demand per request |
| CLI framework | Flask Click | argparse, custom parser |
| Validation library | jsonschema | Manual validation |

**Deliverable**: [research.md](./research.md) - Complete technical research document

---

## Phase 1: Design & Contracts ✅

**Status**: Complete | **Date**: December 26, 2025

### Data Model

**Core Entities**:

1. **ProjectConfig** - Root configuration object
   - version: string (semantic version)
   - projects: dict of ProjectFieldMapping

2. **ProjectFieldMapping** - Per-project field IDs
   - roadmap_title: customfield ID
   - roadmap_description: customfield ID
   - roadmap_image_url_1..4: customfield IDs

3. **RoadmapItem (Enhanced)** - Existing model extended
   - title/description: from custom fields or epic defaults
   - images: list of 0-4 URLs from custom fields

**Relationships**:
- ProjectConfig contains N ProjectFieldMapping instances
- JiraClient uses ProjectFieldMapping to extract RoadmapItem data
- One-to-many: Config → Projects → Epics → RoadmapItems

**Deliverable**: [data-model.md](./data-model.md) - Complete entity definitions with validation rules

### API Contracts

**Configuration Schema**:
- JSON Schema Draft 7 specification
- Strict validation with pattern matching
- Examples for 1-3 projects

**File**: [contracts/config-schema.json](./contracts/config-schema.json)

**Example Configuration**: [contracts/example-config.json](./contracts/example-config.json)

### Quickstart Guide

Comprehensive setup guide covering:
- Prerequisites and environment setup
- CLI command usage with examples
- Step-by-step JIRA field population
- Verification and troubleshooting
- Best practices and operational guidelines

**Deliverable**: [quickstart.md](./quickstart.md) - Complete user guide

### Agent Context Update

Updated Cursor IDE context with:
- Python 3.14 language version
- Flask, requests, python-dotenv, dataclasses dependencies
- JSON configuration storage approach
- Web (backend Flask API) project type

**Status**: ✅ Context file updated successfully

---

## Post-Design Constitution Check ✅

**Re-validation after Phase 1 design artifacts**

### Clean Code & Readability ✅

- ✅ Data model uses clear entity names (ProjectConfig, ProjectFieldMapping)
- ✅ JSON schema provides self-documenting configuration format
- ✅ Quickstart guide demonstrates clear usage patterns
- ✅ No nested complexity in entity relationships (flat project mapping)

### Code Style Standards ✅

- ✅ Follows Python type hints in entity definitions
- ✅ Uses dataclasses for structured data
- ✅ PEP 8 compliant naming throughout design

### Testing & Quality Assurance ✅

- ✅ Test strategy defined in research.md
- ✅ Unit test scenarios identified for all components
- ✅ Integration test coverage planned
- ✅ Manual testing checklist provided

### Design Quality ✅

- ✅ Separation of concerns: Config loading, validation, field creation, data extraction
- ✅ Single responsibility: Each entity has one clear purpose
- ✅ DRY principle: Shared schema used for validation
- ✅ SOLID principles: Dependency injection for config, open for extension

**Final Status**: ✅ **PASSED** - Design maintains constitution compliance

---

## Implementation Readiness

**Ready for Phase 2: Task Generation** ✅

All planning artifacts complete:
- ✅ Technical context defined
- ✅ Research completed (6 key decisions documented)
- ✅ Data model designed (3 core entities)
- ✅ API contracts specified (JSON schema + examples)
- ✅ Quickstart guide written
- ✅ Agent context updated
- ✅ Constitution compliance verified

**Next Step**: Run `/speckit.tasks` to generate implementation tasks

**Estimated Implementation Effort**:
- Configuration loader: 3-4 hours
- CLI command: 4-5 hours
- Field extraction: 3-4 hours
- Testing: 4-6 hours
- **Total**: ~15-20 hours

**Risk Assessment**: Low
- Well-defined requirements
- Clear technical approach
- No external blockers
- Backward compatible changes
