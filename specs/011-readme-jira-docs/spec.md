# Feature Specification: Update README with JIRA Configuration Documentation

**Feature Branch**: `011-readme-jira-docs`
**Created**: 2026-01-28
**Status**: Draft
**Input**: User description: "update the README.md to remove unused configuration like Netlify and add missing new stuff built in this project, I want you to add a complete area for JIRA configuration explaining: What kind of token and permission should be granted to it, What customizations should be made in the Epics Fields with their names and configuration, A clear instruction to map fields and generate the map config using the CLI command, How to make sure everything is UP with JIRA configuration."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - New Developer Onboarding (Priority: P1)

A new developer joins the team and needs to set up their local development environment. They open the README to understand what JIRA credentials they need and how to configure custom field mappings for their projects.

**Why this priority**: This is the most critical path as every new developer, system administrator, and stakeholder needs accurate setup instructions. Without clear JIRA configuration documentation, the system cannot function.

**Independent Test**: Can be fully tested by having a developer with no prior project knowledge follow only the README instructions to set up JIRA authentication and field mappings, then successfully sync roadmap data from JIRA.

**Acceptance Scenarios**:

1. **Given** a new developer reads the README, **When** they reach the JIRA Configuration section, **Then** they understand what API token type is needed (JIRA Cloud API Token) and what permissions are required (read access to Epic custom fields)
2. **Given** a developer has obtained a JIRA API token, **When** they review the JIRA Configuration section, **Then** they see clear instructions for setting the three required environment variables (JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN)
3. **Given** a developer needs to configure custom field mappings, **When** they read the README, **Then** they find step-by-step CLI command instructions with examples showing how to run `flask jira map-fields PROJECT_KEY`
4. **Given** a developer has completed JIRA setup, **When** they follow the validation instructions, **Then** they can verify their configuration is correct using `flask jira validate-config`

---

### User Story 2 - System Administrator Project Setup (Priority: P2)

A system administrator needs to add a new JIRA project to the roadmap system. They need to understand which custom fields must exist in JIRA and how they should be configured in the Epic issue type.

**Why this priority**: Essential for expanding the roadmap to new projects, but occurs less frequently than initial setup. This enables scalability of the roadmap system.

**Independent Test**: Can be tested independently by providing a system administrator with access to JIRA admin panel and README instructions, then verifying they can create required custom fields and complete the field mapping without external help.

**Acceptance Scenarios**:

1. **Given** a JIRA administrator needs to set up custom fields, **When** they read the JIRA Configuration section, **Then** they see a complete list of 14 required custom field types (public_roadmap checkbox, roadmap_status select, roadmap_title text, etc.) with their expected names and data types
2. **Given** an administrator has created custom fields in JIRA, **When** they associate fields with Epic issue type, **Then** the README explains fields must be available on Epic screens (Edit/View screens)
3. **Given** custom fields are created in JIRA, **When** the administrator runs the CLI mapping command, **Then** they can map each field to the roadmap configuration attributes
4. **Given** multiple projects need configuration, **When** they read the README, **Then** they understand they can use `flask jira map-fields --all` to configure all projects sequentially

---

### User Story 3 - Troubleshooting Configuration Issues (Priority: P3)

A developer encounters issues with roadmap data not syncing correctly from JIRA. They need to diagnose whether the problem is with authentication, permissions, or field mappings.

**Why this priority**: Important for operational reliability but less critical than initial setup. This supports day-to-day maintenance and debugging.

**Independent Test**: Can be tested by intentionally misconfiguring JIRA credentials or field mappings, then verifying a developer can use only README instructions to identify and fix the issues using validation commands.

**Acceptance Scenarios**:

1. **Given** a developer suspects authentication issues, **When** they read the troubleshooting section, **Then** they find instructions to test JIRA authentication separately before checking field mappings
2. **Given** field mappings may be incorrect, **When** they run the validation command from README instructions, **Then** the system reports which custom field IDs are invalid or inaccessible
3. **Given** configuration validation passes, **When** they follow README instructions to test sync, **Then** they can run `flask sync run --once` to verify data extraction works correctly
4. **Given** all configuration appears correct, **When** they need additional debugging help, **Then** the README points them to relevant documentation files (JIRA_LIKES_FIELD_MIGRATION.md, CLI quickstart guides)

---

### User Story 4 - Understanding Deployment Configuration (Priority: P2)

A stakeholder or developer needs to understand current deployment options and remove outdated Netlify information that no longer applies to the production deployment strategy.

**Why this priority**: Critical for preventing confusion about deployment, but affects fewer people than JIRA setup. Clean documentation prevents wasted time on deprecated approaches.

**Independent Test**: Can be tested by having someone unfamiliar with the project read only the README and correctly identify the current deployment approach (Docker/Render) without being confused by Netlify references.

**Acceptance Scenarios**:

1. **Given** a reader wants to understand deployment options, **When** they read the README, **Then** they see accurate information about Docker and docker-compose deployment without obsolete Netlify instructions
2. **Given** the project previously mentioned Netlify, **When** developers review the updated README, **Then** all Netlify-specific sections, commands, environment variable tables, and links to netlify.toml files are removed
3. **Given** deployment documentation exists in specs folder, **When** readers need detailed deployment information, **Then** the README still references relevant deployment documentation without conflicting information
4. **Given** the README focuses on essential setup, **When** readers complete the Quick Start section, **Then** they have a working local development environment without unnecessary deployment complexity

---

### Edge Cases

- What happens when a JIRA instance uses non-standard custom field names?
  - CLI auto-matching uses fuzzy matching with 85% confidence threshold
  - Manual selection available when auto-matching fails
  
- How does system handle custom fields that exist globally vs project-scoped?
  - CLI filters to project-scoped fields by default
  - `--include-global` flag available for seeing all fields

- What if a developer has multiple JIRA environments (dev/staging/production)?
  - README must note that custom field IDs differ across JIRA instances
  - Configuration must be mapped separately for each environment

- How to handle optional vs required custom fields?
  - README clearly marks which fields are required vs optional
  - Image URL fields 1-4 can be skipped during CLI mapping

- What if JIRA API token lacks sufficient permissions?
  - README specifies minimum required permission: read access to Epic custom fields
  - Validation command reports permission issues with clear error messages

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: README MUST include a dedicated "JIRA Configuration" section that explains authentication setup, custom field requirements, CLI mapping commands, and validation procedures
- **FR-002**: README MUST document all three required environment variables (JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN) with format examples and security guidance
- **FR-003**: README MUST provide step-by-step instructions for obtaining a JIRA Cloud API token from https://id.atlassian.com/manage-profile/security/api-tokens
- **FR-004**: README MUST list all 14 custom field mapping attributes (public_roadmap, roadmap_status, module, release_year, release_quarter, release_month, documentation_url, roadmap_title, roadmap_description, roadmap_image_url_1-4, roadmap_likes) with their purposes and expected data types
- **FR-005**: README MUST explain that custom fields must be associated with the Epic issue type and available on Epic Edit/View screens
- **FR-006**: README MUST provide clear CLI command examples for field mapping (`flask jira map-fields PROJECT_KEY`, `flask jira map-fields --all`)
- **FR-007**: README MUST document CLI flags for field mapping (--no-auto-match, --include-global, --show-all-types, --dry-run, --all) with use cases
- **FR-008**: README MUST include instructions for validating JIRA configuration using `flask jira validate-config` command
- **FR-009**: README MUST explain how to test JIRA sync using `flask sync run --once` command
- **FR-010**: README MUST describe minimum required permissions for JIRA API token (read access to projects, read/write access to Epic custom fields)
- **FR-011**: README MUST remove all Netlify-specific content including deployment commands, netlify.toml references, environment variable tables for Netlify, and automated deployment workflows
- **FR-012**: README MUST preserve Docker deployment documentation as the primary deployment method
- **FR-013**: README MUST include troubleshooting guidance for common JIRA configuration issues (authentication failures, missing fields, invalid field IDs)
- **FR-014**: README MUST reference existing detailed documentation (JIRA_LIKES_FIELD_MIGRATION.md, CLI quickstart in specs/004-cli-jira-field-mapping/) for readers who need deeper information
- **FR-015**: README MUST maintain accurate "Project Structure" section that reflects current backend services (JiraClient, sync service, cache service, HTML sanitizer, Slack service)

### Key Entities

- **JIRA Configuration Section**: Documentation block explaining authentication, permissions, custom fields, CLI mapping, and validation
  - Attributes: authentication setup, token requirements, permission requirements, field listing, CLI commands, validation procedures
  - Purpose: Central reference for all JIRA-related setup and configuration

- **Environment Variables**: Three required variables for JIRA authentication
  - JIRA_BASE_URL: Atlassian cloud instance URL
  - JIRA_EMAIL: Service account email
  - JIRA_API_TOKEN: API token for authentication
  - Security note: Token should never be committed to git

- **Custom Field Mappings**: 14 field attributes that map to JIRA custom fields
  - Required fields (10): public_roadmap, roadmap_status, module, release_year, release_quarter, release_month, documentation_url, roadmap_title, roadmap_description, roadmap_likes
  - Optional fields (4): roadmap_image_url_1, roadmap_image_url_2, roadmap_image_url_3, roadmap_image_url_4
  - Stored in: backend/config/jira_projects.json

- **CLI Commands**: Flask CLI commands for JIRA management
  - map-fields: Interactive field mapping command
  - validate-config: Configuration validation command
  - list-fields: Field exploration command
  - Flags: --all, --no-auto-match, --include-global, --show-all-types, --dry-run

- **Custom Field Requirements**: JIRA fields that must be created by administrators
  - Field types: checkbox (public_roadmap), select list (roadmap_status, module, release_quarter), number (release_year, release_month, roadmap_likes), text (roadmap_title, documentation_url, image URLs), paragraph (roadmap_description)
  - Association: Must be added to Epic issue type screens

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: New developers can set up complete JIRA authentication and field mapping configuration following only README instructions in under 20 minutes
- **SC-002**: Documentation clearly identifies which custom fields are required vs optional, reducing configuration errors by 80%
- **SC-003**: 100% of Netlify-specific references are removed from README while preserving Docker deployment documentation
- **SC-004**: Developers can validate their JIRA configuration is correct using documented CLI commands, detecting misconfigurations in under 2 minutes
- **SC-005**: README provides sufficient detail that 90% of JIRA configuration questions can be answered without consulting additional documentation
- **SC-006**: System administrators can create all required JIRA custom fields with correct types and associations by following README field listing
- **SC-007**: All CLI command examples in README are executable and produce expected outcomes when run against properly configured JIRA instance
- **SC-008**: README troubleshooting section addresses the top 5 most common JIRA configuration issues (authentication, permissions, missing fields, invalid field IDs, sync failures)
- **SC-009**: Cross-references to detailed documentation (JIRA_LIKES_FIELD_MIGRATION.md, CLI quickstart) are accurate and help readers find deeper technical information when needed
- **SC-010**: README structure flows logically from Quick Start → JIRA Configuration → API Documentation → Development, enabling readers to find information in under 30 seconds

## Assumptions

- JIRA instance is JIRA Cloud (not Server or Data Center) - documented in authentication section
- Users have basic command-line proficiency to run Flask CLI commands
- JIRA administrators have access to create and configure custom fields
- Development team prefers Docker deployment over Netlify serverless functions
- Existing backend/config/jira_projects.json configuration file format remains unchanged
- CLI commands in backend/app/cli/jira_setup.py remain stable
- Feature request routing and Slack integration features are still active (preserve in README)
