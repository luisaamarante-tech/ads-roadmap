# CLI Command Specifications

**Feature**: 004-cli-jira-field-mapping
**Date**: December 29, 2025
**Version**: 1.0

## Overview

This document specifies the CLI commands for retrieving JIRA custom fields and mapping them to the roadmap configuration. All commands are part of the `flask jira` command group.

---

## Command: `flask jira map-fields`

### Purpose

Retrieve custom fields from a JIRA project and interactively map them to roadmap configuration keys, then update the JSON configuration file.

### Synopsis

```bash
flask jira map-fields PROJECT_KEY [OPTIONS]
flask jira map-fields --all [OPTIONS]
```

### Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `PROJECT_KEY` | string | Yes* | JIRA project key (e.g., "NEXUS", "FLOW") |

*Required unless `--all` flag is used

### Options

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--all` | `-a` | flag | false | Map fields for all projects in JIRA_PROJECT_KEYS |
| `--show-all-types` | - | flag | false | Show all custom field types (default: text fields only) |
| `--non-interactive` | - | flag | false | Use defaults or fail (for automation) |
| `--dry-run` | - | flag | false | Show what would be updated without writing |
| `--verbose` | `-v` | flag | false | Enable detailed logging |

### Environment Variables Required

- `JIRA_BASE_URL`: JIRA instance URL (e.g., "https://company.atlassian.net")
- `JIRA_EMAIL`: User email for authentication
- `JIRA_API_TOKEN`: API token for authentication
- `JIRA_PROJECT_KEYS`: Comma-separated project keys (required for `--all` flag)

### Interactive Prompts

For each configuration key (13 total):

```
Select custom field for {config_key_label}:
  1. Field Name 1 (customfield_10001) - Text Field (single line)
  2. Field Name 2 (customfield_10002) - Text Field (multi-line)
  ...
  N. Skip this field

Enter selection [1-N]: _
```

After all selections:

```
Confirm field mappings for project {PROJECT_KEY}:

  Roadmap Title: Field Name 1 (customfield_10001)
  Roadmap Description: Field Name 2 (customfield_10002)
  ...

Save configuration? [Y/n]: _
```

### Behavior

1. **Authentication Check**:
   - Validate JIRA credentials by calling `/rest/api/3/myself`
   - Exit with code 2 if authentication fails

2. **Field Retrieval**:
   - Call `/rest/api/3/field` to get all fields
   - Filter to custom fields only (`custom: true`)
   - Optionally filter to text-type fields (default)
   - Display count of fields found

3. **Interactive Mapping**:
   - For each of 13 config keys, display available fields
   - Prompt user to select by number or skip
   - Validate selection is within range
   - Allow optional fields to be skipped

4. **Confirmation**:
   - Display summary of all selections
   - Prompt to confirm before writing
   - Allow cancellation (exit code 0, no changes)

5. **Configuration Update**:
   - Load existing `jira_projects.json` or create new
   - Update/add project entry with selected mappings
   - Validate against JSON schema
   - Atomic write using temporary file + rename
   - Verify file was written correctly

6. **Summary Display**:
   - Show success message with file path
   - Display next steps (validate, test sync)

### Exit Codes

| Code | Meaning | Example Scenario |
|------|---------|------------------|
| 0 | Success | Configuration updated successfully |
| 1 | Invalid usage | Missing PROJECT_KEY argument |
| 2 | Authentication failure | Invalid JIRA credentials |
| 3 | Network/API error | Cannot connect to JIRA |
| 4 | File I/O error | Cannot write to config file |
| 5 | Validation error | Schema validation failed |

### Examples

**Map fields for single project**:
```bash
flask jira map-fields NEXUS
```

**Map fields for all configured projects**:
```bash
export JIRA_PROJECT_KEYS="NEXUS,FLOW,CONNECT"
flask jira map-fields --all
```

**Show all field types (not just text)**:
```bash
flask jira map-fields NEXUS --show-all-types
```

**Dry run (preview changes)**:
```bash
flask jira map-fields NEXUS --dry-run
```

**Verbose output for debugging**:
```bash
flask jira map-fields NEXUS --verbose
```

### Error Messages

| Scenario | Message | Recovery Hint |
|----------|---------|---------------|
| Missing PROJECT_KEY | `Error: PROJECT_KEY argument is required` | `Provide a project key or use --all flag` |
| Empty JIRA_PROJECT_KEYS with --all | `Error: JIRA_PROJECT_KEYS environment variable is not set` | `Export JIRA_PROJECT_KEYS with comma-separated project keys` |
| Invalid project key format | `Warning: Invalid project key format 'abc'. Skipping.` | `Use uppercase alphanumeric keys (e.g., PROJ1)` |
| Authentication failure | `Error: JIRA authentication failed` | `Verify JIRA_EMAIL and JIRA_API_TOKEN are correct` |
| Network error | `Error: Cannot connect to JIRA API at {url}` | `Check network connection and JIRA_BASE_URL` |
| Project not found | `Error: Project 'XYZ' not found or not accessible` | `Verify project key and user permissions` |
| No custom fields found | `Warning: No custom fields found for project {key}` | `Create custom fields in JIRA or use different project` |
| Config file not writable | `Error: Cannot write to {path}` | `Check file permissions and directory exists` |
| Schema validation failure | `Error: Configuration validation failed: {details}` | `Report bug (should not happen with interactive mode)` |

### Output Format

**Standard output (success)**:
```
Retrieving custom fields for project NEXUS...
✓ Found 45 custom fields (12 text fields)

Mapping custom fields to configuration...

Select custom field for Roadmap Title (public display):
  1. Epic Title (customfield_10001) - Text Field (single line)
  2. Public Title (customfield_10101) - Text Field (single line)
  ...
  13. Skip this field

Enter selection [1-13]: 2

[... repeat for all 13 fields ...]

Confirm field mappings for project NEXUS:

  Public Roadmap:        Show in Roadmap (customfield_14619)
  Roadmap Status:        Delivery Status (customfield_14621)
  Module:                Product Module (customfield_14622)
  Release Year:          Year (customfield_14623)
  Release Quarter:       Quarter (customfield_14624)
  Release Month:         Month (customfield_14625)
  Documentation URL:     Docs Link (customfield_14626)
  Roadmap Title:         Public Title (customfield_10101)
  Roadmap Description:   Public Description (customfield_10102)
  Roadmap Image URL 1:   Image 1 (customfield_10103)
  Roadmap Image URL 2:   Image 2 (customfield_10104)
  Roadmap Image URL 3:   (skipped)
  Roadmap Image URL 4:   (skipped)

Save configuration? [Y/n]: y

Updating configuration file...
✓ Configuration updated successfully

================================================================
Summary
================================================================
Project: NEXUS
Fields Mapped: 11 of 13
Configuration File: backend/config/jira_projects.json

Next steps:
  1. Run validation: flask jira validate-config NEXUS
  2. Test sync: flask sync run --once
  3. Check roadmap display
```

---

## Command: `flask jira validate-config`

### Purpose

Validate that custom field IDs in the JSON configuration file exist and are accessible in JIRA.

### Synopsis

```bash
flask jira validate-config [PROJECT_KEY] [OPTIONS]
```

### Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `PROJECT_KEY` | string | No | JIRA project key to validate (validates all if omitted) |

### Options

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--fix` | - | flag | false | Attempt to auto-fix issues by re-prompting |
| `--verbose` | `-v` | flag | false | Show detailed validation checks |

### Environment Variables Required

- `JIRA_BASE_URL`: JIRA instance URL
- `JIRA_EMAIL`: User email for authentication
- `JIRA_API_TOKEN`: API token for authentication

### Behavior

1. **Configuration Load**:
   - Load `jira_projects.json`
   - Validate JSON schema compliance
   - Exit with error if file missing or invalid

2. **Field Validation** (per project):
   - For each custom field ID in configuration:
     - Call `/rest/api/3/field` to verify field exists
     - Check field is accessible with current credentials
     - Verify field is custom (not system field)
   - Collect validation results

3. **Result Reporting**:
   - Display validation status for each field
   - Summarize counts: valid, invalid, inaccessible
   - Suggest actions for failed validations

4. **Auto-fix** (if `--fix` flag):
   - For invalid field IDs, prompt user to select replacement
   - Update configuration with corrected mappings
   - Re-validate after fixes

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All fields valid |
| 1 | Some fields invalid (details in output) |
| 2 | Authentication failure |
| 3 | Network/API error |
| 4 | Config file not found or invalid |

### Examples

**Validate all projects**:
```bash
flask jira validate-config
```

**Validate specific project**:
```bash
flask jira validate-config NEXUS
```

**Validate with detailed output**:
```bash
flask jira validate-config --verbose
```

**Validate and auto-fix issues**:
```bash
flask jira validate-config NEXUS --fix
```

### Output Format

**All fields valid**:
```
Validating configuration for all projects...

Project: NEXUS (13 fields)
  ✓ public_roadmap (customfield_14619)
  ✓ roadmap_status (customfield_14621)
  ...
  ✓ roadmap_image_url_4 (customfield_10106)

Project: FLOW (13 fields)
  ✓ public_roadmap (customfield_15001)
  ...

================================================================
Validation Summary
================================================================
Projects Validated: 2
Fields Validated: 26
Valid: 26 ✓
Invalid: 0
Inaccessible: 0

Configuration is valid and ready to use.
```

**With validation errors**:
```
Validating configuration for project NEXUS...

  ✓ public_roadmap (customfield_14619)
  ✓ roadmap_status (customfield_14621)
  ...
  ✗ roadmap_title (customfield_10999) - Field not found
  ⚠  roadmap_description (customfield_10102) - Insufficient permissions
  ...

================================================================
Validation Summary
================================================================
Project: NEXUS
Fields Validated: 13
Valid: 10 ✓
Invalid: 1 ✗
Inaccessible: 2 ⚠

Configuration has issues. Run with --fix to resolve.
```

---

## Command: `flask jira list-fields`

### Purpose

List all custom fields available in a JIRA project (utility command for exploration).

### Synopsis

```bash
flask jira list-fields PROJECT_KEY [OPTIONS]
```

### Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `PROJECT_KEY` | string | Yes | JIRA project key |

### Options

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--type` | `-t` | string | all | Filter by field type (text, date, number, all) |
| `--format` | `-f` | string | table | Output format (table, json, csv) |

### Behavior

- Call `/rest/api/3/field`
- Filter to custom fields
- Optionally filter by type
- Display in requested format

### Examples

```bash
# List all custom fields
flask jira list-fields NEXUS

# List only text fields
flask jira list-fields NEXUS --type text

# Export to JSON
flask jira list-fields NEXUS --format json > fields.json
```

### Output Format

**Table format** (default):
```
Custom Fields for Project: NEXUS

ID                  Name                    Type
------------------  ----------------------  ----------------------------
customfield_10001   Epic Title             Text Field (single line)
customfield_10002   Epic Description       Text Field (multi-line)
customfield_10003   Release Date           Date Picker
...
```

**JSON format**:
```json
[
  {
    "id": "customfield_10001",
    "name": "Epic Title",
    "type": "com.atlassian.jira.plugin.system.customfieldtypes:textfield",
    "description": ""
  },
  ...
]
```

---

## Testing Contracts

### Unit Test Coverage

Each CLI command must have unit tests covering:

1. **Success path**: Normal execution with valid inputs
2. **Authentication failure**: Invalid credentials
3. **Network errors**: Connection timeouts, API unavailable
4. **Invalid inputs**: Wrong project keys, invalid selections
5. **File I/O errors**: Permissions issues, disk full
6. **Validation errors**: Schema violations

### Mock Requirements

- Mock `requests` library for JIRA API calls
- Mock `click.prompt()` for user input simulation
- Mock file system operations for atomic writes
- Use `click.testing.CliRunner` for command execution

### Test Fixtures

```python
# Example test structure
def test_map_fields_success(cli_runner, mock_jira_api, mock_config_file):
    """Test successful field mapping workflow."""
    # Given: Valid JIRA credentials and custom fields available
    # When: Running map-fields with valid project key
    # Then: Configuration file updated with selected mappings
    pass

def test_map_fields_auth_failure(cli_runner, mock_jira_api):
    """Test authentication failure handling."""
    # Given: Invalid JIRA credentials
    # When: Running map-fields
    # Then: Exit code 2 with clear error message
    pass
```

---

## Command Compatibility

### Click Version

- **Minimum**: Click 8.0
- **Tested with**: Click 8.1.x
- **Compatibility**: Click 7.x may work but not supported

### Python Version

- **Minimum**: Python 3.11
- **Recommended**: Python 3.14 (project standard)

### Dependencies

- `click>=8.0`
- `requests>=2.28`
- `jsonschema>=4.0`

---

## Security Considerations

1. **Credential Handling**:
   - Never log JIRA_API_TOKEN in verbose mode
   - Mask credentials in error messages
   - Use environment variables (not command arguments) for secrets

2. **File Permissions**:
   - Config file should be readable by application user
   - Recommend `chmod 640` or `644` for config file
   - Warn if file is world-writable

3. **Input Validation**:
   - Validate all user input (project keys, selections)
   - Prevent path traversal in file operations
   - Sanitize output to prevent injection

---

## Future Enhancements

1. **Batch Operations**: Map multiple projects in single session
2. **Config Import/Export**: Share configurations across environments
3. **Field Suggestions**: Auto-suggest likely mappings based on field names
4. **History Tracking**: Maintain changelog of configuration updates
5. **Rollback**: Undo last configuration change

---

## Change Log

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-12-29 | Initial specification for map-fields, validate-config, list-fields commands |
