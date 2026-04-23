# Feature Specification: CLI JIRA Custom Field Retrieval and Mapping

**Feature Branch**: `004-cli-jira-field-mapping`
**Created**: December 29, 2025
**Status**: Draft
**Input**: User description: "I want to make a change in this idea of creating all custom fields automatically using JIRA API through a CLI command. The problem here is that I don't have enough access to create custom fields through API, so the CLI command will only retrieve the custom fields from the API on projects configured in .env JIRA_PROJECT_KEYS and associate the custom fields IDs properly in the JSON file."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Retrieve Custom Fields for Configured Projects (Priority: P1)

As a system administrator without JIRA admin permissions, I need a CLI command that retrieves existing custom fields from configured JIRA projects so that I can identify and map the correct field IDs without needing API permissions to create fields.

**Why this priority**: This is the core functionality that replaces the previous auto-creation approach. Without the ability to discover existing custom fields, administrators cannot properly configure the system to use project-specific custom fields.

**Independent Test**: Can be fully tested by running the CLI command against projects listed in JIRA_PROJECT_KEYS environment variable, verifying that all custom fields for Epic issue types are retrieved, and confirming the field list is displayed with names and IDs without modifying any JIRA configuration.

**Acceptance Scenarios**:

1. **Given** one or more project keys configured in JIRA_PROJECT_KEYS, **When** I run the CLI retrieval command, **Then** the system fetches all custom fields available for the Epic issue type in each project
2. **Given** successful field retrieval, **When** the CLI command completes, **Then** a list of custom fields is displayed with field names and their corresponding IDs for each project
3. **Given** multiple projects in JIRA_PROJECT_KEYS, **When** I run the CLI command, **Then** custom fields are retrieved for all configured projects independently
4. **Given** an invalid or non-existent project key in JIRA_PROJECT_KEYS, **When** I run the CLI command, **Then** the system reports which project key is invalid and continues processing other valid projects
5. **Given** JIRA API authentication credentials, **When** I run the CLI command, **Then** the system validates authentication before attempting field retrieval

---

### User Story 2 - Interactive Field Mapping (Priority: P2)

As a system administrator, I need to interactively select which custom fields map to roadmap attributes (Title, Description, Image URLs 1-4) so that I can correctly configure each project's custom field mappings in the JSON configuration file.

**Why this priority**: This builds on P1's field discovery by enabling administrators to make intelligent mapping decisions. The interactive selection ensures accuracy and reduces configuration errors.

**Independent Test**: Can be fully tested by running the CLI command, viewing the list of available fields, selecting appropriate fields for each roadmap attribute through prompts, and verifying the JSON configuration file is updated with the selected field IDs.

**Acceptance Scenarios**:

1. **Given** retrieved custom fields for a project, **When** the CLI prompts me to select the Roadmap Title field, **Then** I can choose from the list of available custom fields or skip if not applicable
2. **Given** the field selection prompts, **When** I select a field for each required attribute (Title, Description, Image URL 1-4), **Then** my selections are validated and stored
3. **Given** completed field selections for a project, **When** I confirm the mapping, **Then** the JSON configuration file is automatically updated with the selected custom field IDs for that project
4. **Given** an existing project configuration in the JSON file, **When** I run the CLI mapping command, **Then** I can choose to update the existing mapping or keep the current configuration
5. **Given** optional image URL fields, **When** I choose to skip some or all image fields, **Then** the configuration reflects only the selected image fields
6. **Given** field selection in progress, **When** I cancel the operation, **Then** no changes are made to the existing JSON configuration file

---

### User Story 3 - Validate Configuration Against JIRA (Priority: P3)

As a system administrator, I need to validate that the custom field IDs in my JSON configuration file still exist and are accessible in JIRA so that I can detect and fix broken configurations before they cause runtime errors.

**Why this priority**: This provides ongoing maintenance capability but is not required for initial setup. It helps prevent issues after JIRA configuration changes but depends on P1 and P2 being in place first.

**Independent Test**: Can be fully tested by running the validation command with an existing JSON configuration, checking each configured field ID against JIRA, and receiving a report of valid, invalid, or inaccessible fields.

**Acceptance Scenarios**:

1. **Given** a JSON configuration file with custom field mappings, **When** I run the validation command, **Then** the system checks each field ID against JIRA to confirm it exists
2. **Given** field IDs that no longer exist in JIRA, **When** the validation runs, **Then** the system reports which fields are missing and in which projects
3. **Given** field IDs that exist but are not accessible with current permissions, **When** the validation runs, **Then** the system identifies permission issues for specific fields
4. **Given** a successful validation, **When** all fields are confirmed accessible, **Then** the system reports that the configuration is valid and ready for use
5. **Given** validation errors, **When** the command completes, **Then** suggested actions are provided to resolve each issue

---

### Edge Cases

- What happens when JIRA_PROJECT_KEYS environment variable is empty or not set?
- How does the system handle projects where no custom fields exist for the Epic issue type?
- What happens when the JSON configuration file is read-only or in a location without write permissions?
- How does the system behave when JIRA API is temporarily unavailable during field retrieval?
- What happens when a custom field has the same name across different projects but different IDs?
- How does the system handle very long custom field names in the CLI display?
- What happens when a project has hundreds of custom fields?
- How does the system handle custom fields that exist but are not of text type (e.g., date, number fields)?
- What happens when the JSON configuration file contains projects not listed in JIRA_PROJECT_KEYS?

## Requirements *(mandatory)*

### Functional Requirements

**CLI Field Retrieval**:

- **FR-001**: CLI command MUST read project keys from the JIRA_PROJECT_KEYS environment variable
- **FR-002**: CLI command MUST parse comma-separated or space-separated project keys from JIRA_PROJECT_KEYS
- **FR-003**: CLI command MUST retrieve all custom fields associated with the Epic issue type for each project
- **FR-004**: CLI command MUST display retrieved fields in a readable format showing field name and field ID
- **FR-005**: CLI command MUST handle multiple projects sequentially, processing each independently
- **FR-006**: CLI command MUST validate JIRA authentication before attempting field retrieval
- **FR-007**: CLI command MUST report errors for invalid project keys without stopping processing of other projects
- **FR-008**: CLI command MUST indicate which project each set of fields belongs to when displaying results

**Interactive Field Mapping**:

- **FR-009**: CLI command MUST prompt user to select custom fields for each roadmap attribute: Roadmap Title, Roadmap Description, Roadmap Image URL 1, Roadmap Image URL 2, Roadmap Image URL 3, Roadmap Image URL 4
- **FR-010**: CLI command MUST allow users to skip optional fields (image URLs) during selection
- **FR-011**: CLI command MUST validate that selected field IDs are from the retrieved list before accepting them
- **FR-012**: CLI command MUST display current selections for review before confirming changes
- **FR-013**: CLI command MUST update the JSON configuration file with selected field mappings for each project
- **FR-014**: CLI command MUST preserve existing configuration for projects not being updated
- **FR-015**: CLI command MUST support overwriting existing project configurations with user confirmation
- **FR-016**: CLI command MUST handle cancellation gracefully without modifying the configuration file
- **FR-017**: CLI command MUST create the JSON configuration file if it does not exist
- **FR-018**: CLI command MUST validate JSON schema after updating the configuration file

**Configuration Validation**:

- **FR-019**: CLI command MUST provide a separate validation mode that checks existing configurations
- **FR-020**: Validation MUST verify each custom field ID in the configuration exists in JIRA
- **FR-021**: Validation MUST check that configured fields are accessible with current API credentials
- **FR-022**: Validation MUST report which field IDs are invalid or inaccessible
- **FR-023**: Validation MUST indicate which projects have configuration issues
- **FR-024**: Validation MUST provide exit codes indicating validation success or failure

**Error Handling**:

- **FR-025**: CLI command MUST provide clear error messages for authentication failures
- **FR-026**: CLI command MUST report network connectivity issues with JIRA API
- **FR-027**: CLI command MUST handle JSON file read/write permission errors gracefully
- **FR-028**: CLI command MUST detect and report malformed JSON in configuration file
- **FR-029**: CLI command MUST handle JIRA API rate limiting with appropriate retry logic or error messages
- **FR-030**: CLI command MUST display progress indicators for long-running operations

### Key Entities

**Project Field Mapping**:
- Represents custom field assignments for a specific JIRA project
- Contains: project key, field IDs for Roadmap Title, Roadmap Description, Roadmap Image URL 1-4
- Relationships: Multiple mappings exist in the JSON configuration file, one per project

**Custom Field Metadata**:
- Represents information about a JIRA custom field
- Contains: field ID, field name, field type, associated issue type
- Relationships: Retrieved from JIRA API, used to populate selection menus

**Configuration File**:
- JSON structure storing all project-to-custom-field mappings
- Contains: array of project configurations, schema version
- Relationships: Read and written by CLI command, consumed by sync service at runtime

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Administrator can retrieve custom fields for all configured projects in under 30 seconds
- **SC-002**: Administrator can complete interactive field mapping for a single project in under 3 minutes
- **SC-003**: CLI command successfully processes at least 10 projects from JIRA_PROJECT_KEYS without errors
- **SC-004**: 100% of valid custom field IDs are correctly written to the JSON configuration file
- **SC-005**: Validation command detects and reports 100% of invalid or inaccessible field IDs
- **SC-006**: CLI command provides clear error messages for all common failure scenarios (auth, network, permissions)
- **SC-007**: Configuration updates do not corrupt existing valid project mappings in the JSON file
- **SC-008**: Users can successfully map custom fields without JIRA admin permissions, using only read access
- **SC-009**: CLI command completes field retrieval and mapping without requiring manual JIRA UI interaction
- **SC-010**: System handles configuration for projects with different custom field schemas without conflicts

## Assumptions

- JIRA API credentials with read access to custom fields are configured in environment variables
- JIRA_PROJECT_KEYS environment variable contains valid project keys separated by commas or spaces
- Administrators have basic JIRA knowledge to identify which custom fields correspond to roadmap attributes
- Custom field names in JIRA are descriptive enough for administrators to make correct mapping decisions
- The JSON configuration file location is writable by the user running the CLI command
- Network connectivity to JIRA API is available when running CLI commands
- Custom fields in JIRA use standard text field types for storing title, description, and URL values
- All relevant custom fields are configured at the Epic issue type level in JIRA

## Dependencies

- Existing JIRA API integration and authentication mechanism (from previous features)
- JIRA REST API v3 for custom field retrieval
- JIRA_PROJECT_KEYS environment variable configuration
- JSON configuration file structure defined in feature 003-jira-custom-fields
- File system access for reading and writing the JSON configuration file
- CLI framework or library for interactive prompts and user input

## Out of Scope

- Creation of custom fields in JIRA via API (explicitly removed due to permission constraints)
- Automatic field name matching or AI-based field suggestion
- Bulk export/import of configurations across different environments
- Web UI for field mapping (CLI only)
- Field mapping for issue types other than Epic
- Validation of field data quality or content in JIRA epics
- Migration tools to move data between custom fields
- Scheduled re-validation of configurations
- Support for non-standard custom field types (calculated fields, cascading selects, etc.)
- Custom field value transformation or formatting rules
