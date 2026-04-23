# Data Model: README JIRA Configuration Documentation

**Feature**: 011-readme-jira-docs
**Date**: 2026-01-29
**Purpose**: Define the structure and relationships of documentation entities for JIRA configuration.

---

## Overview

This feature involves documentation entities only—no code data models. The "data model" here represents the conceptual structure of documentation sections and their relationships.

---

## Documentation Entities

### Entity 1: JIRA Configuration Section

**Type**: Documentation Section
**Location**: `README.md` (new section after "Quick Start")

**Attributes**:
- **Section Title**: "JIRA Configuration"
- **Subsections** (4):
  1. Authentication Setup
  2. Custom Field Requirements
  3. Field Mapping with CLI
  4. Validation & Troubleshooting

**Purpose**: Centralized reference for all JIRA integration setup and configuration

**Relationships**:
- References → Environment Variables (Entity 2)
- References → Custom Field Mappings (Entity 3)
- References → CLI Commands (Entity 4)
- Links to → External Documentation (JIRA_LIKES_FIELD_MIGRATION.md, CLI quickstart)

---

### Entity 2: Environment Variables

**Type**: Configuration Reference
**Cardinality**: 3 required variables

| Variable Name | Type | Format | Required | Security Level |
|---------------|------|--------|----------|----------------|
| `JIRA_BASE_URL` | String (URL) | `https://DOMAIN.atlassian.net` | Yes | Low (public URL) |
| `JIRA_EMAIL` | String (Email) | Valid email address | Yes | Medium (service account) |
| `JIRA_API_TOKEN` | String (Token) | Base64-encoded secret | Yes | High (credential) |

**Validation Rules**:
- `JIRA_BASE_URL` MUST start with `https://`
- `JIRA_BASE_URL` MUST end with `.atlassian.net` (JIRA Cloud)
- `JIRA_EMAIL` MUST be valid email format
- `JIRA_API_TOKEN` MUST NOT be empty
- `JIRA_API_TOKEN` MUST NOT be committed to git

**Storage Location**: `backend/.env` (local), Kubernetes Secrets (production)

**Purpose**: Authenticate backend service with JIRA Cloud API

**Relationships**:
- Used by → Backend JIRA Client (`app/services/jira_client.py`)
- Documented in → JIRA Configuration Section (Entity 1)
- Referenced in → Backend `.env.example`

---

### Entity 3: Custom Field Mappings

**Type**: Configuration Mapping
**Cardinality**: 14 field attributes per project

| Attribute Name | JIRA Field Type | Required | Default Value | Validation |
|----------------|----------------|----------|---------------|------------|
| `public_roadmap` | Checkbox | Yes | `false` | Boolean |
| `roadmap_status` | Select List (Single) | Yes | None | Must be: Delivered, Now, Next, Future |
| `module` | Select List (Single) | Yes | None | Project-specific values |
| `release_year` | Number | Yes | None | 4-digit year (YYYY) |
| `release_quarter` | Select List (Single) | Yes | None | Must be: Q1, Q2, Q3, Q4 |
| `release_month` | Number | Yes | None | 1-12 |
| `documentation_url` | URL | Yes | None | Valid HTTP/HTTPS URL |
| `roadmap_title` | Text (255 chars) | Yes | None | Max 255 characters |
| `roadmap_description` | Paragraph (Rich Text) | Yes | None | Supports HTML formatting |
| `roadmap_image_url_1` | URL | No | None | Valid image URL |
| `roadmap_image_url_2` | URL | No | None | Valid image URL |
| `roadmap_image_url_3` | URL | No | None | Valid image URL |
| `roadmap_image_url_4` | URL | No | None | Valid image URL |
| `roadmap_likes` | Number | Yes | `0` | Non-negative integer |

**Field ID Format**: `customfield_NNNNN` (where N = 5+ digits)

**JIRA Requirements**:
- All fields MUST be associated with **Epic** issue type
- Fields MUST appear on Epic **Edit Screen**
- Fields MUST appear on Epic **View Screen**
- Field IDs are unique per JIRA instance (dev/staging/prod differ)

**Storage Location**: `backend/config/jira_projects.json`

**Purpose**: Map JIRA custom field IDs to roadmap application attributes

**Relationships**:
- Configured by → CLI Commands (Entity 4)
- Validated by → CLI Commands (Entity 4)
- Used by → Backend Sync Service (`app/services/sync_service.py`)
- Documented in → JIRA Configuration Section (Entity 1)

**Example Mapping** (NEXUS project):
```json
{
  "NEXUS": {
    "public_roadmap": "customfield_14699",
    "roadmap_status": "customfield_14698",
    "module": "customfield_14622",
    ...
  }
}
```

---

### Entity 4: CLI Commands

**Type**: Command-Line Interface Reference
**Cardinality**: 4 commands

#### Command 1: `list-fields`

**Signature**: `flask jira list-fields PROJECT_KEY [OPTIONS]`

**Purpose**: Explore available custom fields in JIRA project

**Arguments**:
- `PROJECT_KEY` (required): JIRA project key (e.g., "NEXUS", "ENGAGE")

**Options**:
| Flag | Type | Default | Purpose |
|------|------|---------|---------|
| `--type TYPE` | String | None | Filter by field type (text, select, checkbox, etc.) |
| `--include-global` | Boolean | False | Include globally-scoped fields |
| `--show-all-types` | Boolean | False | Show all field types (not just common ones) |

**Output**: Table of field IDs, names, and types

**Typical Usage**: Initial discovery before field mapping

---

#### Command 2: `map-fields`

**Signature**: `flask jira map-fields [PROJECT_KEY] [OPTIONS]`

**Purpose**: Interactive wizard to configure custom field mappings

**Arguments**:
- `PROJECT_KEY` (optional): Specific project key, or omit to see selection prompt

**Options**:
| Flag | Type | Default | Purpose |
|------|------|---------|---------|
| `--all` | Boolean | False | Configure all projects sequentially |
| `--no-auto-match` | Boolean | False | Disable fuzzy matching, force manual selection |
| `--include-global` | Boolean | False | Include globally-scoped fields in candidates |
| `--show-all-types` | Boolean | False | Show fields of all types (not just expected types) |
| `--dry-run` | Boolean | False | Preview changes without saving to config file |

**Workflow**:
1. Authenticate with JIRA using environment variables
2. Fetch custom fields for project
3. For each of 14 attributes:
   - Auto-match field using fuzzy matching (85% confidence threshold)
   - Prompt for confirmation or manual selection
4. Save mappings to `backend/config/jira_projects.json`

**Output**: Updated configuration file with field mappings

**Typical Usage**: Initial setup, adding new projects, remapping fields after JIRA changes

---

#### Command 3: `validate-config`

**Signature**: `flask jira validate-config [PROJECT_KEY] [OPTIONS]`

**Purpose**: Verify JIRA configuration correctness

**Arguments**:
- `PROJECT_KEY` (optional): Specific project key, or omit to validate all projects

**Options**:
| Flag | Type | Default | Purpose |
|------|------|---------|---------|
| `--fix` | Boolean | False | Attempt auto-fix by re-prompting for invalid fields |
| `--verbose` | Boolean | False | Show detailed validation checks (field accessibility, permissions) |

**Validation Checks**:
1. Environment variables present and valid format
2. JIRA authentication successful
3. All required field attributes mapped
4. Field IDs exist in JIRA project
5. Fields accessible with current API token
6. Fields associated with Epic issue type
7. Field types match expected types

**Output**: Validation report with pass/fail status per check

**Typical Usage**: After initial setup, troubleshooting sync issues, verifying permissions

---

#### Command 4: `test-create-issue`

**Signature**: `flask jira test-create-issue PROJECT_KEY [OPTIONS]`

**Purpose**: Test JIRA write permissions and field accessibility

**Arguments**:
- `PROJECT_KEY` (required): JIRA project key to test

**Options**:
| Flag | Type | Default | Purpose |
|------|------|---------|---------|
| `--summary TEXT` | String | "[TEST] Feature Request" | Issue summary/title |
| `--type TYPE` | String | "Task" | Issue type name (Task, Epic, Story, etc.) |

**Workflow**:
1. Create test issue in JIRA project
2. Populate custom fields with sample data
3. Verify issue creation successful
4. Display issue key and URL

**Output**: Test issue key or error message

**Typical Usage**: Verify write permissions before enabling automated sync

---

**CLI Command Relationships**:
- `list-fields` → Informs → `map-fields` (user discovers field names)
- `map-fields` → Creates → Custom Field Mappings (Entity 3)
- `validate-config` → Verifies → Custom Field Mappings (Entity 3) + Environment Variables (Entity 2)
- `test-create-issue` → Verifies → JIRA write permissions

**All commands documented in → JIRA Configuration Section (Entity 1)**

---

### Entity 5: Netlify References (Removal Targets)

**Type**: Obsolete Content
**Cardinality**: 17 occurrences in current README

**Categories**:
1. Deployment instructions (5 references)
2. Environment variable tables (4 references)
3. Build command examples (3 references)
4. Configuration file references (2 references)
5. Automated deployment workflows (3 references)

**Removal Strategy**: Delete all Netlify-specific content without replacement (Docker deployment already documented)

**Preservation**: Keep Docker deployment section, generic build instructions, environment variable concepts (without Netlify-specific formatting)

**Purpose**: Remove outdated deployment information to prevent confusion

**Relationships**:
- Replaced by → Docker deployment documentation (existing in README)
- Related deployment details in → `docs/DEPLOYMENT_ONBOARDING.md`

---

## Documentation Relationships Diagram

```text
┌─────────────────────────────────────────────────────┐
│ README.md                                           │
│                                                     │
│ ┌─────────────────────────────────────────────┐   │
│ │ JIRA Configuration Section (Entity 1)       │   │
│ │                                             │   │
│ │ ┌────────────────────────────────────────┐ │   │
│ │ │ 1. Authentication Setup                │ │   │
│ │ │    References: Entity 2 (Env Vars)     │ │   │
│ │ └────────────────────────────────────────┘ │   │
│ │                                             │   │
│ │ ┌────────────────────────────────────────┐ │   │
│ │ │ 2. Custom Field Requirements           │ │   │
│ │ │    References: Entity 3 (Field Map)    │ │   │
│ │ └────────────────────────────────────────┘ │   │
│ │                                             │   │
│ │ ┌────────────────────────────────────────┐ │   │
│ │ │ 3. Field Mapping with CLI              │ │   │
│ │ │    References: Entity 4 (Commands)     │ │   │
│ │ └────────────────────────────────────────┘ │   │
│ │                                             │   │
│ │ ┌────────────────────────────────────────┐ │   │
│ │ │ 4. Validation & Troubleshooting        │ │   │
│ │ │    References: Entity 4 (Commands)     │ │   │
│ │ └────────────────────────────────────────┘ │   │
│ └─────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
         │                    │                   │
         │                    │                   │
         ▼                    ▼                   ▼
   ┌──────────┐     ┌──────────────────┐   ┌───────────┐
   │ Entity 2 │     │    Entity 3      │   │ Entity 4  │
   │ Env Vars │     │ Field Mappings   │   │ CLI Cmds  │
   └──────────┘     └──────────────────┘   └───────────┘
         │                    │                   │
         └────────────────────┴───────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │ backend/.env     │
                    │ jira_projects    │
                    │ .json            │
                    └──────────────────┘
```

---

## Entity State Transitions

### Environment Variables (Entity 2)

```
[Unconfigured] 
    │
    ├─ User creates backend/.env file
    │
    ▼
[Configured - Untested]
    │
    ├─ CLI command attempts JIRA authentication
    │
    ├─ Authentication succeeds ─────► [Configured - Valid]
    │
    └─ Authentication fails ────────► [Configured - Invalid]
```

---

### Custom Field Mappings (Entity 3)

```
[No Mappings]
    │
    ├─ User runs: flask jira map-fields PROJECT_KEY
    │
    ▼
[Mapping in Progress]
    │
    ├─ Auto-match succeeds ─────► [Mapped - Unvalidated]
    │
    └─ Auto-match fails ────────► [Manual Selection Required]
         │
         ├─ User selects field ───► [Mapped - Unvalidated]
         │
         └─ User skips field ─────► [Partially Mapped]
                  │
                  ├─ Required field skipped ──► [Invalid Config]
                  │
                  └─ Optional field skipped ──► [Mapped - Unvalidated]

[Mapped - Unvalidated]
    │
    ├─ User runs: flask jira validate-config
    │
    ├─ Validation succeeds ─────► [Mapped - Valid]
    │
    └─ Validation fails ────────► [Mapped - Invalid]
```

---

### CLI Commands (Entity 4)

No state transitions (commands are stateless operations)

---

## Validation Rules Summary

| Entity | Rule | Enforced By | Error Message |
|--------|------|-------------|---------------|
| Env Vars | `JIRA_BASE_URL` MUST start with `https://` | CLI commands | "Invalid JIRA_BASE_URL: must start with https://" |
| Env Vars | `JIRA_BASE_URL` MUST end with `.atlassian.net` | CLI commands | "Invalid JIRA_BASE_URL: must be JIRA Cloud (*.atlassian.net)" |
| Env Vars | `JIRA_EMAIL` MUST be valid email | CLI commands | "Invalid JIRA_EMAIL: must be valid email address" |
| Env Vars | `JIRA_API_TOKEN` MUST NOT be empty | CLI commands | "JIRA_API_TOKEN is missing or empty" |
| Field Mappings | All 10 required fields MUST be mapped | `validate-config` | "Missing required field: {field_name}" |
| Field Mappings | Field IDs MUST match pattern `customfield_\d{5,}` | `validate-config` | "Invalid field ID format: {field_id}" |
| Field Mappings | Field IDs MUST exist in JIRA project | `validate-config` | "Field not found in JIRA: {field_id}" |
| Field Mappings | Fields MUST be accessible with API token | `validate-config` | "Permission denied for field: {field_id}" |
| CLI Commands | `PROJECT_KEY` MUST match pattern `[A-Z][A-Z0-9]{1,9}` | All commands | "Invalid project key format: {project_key}" |

---

## Documentation Dependencies

This feature's entities depend on:

| Dependency | Type | Purpose |
|------------|------|---------|
| `backend/app/cli/jira_setup.py` | Source Code | CLI command implementations (document their usage) |
| `backend/config/jira_projects.json` | Configuration File | Field mapping storage format (document structure) |
| `backend/.env.example` | Template File | Environment variable examples (document variables) |
| `docs/JIRA_LIKES_FIELD_MIGRATION.md` | Documentation | Migration guide for likes field (cross-reference) |
| `specs/004-cli-jira-field-mapping/quickstart.md` | Documentation | CLI quickstart (cross-reference) |

---

## Success Metrics

| Entity | Metric | Target | Measurement |
|--------|--------|--------|-------------|
| JIRA Config Section | Completion time for new developer setup | < 20 minutes | User testing (SC-001) |
| Environment Variables | Authentication success rate on first attempt | > 80% | Telemetry from validation command |
| Custom Field Mappings | Configuration errors requiring support | < 20% | Support ticket analysis (SC-002) |
| CLI Commands | Successful validation on first run | > 75% | Telemetry from validate-config |
| Netlify Removal | References remaining in README | 0 | Grep search (SC-003) |

---

## Notes

- **No code changes required**: All entities are documentation constructs
- **Existing systems unchanged**: CLI commands, config format, and environment variables already exist
- **Documentation-only deliverable**: README.md update is the sole artifact
- **Cross-references preserved**: Links to detailed docs (`JIRA_LIKES_FIELD_MIGRATION.md`, CLI quickstart) maintained for deeper technical information
