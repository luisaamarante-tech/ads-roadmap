# Data Model: CLI JIRA Custom Field Retrieval and Mapping

**Feature**: 004-cli-jira-field-mapping
**Date**: December 29, 2025
**Phase**: 1 - Design & Contracts

## Overview

This document defines the data structures and relationships for the CLI JIRA custom field mapping feature. The model focuses on representing custom field metadata retrieved from JIRA, user selection state during interactive prompts, and the persistent configuration format.

## Entity Diagram

```
┌─────────────────────────────────┐
│     CustomFieldMetadata         │
│─────────────────────────────────│
│ + id: str                       │  Retrieved from JIRA API
│ + name: str                     │  /rest/api/3/field
│ + description: str              │
│ + field_type: str               │
│ + is_custom: bool               │
│ + project_key: str              │
└─────────────────────────────────┘
           │
           │ 1:N (user selects from)
           ▼
┌─────────────────────────────────┐
│      FieldMapping               │
│─────────────────────────────────│  Temporary during CLI session
│ + config_key: str               │  e.g., "roadmap_title"
│ + field_id: str                 │  e.g., "customfield_10101"
│ + field_name: str               │  e.g., "Roadmap Title"
│ + is_selected: bool             │
└─────────────────────────────────┘
           │
           │ N:1 (aggregated into)
           ▼
┌─────────────────────────────────┐
│   ProjectFieldConfiguration     │
│─────────────────────────────────│  Persisted to JSON
│ + project_key: str              │  e.g., "NEXUS"
│ + public_roadmap: str           │  customfield_XXXXX
│ + roadmap_status: str           │  customfield_XXXXX
│ + module: str                   │  customfield_XXXXX
│ + release_year: str             │  customfield_XXXXX
│ + release_quarter: str          │  customfield_XXXXX
│ + release_month: str            │  customfield_XXXXX
│ + documentation_url: str        │  customfield_XXXXX
│ + roadmap_title: str            │  customfield_XXXXX
│ + roadmap_description: str      │  customfield_XXXXX
│ + roadmap_image_url_1: str      │  customfield_XXXXX
│ + roadmap_image_url_2: str      │  customfield_XXXXX
│ + roadmap_image_url_3: str      │  customfield_XXXXX
│ + roadmap_image_url_4: str      │  customfield_XXXXX
└─────────────────────────────────┘
           │
           │ N:1 (stored in)
           ▼
┌─────────────────────────────────┐
│   JiraProjectsConfig            │
│─────────────────────────────────│  Root config object
│ + version: str                  │  "1.0"
│ + projects: dict                │  {project_key: ProjectFieldConfiguration}
└─────────────────────────────────┘
```

## Entity Definitions

### 1. CustomFieldMetadata

**Purpose**: Represents a custom field retrieved from JIRA API for display and selection during CLI interaction.

**Source**: JIRA REST API `/rest/api/3/field` response

**Attributes**:

| Attribute | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `id` | `str` | Yes | JIRA custom field ID | `"customfield_10101"` |
| `name` | `str` | Yes | Human-readable field name | `"Roadmap Title"` |
| `description` | `str` | No | Field description from JIRA | `"Public-facing title for roadmap"` |
| `field_type` | `str` | Yes | JIRA field type identifier | `"com.atlassian.jira.plugin.system.customfieldtypes:textfield"` |
| `is_custom` | `bool` | Yes | Whether field is custom (vs. system) | `true` |
| `project_key` | `str` | Yes | Project this field was retrieved from | `"NEXUS"` |

**Lifecycle**: Created when CLI retrieves fields; exists only during CLI session; not persisted.

**Python Implementation**:
```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class CustomFieldMetadata:
    """Metadata for a JIRA custom field retrieved via API."""

    id: str
    name: str
    field_type: str
    is_custom: bool
    project_key: str
    description: Optional[str] = None

    @property
    def display_name(self) -> str:
        """Formatted name for CLI display."""
        return f"{self.name} ({self.id})"

    @property
    def field_type_display(self) -> str:
        """Human-readable field type."""
        type_map = {
            "textfield": "Text Field (single line)",
            "textarea": "Text Field (multi-line)",
            "url": "URL",
        }
        for key, display in type_map.items():
            if key in self.field_type:
                return display
        return "Other"

    def is_text_field(self) -> bool:
        """Check if field is text-based (suitable for roadmap data)."""
        text_types = ["textfield", "textarea", "url", "readonlyfield"]
        return any(t in self.field_type for t in text_types)

    @classmethod
    def from_jira_response(cls, data: dict, project_key: str) -> "CustomFieldMetadata":
        """Create instance from JIRA API response."""
        return cls(
            id=data["id"],
            name=data["name"],
            field_type=data.get("schema", {}).get("custom", "unknown"),
            is_custom=data.get("custom", False),
            project_key=project_key,
            description=data.get("description"),
        )
```

**Validation Rules**:
- `id` must match pattern `customfield_\d{5,}`
- `name` must not be empty
- `is_custom` must be `true` (we only work with custom fields)

**Relationships**:
- Many `CustomFieldMetadata` instances are displayed for user to select from
- User selection creates `FieldMapping` instances

---

### 2. FieldMapping

**Purpose**: Represents a user's selection mapping a config key to a specific JIRA custom field during CLI interaction.

**Source**: User selection during `flask jira map-fields` command

**Attributes**:

| Attribute | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `config_key` | `str` | Yes | Configuration attribute name | `"roadmap_title"` |
| `field_id` | `str` | Yes/No | Selected JIRA field ID (empty if skipped) | `"customfield_10101"` |
| `field_name` | `str` | No | Selected field name for confirmation display | `"Roadmap Title"` |
| `is_selected` | `bool` | Yes | Whether user selected a field vs. skipping | `true` |

**Lifecycle**: Created during CLI prompt interaction; aggregated into `ProjectFieldConfiguration`; not persisted directly.

**Python Implementation**:
```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class FieldMapping:
    """User's selection for a specific config field."""

    config_key: str
    field_id: str
    field_name: Optional[str] = None
    is_selected: bool = True

    @property
    def is_optional(self) -> bool:
        """Check if this mapping is optional (can be skipped)."""
        optional_fields = [
            "roadmap_image_url_1",
            "roadmap_image_url_2",
            "roadmap_image_url_3",
            "roadmap_image_url_4",
        ]
        return self.config_key in optional_fields

    @property
    def display_label(self) -> str:
        """Human-readable label for CLI prompts."""
        labels = {
            "public_roadmap": "Public Roadmap (checkbox)",
            "roadmap_status": "Roadmap Status (DELIVERED/NOW/NEXT/FUTURE)",
            "module": "Module/Product Area",
            "release_year": "Release Year",
            "release_quarter": "Release Quarter (Q1-Q4)",
            "release_month": "Release Month (1-12)",
            "documentation_url": "Documentation URL",
            "roadmap_title": "Roadmap Title (public display)",
            "roadmap_description": "Roadmap Description (public display)",
            "roadmap_image_url_1": "Roadmap Image URL 1 (optional)",
            "roadmap_image_url_2": "Roadmap Image URL 2 (optional)",
            "roadmap_image_url_3": "Roadmap Image URL 3 (optional)",
            "roadmap_image_url_4": "Roadmap Image URL 4 (optional)",
        }
        return labels.get(self.config_key, self.config_key)
```

**Validation Rules**:
- `config_key` must be one of the 13 defined configuration fields
- `field_id` must match pattern `customfield_\d{5,}` if `is_selected` is `true`
- Optional fields can have empty `field_id` if `is_selected` is `false`

**Relationships**:
- Created from user selecting a `CustomFieldMetadata` instance
- Multiple `FieldMapping` instances are collected into a `ProjectFieldConfiguration`

---

### 3. ProjectFieldConfiguration

**Purpose**: Complete custom field mapping for a single JIRA project, persisted to JSON configuration file.

**Source**: Aggregated from `FieldMapping` selections; validated against JSON schema

**Attributes**:

All attributes are custom field IDs (strings matching `customfield_\d{5,}`):

| Attribute | Required | Description | Example |
|-----------|----------|-------------|---------|
| `public_roadmap` | Yes | Field marking epic as public | `"customfield_14619"` |
| `roadmap_status` | Yes | Delivery status field | `"customfield_14621"` |
| `module` | Yes | Product module/area | `"customfield_14622"` |
| `release_year` | Yes | Release year | `"customfield_14623"` |
| `release_quarter` | Yes | Release quarter (Q1-Q4) | `"customfield_14624"` |
| `release_month` | Yes | Release month (1-12) | `"customfield_14625"` |
| `documentation_url` | Yes | Documentation URL | `"customfield_14626"` |
| `roadmap_title` | Yes | Public roadmap title | `"customfield_10101"` |
| `roadmap_description` | Yes | Public roadmap description | `"customfield_10102"` |
| `roadmap_image_url_1` | Yes* | First image URL | `"customfield_10103"` |
| `roadmap_image_url_2` | Yes* | Second image URL | `"customfield_10104"` |
| `roadmap_image_url_3` | Yes* | Third image URL | `"customfield_10105"` |
| `roadmap_image_url_4` | Yes* | Fourth image URL | `"customfield_10106"` |

**Note**: Image URL fields are required in schema for consistency but can be set to placeholder values (e.g., `"customfield_00000"`) if not used. Future enhancement may make these truly optional.

**Lifecycle**: Created by CLI command; persisted to `backend/config/jira_projects.json`; loaded at application startup; consumed by sync service at runtime.

**Python Implementation**:
```python
from dataclasses import dataclass, asdict
from typing import Dict

@dataclass
class ProjectFieldConfiguration:
    """Custom field mapping for a JIRA project."""

    public_roadmap: str
    roadmap_status: str
    module: str
    release_year: str
    release_quarter: str
    release_month: str
    documentation_url: str
    roadmap_title: str
    roadmap_description: str
    roadmap_image_url_1: str
    roadmap_image_url_2: str
    roadmap_image_url_3: str
    roadmap_image_url_4: str

    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_mappings(cls, mappings: list[FieldMapping]) -> "ProjectFieldConfiguration":
        """Create from list of field mappings."""
        mapping_dict = {m.config_key: m.field_id for m in mappings}
        return cls(**mapping_dict)

    def validate_all_fields_set(self) -> bool:
        """Check that all fields have valid custom field IDs."""
        import re
        pattern = re.compile(r'^customfield_\d{5,}$')
        for field_id in asdict(self).values():
            if not pattern.match(field_id):
                return False
        return True
```

**Validation Rules** (enforced by JSON schema):
- All attributes required (even if placeholder)
- All values must match pattern `^customfield_\d{5,}$`
- No additional attributes allowed (`additionalProperties: false`)

**Relationships**:
- Stored within `JiraProjectsConfig` under `projects` dictionary
- Key is project key (e.g., `"NEXUS"`), value is this configuration

---

### 4. JiraProjectsConfig

**Purpose**: Root configuration object containing mappings for all JIRA projects.

**Source**: Loaded from `backend/config/jira_projects.json`; updated by CLI commands; validated by `backend/config/jira_projects.schema.json`

**Attributes**:

| Attribute | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `version` | `str` | Yes | Configuration format version | `"1.0"` |
| `projects` | `dict[str, ProjectFieldConfiguration]` | Yes | Project key to field mapping | `{"NEXUS": {...}, "FLOW": {...}}` |

**Lifecycle**: Single instance per application; loaded at startup; updated by CLI; persisted to disk.

**JSON Structure**:
```json
{
  "version": "1.0",
  "projects": {
    "NEXUS": {
      "public_roadmap": "customfield_14619",
      "roadmap_status": "customfield_14621",
      "module": "customfield_14622",
      "release_year": "customfield_14623",
      "release_quarter": "customfield_14624",
      "release_month": "customfield_14625",
      "documentation_url": "customfield_14626",
      "roadmap_title": "customfield_10101",
      "roadmap_description": "customfield_10102",
      "roadmap_image_url_1": "customfield_10103",
      "roadmap_image_url_2": "customfield_10104",
      "roadmap_image_url_3": "customfield_10105",
      "roadmap_image_url_4": "customfield_10106"
    },
    "FLOW": {
      "public_roadmap": "customfield_15001",
      ...
    }
  }
}
```

**Python Implementation**:
```python
from dataclasses import dataclass
from typing import Dict

@dataclass
class JiraProjectsConfig:
    """Root configuration for all JIRA projects."""

    version: str
    projects: Dict[str, ProjectFieldConfiguration]

    def add_or_update_project(self, project_key: str, config: ProjectFieldConfiguration) -> None:
        """Add or update a project configuration."""
        self.projects[project_key] = config

    def get_project(self, project_key: str) -> Optional[ProjectFieldConfiguration]:
        """Get configuration for a specific project."""
        return self.projects.get(project_key)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "version": self.version,
            "projects": {
                key: config.to_dict()
                for key, config in self.projects.items()
            }
        }

    @classmethod
    def from_dict(cls, data: dict) -> "JiraProjectsConfig":
        """Create from dictionary (loaded from JSON)."""
        projects = {
            key: ProjectFieldConfiguration(**value)
            for key, value in data["projects"].items()
        }
        return cls(version=data["version"], projects=projects)
```

**Validation Rules** (enforced by JSON schema):
- `version` must match pattern `^\d+\.\d+$`
- `projects` must have at least 1 entry (`minProperties: 1`)
- Project keys must match pattern `^[A-Z][A-Z0-9]{1,9}$` (JIRA project key format)
- Each project value must be valid `ProjectFieldConfiguration`

**File Location**: `backend/config/jira_projects.json`

**Schema Location**: `backend/config/jira_projects.schema.json`

---

## State Transitions

### CLI Field Mapping Session Flow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. INITIALIZATION                                           │
│    Read JIRA_PROJECT_KEYS from environment                 │
│    Validate project key format                             │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. FIELD RETRIEVAL (per project)                           │
│    Call JIRA API /rest/api/3/field                         │
│    Filter custom fields (custom: true)                     │
│    Create CustomFieldMetadata instances                    │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. INTERACTIVE MAPPING (per config key)                    │
│    Display available fields to user                        │
│    Prompt for selection (or skip if optional)              │
│    Create FieldMapping instance                            │
│    Repeat for all 13 config keys                           │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. CONFIRMATION                                             │
│    Display all selected mappings                           │
│    Prompt user to confirm or cancel                        │
└─────────────────────────────────────────────────────────────┘
                           │
                 ┌─────────┴─────────┐
                 │                   │
            Confirm               Cancel
                 │                   │
                 ▼                   ▼
┌─────────────────────────────┐  [Exit without changes]
│ 5. PERSISTENCE              │
│    Load existing config     │
│    Update/add project       │
│    Validate against schema  │
│    Atomic write to file     │
└─────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────┐
│ 6. VERIFICATION             │
│    Reload config from file  │
│    Confirm valid JSON       │
│    Display success message  │
└─────────────────────────────┘
```

---

## Data Validation

### Field ID Format Validation

```python
import re

CUSTOM_FIELD_ID_PATTERN = re.compile(r'^customfield_\d{5,}$')

def is_valid_custom_field_id(field_id: str) -> bool:
    """Validate custom field ID format."""
    return bool(CUSTOM_FIELD_ID_PATTERN.match(field_id))
```

### Project Key Format Validation

```python
PROJECT_KEY_PATTERN = re.compile(r'^[A-Z][A-Z0-9]{1,9}$')

def is_valid_project_key(key: str) -> bool:
    """Validate JIRA project key format."""
    return bool(PROJECT_KEY_PATTERN.match(key))
```

### JSON Schema Validation

- Performed by `backend/app/services/config_loader.py::load_config()`
- Uses `jsonschema` library with `backend/config/jira_projects.schema.json`
- Validates structure, data types, required fields, patterns, and additional properties

---

## Error States

| Error Condition | Detection | Handling | Recovery |
|----------------|-----------|----------|----------|
| Invalid field ID selected | Pattern validation fails | Prompt user to select again | Re-prompt for same config key |
| Duplicate field ID selected | Check if ID already used | Warn user, allow or reject | Show warning, ask to confirm |
| Required field skipped | Optional check fails | Error message | Force selection for required fields |
| Config file corrupted | JSON parse error | Display error, create backup | Offer to recreate from scratch |
| Schema validation failure | jsonschema validation fails | Display validation errors | Fix manually or run CLI again |

---

## Persistence Format

**File**: `backend/config/jira_projects.json`

**Format**: JSON with 2-space indentation, trailing newline

**Access Pattern**:
- **Read**: Application startup (once) by `Config.load_project_config()`
- **Write**: CLI command execution (infrequent) by `flask jira map-fields`
- **Validation**: Every read by `config_loader.py`

**Concurrency**: No locking; last-write-wins (acceptable for administrative tool)

---

## Integration Points

### With Existing Models

**RoadmapItem** (`backend/app/models/roadmap.py`):
- Consumes custom field IDs from `ProjectFieldConfiguration`
- Uses `Config.get_project_custom_fields(project_key)` to get field IDs
- No changes to RoadmapItem model structure required

**Config** (`backend/app/config.py`):
- Loads `JiraProjectsConfig` at startup
- Provides `get_project_custom_fields(project_key)` method
- No schema changes required

### With Services

**JiraClient** (`backend/app/services/jira_client.py`):
- New method: `get_custom_fields(project_key: str) -> list[CustomFieldMetadata]`
- Calls JIRA API `/rest/api/3/field`
- Returns parsed field metadata for CLI display

**ConfigLoader** (`backend/app/services/config_loader.py`):
- Existing validation continues to work
- No changes needed (already validates against schema)

---

## Future Enhancements

1. **Versioned Configurations**: Track configuration history for rollback
2. **Field Usage Analytics**: Track which custom fields are actually populated in epics
3. **Auto-suggestions**: Fuzzy match field names to suggest likely mappings
4. **Bulk Import/Export**: Support exporting/importing configurations across environments
5. **Field Type Validation**: Warn if selected field type doesn't match expected type (e.g., selecting a date field for title)

---

## Summary

This data model provides a clear separation between:
- **Transient** CLI session data (`CustomFieldMetadata`, `FieldMapping`)
- **Persistent** configuration data (`ProjectFieldConfiguration`, `JiraProjectsConfig`)

The model supports the key workflows:
- Retrieving and displaying fields for user selection
- Interactive mapping with validation
- Atomic persistence to JSON configuration
- Schema-validated configuration loading

All entities have clear validation rules and lifecycle management, ensuring data integrity throughout the CLI interaction and persistence process.
