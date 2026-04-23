# Quickstart Guide: CLI JIRA Custom Field Mapping

**Feature**: 004-cli-jira-field-mapping
**Date**: December 29, 2025
**For**: Developers and System Administrators

## Overview

This guide helps you quickly set up and use the CLI commands to retrieve JIRA custom fields and map them to the roadmap configuration without requiring JIRA admin permissions.

**Time to Complete**: 10-15 minutes per project

---

## Prerequisites

### 1. JIRA Access

You need:
- ✅ Valid JIRA account with access to project(s)
- ✅ Read access to custom fields on Epic issue type
- ❌ JIRA admin permissions NOT required

### 2. Environment Setup

Ensure these environment variables are set:

```bash
export JIRA_BASE_URL="https://yourcompany.atlassian.net"
export JIRA_EMAIL="your.email@company.com"
export JIRA_API_TOKEN="your-jira-api-token"
export JIRA_PROJECT_KEYS="NEXUS,FLOW"  # Comma-separated project keys
```

**How to get JIRA API Token**:
1. Go to: https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Give it a label (e.g., "Roadmap CLI")
4. Copy the token and set it as `JIRA_API_TOKEN`

### 3. Backend Environment

```bash
# Navigate to backend directory
cd backend

# Activate virtual environment (if using venv)
source venv/bin/activate  # Linux/Mac
# OR
.\venv\Scripts\activate  # Windows

# Verify Flask CLI is available
flask --version
```

---

## New Features (Enhancement)

### Automatic Field Matching 🆕
Fields are automatically matched to configuration keys based on name similarity. Saves time by reducing manual selection from 13 fields to typically ~3-5 fields.

### Project-Scope Filtering 🆕
By default, only shows custom fields specific to your project, filtering out global fields shared across all projects. Reduces field list by ~30-70% in multi-project environments. **Optimized for speed** - uses field metadata only, no API calls!

### CLI Flags Available

| Flag | Description | Default | Example |
|------|-------------|---------|---------|
| `--no-auto-match` | Disable automatic field matching | Auto-match enabled | `flask jira map-fields NEXUS --no-auto-match` |
| `--include-global` | Include global custom fields | Project-scoped only | `flask jira map-fields NEXUS --include-global` |
| `--show-all-types` | Show all field types (not just text) | Text fields only | `flask jira map-fields NEXUS --show-all-types` |
| `--dry-run` | Preview changes without writing | Write enabled | `flask jira map-fields NEXUS --dry-run` |
| `--all` | Map fields for all projects in JIRA_PROJECT_KEYS | Single project | `flask jira map-fields --all` |

---

## Quick Start: Map Fields for a Single Project

### Step 1: Run the CLI Command (Enhanced with Auto-Matching)

```bash
flask jira map-fields NEXUS
```

Expected output (with automatic field matching):
```
Retrieving custom fields for project NEXUS...
Filtering to project-scoped fields... ✓ (15 of 45 fields)
✓ 12 text fields after filtering

Attempting automatic field matching...

  ✓ roadmap_title              → Roadmap Title (customfield_10101) [100% confidence]
  ✓ roadmap_description        → Roadmap Description (customfield_10102) [100% confidence]
  ✓ roadmap_status             → Delivery Status (customfield_14621) [87% confidence]
  ✓ module                     → Product Module (customfield_14622) [95% confidence]
  ✓ release_year               → Release Year (customfield_14623) [100% confidence]
  ✓ release_quarter            → Release Quarter (customfield_14624) [100% confidence]
  ✓ release_month              → Release Month (customfield_14625) [100% confidence]
  ✓ documentation_url          → Docs URL (customfield_14626) [85% confidence]

Auto-matched: 8 fields
Need input:   5 fields

Review auto-matched fields? [y/N]: n
```

**New Feature Benefits**:
- 🎯 **Auto-matching**: Fields with similar names are automatically detected (>80% confidence)
- 🎯 **Project-scoped**: Only shows fields specific to your project (filters out 67% noise)
- ⚡ **Faster**: ~1 minute vs 2-3 minutes for manual selection
```

### Step 2: Select Fields Interactively

For each roadmap attribute, you'll see a numbered list of custom fields:

```
Select custom field for Roadmap Title (public display):
  1. Epic Title (customfield_10001) - Text Field (single line)
  2. Public Title (customfield_10101) - Text Field (single line)
  3. Feature Name (customfield_10205) - Text Field (single line)
  ...
  15. Skip this field

Enter selection [1-15]:
```

**What to select**:
- Look for field names that match the purpose (e.g., "Public Title" for Roadmap Title)
- Note the field ID (e.g., `customfield_10101`)
- Choose "Skip" only for optional image URL fields

**Repeat for all 13 fields**:
1. Public Roadmap (checkbox)
2. Roadmap Status
3. Module/Product Area
4. Release Year
5. Release Quarter
6. Release Month
7. Documentation URL
8. Roadmap Title *(new in this feature)*
9. Roadmap Description *(new in this feature)*
10. Roadmap Image URL 1 *(optional)*
11. Roadmap Image URL 2 *(optional)*
12. Roadmap Image URL 3 *(optional)*
13. Roadmap Image URL 4 *(optional)*

### Step 3: Confirm Your Selections

After all selections, review the summary:

```
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

Save configuration? [Y/n]:
```

Type `Y` and press Enter to save.

### Step 4: Verify the Configuration

```bash
# View the updated configuration file
cat backend/config/jira_projects.json
```

You should see your project with all field mappings:

```json
{
  "version": "1.0",
  "projects": {
    "NEXUS": {
      "public_roadmap": "customfield_14619",
      "roadmap_status": "customfield_14621",
      ...
      "roadmap_title": "customfield_10101",
      "roadmap_description": "customfield_10102",
      "roadmap_image_url_1": "customfield_10103",
      "roadmap_image_url_2": "customfield_10104",
      "roadmap_image_url_3": "customfield_10105",
      "roadmap_image_url_4": "customfield_10106"
    }
  }
}
```

---

## Advanced Usage

### Map All Projects at Once

If you have multiple projects in `JIRA_PROJECT_KEYS`:

```bash
flask jira map-fields --all
```

This will run the interactive mapping for each project sequentially.

### Show All Custom Field Types

By default, only text-type fields are shown. To see all custom fields:

```bash
flask jira map-fields NEXUS --show-all-types
```

### Dry Run (Preview Without Saving)

To see what would change without actually updating the file:

```bash
flask jira map-fields NEXUS --dry-run
```

### Verbose Output for Debugging

Enable detailed logging:

```bash
flask jira map-fields NEXUS --verbose
```

---

## Validation and Testing

### Step 1: Validate Configuration

After mapping, validate that all field IDs are accessible:

```bash
flask jira validate-config NEXUS
```

Expected output:
```
Validating configuration for project NEXUS...

  ✓ public_roadmap (customfield_14619)
  ✓ roadmap_status (customfield_14621)
  ✓ module (customfield_14622)
  ...
  ✓ roadmap_image_url_4 (customfield_10106)

================================================================
Validation Summary
================================================================
Fields Validated: 13
Valid: 13 ✓
Invalid: 0
Inaccessible: 0

Configuration is valid and ready to use.
```

### Step 2: Test Sync

Run a test sync to verify data extraction works:

```bash
# Run sync once (don't start background scheduler)
flask sync run --once
```

Check the sync output for your project to ensure fields are being read correctly.

### Step 3: Verify in Roadmap UI

1. Start the backend: `flask run`
2. Start the frontend: `cd ../frontend && npm run dev`
3. Open the roadmap in your browser
4. Verify that:
   - Epics appear with custom titles and descriptions
   - Images display when URLs are present
   - All data looks correct

---

## Common Issues and Solutions

### Issue: "JIRA authentication failed"

**Cause**: Invalid credentials

**Solution**:
```bash
# Test JIRA authentication
curl -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  "$JIRA_BASE_URL/rest/api/3/myself"
```

If this returns 401/403, regenerate your API token.

---

### Issue: "No custom fields found for project"

**Cause**: Project has no custom fields or they're not on Epic issue type

**Solution**:
1. Verify custom fields exist in JIRA: Settings → Issues → Custom Fields
2. Check fields are associated with Epic issue type
3. Verify you have permission to view the fields

---

### Issue: "Cannot write to configuration file"

**Cause**: Permission denied on `backend/config/jira_projects.json`

**Solution**:
```bash
# Check file permissions
ls -la backend/config/jira_projects.json

# Make writable (if needed)
chmod 644 backend/config/jira_projects.json
```

---

### Issue: "Project 'XYZ' not found or not accessible"

**Cause**: Project key doesn't exist or you don't have access

**Solution**:
1. Verify project key is correct (uppercase, alphanumeric)
2. Check you can access the project in JIRA UI
3. Verify project key in JIRA: Project Settings → Details

---

### Issue: "Selected field doesn't appear in sync"

**Cause**: Field is empty in JIRA epics or wrong field selected

**Solution**:
1. Check epic in JIRA has value in the custom field
2. Run validation to verify field is accessible: `flask jira validate-config`
3. Re-run mapping if wrong field was selected

---

## Tips and Best Practices

### 1. Field Naming Convention

When creating custom fields in JIRA (manually), use clear names:
- ✅ "Roadmap Title" (clear purpose)
- ✅ "Public Description" (clear scope)
- ❌ "Field 1" (ambiguous)
- ❌ "Custom Text" (unclear purpose)

### 2. Optional Image Fields

You can skip image URL fields if you don't plan to use images:
- Select "Skip this field" when prompted
- Fields will be set to placeholder IDs in configuration
- No images will be displayed in roadmap (expected behavior)

### 3. Testing Changes

After mapping fields, always:
1. ✅ Run validation
2. ✅ Test sync
3. ✅ Check roadmap UI
4. ✅ Verify with real epic data

### 4. Documentation

Keep a record of your field mappings:
```bash
# Export current configuration
cp backend/config/jira_projects.json \
   backend/config/jira_projects.backup.json

# Add to version control
git add backend/config/jira_projects.json
git commit -m "feat(config): map JIRA custom fields for NEXUS project"
```

### 5. Multiple Environments

If you have dev/staging/production JIRA instances:
- Field IDs may differ across environments
- Run `map-fields` separately for each environment
- Store configurations in environment-specific files or use environment variables

---

## Utility Commands

### List All Custom Fields

Explore available fields without mapping:

```bash
flask jira list-fields NEXUS
```

Output:
```
Custom Fields for Project: NEXUS

ID                  Name                    Type
------------------  ----------------------  ----------------------------
customfield_10001   Epic Title             Text Field (single line)
customfield_10002   Epic Description       Text Field (multi-line)
...
```

### Export Field List to JSON

```bash
flask jira list-fields NEXUS --format json > nexus-fields.json
```

Useful for sharing with team or documentation.

---

## Next Steps

After completing the quickstart:

1. **Add More Projects**: Run `map-fields` for each project in your JIRA instance
2. **Set Up Sync**: Configure automated sync schedule (see main README)
3. **Customize Display**: Adjust frontend to show images and custom content
4. **Monitor**: Set up logging and monitoring for sync errors

---

## Command Reference

| Command | Purpose | Example |
|---------|---------|---------|
| `flask jira map-fields PROJECT_KEY` | Map fields for one project | `flask jira map-fields NEXUS` |
| `flask jira map-fields --all` | Map fields for all projects | `flask jira map-fields --all` |
| `flask jira validate-config [PROJECT]` | Validate configuration | `flask jira validate-config NEXUS` |
| `flask jira list-fields PROJECT_KEY` | List available fields | `flask jira list-fields NEXUS` |

---

## Getting Help

**View command help**:
```bash
flask jira map-fields --help
flask jira validate-config --help
flask jira list-fields --help
```

**Enable verbose output for debugging**:
```bash
flask jira map-fields NEXUS --verbose
```

**Check logs**:
```bash
tail -f backend/logs/app.log  # If logging is configured
```

**Report issues**:
- Include command output with `--verbose` flag
- Share configuration file (mask sensitive data)
- Provide JIRA project key and field IDs

---

## Summary Checklist

Before considering the setup complete:

- [ ] Environment variables set (`JIRA_BASE_URL`, `JIRA_EMAIL`, `JIRA_API_TOKEN`, `JIRA_PROJECT_KEYS`)
- [ ] API token tested and working
- [ ] Ran `flask jira map-fields` for each project
- [ ] Selected all 13 fields (or skipped optional ones intentionally)
- [ ] Confirmed and saved configuration
- [ ] Ran `flask jira validate-config` successfully
- [ ] Tested sync with `flask sync run --once`
- [ ] Verified roadmap display in UI
- [ ] Committed configuration to version control
- [ ] Documented field mappings for team reference

---

## Time Estimates

| Task | Time |
|------|------|
| Environment setup (first time) | 5 minutes |
| Map fields for one project | 5-7 minutes |
| Validate and test | 3 minutes |
| Map additional projects | 5 minutes each |

**Total for first project**: ~15 minutes
**Total for additional projects**: ~5 minutes each

---

## Further Reading

- [CLI Command Specifications](./contracts/cli-commands.md) - Detailed command documentation
- [Data Model](./data-model.md) - Understanding the configuration structure
- [Research Notes](./research.md) - Technical decisions and alternatives
- [Feature Specification](./spec.md) - Complete feature requirements

---

**Ready to start?** Jump to [Quick Start: Map Fields for a Single Project](#quick-start-map-fields-for-a-single-project) and configure your first project in 10 minutes!
