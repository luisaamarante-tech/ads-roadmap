# Data Model: JIRA Custom Fields Configuration

**Feature**: 003-jira-custom-fields
**Date**: December 26, 2025

## Overview

This document defines the data structures and relationships for JSON-based JIRA custom field configuration. The model supports per-project custom field mappings with validation and fallback behavior.

## Entity Definitions

### ProjectConfig

Represents the complete configuration file structure containing all project custom field mappings.

**Fields**:

| Field | Type | Required | Description | Validation |
|-------|------|----------|-------------|------------|
| `version` | string | Yes | Configuration schema version | Semantic version format (e.g., "1.0") |
| `projects` | dict[str, ProjectFieldMapping] | Yes | Project key to field mapping | At least 1 project required |

**Example**:
```json
{
  "version": "1.0",
  "projects": {
    "PROJ1": { ... },
    "PROJ2": { ... }
  }
}
```

**Validation Rules**:
- Version must match pattern: `^\d+\.\d+$`
- Projects dictionary cannot be empty
- Project keys must be valid JIRA project keys (uppercase alphanumeric, 2-10 chars)

**Relationships**:
- Contains multiple `ProjectFieldMapping` instances
- Loaded once at application startup
- Cached in memory for fast lookup

---

### ProjectFieldMapping

Represents the custom field ID mapping for a single JIRA project.

**Fields**:

| Field | Type | Required | Description | Validation |
|-------|------|----------|-------------|------------|
| `roadmap_title` | string | Yes | Custom field ID for public roadmap title | Must match `customfield_\d{5,}` |
| `roadmap_description` | string | Yes | Custom field ID for public roadmap description | Must match `customfield_\d{5,}` |
| `roadmap_image_url_1` | string | Yes | Custom field ID for first image URL | Must match `customfield_\d{5,}` |
| `roadmap_image_url_2` | string | Yes | Custom field ID for second image URL | Must match `customfield_\d{5,}` |
| `roadmap_image_url_3` | string | Yes | Custom field ID for third image URL | Must match `customfield_\d{5,}` |
| `roadmap_image_url_4` | string | Yes | Custom field ID for fourth image URL | Must match `customfield_\d{5,}` |

**Example**:
```json
{
  "roadmap_title": "customfield_10101",
  "roadmap_description": "customfield_10102",
  "roadmap_image_url_1": "customfield_10103",
  "roadmap_image_url_2": "customfield_10104",
  "roadmap_image_url_3": "customfield_10105",
  "roadmap_image_url_4": "customfield_10106"
}
```

**Validation Rules**:
- All 6 fields must be present (no optional fields)
- Field IDs must be unique within the project
- Field IDs must follow JIRA custom field format
- Field IDs must be valid integers after "customfield_" prefix

**Relationships**:
- Belongs to a `ProjectConfig`
- Referenced by project key (e.g., "PROJ1")
- Used by `JiraClient` to extract custom field values

---

### RoadmapItem (Enhanced)

Extended version of existing RoadmapItem dataclass to support custom fields and image URLs.

**New/Modified Fields**:

| Field | Type | Required | Description | Validation |
|-------|------|----------|-------------|------------|
| `title` | string | Yes | Display title (custom field or epic summary) | Max 200 chars |
| `description` | string | Yes | Display description (custom field or epic description) | Max 5000 chars |
| `images` | list[str] | No | List of image URLs (0-4 items) | Valid HTTP(S) URLs |

**Existing Fields** (unchanged):
- `id`: JIRA issue key
- `status`: DeliveryStatus enum
- `module`: Product module name
- `release_year`, `release_quarter`, `release_month`: Release timing
- `documentation_url`: Optional documentation link
- `last_synced_at`: Timestamp of last sync

**Field Sources**:

| Field | Primary Source | Fallback Source |
|-------|---------------|-----------------|
| `title` | `custom_field[roadmap_title]` | `epic.fields.summary` |
| `description` | `custom_field[roadmap_description]` | `epic.fields.description` |
| `images` | `custom_field[image_url_1..4]` | Empty list (no fallback) |

**Validation Rules**:
- `title`: Trimmed, non-empty after fallback
- `description`: Trimmed, non-empty after fallback
- `images`: Filter empty strings, validate URL format, max 4 items

**Serialization** (`to_dict()` output):
```json
{
  "id": "PROJ-123",
  "title": "Custom Roadmap Title",
  "description": "Custom roadmap description for public display",
  "status": "NOW",
  "module": "Platform",
  "moduleId": "platform",
  "releaseYear": 2025,
  "releaseQuarter": "Q1",
  "releaseMonth": 3,
  "images": [
    "https://example.com/image1.png",
    "https://example.com/image2.png"
  ],
  "documentationUrl": "https://docs.example.com",
  "lastSyncedAt": "2025-12-26T10:30:00Z"
}
```

**Relationships**:
- Sources data from JIRA epic via `JiraClient`
- Uses `ProjectFieldMapping` to determine which custom fields to extract
- Serialized to JSON for API responses

---

### CustomFieldDefinition

Represents a JIRA custom field configuration for creation via CLI.

**Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Human-readable field name |
| `description` | string | Yes | Field description in JIRA |
| `type` | string | Yes | JIRA field type key |
| `searcherKey` | string | Yes | JIRA searcher key |
| `config_key` | string | Yes | Key in ProjectFieldMapping |

**Predefined Field Configurations**:

```python
CUSTOM_FIELDS = [
    {
        "name": "Roadmap Title",
        "description": "Public-facing title for roadmap display",
        "type": "com.atlassian.jira.plugin.system.customfieldtypes:textfield",
        "searcherKey": "com.atlassian.jira.plugin.system.customfieldtypes:textsearcher",
        "config_key": "roadmap_title"
    },
    {
        "name": "Roadmap Description",
        "description": "Public-facing description for roadmap display",
        "type": "com.atlassian.jira.plugin.system.customfieldtypes:textarea",
        "searcherKey": "com.atlassian.jira.plugin.system.customfieldtypes:textsearcher",
        "config_key": "roadmap_description"
    },
    {
        "name": "Roadmap Image URL 1",
        "description": "First image URL for roadmap display",
        "type": "com.atlassian.jira.plugin.system.customfieldtypes:textfield",
        "searcherKey": "com.atlassian.jira.plugin.system.customfieldtypes:textsearcher",
        "config_key": "roadmap_image_url_1"
    },
    # ... (Image URL 2, 3, 4 follow same pattern)
]
```

**Usage**:
- Used by CLI command to create fields in JIRA
- Not persisted (configuration constants in code)
- Ensures consistent field naming across projects

---

## Relationships Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      ProjectConfig                          │
│  • version: string                                          │
│  • projects: dict[str, ProjectFieldMapping]                 │
└───────────────────────────┬─────────────────────────────────┘
                            │ 1:N
                            │
            ┌───────────────┴────────────────┐
            │                                │
┌───────────▼────────────────┐   ┌──────────▼──────────────┐
│  ProjectFieldMapping       │   │  ProjectFieldMapping    │
│  (PROJ1)                   │   │  (PROJ2)                │
│  • roadmap_title           │   │  • roadmap_title        │
│  • roadmap_description     │   │  • roadmap_description  │
│  • roadmap_image_url_1..4  │   │  • roadmap_image_url_1..4│
└────────────┬───────────────┘   └──────────┬──────────────┘
             │                              │
             │ used by                      │ used by
             │                              │
┌────────────▼──────────────────────────────▼─────────────────┐
│                      JiraClient                              │
│  • extract_roadmap_item(issue) → RoadmapItem                │
│  • Looks up project's custom field mapping                  │
│  • Extracts custom field values from JIRA issue             │
│  • Falls back to default epic fields if needed              │
└──────────────────────────┬───────────────────────────────────┘
                           │ produces
                           │
                ┌──────────▼──────────────┐
                │   RoadmapItem           │
                │   • title (custom)      │
                │   • description (custom)│
                │   • images (0-4 URLs)   │
                │   • ... other fields    │
                └─────────────────────────┘
```

## Data Flow

### Configuration Loading Flow

```
Application Startup
        │
        ▼
┌─────────────────────────┐
│ Config.load_config()    │
│ • Read jira_projects.json
│ • Validate JSON syntax  │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ Validate against schema │
│ • Check required fields │
│ • Validate field ID fmt │
└───────────┬─────────────┘
            │
      Valid │ Invalid
            ├─────────────────────┐
            ▼                     ▼
┌─────────────────────┐  ┌────────────────────┐
│ Cache in memory     │  │ Log warning        │
│ • ProjectConfig obj │  │ Use env var config │
└─────────────────────┘  └────────────────────┘
```

### Field Extraction Flow

```
JiraClient.extract_roadmap_item(issue)
        │
        ▼
┌──────────────────────────────┐
│ Get project key from issue   │
│ project = issue.fields.project.key
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│ Lookup project config        │
│ mapping = config.projects[project]
└──────────────┬───────────────┘
               │
         Found │ Not Found
               ├─────────────────────┐
               ▼                     ▼
┌──────────────────────┐  ┌──────────────────────┐
│ Extract custom fields│  │ Use default fields   │
│ • Get custom field IDs│ │ • title = summary    │
│ • Extract values     │  │ • desc = description │
└──────────┬───────────┘  └──────────┬───────────┘
           │                         │
           ▼                         │
┌──────────────────────┐            │
│ Validate & fallback  │            │
│ • Check if empty     │            │
│ • Use default if so  │            │
└──────────┬───────────┘            │
           │                        │
           └────────┬───────────────┘
                    │
                    ▼
         ┌────────────────────┐
         │ Create RoadmapItem │
         │ • title (resolved) │
         │ • description      │
         │ • images (0-4)     │
         └────────────────────┘
```

### CLI Field Creation Flow

```
flask jira setup-fields PROJ1
        │
        ▼
┌──────────────────────────────┐
│ Validate authentication      │
│ • Check JIRA credentials     │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│ Get Epic issue type ID       │
│ GET /rest/api/3/issuetype    │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│ Check for existing fields    │
│ GET /rest/api/3/field        │
│ • Filter by name             │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│ Create missing fields        │
│ POST /rest/api/3/field       │
│ • Loop through 6 fields      │
│ • Skip if exists             │
│ • Show progress              │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│ Update config file           │
│ • Load current config        │
│ • Add/update project entry   │
│ • Write back to JSON         │
└──────────────┬───────────────┘
               │
               ▼
        Display summary
        • Fields created
        • Config updated
```

## Storage Schema

### JSON Configuration File Schema

Location: `backend/config/jira_projects.json`

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["version", "projects"],
  "properties": {
    "version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+$",
      "description": "Configuration format version"
    },
    "projects": {
      "type": "object",
      "minProperties": 1,
      "patternProperties": {
        "^[A-Z][A-Z0-9]{1,9}$": {
          "type": "object",
          "required": [
            "roadmap_title",
            "roadmap_description",
            "roadmap_image_url_1",
            "roadmap_image_url_2",
            "roadmap_image_url_3",
            "roadmap_image_url_4"
          ],
          "properties": {
            "roadmap_title": {
              "type": "string",
              "pattern": "^customfield_\\d{5,}$"
            },
            "roadmap_description": {
              "type": "string",
              "pattern": "^customfield_\\d{5,}$"
            },
            "roadmap_image_url_1": {
              "type": "string",
              "pattern": "^customfield_\\d{5,}$"
            },
            "roadmap_image_url_2": {
              "type": "string",
              "pattern": "^customfield_\\d{5,}$"
            },
            "roadmap_image_url_3": {
              "type": "string",
              "pattern": "^customfield_\\d{5,}$"
            },
            "roadmap_image_url_4": {
              "type": "string",
              "pattern": "^customfield_\\d{5,}$"
            }
          },
          "additionalProperties": false
        }
      },
      "additionalProperties": false
    }
  },
  "additionalProperties": false
}
```

## State Transitions

### Configuration Lifecycle

```
[Nonexistent]
     │
     │ CLI: setup-fields
     ▼
[Initial Project Added]
     │
     │ CLI: setup-fields (different project)
     ▼
[Multiple Projects]
     │
     │ Manual edit / CLI update
     ▼
[Modified]
     │
     │ App restart / reload
     ▼
[Revalidated & Cached]
```

**State Rules**:
- Config file is **immutable** at runtime (no hot-reload in v1)
- CLI command can **create** or **update** project entries
- Application **reads** config on startup only
- Changes require **application restart** to take effect

### Field Value Resolution

```
Extract Epic from JIRA
     │
     ▼
Check project in config?
     │
     ├─ Yes ──────────────────┐
     │                        │
     ▼                        ▼
Get custom field IDs    Use default fields
     │                        │
     ▼                        │
Extract custom values         │
     │                        │
     ▼                        │
Values empty? ───Yes──────────┤
     │ No                     │
     │                        │
     └────────┬───────────────┘
              │
              ▼
       Use title/description
       (custom or fallback)
```

## Validation Rules Summary

### ProjectConfig Validation

- ✅ Version is semantic version string
- ✅ At least 1 project exists
- ✅ Project keys match JIRA format (2-10 uppercase alphanumeric)
- ✅ No duplicate project keys

### ProjectFieldMapping Validation

- ✅ All 6 required fields present
- ✅ Field IDs match `customfield_\d{5,}` pattern
- ✅ No duplicate field IDs within project
- ✅ Field IDs are valid (numeric portion parseable as integer)

### RoadmapItem Validation

- ✅ Title non-empty (post-fallback)
- ✅ Description non-empty (post-fallback)
- ✅ Title max 200 characters
- ✅ Description max 5000 characters
- ✅ Images are valid HTTP(S) URLs
- ✅ Images list max 4 items
- ✅ Empty image URLs filtered out

## Error Handling

### Configuration Errors

| Error Scenario | Handling Strategy | Impact |
|----------------|-------------------|--------|
| File not found | Log warning, use env vars | Backward compatible |
| Invalid JSON syntax | Log warning, use env vars | Graceful degradation |
| Schema violation | Log warning, use env vars | Partial functionality |
| Invalid field ID format | Log warning per project | Project skipped |

### Runtime Errors

| Error Scenario | Handling Strategy | Impact |
|----------------|-------------------|--------|
| Project not in config | Use default fields | Silent fallback |
| Custom field value empty | Use default field value | Automatic fallback |
| Invalid image URL | Skip that image | Partial image list |
| All images invalid | Return empty list | No images shown |

### CLI Command Errors

| Error Scenario | Handling Strategy | Impact |
|----------------|-------------------|--------|
| Authentication failure | Exit with error message | Command fails |
| Project not found | Exit with error message | Command fails |
| Field creation fails | Rollback, exit with error | Command fails |
| Config write fails | Exit with error message | Fields created but not saved |

## Performance Characteristics

### Configuration Loading

- **Time Complexity**: O(1) - single file read
- **Space Complexity**: O(n) where n = number of projects
- **Cache Duration**: Application lifetime (until restart)

### Field Lookup

- **Time Complexity**: O(1) - dictionary lookup by project key
- **Space Complexity**: O(1) - single reference
- **Frequency**: Once per epic during sync

### Field Extraction

- **Time Complexity**: O(1) - direct field access + O(4) URL validation
- **Space Complexity**: O(1) - fixed field count
- **Frequency**: Once per epic during sync

## Data Constraints

### Size Limits

- **Max projects**: 1000 (reasonable for enterprise)
- **Max config file size**: ~100 KB (1000 projects × 100 bytes)
- **Max title length**: 200 characters
- **Max description length**: 5000 characters
- **Max images per item**: 4 URLs
- **Max image URL length**: 2048 characters (HTTP spec limit)

### Format Constraints

- **Project key**: 2-10 uppercase alphanumeric characters
- **Field ID**: `customfield_` + 5+ digit number
- **Version**: `major.minor` format (e.g., "1.0")
- **Image URL**: HTTP(S) protocol, valid URL format
