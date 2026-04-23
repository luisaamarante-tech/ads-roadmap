# Data Model: JIRA Text Formatting Preservation

**Feature**: 009-jira-text-formatting
**Date**: January 21, 2026
**Status**: Complete

## Overview

This document describes the data model changes for preserving JIRA text formatting. The changes are minimal: the `description` field content changes from plain text to sanitized HTML, but the field type remains `str`.

## Entity Changes

### RoadmapItem (Modified)

**Location**: `backend/app/models/roadmap.py`

**Changes**: None to data structure; only content format of `description` field changes

**Before**:
```python
@dataclass
class RoadmapItem:
    id: str
    title: str
    description: str  # Plain text from ADF conversion
    status: DeliveryStatus
    # ... other fields
```

**After**:
```python
@dataclass
class RoadmapItem:
    id: str
    title: str
    description: str  # Sanitized HTML from ADF conversion
    status: DeliveryStatus
    # ... other fields
```

**Field Semantics Change**:

| Field | Type | Before | After | Notes |
|-------|------|--------|-------|-------|
| `description` | `str` | Plain text with line breaks | Sanitized HTML | No type change; content format changes |

**Example Values**:

**Before (Plain Text)**:
```
"This feature adds authentication.\n\nIt includes:\n• Email login\n• Password reset\n\nSee documentation for details."
```

**After (Sanitized HTML)**:
```html
"<p>This feature adds authentication.</p><p>It includes:</p><ul><li>Email login</li><li>Password reset</li></ul><p>See <a href=\"https://docs.example.com\" rel=\"noopener noreferrer\" target=\"_blank\">documentation</a> for details.</p>"
```

**Why No Type Change**:
- Both plain text and HTML are strings
- API contract remains unchanged (JSON field is still `string`)
- Frontend consumers don't need code changes (v-html handles both)
- Backward compatible with cached plain text descriptions
- Avoids complex migration or versioning

## New Entities

### None

No new entities required. Changes are isolated to content processing.

## Processing Flow

### Backend: JIRA Sync → Cache

```
JIRA API (ADF JSON)
    ↓
JiraClient._extract_description(adf_dict)
    ↓
JiraClient._adf_to_html(adf_dict) → HTML string
    ↓
HTMLSanitizer.sanitize(html) → Sanitized HTML
    ↓
RoadmapItem(description=sanitized_html)
    ↓
Cache (Redis) → JSON with HTML description
```

### Frontend: Cache → Display

```
API Response (JSON)
    ↓
RoadmapItem interface (description: string)
    ↓
RoadmapCard component
    ↓
v-html rendering → DOM with formatted content
```

## Validation Rules

### Backend Validation

**During ADF Conversion**:
- ✓ Handle null/empty descriptions → return empty string
- ✓ Handle malformed ADF → fall back to text extraction or empty
- ✓ Unknown node types → render children or skip gracefully

**During HTML Sanitization**:
- ✓ Strip disallowed tags (script, iframe, object, embed, etc.)
- ✓ Remove event handlers (onclick, onerror, onload, etc.)
- ✓ Validate link URLs (allow only http/https protocols)
- ✓ Add security attributes to links (rel="noopener noreferrer")
- ✓ Escape HTML entities in text content

### Frontend Validation

**No validation needed** - content is pre-sanitized by backend

**Display Rules**:
- Render HTML using `v-html` directive
- Apply scoped styles to formatted elements
- Ensure mobile responsive display
- Maintain accessibility (screen reader compatible)

## Migration Strategy

### Backward Compatibility

**Existing Cached Data**:
- Old cached items have plain text descriptions
- New syncs will have HTML descriptions
- Frontend `v-html` handles both correctly (plain text displays as-is, HTML renders formatted)

**No Migration Script Needed**:
- Cache naturally refreshes over time (10-minute TTL)
- Within hours, all descriptions will be HTML
- No breaking changes to API or frontend

**Transition Period**:
- Day 1: Some epics have plain text, new syncs have HTML
- Day 2+: All epics have HTML as cache refreshes
- No observable issues during transition

### Rollback Strategy

**If Issues Arise**:
1. Revert backend changes to use `_adf_to_text()` again
2. Cache clears automatically or manually flush Redis
3. Next sync restores plain text descriptions
4. No data loss, no frontend changes needed

## State Transitions

### None

RoadmapItem has no state machine. Description field is immutable after sync (until next sync overwrites it).

## Relationships

### No Changes

RoadmapItem relationships remain unchanged:
- **Module**: One-to-many (Module has many RoadmapItems)
- **Images**: One-to-many (RoadmapItem has 0-4 images)
- **Documentation URL**: Optional one-to-one link

Description formatting doesn't affect relationships.

## Data Examples

### Example 1: Basic Formatting

**ADF Input** (from JIRA):
```json
{
  "type": "doc",
  "version": 1,
  "content": [
    {
      "type": "paragraph",
      "content": [
        {"type": "text", "text": "This feature adds "},
        {"type": "text", "text": "authentication", "marks": [{"type": "strong"}]},
        {"type": "text", "text": " support."}
      ]
    }
  ]
}
```

**HTML Output** (sanitized):
```html
<p>This feature adds <strong>authentication</strong> support.</p>
```

**JSON API Response**:
```json
{
  "id": "PROJ-123",
  "title": "User Authentication",
  "description": "<p>This feature adds <strong>authentication</strong> support.</p>",
  "status": "NOW",
  "module": "Security",
  ...
}
```

### Example 2: Lists and Links

**ADF Input**:
```json
{
  "type": "doc",
  "version": 1,
  "content": [
    {
      "type": "paragraph",
      "content": [
        {"type": "text", "text": "Features:"}
      ]
    },
    {
      "type": "bulletList",
      "content": [
        {
          "type": "listItem",
          "content": [
            {
              "type": "paragraph",
              "content": [
                {"type": "text", "text": "Email login"}
              ]
            }
          ]
        },
        {
          "type": "listItem",
          "content": [
            {
              "type": "paragraph",
              "content": [
                {"type": "text", "text": "OAuth2 "},
                {
                  "type": "text",
                  "text": "integration",
                  "marks": [
                    {
                      "type": "link",
                      "attrs": {"href": "https://oauth.net/2/"}
                    }
                  ]
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

**HTML Output**:
```html
<p>Features:</p>
<ul>
  <li>Email login</li>
  <li>OAuth2 <a href="https://oauth.net/2/" rel="noopener noreferrer" target="_blank">integration</a></li>
</ul>
```

### Example 3: Code Block

**ADF Input**:
```json
{
  "type": "doc",
  "version": 1,
  "content": [
    {
      "type": "paragraph",
      "content": [
        {"type": "text", "text": "Example usage:"}
      ]
    },
    {
      "type": "codeBlock",
      "attrs": {"language": "python"},
      "content": [
        {"type": "text", "text": "auth.login(username, password)"}
      ]
    }
  ]
}
```

**HTML Output**:
```html
<p>Example usage:</p>
<pre><code class="language-python">auth.login(username, password)</code></pre>
```

## Security Considerations

### XSS Prevention

**Allowlist-Based Sanitization**:
- Only safe HTML tags allowed: `p`, `br`, `strong`, `em`, `u`, `s`, `ul`, `ol`, `li`, `code`, `pre`, `h1-h6`, `blockquote`, `a`
- Only safe attributes allowed: `href`, `rel`, `target`, `class`
- All other tags/attributes stripped

**URL Validation**:
- Links must use `http://` or `https://` protocols
- JavaScript URLs (`javascript:`) blocked
- Data URLs (`data:`) blocked
- Relative URLs resolved to absolute (if needed)

**Security Headers**:
- All links get `rel="noopener noreferrer"` and `target="_blank"`
- Prevents tabnapping attacks

**Defense in Depth**:
- Backend sanitization (primary defense)
- CSP headers prevent inline scripts (secondary defense)
- Frontend uses v-html only with pre-sanitized content (tertiary defense)

## Performance Considerations

### Conversion Performance

**ADF to HTML Conversion**:
- Estimated time: <50ms per epic (recursive processing)
- Runs during JIRA sync, not on user requests
- No impact on page load time (cached data)

**Storage Impact**:
- HTML is slightly larger than plain text (~20-30% increase)
- Typical description: 500-2000 characters
- Cache size increase: negligible (hundreds of KB, not MB)

**Rendering Performance**:
- `v-html` is Vue's native directive, optimized
- No third-party library overhead
- Browser handles HTML rendering natively

## Testing Requirements

### Unit Tests

**Backend**:
- `test_adf_to_html_*`: Test each ADF node type conversion
- `test_sanitize_html_*`: Test XSS prevention for malicious inputs
- `test_extract_description_*`: Test integration of conversion + sanitization

**Frontend**:
- `test_roadmap_card_formatted_description`: Test v-html rendering
- `test_roadmap_card_formatting_styles`: Test CSS applies correctly
- `test_roadmap_card_accessibility`: Test screen reader compatibility

### Integration Tests

**End-to-End**:
- Create JIRA epic with formatted description
- Sync to backend
- Verify HTML in cache
- Verify formatted display on frontend

**Backward Compatibility**:
- Test plain text descriptions still display correctly
- Test mixed content (some HTML, some plain text)

## Conclusion

The data model change is minimal: only the content format of the `description` field changes from plain text to sanitized HTML. The field type (`str`) and API contract remain unchanged, ensuring backward compatibility and smooth deployment.
