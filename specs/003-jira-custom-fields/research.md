# Research: JIRA Custom Fields Configuration

**Feature**: 003-jira-custom-fields
**Date**: December 26, 2025
**Status**: Complete

## Overview

This document captures research findings and technical decisions for implementing JSON-based JIRA custom field configuration with CLI setup automation.

## Research Areas

### 1. JSON Configuration Format

**Decision**: Use flat project-key-based mapping with explicit field names

**Rationale**:
- **Simplicity**: Direct key-value mapping is easy to read and maintain
- **Validation**: Clear schema enables strong validation with jsonschema library
- **Editor support**: Standard JSON format works with all IDEs and provides autocomplete with schema
- **Version control friendly**: Text format enables clear diffs when configurations change

**Alternatives Considered**:

| Alternative | Pros | Cons | Rejection Reason |
|------------|------|------|------------------|
| YAML configuration | More human-readable, supports comments | Requires PyYAML dependency, less strict parsing | JSON is sufficient and has no additional dependencies |
| Environment variables (current) | Simple, 12-factor compliant | Doesn't scale to multiple projects | Cannot support per-project mappings |
| Database storage | Centralized, supports UI editor | Adds deployment complexity, requires migrations | Overkill for static configuration |
| Python config file | Full programming language, dynamic | Security risk, harder to validate | Configuration should be data, not code |

**Selected Format**:

```json
{
  "version": "1.0",
  "projects": {
    "PROJ1": {
      "roadmap_title": "customfield_10101",
      "roadmap_description": "customfield_10102",
      "roadmap_image_url_1": "customfield_10103",
      "roadmap_image_url_2": "customfield_10104",
      "roadmap_image_url_3": "customfield_10105",
      "roadmap_image_url_4": "customfield_10106"
    },
    "PROJ2": {
      "roadmap_title": "customfield_10201",
      "roadmap_description": "customfield_10202",
      "roadmap_image_url_1": "customfield_10203",
      "roadmap_image_url_2": "customfield_10204",
      "roadmap_image_url_3": "customfield_10205",
      "roadmap_image_url_4": "customfield_10206"
    }
  }
}
```

### 2. JIRA REST API v3 Custom Field Creation

**Decision**: Use `/rest/api/3/field` endpoint with Epic issue type context

**Research Findings**:

**JIRA Custom Field API**:
- Endpoint: `POST /rest/api/3/field`
- Required fields: `name`, `description`, `type`, `searcherKey`
- Context configuration: `issueTypeIds` to restrict to Epic only
- Field types: Use `textfield` (single line) for title and URLs, `paragraph` (multiline) for description

**Field Type Options**:

| Field Type | Searcher Key | Use Case | Selected For |
|------------|-------------|----------|--------------|
| `com.atlassian.jira.plugin.system.customfieldtypes:textfield` | `com.atlassian.jira.plugin.system.customfieldtypes:textsearcher` | Single-line text | Title, Image URLs |
| `com.atlassian.jira.plugin.system.customfieldtypes:textarea` | `com.atlassian.jira.plugin.system.customfieldtypes:textsearcher` | Multi-line text | Description |
| `com.atlassian.jira.plugin.system.customfieldtypes:url` | `com.atlassian.jira.plugin.system.customfieldtypes:exacttextsearcher` | URL with validation | Rejected - limits flexibility |

**Epic Issue Type Detection**:
- Use `/rest/api/3/issuetype` to get all issue types
- Filter for `issuetype.name == "Epic"` or `issuetype.hierarchyLevel == 1`
- Extract `issueTypeId` for context configuration

**Duplicate Detection**:
- Use `/rest/api/3/field` (GET) to list all custom fields
- Match by exact field name: "Roadmap Title", "Roadmap Description", etc.
- Check field context to verify Epic association

**Rationale**:
- Text fields are more flexible than URL fields (allow empty, no strict validation)
- Epic-only context prevents fields from appearing in other issue types
- Standard field types ensure compatibility across JIRA Cloud instances

### 3. Configuration Loading Strategy

**Decision**: Load on startup with lazy project-specific lookup

**Approach**:
1. **Startup validation**: Load and validate JSON schema on application start
2. **Warning-only errors**: Log warnings for malformed configs but don't block startup
3. **Lazy lookup**: Retrieve project-specific mappings when processing each epic
4. **Fallback behavior**: Use default epic fields when project not in config

**Rationale**:
- **Resilience**: Application continues working even with config issues
- **Performance**: One-time load, cached in memory, no repeated file I/O
- **Flexibility**: Hot-reload possible by re-reading file (future enhancement)

**Error Handling Levels**:

| Error Type | Handling | Reason |
|------------|----------|--------|
| File missing | Warning, use defaults | Backward compatibility with env var config |
| Invalid JSON syntax | Warning, use defaults | Don't break on syntax errors |
| Schema violation | Warning, use defaults | Allow partial configs to work |
| Invalid field ID format | Warning per project | One bad project shouldn't break others |
| Project not in config | Silent, use defaults | Expected for unconfigured projects |

### 4. Flask CLI Command Pattern

**Decision**: Use Flask's `@app.cli.command()` decorator with Click

**Command Syntax**:
```bash
flask jira setup-fields <project-key>
```

**Research Findings**:

**Flask CLI Integration**:
- Flask uses Click library for CLI commands
- Commands registered via `@app.cli.command()` decorator
- Automatic help generation and argument validation
- Access to application context (config, logging)

**Best Practices**:
- Use Click decorators for arguments: `@click.argument('project_key')`
- Use Click options for flags: `@click.option('--dry-run', is_flag=True)`
- Use `click.echo()` for output (handles Unicode correctly)
- Use `click.style()` for colored output (errors, success, warnings)
- Return exit codes: `sys.exit(0)` success, `sys.exit(1)` error

**Progress Indication**:
```python
with click.progressbar(field_configs, label='Creating fields') as bar:
    for field_config in bar:
        create_field(field_config)
```

**Rationale**:
- Consistent with Flask ecosystem conventions
- Built-in argument parsing and validation
- Professional CLI UX with colors and progress bars
- Testable through Click's CliRunner

### 5. Custom Field Value Extraction

**Decision**: Extend existing field extraction with custom field priority

**Extraction Logic**:
1. **Check for custom fields**: Look up project in config, extract custom field values
2. **Validate custom values**: Ensure non-empty strings
3. **Fallback to defaults**: If custom fields empty or missing, use epic's summary/description
4. **URL validation**: Validate image URL format, skip invalid entries

**Image URL Handling**:
- Extract from 4 separate custom fields (not attachments)
- Validate URL format: `^https?://.*\.(jpg|jpeg|png|gif|webp).*$`
- Filter empty strings and None values
- Return list of 0-4 valid URLs
- Frontend displays images in order provided

**Field Priority**:
```
Title:       custom_field[roadmap_title] || epic.summary
Description: custom_field[roadmap_description] || epic.description
Images:      [custom_field[image_1..4]] (no fallback)
```

**Rationale**:
- **Backward compatible**: Existing epics without custom fields continue working
- **Graceful degradation**: Missing or empty custom fields don't break display
- **Flexible validation**: URL format check without strict hostname validation
- **Explicit image fields**: More reliable than parsing attachments

### 6. JSON Schema Validation

**Decision**: Use jsonschema library with Draft 7 specification

**Schema Structure**:
- **$schema**: Reference JSON Schema Draft 7
- **version**: Semantic version for config format changes
- **projects**: Object with project keys as properties
- **field names**: Standardized keys (roadmap_title, etc.)
- **field ID pattern**: Regex for customfield_\d+ format

**Validation Rules**:
- `version` is required string matching semver pattern
- `projects` is required object with at least 1 project
- Each project must have all 6 required field keys
- Field IDs must match JIRA custom field format: `customfield_\d{5,}`
- No additional properties allowed (strict schema)

**Rationale**:
- Industry standard validation library
- Clear error messages with property paths
- Supports future schema evolution with version field
- Strict validation prevents typos and misconfigurations

## Technical Dependencies

### New Libraries

| Library | Version | Purpose | License |
|---------|---------|---------|---------|
| jsonschema | ^4.20.0 | JSON validation | MIT |
| click | ^8.1.7 (already present via Flask) | CLI framework | BSD-3-Clause |

### JIRA API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/rest/api/3/field` | GET | List existing custom fields |
| `/rest/api/3/field` | POST | Create new custom field |
| `/rest/api/3/issuetype` | GET | Get Epic issue type ID |
| `/rest/api/3/field/{fieldId}/context` | POST | Configure field context |

### Permissions Required

- **JIRA Administration**: Global permission to create custom fields
- **Project Administration**: Minimum required to configure field contexts

## Migration Strategy

### Backward Compatibility

**Existing Environment Variables**: Keep support for legacy single-project mode
- If `jira_projects.json` doesn't exist, use env var field mappings
- Allows gradual migration project by project
- No breaking changes to existing deployments

**Migration Path**:
1. Deploy new code with JSON config support
2. Run CLI command for first project
3. Verify configuration works
4. Gradually add more projects
5. Eventually deprecate env var config (future)

### Configuration Priority

```
1. JSON config file (if present and valid)
2. Environment variables (backward compatibility)
3. Default values (customfield_100XX fallback)
```

## Performance Considerations

### Configuration Loading

- **Load time**: < 100ms for 100 projects (in-memory dict lookup)
- **Memory footprint**: ~1 KB per project (negligible)
- **Startup impact**: Single file read, one-time validation

### CLI Command Performance

- **Field creation**: ~2-3 seconds per field
- **Total for 6 fields**: ~15-20 seconds
- **Network bound**: JIRA API rate limits may apply
- **Optimization**: Create fields in parallel (future enhancement)

## Security Considerations

### Configuration File Access

- **Location**: Inside backend directory, not web-accessible
- **Permissions**: Read-only for application user
- **Git tracking**: Should be version controlled (no secrets)

### JIRA API Security

- **Authentication**: Existing bearer token from environment variables
- **Authorization**: Requires admin permissions (appropriate for setup task)
- **Rate limiting**: Respect JIRA Cloud rate limits (5 req/sec recommended)

### Input Validation

- **Project key**: Alphanumeric only, prevent injection
- **Field IDs**: Regex validation, must match customfield_\d+
- **URLs**: Format validation, no credential extraction

## Testing Strategy

### Unit Tests

1. **ConfigLoader**: Valid/invalid JSON, missing files, schema violations
2. **CLI Commands**: Dry run, successful creation, error handling
3. **Field Extraction**: Custom fields, fallbacks, empty values, URL validation
4. **Schema Validation**: Valid configs, various violation scenarios

### Integration Tests

1. **End-to-end sync**: Epic with custom fields → API response includes custom data
2. **Multi-project**: Different projects use correct field mappings
3. **Backward compatibility**: Projects not in config still work

### Manual Testing Checklist

- [ ] CLI creates all 6 fields in JIRA
- [ ] Fields appear only on Epic issue type
- [ ] Configuration file auto-updates with field IDs
- [ ] Sync correctly extracts custom field values
- [ ] Empty custom fields fall back to defaults
- [ ] Invalid URLs are filtered out
- [ ] Multiple projects work independently

## Open Questions

**None** - All technical decisions resolved through research.

## References

- [JIRA REST API v3 Documentation](https://developer.atlassian.com/cloud/jira/platform/rest/v3/)
- [JIRA Custom Fields Guide](https://support.atlassian.com/jira-cloud-administration/docs/create-custom-fields/)
- [JSON Schema Specification](https://json-schema.org/specification.html)
- [Flask CLI Documentation](https://flask.palletsprojects.com/en/3.0.x/cli/)
- [Click Documentation](https://click.palletsprojects.com/)
