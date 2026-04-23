# Quickstart: JIRA Custom Fields Configuration

**Feature**: 003-jira-custom-fields
**Date**: December 26, 2025

## Overview

This guide walks you through setting up JIRA custom field configuration for your roadmap projects. You'll learn how to:

1. Set up custom fields for a JIRA project using the CLI
2. Configure multiple projects with different field mappings
3. Verify that custom field data appears in your roadmap
4. Troubleshoot common issues

**Time to complete**: ~10 minutes per project

---

## Prerequisites

Before starting, ensure you have:

- ✅ JIRA Cloud instance with projects created
- ✅ JIRA administrator permissions (to create custom fields)
- ✅ Backend application deployed and running
- ✅ Environment variables configured:
  - `JIRA_BASE_URL`: Your JIRA Cloud URL (e.g., `https://your-domain.atlassian.net`)
  - `JIRA_EMAIL`: Your JIRA account email
  - `JIRA_API_TOKEN`: JIRA API token (generate at [Atlassian Account Settings](https://id.atlassian.com/manage-profile/security/api-tokens))
- ✅ Python 3.14+ environment with dependencies installed
- ✅ Flask application accessible via command line

---

## Step 1: Set Up Your First Project

### 1.1 Run the CLI Setup Command

Navigate to your backend directory and run:

```bash
cd backend
flask jira setup-fields <PROJECT_KEY>
```

**Example**:
```bash
flask jira setup-fields WENI
```

### 1.2 Monitor Progress

The command will display progress as it:

1. ✅ Validates JIRA authentication
2. ✅ Retrieves the Epic issue type ID
3. ✅ Checks for existing custom fields
4. ✅ Creates **13 custom fields** for Epics:
   - **Existing fields** (7): Public Roadmap, Roadmap Status, Module, Release Year, Release Quarter, Release Month, Documentation URL
   - **New fields** (6): Roadmap Title, Roadmap Description, Roadmap Image URL 1-4
5. ✅ Updates the configuration file (`backend/config/jira_projects.json`)

**Expected output**:
```
Validating JIRA authentication...
✓ Authentication successful

Retrieving Epic issue type ID...
✓ Found Epic issue type: 10001

Checking existing custom fields...
✓ No existing fields found

Creating custom fields...
[████████████████████] 6/6 fields created

Updating configuration file...
✓ Configuration updated: backend/config/jira_projects.json

Summary:
--------
Project: WENI
Fields Created: 6
  • Roadmap Title (customfield_10101)
  • Roadmap Description (customfield_10102)
  • Roadmap Image URL 1 (customfield_10103)
  • Roadmap Image URL 2 (customfield_10104)
  • Roadmap Image URL 3 (customfield_10105)
  • Roadmap Image URL 4 (customfield_10106)

Configuration file updated successfully.
Next steps: Add custom field values to your epics in JIRA.
```

### 1.3 Verify Configuration File

Check that the configuration file was created:

```bash
cat backend/config/jira_projects.json
```

**Expected content**:
```json
{
  "version": "1.0",
  "projects": {
    "WENI": {
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

## Step 2: Add Custom Field Values in JIRA

### 2.1 Navigate to an Epic

1. Log in to JIRA
2. Go to your project (e.g., WENI)
3. Open an existing Epic or create a new one

### 2.2 Populate Custom Fields

Scroll down to the custom fields section and fill in:

| Field | Example Value | Required |
|-------|---------------|----------|
| **Roadmap Title** | "AI-Powered Chat Bot Enhancement" | No* |
| **Roadmap Description** | "Enhance our chatbot with advanced AI capabilities including natural language understanding, sentiment analysis, and multi-language support." | No* |
| **Roadmap Image URL 1** | https://example.com/images/chatbot-ui.png | No |
| **Roadmap Image URL 2** | https://example.com/images/ai-flow.png | No |
| **Roadmap Image URL 3** | | No |
| **Roadmap Image URL 4** | | No |

**\*Note**: If these fields are empty, the system will use the epic's default summary and description.

### 2.3 Save the Epic

Click "Update" to save your changes.

---

## Step 3: Verify Roadmap Display

### 3.1 Restart Application (if needed)

If your application was running before you added the configuration file, restart it:

```bash
# Stop the application (Ctrl+C if running in foreground)
# Start it again
flask run
# or
python run.py
```

### 3.2 Trigger a Sync

The application syncs automatically, but you can trigger a manual sync:

```bash
curl -X POST http://localhost:5000/api/sync
```

### 3.3 Check the Roadmap API

Request the roadmap data:

```bash
curl http://localhost:5000/api/roadmap
```

**Look for your custom fields in the response**:
```json
{
  "items": [
    {
      "id": "WENI-123",
      "title": "AI-Powered Chat Bot Enhancement",
      "description": "Enhance our chatbot with advanced AI capabilities...",
      "images": [
        "https://example.com/images/chatbot-ui.png",
        "https://example.com/images/ai-flow.png"
      ],
      "status": "NOW",
      "module": "Platform",
      "releaseYear": 2025,
      "releaseQuarter": "Q1",
      ...
    }
  ]
}
```

### 3.4 View in Frontend

Open your frontend application (e.g., http://localhost:5173) and verify:

- ✅ Custom titles appear instead of epic summaries
- ✅ Custom descriptions appear instead of epic descriptions
- ✅ Images are displayed (if provided)

---

## Step 4: Add More Projects

### 4.1 Repeat for Additional Projects

Run the setup command for each additional project:

```bash
flask jira setup-fields FLOWS
flask jira setup-fields INTG
```

### 4.2 Verify Multi-Project Configuration

Check that all projects are in the config file:

```bash
cat backend/config/jira_projects.json
```

**Expected content**:
```json
{
  "version": "1.0",
  "projects": {
    "WENI": { ... },
    "FLOWS": { ... },
    "INTG": { ... }
  }
}
```

---

## Common Tasks

### Check Existing Configuration

View the current configuration:

```bash
cat backend/config/jira_projects.json | python -m json.tool
```

### Manually Edit Configuration

If you need to update field IDs manually:

1. Edit `backend/config/jira_projects.json`
2. Ensure the JSON is valid (use [JSONLint](https://jsonlint.com/))
3. Restart the application

### Re-run Setup for Existing Project

If you run the setup command for a project that already has fields:

```bash
flask jira setup-fields WENI
```

**The command will**:
- ✅ Detect existing fields and skip creating duplicates
- ✅ Update the configuration file with current field IDs
- ✅ Report which fields already existed

### Validate Configuration

Check if your configuration is valid:

```bash
python -c "
import json
import jsonschema

# Load schema
with open('specs/003-jira-custom-fields/contracts/config-schema.json') as f:
    schema = json.load(f)

# Load config
with open('backend/config/jira_projects.json') as f:
    config = json.load(f)

# Validate
try:
    jsonschema.validate(config, schema)
    print('✓ Configuration is valid')
except jsonschema.ValidationError as e:
    print(f'✗ Configuration error: {e.message}')
"
```

---

## Troubleshooting

### Issue: "Authentication failed"

**Symptoms**: CLI command fails with authentication error

**Solutions**:
1. Verify `JIRA_BASE_URL` is correct (should be `https://your-domain.atlassian.net`)
2. Verify `JIRA_EMAIL` matches your Atlassian account email
3. Verify `JIRA_API_TOKEN` is valid (generate new token if needed)
4. Test authentication manually:
   ```bash
   curl -u "your-email@example.com:your-api-token" \
     "https://your-domain.atlassian.net/rest/api/3/myself"
   ```

### Issue: "Insufficient permissions" or "400 Bad Request"

**Symptoms**: CLI command fails with permission error or Bad Request

**Solutions**:

**For API Restrictions (400 Bad Request)**:
Many JIRA Cloud instances restrict custom field creation via API. If you encounter this:

1. **Create fields manually in JIRA**:
   - Go to JIRA Settings → Issues → Custom Fields
   - Click "Create custom field"
   - Create each of the 6 fields (see table in Step 2.2)
   - Associate with Epic issue type only

2. **Run the command again**:
   ```bash
   flask jira setup-fields YOUR_PROJECT
   ```
   The command will detect existing fields and update configuration

3. **See detailed guide**:
   - Read `backend/CLI_TROUBLESHOOTING.md` for step-by-step instructions

**For Permissions (403 Forbidden)**:
1. Verify you have JIRA Administrator permissions (not just Project Admin)
2. Check that your API token has the correct scopes
3. Contact your JIRA administrator to grant permissions

### Issue: "Project not found"

**Symptoms**: CLI command reports that the project doesn't exist

**Solutions**:
1. Verify the project key is correct (case-sensitive, uppercase)
2. Check that the project exists in JIRA
3. Verify your account has access to the project

### Issue: Custom fields not appearing in JIRA

**Symptoms**: Fields were created but don't show up on epics

**Solutions**:
1. Refresh the JIRA page (hard refresh: Ctrl+Shift+R or Cmd+Shift+R)
2. Check the field configuration in JIRA Settings → Issues → Custom Fields
3. Verify the field context is set to the Epic issue type
4. Add the fields to your Epic screen scheme if needed

### Issue: Roadmap still shows default epic titles

**Symptoms**: API returns epic summary instead of custom title

**Solutions**:
1. Verify custom fields are populated in JIRA
2. Check that configuration file was updated correctly
3. Restart the application to reload configuration
4. Trigger a manual sync
5. Check application logs for configuration errors:
   ```bash
   tail -f backend/logs/app.log | grep -i "config\|custom field"
   ```

### Issue: Images not displaying

**Symptoms**: Image URLs are in API response but don't show in frontend

**Solutions**:
1. Verify image URLs are publicly accessible (test in browser)
2. Check CORS headers on image host
3. Verify URLs use HTTPS protocol
4. Check that URLs point to valid image files (jpg, png, gif, webp)
5. Inspect browser console for image loading errors

### Issue: Configuration file not found

**Symptoms**: Application logs "Configuration file not found, using defaults"

**Solutions**:
1. Verify file exists at `backend/config/jira_projects.json`
2. Check file permissions (application user needs read access)
3. Verify working directory is correct when starting application
4. Use absolute path in configuration loader if needed

---

## Best Practices

### Field Value Guidelines

**Roadmap Title**:
- ✅ Keep under 100 characters for best display
- ✅ Use clear, customer-facing language
- ✅ Avoid internal jargon or ticket numbers
- ✅ Example: "Enhanced Mobile Experience" not "MOBILE-123 refactor"

**Roadmap Description**:
- ✅ Aim for 2-4 sentences
- ✅ Focus on user benefits, not technical details
- ✅ Use plain language accessible to non-technical audience
- ✅ Example: "Users can now access all features on mobile devices with improved performance and intuitive navigation" not "Implemented React Native with Redux state management"

**Image URLs**:
- ✅ Use high-quality images (minimum 800x600px)
- ✅ Optimize for web (< 500KB per image)
- ✅ Use descriptive filenames
- ✅ Host on reliable CDN or image hosting service
- ✅ Use HTTPS URLs only
- ❌ Don't use images with sensitive information
- ❌ Don't use very large images (> 2MB)

### Configuration Management

- ✅ **Version control**: Commit `jira_projects.json` to git
- ✅ **Documentation**: Add comments in commit messages when changing field IDs
- ✅ **Validation**: Always validate JSON before committing
- ✅ **Backup**: Keep a backup before manual edits
- ❌ **Don't**: Store API tokens in the config file
- ❌ **Don't**: Share sensitive project-specific information

### Operational Guidelines

- ✅ **Regular audits**: Review field mappings quarterly
- ✅ **Monitor logs**: Watch for configuration warnings in logs
- ✅ **Test changes**: Validate on staging before production
- ✅ **Document changes**: Keep a changelog of configuration updates
- ❌ **Don't**: Edit configuration in production without testing
- ❌ **Don't**: Delete fields without updating configuration

---

## Next Steps

Now that you have custom fields configured:

1. ✅ **Populate all public epics** with custom field values
2. ✅ **Set up additional projects** using the CLI command
3. ✅ **Train your team** on using custom fields for roadmap content
4. ✅ **Monitor sync logs** to ensure data flows correctly
5. ✅ **Review roadmap display** regularly for quality

For detailed implementation information, see:
- [Technical Plan](./plan.md)
- [Data Model](./data-model.md)
- [API Contracts](./contracts/)

---

## Reference

### CLI Commands

| Command | Description |
|---------|-------------|
| `flask jira setup-fields <PROJECT_KEY>` | Create custom fields for a project |
| `flask jira setup-fields <PROJECT_KEY> --dry-run` | Preview without creating |
| `curl -X POST /api/sync` | Trigger manual sync |

### Configuration File Location

- **Path**: `backend/config/jira_projects.json`
- **Format**: JSON
- **Schema**: `specs/003-jira-custom-fields/contracts/config-schema.json`
- **Example**: `specs/003-jira-custom-fields/contracts/example-config.json`

### Custom Field Names

- `Roadmap Title` - Public display title
- `Roadmap Description` - Public display description
- `Roadmap Image URL 1` - First image
- `Roadmap Image URL 2` - Second image
- `Roadmap Image URL 3` - Third image
- `Roadmap Image URL 4` - Fourth image

### API Endpoints

- `GET /api/roadmap` - Get all roadmap items
- `GET /api/roadmap?module=platform` - Filter by module
- `POST /api/sync` - Trigger manual JIRA sync
- `GET /api/health` - Check application health

---

**Questions or issues?** Check the [Troubleshooting](#troubleshooting) section or contact the development team.
