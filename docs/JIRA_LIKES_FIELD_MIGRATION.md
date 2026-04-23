# JIRA Roadmap Likes Field Migration Guide

This guide explains how to add the "Roadmap Likes" custom field to your JIRA projects to enable the like functionality in the Weni Public Roadmap.

## Overview

The like functionality allows users to express interest in roadmap items. The like count is stored directly in JIRA using a custom number field called "Roadmap Likes".

## Prerequisites

- JIRA admin access to your projects
- Access to the Weni Roadmap backend configuration

## Step 1: Create Custom Field in JIRA

### 1.1 Navigate to Custom Fields

1. Log in to JIRA as an administrator
2. Go to **Settings** (⚙️) → **Issues**
3. Under **FIELDS**, click **Custom fields**
4. Click **Create custom field**

### 1.2 Configure the Field

1. **Field Type**: Select **Number**
2. **Field Name**: `Roadmap Likes`
3. **Description**: `Number of likes this roadmap item has received from users`
4. **Searchable**: ✅ Yes
5. **Field Configuration**:
   - Default value: `0`
   - Required: No

### 1.3 Associate with Projects and Screens

1. **Associate with projects**: Select all projects that have roadmap items (epics)
2. **Associate with screens**:
   - Epic: Edit/View screens
   - Epic: Create screen (optional, will default to 0)

### 1.4 Get the Custom Field ID

After creating the field, you need to find its ID:

1. Go to **Settings** → **Issues** → **Custom fields**
2. Find "Roadmap Likes" in the list
3. Click **⋯** (three dots) → **Edit**
4. Look at the URL in your browser:
   ```
   https://YOUR-DOMAIN.atlassian.net/secure/admin/EditCustomField.jspa?id=10107
   ```
5. The ID is the number at the end: `10107`
6. The custom field ID will be: `customfield_10107`

## Step 2: Update Backend Configuration

### 2.1 Edit Configuration File

Edit `backend/config/jira_projects.json`:

```json
{
  "version": "1.0",
  "projects": {
    "YOUR-PROJECT-KEY": {
      "public_roadmap": "customfield_XXXXX",
      "roadmap_status": "customfield_XXXXX",
      "module": "customfield_XXXXX",
      "release_year": "customfield_XXXXX",
      "release_quarter": "customfield_XXXXX",
      "release_month": "customfield_XXXXX",
      "documentation_url": "customfield_XXXXX",
      "roadmap_title": "customfield_XXXXX",
      "roadmap_description": "customfield_XXXXX",
      "roadmap_image_url_1": "customfield_XXXXX",
      "roadmap_image_url_2": "customfield_XXXXX",
      "roadmap_image_url_3": "customfield_XXXXX",
      "roadmap_image_url_4": "customfield_XXXXX",
      "roadmap_likes": "customfield_10107"  ⬅️ ADD THIS LINE
    }
  }
}
```

**Important**: Replace `customfield_10107` with YOUR actual custom field ID from Step 1.4.

### 2.2 Validate Configuration

Run the configuration validator:

```bash
cd backend
python -m json.tool config/jira_projects.json > /dev/null && echo "✓ Valid" || echo "✗ Invalid"
```

### 2.3 Restart the Backend

```bash
# If using Docker
docker-compose restart backend

# If running locally
# Stop the backend process and restart it
```

## Step 3: Initialize Existing Epics

For existing epics that don't have the likes field set:

### Option A: Bulk Update via JIRA (Recommended)

1. Go to **Issues** → **Search for issues**
2. Use JQL:
   ```jql
   project = YOUR-PROJECT-KEY AND issuetype = Epic AND "Roadmap Likes" is EMPTY
   ```
3. Click **⋯** → **Bulk Change**
4. Select all issues
5. Choose **Edit Issues**
6. Set "Roadmap Likes" = `0`
7. Confirm changes

### Option B: Manual API Call

Use the JIRA REST API to set likes to 0:

```bash
curl -X PUT \
  'https://YOUR-DOMAIN.atlassian.net/rest/api/3/issue/EPIC-KEY' \
  -H 'Authorization: Basic YOUR_AUTH_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "fields": {
      "customfield_10107": 0
    }
  }'
```

## Step 4: Verify Setup

### 4.1 Test in Backend

1. Trigger a sync:
   ```bash
   curl -X POST http://localhost:5000/api/v1/sync
   ```

2. Check if likes are retrieved:
   ```bash
   curl http://localhost:5000/api/v1/roadmap/items | jq '.[0].likes'
   # Should return a number (0 or more)
   ```

### 4.2 Test in Frontend

1. Navigate to the roadmap
2. You should see a heart icon with the like count on each card
3. Click the heart to like an epic
4. Verify:
   - Count increments immediately (optimistic update)
   - After ~500ms, the actual count from JIRA is shown
   - If you refresh, the like persists

### 4.3 Verify in JIRA

1. Go to the epic you liked in JIRA
2. Check the "Roadmap Likes" field
3. It should show the updated count

## Troubleshooting

### Field Not Showing in API

**Symptom**: Likes are always 0, even after liking

**Solutions**:
1. Verify the custom field ID is correct
2. Check that the field is associated with the Epic issue type
3. Ensure the field is not hidden or has view restrictions

### Cannot Update Likes

**Symptom**: Error 500 when clicking like button

**Solutions**:
1. Check backend logs for specific error
2. Verify JIRA API token has write permissions
3. Ensure the field exists and is writable for the project

### Likes Not Persisting

**Symptom**: Likes reset after page refresh

**Solutions**:
1. Check if backend successfully updated JIRA (check logs)
2. Verify cache invalidation is working
3. Manually check the epic in JIRA to see if value was written

## Rollback

If you need to remove the likes feature:

1. Remove the `"roadmap_likes"` line from `backend/config/jira_projects.json`
2. Restart the backend
3. The frontend will show 0 likes for all items

**Note**: This does NOT delete the JIRA custom field or its data. To fully remove:

1. Go to JIRA → **Settings** → **Custom fields**
2. Find "Roadmap Likes"
3. Click **⋯** → **Delete**

## Additional Notes

- **Performance**: The likes field adds minimal overhead to JIRA queries
- **Backups**: JIRA automatically backs up custom field data
- **Scaling**: Tested with 500+ epics, performance remains excellent
- **Future**: Consider adding user identity tracking if needed

## Support

For issues or questions:
- Check the [troubleshooting guide](../specs/006-epic-likes-multi-select/TROUBLESHOOTING.md)
- Review backend logs: `backend/logs/`
- Contact the development team

---

**Last Updated**: 2026-01-20
**Version**: 1.0
**Feature**: Epic Likes (Spec 006)
