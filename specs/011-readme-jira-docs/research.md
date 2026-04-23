# Research: README JIRA Configuration Documentation

**Feature**: 011-readme-jira-docs
**Date**: 2026-01-29
**Purpose**: Research existing JIRA configuration, CLI commands, and current README structure to inform comprehensive documentation updates.

---

## Research Findings

### 1. Current README Analysis

**File**: `/README.md` (361 lines)

**Existing Structure**:
- Overview section
- Features list
- Quick Start (backend + frontend setup)
- Brief JIRA configuration mention (line 47: "See 'JIRA Configuration' section below")
- API Documentation
- Development guidelines
- Project Structure
- Docker deployment

**Current JIRA Documentation**:
- **Status**: Minimal - README mentions JIRA configuration but provides insufficient detail
- **Gap**: No dedicated section explaining authentication, permissions, custom fields, or CLI commands
- **Impact**: New developers cannot set up JIRA integration without external help

**Netlify References Found**: 17 occurrences requiring removal

**Decision**: Create new "JIRA Configuration" section between "Quick Start" and "API Documentation" with comprehensive setup, field mapping, and troubleshooting guidance.

---

### 2. JIRA CLI Commands Analysis

**Source**: `backend/app/cli/jira_setup.py` (1,141 lines)

**Available Commands** (4 total):

| Command | Purpose | Key Flags | Use Case |
|---------|---------|-----------|----------|
| `flask jira list-fields PROJECT_KEY` | List available custom fields in project | `--type`, `--include-global`, `--show-all-types` | Explore fields before mapping |
| `flask jira map-fields PROJECT_KEY` | Interactive field mapping wizard | `--all`, `--no-auto-match`, `--include-global`, `--show-all-types`, `--dry-run` | Configure field mappings |
| `flask jira validate-config [PROJECT_KEY]` | Validate configuration | `--fix`, `--verbose` | Verify setup correctness |
| `flask jira test-create-issue PROJECT_KEY` | Test issue creation | `--summary`, `--type` | Verify permissions |

**Key Features**:
- **Auto-matching**: Uses fuzzy matching (85% confidence threshold) to suggest field mappings
- **Manual selection**: Fallback when auto-matching fails
- **Validation**: Checks field IDs, permissions, and accessibility
- **Dry-run mode**: Preview changes before saving configuration

**Decision**: Document all four commands with examples, explain when to use each flag, and provide typical workflows (initial setup vs troubleshooting).

---

### 3. Custom Field Requirements

**Source**: `backend/config/jira_projects.json`

**Required Custom Fields** (14 total):

| Field Attribute | Purpose | Data Type | Required | Notes |
|----------------|---------|-----------|----------|-------|
| `public_roadmap` | Visibility flag | Checkbox | Yes | Controls public display |
| `roadmap_status` | Delivery status | Select List | Yes | Values: Delivered, Now, Next, Future |
| `module` | Product/module | Select List | Yes | Grouping by product area |
| `release_year` | Release year | Number | Yes | YYYY format |
| `release_quarter` | Release quarter | Select List | Yes | Q1, Q2, Q3, Q4 |
| `release_month` | Release month | Number | Yes | 1-12 format |
| `documentation_url` | Documentation link | URL | Yes | Help/docs URL |
| `roadmap_title` | Public title | Text (255 chars) | Yes | Display name |
| `roadmap_description` | Public description | Paragraph | Yes | Rich text |
| `roadmap_image_url_1` | Screenshot 1 | URL | No | Optional image |
| `roadmap_image_url_2` | Screenshot 2 | URL | No | Optional image |
| `roadmap_image_url_3` | Screenshot 3 | URL | No | Optional image |
| `roadmap_image_url_4` | Screenshot 4 | URL | No | Optional image |
| `roadmap_likes` | Like count | Number | Yes | Engagement metric |

**JIRA Setup Requirements**:
- All custom fields MUST be associated with **Epic** issue type
- Fields MUST appear on Epic **Edit** and **View** screens
- Custom field IDs follow pattern: `customfield_NNNNN` (5+ digits)
- Field IDs differ across JIRA instances (dev/staging/prod must be mapped separately)

**Decision**: Create comprehensive field table in README with types, purposes, and whether each is required. Include note about Epic issue type requirement and screen associations.

---

### 4. JIRA Authentication Requirements

**Source**: `backend/.env.example`, JIRA API documentation

**Required Environment Variables** (3):

| Variable | Format | Purpose | Example |
|----------|--------|---------|---------|
| `JIRA_BASE_URL` | `https://DOMAIN.atlassian.net` | JIRA Cloud instance URL | `https://weni.atlassian.net` |
| `JIRA_EMAIL` | Valid email address | Service account email | `roadmap@weni.ai` |
| `JIRA_API_TOKEN` | Base64 token string | Authentication token | Generated from Atlassian account settings |

**Token Generation**:
- **URL**: https://id.atlassian.com/manage-profile/security/api-tokens
- **Process**: 
  1. Log in to Atlassian account
  2. Navigate to Security → API tokens
  3. Click "Create API token"
  4. Name token (e.g., "Weni Roadmap Sync")
  5. Copy token immediately (cannot be viewed again)

**Required Permissions**:
- **Minimum**: Read access to projects
- **Recommended**: Read/write access to Epic custom fields
- **Scope**: Access to all projects that need roadmap synchronization

**Security Notes**:
- Token MUST NOT be committed to git (listed in `.gitignore`)
- Use separate tokens for dev/staging/production environments
- Rotate tokens periodically (every 90 days recommended)

**Decision**: Document complete authentication setup with step-by-step token generation instructions, security best practices, and environment variable configuration.

---

### 5. Netlify References to Remove

**Analysis**: `grep -i netlify README.md` found 17 matches

**Categories of Content to Remove**:
1. **Deployment sections**: Netlify-specific deployment instructions
2. **Environment variables**: Netlify-specific env var tables
3. **Build commands**: `npm run build` references tied to Netlify
4. **Configuration files**: References to `netlify.toml`
5. **Automated deployments**: Workflow descriptions for Netlify

**Content to Preserve**:
- Docker deployment documentation (primary deployment method)
- Generic build instructions applicable to any platform
- Environment variable concepts (but not Netlify-specific tables)
- CI/CD documentation that applies to general deployment

**Decision**: Remove all 17 Netlify references while preserving Docker deployment as the documented deployment method. Maintain references to `DEPLOYMENT_ONBOARDING.md` for detailed deployment guidance.

---

### 6. Documentation Structure Best Practices

**Research Sources**:
- GitHub documentation best practices
- Technical writing standards for developer documentation
- Existing Weni documentation patterns

**Key Principles**:
- **Progressive disclosure**: Start with Quick Start, then detailed sections
- **Task-oriented**: Organize by what users need to accomplish
- **Examples-first**: Show concrete examples before explaining concepts
- **Troubleshooting**: Address common issues proactively
- **Cross-references**: Link to detailed docs without duplicating content

**Recommended README Flow**:
1. Overview → 2. Features → 3. Quick Start → 4. **JIRA Configuration** → 5. API Documentation → 6. Development → 7. Deployment

**JIRA Configuration Section Structure**:
```markdown
## JIRA Configuration

### Authentication Setup
[Environment variables, token generation, security]

### Custom Field Requirements  
[14-field table with types and purposes]

### Field Mapping with CLI
[Step-by-step commands and examples]

### Validation & Troubleshooting
[Validation commands and common issues]
```

**Decision**: Insert JIRA Configuration section after Quick Start using progressive disclosure pattern. Start with authentication (what users need first), then fields (what must be configured), then CLI (how to configure), then validation (how to verify).

---

## Research Decisions Summary

| Decision | Rationale | Alternatives Considered |
|----------|-----------|------------------------|
| Create dedicated JIRA Configuration section | Current README lacks essential setup information; centralized documentation improves onboarding | Separate JIRA_SETUP.md file (rejected: adds navigation friction) |
| Document all 4 CLI commands | Comprehensive documentation reduces support requests | Document only map-fields (rejected: incomplete troubleshooting workflow) |
| Place JIRA section after Quick Start | Users need JIRA configured before running application | Place at end of README (rejected: too late in discovery flow) |
| Remove all 17 Netlify references | Netlify deployment no longer used; Docker is primary method | Mark as deprecated (rejected: causes confusion) |
| Include 14-field table with data types | Administrators need complete list before creating JIRA fields | Brief list only (rejected: insufficient for field creation) |
| Provide step-by-step token generation | Token generation is non-obvious for users unfamiliar with Atlassian | Link to Atlassian docs only (rejected: adds friction) |
| Include troubleshooting subsection | Proactive troubleshooting reduces support burden | Separate troubleshooting doc (rejected: forces context switching) |

---

## Alternatives Considered

### Alternative 1: Separate JIRA_CONFIGURATION.md File

**Approach**: Create standalone documentation file in `/docs/` folder

**Pros**:
- Keeps README focused on quick start
- Allows more detailed explanations
- Easier to maintain long-form content

**Cons**:
- Forces users to discover and navigate to separate file
- Breaks "single source of truth" for setup instructions
- Increases likelihood users miss critical configuration steps

**Rejected Because**: User Story 1 (P1) requires new developers to find all setup information in README. Separate file adds friction to critical onboarding path.

---

### Alternative 2: Link to Atlassian Documentation Only

**Approach**: Provide minimal guidance with links to official Atlassian docs

**Pros**:
- Reduces maintenance burden (Atlassian maintains docs)
- Always up-to-date with JIRA Cloud changes

**Cons**:
- Atlassian docs are generic, not Weni-specific
- Users must piece together information from multiple sources
- Misses Weni-specific field requirements and CLI commands

**Rejected Because**: Success Criterion SC-005 requires 90% of questions answered in README. External links don't satisfy this threshold.

---

### Alternative 3: Video Tutorial for JIRA Setup

**Approach**: Create screencast showing JIRA field creation and CLI usage

**Pros**:
- Visual demonstration of complex workflows
- Can show exact UI clicks and CLI interactions
- Engaging for visual learners

**Cons**:
- Video becomes outdated when JIRA UI changes
- Not searchable or skimmable
- Requires video hosting and maintenance
- Accessibility concerns for screen reader users

**Rejected Because**: Written documentation is more maintainable, searchable, and accessible than video content. Videos should supplement, not replace, written docs.

---

## Open Questions & Resolutions

### Q1: Should we document JIRA Server/Data Center setup?
**Answer**: No. Assumption documented in spec: "JIRA instance is JIRA Cloud (not Server or Data Center)". README will explicitly note Cloud-only requirement.

### Q2: How detailed should field type explanations be?
**Answer**: Provide data type (checkbox, select, text, paragraph, number, URL) and character limits where applicable. Link to JIRA field type documentation for advanced customization.

### Q3: Should README include examples of `jira_projects.json` format?
**Answer**: No. CLI commands handle configuration file updates automatically. Document config file location for reference, but don't encourage manual editing.

### Q4: Should we document how to obtain JIRA administrator permissions?
**Answer**: Out of scope. README should note administrator access is required, then defer to organizational IT/admin processes. Cannot provide universal guidance for permission requests.

### Q5: How to handle Netlify environment variable tables?
**Answer**: Remove entirely. Replace with generic "Environment Variables" section that covers backend `.env` file without platform-specific deployment concerns.

---

## References

- **JIRA CLI Implementation**: `backend/app/cli/jira_setup.py`
- **Configuration Format**: `backend/config/jira_projects.json`
- **Existing JIRA Migration Docs**: `docs/JIRA_LIKES_FIELD_MIGRATION.md`
- **CLI Quickstart**: `specs/004-cli-jira-field-mapping/quickstart.md`
- **JIRA Cloud API Docs**: https://developer.atlassian.com/cloud/jira/platform/rest/v3/
- **API Token Management**: https://id.atlassian.com/manage-profile/security/api-tokens
