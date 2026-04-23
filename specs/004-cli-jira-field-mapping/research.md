# Research: CLI JIRA Custom Field Retrieval and Mapping

**Feature**: 004-cli-jira-field-mapping
**Date**: December 29, 2025
**Phase**: 0 - Research & Technical Decisions

## Overview

This document captures technical research and decisions for implementing CLI commands that retrieve JIRA custom fields and provide interactive mapping to the JSON configuration file. The research focuses on CLI interaction patterns, JIRA API capabilities with read-only permissions, and robust error handling.

## Research Areas

### 1. JIRA REST API v3 - Custom Field Retrieval (Read-Only Access)

**Research Question**: What JIRA API endpoints are available for retrieving custom fields without admin permissions?

**Decision**: Use `/rest/api/3/field` endpoint with basic authentication

**Rationale**:
- The `/rest/api/3/field` endpoint returns all fields (system and custom) visible to the authenticated user
- Does NOT require JIRA admin permissions - only requires valid user credentials with project access
- Returns field metadata including: `id`, `name`, `description`, `custom` (boolean), `schema` (field type)
- Can be filtered by checking if `custom: true` in response to isolate custom fields
- Provides `searcherKey` which indicates the field's data type and search behavior

**API Response Structure**:
```json
[
  {
    "id": "customfield_10001",
    "name": "Roadmap Title",
    "description": "Public-facing title for roadmap",
    "custom": true,
    "schema": {
      "type": "string",
      "custom": "com.atlassian.jira.plugin.system.customfieldtypes:textfield",
      "customId": 10001
    }
  }
]
```

**Alternative Considered**: `/rest/api/3/field/search` with pagination
- **Rejected**: More complex pagination handling; `/rest/api/3/field` returns all fields in one call (typically <100 fields even in large instances)

**Implementation Notes**:
- Filter by Epic issue type: Check field contexts via `/rest/api/3/field/{fieldId}/context` if needed to verify field is available on Epics
- However, simpler approach: Retrieve all custom fields, display all to user, let them select (wrong selections will be caught during validation)
- Cache field list per project during single CLI session to avoid repeated API calls

**References**:
- [JIRA Cloud REST API - Get fields](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-fields/#api-rest-api-3-field-get)
- Existing implementation in `backend/app/cli/jira_setup.py::detect_existing_fields()` line 106-141

---

### 2. Interactive CLI Prompts with Click

**Research Question**: How to implement user-friendly interactive field selection in Click CLI commands?

**Decision**: Use Click's built-in `click.prompt()` with numbered menus and validation

**Rationale**:
- Click is already a dependency (`backend/app/cli/jira_setup.py` uses Click extensively)
- `click.prompt()` supports type validation, default values, and custom validation functions
- `click.Choice()` type provides built-in menu-style selection for predefined options
- Can display field list with numbers, then prompt for number selection (simpler than third-party libraries)

**Interaction Pattern**:
```python
# Display available fields
click.echo("Available custom fields for project PROJ1:")
for idx, field in enumerate(available_fields, start=1):
    click.echo(f"  {idx}. {field['name']} ({field['id']})")
click.echo(f"  {len(available_fields) + 1}. Skip this field")

# Prompt for selection
selection = click.prompt(
    "Select field for Roadmap Title",
    type=click.IntRange(1, len(available_fields) + 1),
    default=len(available_fields) + 1  # Default to "skip"
)
```

**Alternative Considered**: `inquirer` or `questionary` libraries for rich interactive menus
- **Rejected**: Additional dependencies; Click's approach is sufficient and consistent with existing CLI style
- **Benefit of alternatives**: Better visual menus with arrow key navigation
- **Why not needed**: CLI tool used infrequently by admins; simplicity > visual polish

**Implementation Notes**:
- Display field name and ID together for transparency
- Allow "skip" option for optional fields (image URLs)
- Confirm selections before writing to config file
- Support `--non-interactive` flag for future automation (accept defaults or fail with error)

**References**:
- [Click Documentation - Prompts](https://click.palletsprojects.com/en/8.1.x/prompts/)
- Existing usage: `backend/app/cli/jira_setup.py` line 254-274 (`@click.option`, `@click.argument`)

---

### 3. Environment Variable Parsing for Multiple Project Keys

**Research Question**: How to robustly parse comma-separated or space-separated project keys from `JIRA_PROJECT_KEYS`?

**Decision**: Use existing `Config.get_project_keys()` method with enhanced validation

**Rationale**:
- Already implemented in `backend/app/config.py` line 40-44
- Handles comma-separated keys, strips whitespace, filters empty strings
- Returns `list[str]` which is easy to iterate over

**Enhancement Needed**: Add validation for JIRA project key format (2-10 uppercase alphanumeric characters starting with letter)

**Validation Pattern**:
```python
import re

PROJECT_KEY_PATTERN = re.compile(r'^[A-Z][A-Z0-9]{1,9}$')

def validate_project_key(key: str) -> bool:
    """Validate JIRA project key format."""
    return bool(PROJECT_KEY_PATTERN.match(key))
```

**Error Handling**:
- Invalid keys: Warn and skip, continue processing other keys
- Empty `JIRA_PROJECT_KEYS`: Error and exit with helpful message
- Non-existent project: JIRA API will return 404, catch and report clearly

**Alternative Considered**: Support `JIRA_PROJECT_KEYS` as JSON array
- **Rejected**: Breaks backward compatibility; comma-separated is simpler for shell environment variables

**References**:
- [JIRA Project Key Constraints](https://support.atlassian.com/jira-cloud-administration/docs/what-is-a-jira-project/#project-keys)
- Existing implementation: `backend/app/config.py::get_project_keys()`

---

### 4. JSON Configuration File Management

**Research Question**: How to safely update JSON configuration file while preserving existing projects and handling concurrent access?

**Decision**: Read-modify-write with atomic file replacement using temporary file + rename

**Rationale**:
- Python's `json` module provides robust read/write capabilities
- Atomic file operations prevent corruption if CLI crashes mid-write
- Preserve existing project configurations not being updated in this CLI session

**Safe Update Pattern**:
```python
import json
import tempfile
import shutil
from pathlib import Path

def atomic_update_config(config_path: Path, project_key: str, field_mappings: dict) -> bool:
    """Atomically update configuration file with new project mapping."""
    # Read existing config
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = json.load(f)
    else:
        config = {"version": "1.0", "projects": {}}

    # Update specific project
    config["projects"][project_key] = field_mappings

    # Write to temporary file
    temp_fd, temp_path = tempfile.mkstemp(dir=config_path.parent, text=True)
    try:
        with os.fdopen(temp_fd, 'w') as temp_file:
            json.dump(config, temp_file, indent=2)
            temp_file.write('\n')  # Trailing newline

        # Atomic rename (replaces original)
        shutil.move(temp_path, config_path)
        return True
    except Exception:
        # Clean up temp file on error
        Path(temp_path).unlink(missing_ok=True)
        raise
```

**Validation After Write**:
- Load updated config and validate against JSON schema (`jira_projects.schema.json`)
- Use existing `config_loader.py::load_config()` function which already validates schema

**Concurrency Consideration**:
- CLI tool is administrative, expected single-user usage
- No file locking needed for this use case
- If multiple CLI runs happen simultaneously, last-write-wins (acceptable for admin tool)

**Alternative Considered**: Database-backed configuration
- **Rejected**: Over-engineering for simple key-value storage; file-based is easier to version control and deploy

**References**:
- Python `tempfile` module: [Docs](https://docs.python.org/3/library/tempfile.html)
- Existing schema validation: `backend/app/services/config_loader.py` line 50-70

---

### 5. Error Handling and User Feedback Patterns

**Research Question**: How to provide clear error messages and recovery guidance for common failure scenarios?

**Decision**: Structured error handling with actionable messages and exit codes

**Error Categories and Handling**:

| Error Category | Detection | User Message | Exit Code | Recovery Action |
|----------------|-----------|--------------|-----------|-----------------|
| Missing environment variable | `JIRA_PROJECT_KEYS` empty | "Environment variable JIRA_PROJECT_KEYS is not set. Example: export JIRA_PROJECT_KEYS='PROJ1,PROJ2'" | 1 | Set environment variable |
| Authentication failure | JIRA API 401/403 | "JIRA authentication failed. Verify JIRA_EMAIL and JIRA_API_TOKEN are correct." | 2 | Check credentials |
| Network/API unavailable | Connection timeout, 500+ errors | "Cannot connect to JIRA API. Check network connection and JIRA_BASE_URL. Details: {error}" | 3 | Check network/URL |
| Invalid project key | JIRA API 404 for project | "Project 'XYZ' not found in JIRA or not accessible. Skipping." | 0 | Continue with other projects |
| Config file write error | Permission denied on file write | "Cannot write to {config_path}. Check file permissions." | 4 | Fix file permissions |
| JSON schema validation failure | Schema validation error after write | "Updated configuration is invalid: {validation_error}. Config not saved." | 5 | Report bug (should not happen) |
| Rate limit exceeded | JIRA API 429 | "JIRA API rate limit exceeded. Wait 60 seconds and try again." | 6 | Wait and retry |

**Implementation Pattern**:
```python
class JiraCliError(Exception):
    """Base exception for JIRA CLI errors."""
    def __init__(self, message: str, exit_code: int, recovery_hint: str = ""):
        self.message = message
        self.exit_code = exit_code
        self.recovery_hint = recovery_hint
        super().__init__(self.message)

# Usage in CLI command
try:
    # ... operation ...
except JiraCliError as e:
    click.secho(f"✗ Error: {e.message}", fg="red")
    if e.recovery_hint:
        click.echo(f"💡 {e.recovery_hint}")
    sys.exit(e.exit_code)
```

**Progress Indicators**:
- Use Click's `click.progressbar()` for multi-project processing
- Use spinner or "..." pattern for API calls: `click.echo("Retrieving fields...", nl=False)` → `click.echo(" ✓")`
- Display summary at end with counts and next steps

**Rationale**:
- Structured approach makes errors debuggable
- Exit codes enable scripting/automation
- Recovery hints reduce support burden

**Alternative Considered**: Verbose/debug logging mode
- **Also implement**: Add `--verbose` flag that enables detailed logging to help debug API issues

**References**:
- [Click Documentation - Utilities](https://click.palletsprojects.com/en/8.1.x/utils/)
- Existing error handling: `backend/app/cli/jira_setup.py` line 179-208 (field creation error handling)

---

### 6. CLI Command Structure and Naming

**Research Question**: Should we modify existing `setup-fields` command or create new commands?

**Decision**: Create new CLI commands under `flask jira` group: `map-fields` and `validate-config`

**Rationale**:
- Clear separation of concerns: `setup-fields` creates fields (requires admin), `map-fields` retrieves and maps (read-only)
- Allows both workflows to coexist (some orgs may have admin access, others don't)
- Follows Click's command group pattern already established
- `validate-config` as separate command enables checking configurations independently

**Command Signatures**:
```bash
# Map fields for specific project (interactive)
flask jira map-fields PROJECT_KEY

# Map fields for all projects in JIRA_PROJECT_KEYS
flask jira map-fields --all

# Non-interactive mode (uses defaults or fails)
flask jira map-fields PROJECT_KEY --non-interactive

# Validate existing configuration
flask jira validate-config

# Validate specific project
flask jira validate-config PROJECT_KEY
```

**Backward Compatibility**:
- Keep existing `setup-fields` command unchanged (deprecated but functional)
- Add deprecation warning: "Note: This command requires JIRA admin permissions. Use 'map-fields' if you only have read access."

**Alternative Considered**: Subcommands `flask jira fields map` and `flask jira fields validate`
- **Rejected**: Adds extra nesting level; current flat structure is simpler

**References**:
- [Click Documentation - Commands and Groups](https://click.palletsprojects.com/en/8.1.x/commands/)
- Existing CLI group: `backend/app/cli/jira_setup.py` line 248-251 (`@click.group("jira")`)

---

### 7. Field Filtering and Type Detection

**Research Question**: How to identify which custom fields are relevant for roadmap configuration?

**Decision**: Display all custom fields, let user select; optionally filter by text-type fields

**Rationale**:
- Cannot reliably auto-detect field purpose from name alone (fields may have org-specific names)
- User knows their JIRA configuration best - provide full list for informed selection
- Optional filter for text fields to reduce noise (roadmap fields are all text-based)

**Filtering Logic**:
```python
def is_text_field(field_schema: dict) -> bool:
    """Check if custom field is text-based (suitable for roadmap data)."""
    text_field_types = [
        "com.atlassian.jira.plugin.system.customfieldtypes:textfield",     # Single-line text
        "com.atlassian.jira.plugin.system.customfieldtypes:textarea",      # Multi-line text
        "com.atlassian.jira.plugin.system.customfieldtypes:url",           # URL field
        "com.atlassian.jira.plugin.system.customfieldtypes:readonlyfield", # Read-only text
    ]
    custom_type = field_schema.get("custom", "")
    return custom_type in text_field_types
```

**CLI Option**:
```bash
# Show only text fields (default)
flask jira map-fields PROJECT_KEY

# Show all custom fields (including dates, numbers, etc.)
flask jira map-fields PROJECT_KEY --show-all-types
```

**Display Format**:
```
Available custom fields for project PROJ1:
  1. Roadmap Title (customfield_10101) - Text Field (single line)
  2. Roadmap Description (customfield_10102) - Text Field (multi-line)
  3. Image URL 1 (customfield_10103) - URL
  ...
  8. Skip this field
```

**Alternative Considered**: Fuzzy name matching (e.g., if field name contains "title" → suggest for roadmap_title)
- **Maybe later**: Could add as helpful suggestions, but not auto-select (too risky)

**References**:
- [JIRA Custom Field Types](https://support.atlassian.com/jira-cloud-administration/docs/custom-field-types/)

---

## Technical Decisions Summary

| Decision Area | Choice | Key Benefit |
|---------------|--------|-------------|
| **JIRA API Endpoint** | `/rest/api/3/field` | Works with read-only permissions |
| **Interactive Prompts** | Click's `click.prompt()` | No additional dependencies |
| **Project Key Parsing** | Existing `Config.get_project_keys()` | Reuses working implementation |
| **Config File Updates** | Atomic write with temp file | Prevents corruption |
| **Error Handling** | Structured exceptions with exit codes | Actionable feedback |
| **CLI Commands** | New `map-fields` and `validate-config` | Clear separation from admin commands |
| **Field Filtering** | Optional text-only filter | User controls what they see |

## Implementation Sequence

1. **Phase 1a - API Integration**:
   - Extend `backend/app/services/jira_client.py` with `get_custom_fields()` method
   - Add field type detection helpers
   - Unit tests with mocked API responses

2. **Phase 1b - CLI Commands**:
   - Implement `map-fields` command in `backend/app/cli/jira_setup.py`
   - Interactive prompts for each field mapping
   - Atomic config file updates
   - Unit tests with `click.testing.CliRunner`

3. **Phase 1c - Validation**:
   - Implement `validate-config` command
   - Check each field ID against JIRA API
   - Report missing or inaccessible fields
   - Unit and integration tests

4. **Phase 1d - Polish**:
   - Error handling for all failure scenarios
   - Progress indicators and user feedback
   - Documentation in quickstart.md

## Open Questions

None - all technical unknowns resolved through research.

## References

- [JIRA Cloud REST API v3 Documentation](https://developer.atlassian.com/cloud/jira/platform/rest/v3/)
- [Click CLI Framework](https://click.palletsprojects.com/)
- [Python JSON Module](https://docs.python.org/3/library/json.html)
- Existing codebase: `backend/app/cli/jira_setup.py`, `backend/app/services/jira_client.py`
