# Feature Specification: JIRA Custom Fields Configuration

**Feature Branch**: `003-jira-custom-fields`
**Created**: December 26, 2025
**Status**: Draft
**Input**: User description: "I want to add more fields into the JIRA collected information: 1. Roadmap Title: instead of getting the title of the epic I want to get from a custom field 2. Roadmap Description: same thing here, I want to get from a custom field 3. Roadmap Image URL 1, 2, 3 and 4: I want you to expect 4 image URLS in a maximum for each epic and show them when it exists (not-required). The second improvement is that you should expect different custom field IDs for different projects. So instead of getting each one individually on the .env, it should be a json configuration file with project and it corresponding custom field ID for each custom field. The third improvement is that I want you to create a CLI command that I can create all the custom fields to a specific project at once only in the Epic work type."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Configure Custom Fields for JIRA Projects (Priority: P1)

As a system administrator, I need to configure which JIRA custom fields to use for each project so that the roadmap system can correctly extract roadmap data from different JIRA projects with different custom field configurations.

**Why this priority**: This is foundational - without proper configuration management, the system cannot support multiple projects with different custom field IDs. This enables the core capability of multi-project support.

**Independent Test**: Can be fully tested by creating a JSON configuration file with multiple project mappings, verifying the file format is valid, and confirming the system can read and parse the configuration correctly without needing to connect to JIRA.

**Acceptance Scenarios**:

1. **Given** a JIRA project with custom fields already created, **When** I add the project configuration to the JSON file with custom field IDs, **Then** the configuration is stored and validated successfully
2. **Given** multiple JIRA projects with different custom field IDs, **When** I configure each project in the JSON file, **Then** each project has its own independent custom field mapping
3. **Given** a malformed JSON configuration, **When** the system attempts to load the configuration, **Then** a clear error message indicates which part of the configuration is invalid
4. **Given** a project configuration with missing required fields, **When** the system validates the configuration, **Then** it reports which fields are missing

---

### User Story 2 - Create Custom Fields via CLI Command (Priority: P2)

As a system administrator, I need a CLI command to automatically create all required custom fields in a JIRA project so that I can quickly set up new projects without manually creating each field through the JIRA interface.

**Why this priority**: This automates the setup process and ensures consistency across projects. While P1 handles existing configurations, this story makes onboarding new projects fast and error-free.

**Independent Test**: Can be fully tested by running the CLI command against a test JIRA project, verifying that all 6 custom fields (Title, Description, Image URL 1-4) are created as Epic-level fields, and confirming the configuration file is automatically updated with the new field IDs.

**Acceptance Scenarios**:

1. **Given** a JIRA project without the required custom fields, **When** I run the CLI setup command with the project key, **Then** all 6 custom fields are created for the Epic issue type only
2. **Given** a JIRA project where some custom fields already exist, **When** I run the CLI setup command, **Then** existing fields are detected and not duplicated
3. **Given** a successful custom field creation, **When** the CLI command completes, **Then** the JSON configuration file is automatically updated with the new custom field IDs for that project
4. **Given** insufficient JIRA permissions, **When** I run the CLI setup command, **Then** a clear error message indicates the required permissions
5. **Given** an invalid project key, **When** I run the CLI setup command, **Then** the system reports that the project does not exist

---

### User Story 3 - Extract Roadmap Data from Custom Fields (Priority: P3)

As a roadmap viewer, I want to see roadmap entries with custom titles, descriptions, and optional images pulled from JIRA custom fields so that roadmap content can be tailored specifically for public display rather than using internal epic titles and descriptions.

**Why this priority**: This delivers the end-user value but depends on P1 (configuration) being in place. The enhanced data display is the ultimate goal but cannot function without the configuration layer.

**Independent Test**: Can be fully tested by creating a JIRA epic with populated custom fields, running the data sync process, and verifying the roadmap display shows the custom field values instead of default epic fields, including up to 4 images when present.

**Acceptance Scenarios**:

1. **Given** a JIRA epic with custom roadmap title and description fields populated, **When** the sync process runs, **Then** the roadmap displays the custom field values instead of the epic's default title and description
2. **Given** a JIRA epic with 4 image URLs in the custom image fields, **When** the sync process runs, **Then** all 4 images are available for display in the roadmap
3. **Given** a JIRA epic with only 2 image URLs populated, **When** the sync process runs, **Then** only the 2 populated images are shown and empty image fields are ignored
4. **Given** a JIRA epic with no image URLs, **When** the sync process runs, **Then** the roadmap entry displays without images and does not show empty placeholders
5. **Given** custom fields that are empty in JIRA, **When** the sync process runs, **Then** the system falls back to the default epic title and description

---

### Edge Cases

- What happens when a project is configured in the JSON file but the custom field IDs no longer exist in JIRA?
- How does the system handle invalid URLs in the image URL fields?
- What happens when the JSON configuration file is missing or corrupted at runtime?
- How does the system behave when JIRA API rate limits are reached during the CLI setup command?
- What happens when a custom field ID exists but is configured for a different issue type (not Epic)?
- How does the system handle duplicate project keys in the configuration file?
- What happens when an image URL field contains non-URL text?
- How does the system handle very long text in the custom title or description fields that might exceed display limits?

## Requirements *(mandatory)*

### Functional Requirements

**Configuration Management**:

- **FR-001**: System MUST support a JSON configuration file that maps JIRA project keys to their custom field IDs
- **FR-002**: System MUST validate the JSON configuration file on startup and report any schema violations
- **FR-003**: Configuration file MUST support mapping at least 6 custom fields per project: Roadmap Title, Roadmap Description, Roadmap Image URL 1, Roadmap Image URL 2, Roadmap Image URL 3, Roadmap Image URL 4
- **FR-004**: System MUST support multiple project configurations in a single JSON file
- **FR-005**: System MUST provide clear error messages when a referenced project is missing from the configuration

**CLI Setup Command**:

- **FR-006**: System MUST provide a CLI command that accepts a JIRA project key as input
- **FR-007**: CLI command MUST create custom fields for Epic issue type only, not for other issue types
- **FR-008**: CLI command MUST create exactly 6 custom fields with descriptive names: "Roadmap Title", "Roadmap Description", "Roadmap Image URL 1", "Roadmap Image URL 2", "Roadmap Image URL 3", "Roadmap Image URL 4"
- **FR-009**: CLI command MUST detect if custom fields already exist and skip creating duplicates
- **FR-010**: CLI command MUST automatically update the JSON configuration file with the created custom field IDs
- **FR-011**: CLI command MUST validate JIRA authentication before attempting to create fields
- **FR-012**: CLI command MUST display progress indicators during field creation
- **FR-013**: CLI command MUST provide a summary of created fields upon successful completion

**Data Extraction**:

- **FR-014**: System MUST read custom field IDs from the JSON configuration based on the JIRA project of each epic
- **FR-015**: System MUST extract the Roadmap Title from the configured custom field instead of the epic's default summary field
- **FR-016**: System MUST extract the Roadmap Description from the configured custom field instead of the epic's default description field
- **FR-017**: System MUST extract up to 4 image URLs from the respective custom fields
- **FR-018**: System MUST handle missing or empty custom field values gracefully
- **FR-019**: System MUST fall back to default epic title and description when custom fields are empty
- **FR-020**: System MUST validate that image URL fields contain valid URL format before including them
- **FR-021**: System MUST ignore empty image URL fields and only include populated ones
- **FR-022**: System MUST handle epics from projects not configured in the JSON file by using default field values

**Data Display**:

- **FR-023**: Roadmap display MUST show custom title when available, otherwise default epic title
- **FR-024**: Roadmap display MUST show custom description when available, otherwise default epic description
- **FR-025**: Roadmap display MUST show only the image URLs that are populated (0 to 4 images)
- **FR-026**: Roadmap display MUST handle the absence of images without showing broken image placeholders

### Key Entities

**Project Configuration**:
- Represents the mapping between a JIRA project and its custom field IDs
- Contains: project key, custom field IDs for title, description, and 4 image URLs
- Relationships: Multiple configurations can exist in one JSON file, each independent

**Custom Field Mapping**:
- Represents the linkage between a logical field (e.g., "Roadmap Title") and a JIRA custom field ID
- Contains: field name/purpose, JIRA custom field ID (e.g., "customfield_10001")
- Relationships: Belongs to a specific project configuration

**Roadmap Entry**:
- Enhanced to include custom fields alongside existing epic data
- Contains: custom title, custom description, array of image URLs (0-4), plus existing roadmap fields
- Relationships: Sourced from a JIRA epic via project-specific custom field mapping

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Administrator can configure a new JIRA project in under 5 minutes using the CLI command
- **SC-002**: System correctly handles at least 10 different JIRA projects with unique custom field configurations
- **SC-003**: CLI command successfully creates all 6 required custom fields without manual JIRA UI interaction
- **SC-004**: Roadmap sync process correctly displays custom field data from multiple projects without errors
- **SC-005**: 100% of configured image URLs that are valid are displayed in the roadmap
- **SC-006**: System handles missing configuration gracefully with clear error messages for 100% of misconfiguration scenarios
- **SC-007**: Configuration changes take effect without requiring system restart or deployment
- **SC-008**: CLI command detects and reports errors (invalid project, permission issues) within 30 seconds

## Assumptions

- JIRA API authentication details (bearer token) are already configured and remain in environment variables
- The system has network access to JIRA API endpoints
- Administrators have JIRA project admin permissions required to create custom fields
- Image URLs stored in JIRA custom fields point to publicly accessible images
- JIRA custom field IDs follow the standard format (e.g., "customfield_10XXX")
- The JSON configuration file is stored in a location accessible to the application at runtime
- Text-type custom fields in JIRA are sufficient for storing URLs (no special URL field type required)

## Dependencies

- Existing JIRA API integration and authentication mechanism
- JIRA REST API v3 for custom field creation and retrieval
- File system access for reading/writing the JSON configuration file

## Out of Scope

- Automatic discovery of custom fields across all projects
- Image hosting or storage - only URL references are managed
- Image validation beyond URL format checking
- Custom field deletion or modification after creation
- Migration of existing epic data to new custom fields
- User interface for managing the JSON configuration file
- Support for custom fields on issue types other than Epic
- Versioning or history tracking of configuration changes
