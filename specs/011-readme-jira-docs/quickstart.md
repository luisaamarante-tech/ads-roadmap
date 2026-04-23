# Quickstart: README JIRA Configuration Documentation

**Feature**: 011-readme-jira-docs
**Date**: 2026-01-29
**For**: Developers implementing the README documentation updates

---

## Prerequisites

- Write access to `/README.md` in repository root
- Understanding of existing JIRA CLI commands (`backend/app/cli/jira_setup.py`)
- Familiarity with JIRA custom field configuration concepts

---

## Implementation Checklist

### Phase 1: Remove Netlify References (15 minutes)

**Goal**: Clean up obsolete Netlify deployment documentation

1. **Search for Netlify references**:
   ```bash
   grep -n -i "netlify" README.md
   ```

2. **Remove sections** (17 total occurrences):
   - Netlify deployment instructions
   - Netlify environment variable tables
   - Build commands tied to Netlify
   - References to `netlify.toml`
   - Automated Netlify deployment workflows

3. **Preserve**:
   - Docker deployment section (lines ~280-320)
   - Generic build instructions (applicable to any platform)
   - Environment variable concepts (not Netlify-specific formatting)

4. **Verify removal**:
   ```bash
   grep -i "netlify" README.md  # Should return no matches
   ```

---

### Phase 2: Create JIRA Configuration Section (45 minutes)

**Goal**: Add comprehensive JIRA setup documentation

**Location**: Insert after "Quick Start" section, before "API Documentation"

**Structure**:

```markdown
## JIRA Configuration

### Authentication Setup

[Environment variables table]
[Token generation steps]
[Security notes]

### Custom Field Requirements

[14-field table with types, purposes, required status]
[JIRA setup notes: Epic association, screen requirements]

### Field Mapping with CLI

[Step-by-step workflow]
[Command examples for each CLI command]
[Flag documentation]

### Validation & Troubleshooting

[Validation command usage]
[Common issues and solutions]
[Cross-references to detailed docs]
```

#### Subsection 1: Authentication Setup

**Content to include**:
1. Three required environment variables:
   - `JIRA_BASE_URL`: Format, example
   - `JIRA_EMAIL`: Format, example
   - `JIRA_API_TOKEN`: Format, example

2. Token generation steps:
   - URL: https://id.atlassian.com/manage-profile/security/api-tokens
   - Step-by-step process (5 steps)
   - Security warning about immediate copy

3. Required permissions:
   - Minimum: Read access to projects
   - Recommended: Read/write access to Epic custom fields

4. Security best practices:
   - Never commit tokens to git
   - Use separate tokens per environment
   - Rotate every 90 days

---

#### Subsection 2: Custom Field Requirements

**Content to include**:
1. Comprehensive field table (14 fields):
   - Field Attribute Name
   - JIRA Field Type
   - Required (Yes/No)
   - Purpose

2. JIRA setup requirements:
   - Associate with Epic issue type
   - Add to Epic Edit screen
   - Add to Epic View screen

3. Field ID pattern note:
   - Format: `customfield_NNNNN` (5+ digits)
   - IDs differ across JIRA instances

---

#### Subsection 3: Field Mapping with CLI

**Content to include**:
1. **Initial setup workflow**:
   ```bash
   # 1. Explore available fields
   flask jira list-fields PROJECT_KEY
   
   # 2. Map fields interactively
   flask jira map-fields PROJECT_KEY
   
   # 3. Validate configuration
   flask jira validate-config PROJECT_KEY
   ```

2. **Command reference**:
   - `flask jira list-fields` + flags
   - `flask jira map-fields` + flags (including --all, --no-auto-match, --dry-run)
   - `flask jira validate-config` + flags
   - `flask jira test-create-issue` + flags

3. **Typical workflows**:
   - Initial setup (3-command sequence)
   - Adding new projects (--all flag usage)
   - Troubleshooting (validation with --verbose)

---

#### Subsection 4: Validation & Troubleshooting

**Content to include**:
1. **Validation command**:
   ```bash
   flask jira validate-config [PROJECT_KEY] --verbose
   ```

2. **Common issues** (top 5):
   - Authentication failures → Check env vars
   - Missing fields → Re-run map-fields
   - Invalid field IDs → Verify field exists in JIRA
   - Permission errors → Check API token permissions
   - Sync failures → Run test-create-issue

3. **Cross-references**:
   - Link to `docs/JIRA_LIKES_FIELD_MIGRATION.md` for likes field details
   - Link to `specs/004-cli-jira-field-mapping/quickstart.md` for CLI deep dive

---

### Phase 3: Update Cross-References (10 minutes)

**Goal**: Ensure links to JIRA Configuration section are accurate

1. **Update Quick Start section**:
   - Change "See 'JIRA Configuration' section below" to use anchor link: `[JIRA Configuration](#jira-configuration)`

2. **Verify internal links**:
   ```bash
   # Check for broken anchors
   grep -n "JIRA Configuration" README.md
   ```

3. **Test anchor navigation**:
   - View README.md in GitHub/GitLab/browser
   - Click internal links to verify they jump to correct sections

---

### Phase 4: Validation (15 minutes)

**Goal**: Ensure documentation is complete and accurate

**Checklist**:
- [ ] No Netlify references remain (`grep -i netlify README.md` returns 0 matches)
- [ ] JIRA Configuration section exists after Quick Start
- [ ] All 14 custom fields documented with types and purposes
- [ ] All 4 CLI commands documented with examples
- [ ] Environment variables table includes format examples
- [ ] Token generation steps are complete (5 steps)
- [ ] Troubleshooting subsection addresses top 5 common issues
- [ ] Cross-references to detailed docs are accurate
- [ ] Internal anchor links navigate correctly
- [ ] No trailing whitespace (run pre-commit hooks)

---

## Pre-Commit Validation

Before committing README changes:

```bash
# 1. Check for trailing whitespace
git diff --check

# 2. Verify no Netlify references
grep -i "netlify" README.md  # Should return nothing

# 3. Verify JIRA section exists
grep "## JIRA Configuration" README.md  # Should return 1 match

# 4. Run pre-commit hooks
git add README.md
pre-commit run --files README.md
```

---

## Testing Documentation

### Test 1: New Developer Simulation

**Scenario**: Simulate new developer following README for first time

**Steps**:
1. Have a developer unfamiliar with project read only the JIRA Configuration section
2. Ask them to:
   - Obtain a JIRA API token
   - Configure environment variables
   - Run field mapping CLI command
   - Validate their configuration

**Success Criteria**:
- Completes setup in < 20 minutes (SC-001)
- No external support required (SC-005 - 90% self-service)

---

### Test 2: Accuracy Verification

**Scenario**: Verify CLI command examples are executable

**Steps**:
1. Copy each CLI command example from README
2. Execute in terminal with actual JIRA credentials
3. Verify output matches documented behavior

**Success Criteria**:
- All commands execute without errors (SC-007)
- Output matches documented examples

---

### Test 3: Cross-Reference Validation

**Scenario**: Ensure links to detailed docs are correct

**Steps**:
1. Click every cross-reference link in JIRA Configuration section
2. Verify target document exists and contains relevant information

**Success Criteria**:
- All links resolve successfully (SC-009)
- Linked content is relevant to context

---

## Common Pitfalls to Avoid

| Pitfall | Impact | Prevention |
|---------|--------|------------|
| Including outdated CLI flags | Users run invalid commands | Verify flags against `backend/app/cli/jira_setup.py` |
| Missing required vs optional field distinction | Users skip required fields | Mark required fields explicitly in table |
| Incomplete token generation steps | Users cannot generate tokens | Test token generation flow personally |
| Vague troubleshooting guidance | Users cannot self-resolve issues | Provide specific commands for each issue type |
| Netlify content remnants | Confusion about deployment | Use grep to verify complete removal |

---

## Estimated Timeline

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| Phase 1: Netlify Removal | 15 min | None |
| Phase 2: JIRA Section | 45 min | Phase 1 complete |
| Phase 3: Cross-References | 10 min | Phase 2 complete |
| Phase 4: Validation | 15 min | All phases complete |
| **Total** | **85 min** | - |

---

## Success Metrics Verification

After implementation, verify these metrics:

| Metric (from spec) | How to Verify | Target |
|-------------------|---------------|--------|
| SC-001: Setup time | Time new developer following README | < 20 min |
| SC-002: Config error reduction | Count of required vs optional fields clearly marked | 100% |
| SC-003: Netlify references removed | `grep -i netlify README.md` | 0 matches |
| SC-005: Self-service percentage | Questions answerable in README only | 90% |
| SC-007: Executable examples | CLI commands run successfully | 100% |

---

## References

- **Feature Spec**: `specs/011-readme-jira-docs/spec.md`
- **Research**: `specs/011-readme-jira-docs/research.md`
- **Data Model**: `specs/011-readme-jira-docs/data-model.md`
- **CLI Source Code**: `backend/app/cli/jira_setup.py`
- **Config Format**: `backend/config/jira_projects.json`
- **Existing JIRA Docs**: `docs/JIRA_LIKES_FIELD_MIGRATION.md`
