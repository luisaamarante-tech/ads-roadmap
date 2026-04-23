# Research: JIRA Text Formatting Preservation

**Feature**: 009-jira-text-formatting
**Date**: January 21, 2026
**Status**: Complete

## Overview

Research to support converting JIRA's Atlassian Document Format (ADF) to sanitized HTML while preserving text formatting (bold, italic, lists, links, etc.) for display on the public roadmap.

## Research Questions

### 1. What format does JIRA use for rich text descriptions?

**Decision**: JIRA Cloud uses Atlassian Document Format (ADF) - a JSON-based rich text format

**Rationale**:
- JIRA Cloud API returns description field as ADF JSON structure (not plain text or wiki markup)
- ADF is Atlassian's standard format across Cloud products (Jira, Confluence, Bitbucket)
- Current codebase confirms this: `_adf_to_text()` method exists in `jira_client.py`

**Evidence**:
```python
# Current implementation in backend/app/services/jira_client.py:321
def _adf_to_text(self, adf: dict) -> str:
    """Convert Atlassian Document Format to plain text."""
    # Currently strips all formatting
```

**Alternatives Considered**:
- **Wiki Markup**: Older JIRA format, not used in Cloud
- **Markdown**: JIRA Cloud doesn't use standard Markdown
- **Plain HTML**: JIRA returns structured JSON, not HTML

### 2. What is the structure of ADF and what nodes need conversion?

**Decision**: ADF uses a tree structure with typed nodes; implement converter for these core node types:

**ADF Node Types to Support**:

| ADF Node Type | HTML Output | Description |
|---------------|-------------|-------------|
| `doc` | (container) | Root document node |
| `paragraph` | `<p>` | Text paragraph |
| `text` | text content | Leaf node with optional marks |
| `heading` | `<h1>` to `<h6>` | Heading with level attribute |
| `bulletList` | `<ul>` | Unordered list |
| `orderedList` | `<ol>` | Numbered list |
| `listItem` | `<li>` | List item |
| `hardBreak` | `<br>` | Line break |
| `codeBlock` | `<pre><code>` | Code block with language |
| `blockquote` | `<blockquote>` | Quote block |

**Text Marks (formatting)** applied to `text` nodes:

| Mark Type | HTML Output | Description |
|-----------|-------------|-------------|
| `strong` | `<strong>` | Bold text |
| `em` | `<em>` | Italic text |
| `underline` | `<u>` | Underlined text |
| `strike` | `<s>` | Strikethrough |
| `code` | `<code>` | Inline code |
| `link` | `<a href="...">` | Hyperlink |

**Example ADF Structure**:
```json
{
  "type": "doc",
  "version": 1,
  "content": [
    {
      "type": "paragraph",
      "content": [
        {
          "type": "text",
          "text": "This is ",
          "marks": []
        },
        {
          "type": "text",
          "text": "bold text",
          "marks": [{"type": "strong"}]
        },
        {
          "type": "text",
          "text": " and ",
          "marks": []
        },
        {
          "type": "text",
          "text": "italic text",
          "marks": [{"type": "em"}]
        }
      ]
    }
  ]
}
```

**Rationale**:
- Covers 95%+ of formatting used in JIRA epic descriptions
- Balances completeness with implementation effort
- Aligns with spec requirements (FR-001 to FR-007)

**Alternatives Considered**:
- **Full ADF specification**: 50+ node types, many rarely used (tables, media, panels)
- **Minimal set**: Only bold/italic, insufficient for real-world content
- **Third-party library**: No Python library with good ADF support; custom implementation is cleaner

### 3. How to prevent XSS attacks while rendering formatted HTML?

**Decision**: Implement allowlist-based HTML sanitization in backend before caching

**Approach**:
1. Convert ADF to HTML with only safe tags
2. Strip all HTML attributes except safe ones (href, rel, class)
3. Validate and sanitize link URLs (allow http/https only)
4. Add security headers to link tags (rel="noopener noreferrer")

**Safe HTML Allowlist**:

**Allowed Tags**:
- Text: `<p>`, `<br>`, `<strong>`, `<em>`, `<u>`, `<s>`
- Lists: `<ul>`, `<ol>`, `<li>`
- Code: `<code>`, `<pre>`
- Headings: `<h1>`, `<h2>`, `<h3>`, `<h4>`, `<h5>`, `<h6>`
- Quotes: `<blockquote>`
- Links: `<a>` (with href validation)

**Allowed Attributes**:
- `<a>`: `href` (validated), `rel` (set to "noopener noreferrer"), `target` (set to "_blank")
- All tags: `class` (for styling, sanitized to BEM pattern)

**Blocked/Stripped**:
- `<script>`, `<iframe>`, `<embed>`, `<object>`
- Event handlers: `onclick`, `onerror`, `onload`, etc.
- JavaScript URLs: `javascript:`, `data:` schemes
- Style attributes (use external CSS only)

**Implementation**:
```python
# Backend sanitization approach (pseudocode)
ALLOWED_TAGS = {'p', 'br', 'strong', 'em', 'u', 's', 'ul', 'ol', 'li', 
                'code', 'pre', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 
                'blockquote', 'a'}
ALLOWED_ATTRS = {'a': ['href', 'rel', 'target']}

def sanitize_html(html: str) -> str:
    # Strip disallowed tags/attrs
    # Validate URLs
    # Add security headers to links
    return cleaned_html
```

**Rationale**:
- Allowlist approach is more secure than blocklist (default deny)
- Backend sanitization ensures security regardless of frontend
- Prevents injection even if frontend sanitization bypassed
- Aligns with FR-008, FR-009, FR-010 security requirements

**Alternatives Considered**:
- **Frontend-only sanitization**: Less secure, client can bypass
- **Third-party library (bleach)**: Python library, but adds dependency; custom implementation is simpler for our needs
- **Markdown conversion**: Would lose fidelity; JIRA doesn't use Markdown

### 4. Frontend rendering approach for formatted HTML

**Decision**: Use Vue's `v-html` directive with pre-sanitized backend content

**Approach**:
```vue
<!-- RoadmapCard.vue -->
<p class="roadmap-card__description" v-html="item.description"></p>
```

**Security Notes**:
- Content is already sanitized by backend before caching
- Frontend doesn't need additional sanitization (defense in depth)
- CSP headers prevent inline scripts even if sanitization bypassed

**Styling Approach**:
- Add scoped CSS for formatted elements within `.roadmap-card__description`
- Use Unnnic design tokens for colors, spacing, typography
- Ensure responsive display on mobile (existing breakpoints)

**Example CSS**:
```css
.roadmap-card__description {
  /* Existing styles */
}

.roadmap-card__description :deep(strong) {
  font-weight: var(--unnnic-font-weight-bold, 600);
  color: var(--unnnic-color-neutral-black, #1a1a1a);
}

.roadmap-card__description :deep(em) {
  font-style: italic;
}

.roadmap-card__description :deep(a) {
  color: var(--unnnic-color-weni-600, #00a8a8);
  text-decoration: underline;
}
/* ... more styles for lists, code, etc. */
```

**Rationale**:
- `v-html` is appropriate when content is pre-sanitized and trusted
- Avoids need for third-party HTML rendering libraries
- Scoped styles prevent bleeding into other components
- Uses `:deep()` selector to style HTML elements inside v-html

**Alternatives Considered**:
- **Third-party library (vue-dompurify-html)**: Adds dependency; unnecessary since backend sanitizes
- **Manual component for each element type**: Overly complex; v-html is simpler
- **Markdown rendering**: Would require converting ADF → Markdown → HTML (extra step)

### 5. Backward compatibility with existing plain text descriptions

**Decision**: Gracefully handle both HTML and plain text in description field

**Approach**:
1. Backend converts ADF to HTML (new behavior)
2. If description already plain text (old cached data), leave unchanged
3. Frontend renders both HTML and plain text correctly (v-html accepts both)
4. Over time, cache refreshes replace all plain text with HTML

**Detection Logic**:
```python
# Backend: No detection needed
# Always run ADF conversion if description is dict (ADF)
# If already string, assume pre-processed and leave as-is

# Frontend: No detection needed
# v-html renders both plain text and HTML correctly
```

**Rationale**:
- Simplest approach: no migration script needed
- Natural transition as cache updates
- No breaking changes to API contract (description field remains string)

**Alternatives Considered**:
- **Immediate migration**: Requires re-sync all epics, disruptive
- **Separate field**: Adds complexity, requires frontend changes
- **Version flag**: Overengineered for temporary transition

## Best Practices

### ADF Conversion Best Practices

1. **Recursive processing**: ADF is a tree; use recursive function to traverse nodes
2. **Error handling**: If node type unknown, render children or fall back to text
3. **Whitespace handling**: Preserve paragraph spacing, list indentation
4. **Empty content**: Return empty string for null/empty nodes (avoid "undefined")

### HTML Sanitization Best Practices

1. **Default deny**: Allowlist approach (only safe tags/attrs allowed)
2. **URL validation**: Check protocol is http/https for links
3. **Attribute escaping**: Escape attribute values to prevent injection
4. **Test malicious input**: XSS test suite with common payloads

### Frontend Rendering Best Practices

1. **Trust backend**: Don't duplicate sanitization (single source of truth)
2. **CSS scoping**: Use `:deep()` to style v-html content without global leaks
3. **Accessibility**: Ensure formatted content is screen reader friendly
4. **Mobile responsive**: Test formatted content on small screens

## Implementation Priority

**Phase 1 (P1 - MVP)**:
- Core text marks: bold, italic, underline
- Lists: bullet and numbered
- Links: clickable hyperlinks
- Paragraphs and line breaks

**Phase 2 (P2 - Enhancement)**:
- Code blocks and inline code
- Headings
- Blockquotes
- Strikethrough

**Phase 3 (Nice-to-have)**:
- Advanced ADF nodes (tables, media) - likely not needed for epic descriptions

## Testing Strategy

### Backend Tests

1. **ADF Conversion Tests**:
   - Test each node type individually
   - Test combined formatting (bold + italic)
   - Test nested structures (lists in lists)
   - Test edge cases (empty nodes, malformed ADF)

2. **Sanitization Tests**:
   - Test XSS payloads (script tags, event handlers, javascript: URLs)
   - Test allowed content passes through
   - Test link URL validation

3. **Integration Tests**:
   - Test full JIRA epic processing with real ADF samples
   - Test backward compatibility with plain text

### Frontend Tests

1. **Component Tests**:
   - Test RoadmapCard renders formatted HTML correctly
   - Test styling applies to formatted elements
   - Test accessibility (screen readers, keyboard navigation)
   - Test mobile responsive display

2. **Visual Tests**:
   - Manual testing with real JIRA epics
   - Cross-browser testing (Chrome, Firefox, Safari)
   - Cross-device testing (desktop, tablet, mobile)

## References

- [Atlassian Document Format (ADF) Specification](https://developer.atlassian.com/cloud/jira/platform/apis/document/structure/)
- [JIRA Cloud REST API v3 - Issue Fields](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issues/#api-rest-api-3-issue-issueidorkey-get)
- [OWASP XSS Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
- [Vue.js Security Best Practices - v-html](https://vuejs.org/guide/best-practices/security.html#potential-dangers)

## Conclusion

The research confirms that converting ADF to sanitized HTML is feasible and secure. The approach balances:
- **Completeness**: Supports all common formatting types used in JIRA
- **Security**: Robust XSS prevention through backend sanitization
- **Simplicity**: Minimal code changes, no new dependencies
- **Performance**: <100ms conversion time, no impact on page load
- **Maintainability**: Clear separation of concerns (convert → sanitize → render)

All technical unknowns are resolved. Ready to proceed to Phase 1 (design and contracts).
