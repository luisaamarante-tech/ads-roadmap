# Contract: ADF to HTML Conversion Specification

**Feature**: 009-jira-text-formatting
**Date**: January 21, 2026
**Version**: 1.0

## Overview

This document specifies the contract for converting Atlassian Document Format (ADF) to sanitized HTML. This contract ensures consistent behavior across the codebase and provides a testing specification.

## API Contract

### Function Signature

```python
def _adf_to_html(self, adf: dict) -> str:
    """
    Convert Atlassian Document Format to sanitized HTML.

    Args:
        adf: ADF JSON structure from JIRA description field

    Returns:
        Sanitized HTML string safe for frontend rendering
    """
```

### Input Format

**Type**: `dict` (JSON object)

**Structure**: ADF document with required fields:
```python
{
    "type": "doc",         # Required: document root
    "version": 1,          # Required: ADF version
    "content": [...]       # Required: array of content nodes
}
```

**Null/Empty Handling**:
- `None` → `""`
- `{}` → `""`
- `{"type": "doc", "content": []}` → `""`

### Output Format

**Type**: `str` (HTML string)

**Guarantees**:
- ✓ Valid HTML5 markup
- ✓ All tags properly closed
- ✓ XSS-safe (sanitized)
- ✓ No inline styles or scripts
- ✓ UTF-8 compatible

## Node Type Conversion Mapping

### Block-Level Nodes

| ADF Type | HTML Output | Attributes | Example |
|----------|-------------|------------|---------|
| `doc` | (wrapper) | - | `<div>...</div>` or no wrapper |
| `paragraph` | `<p>...</p>` | - | `<p>This is text.</p>` |
| `heading` | `<h1>` to `<h6>` | `attrs.level` (1-6) | `<h2>Section Title</h2>` |
| `bulletList` | `<ul>...</ul>` | - | `<ul><li>Item</li></ul>` |
| `orderedList` | `<ol>...</ol>` | - | `<ol><li>Item</li></ol>` |
| `listItem` | `<li>...</li>` | - | `<li>List item content</li>` |
| `codeBlock` | `<pre><code>...</code></pre>` | `attrs.language` (optional) | `<pre><code class="language-python">code</code></pre>` |
| `blockquote` | `<blockquote>...</blockquote>` | - | `<blockquote>Quote text</blockquote>` |
| `hardBreak` | `<br>` | - | `Line 1<br>Line 2` |

### Inline Nodes

| ADF Type | HTML Output | Notes |
|----------|-------------|-------|
| `text` | plain text | Content goes in text node; marks applied as wrappers |

### Text Marks (Formatting)

Text marks wrap text content:

| Mark Type | HTML Tag | Attributes | Example |
|-----------|----------|------------|---------|
| `strong` | `<strong>` | - | `<strong>bold text</strong>` |
| `em` | `<em>` | - | `<em>italic text</em>` |
| `underline` | `<u>` | - | `<u>underlined</u>` |
| `strike` | `<s>` | - | `<s>strikethrough</s>` |
| `code` | `<code>` | - | `<code>inline code</code>` |
| `link` | `<a>` | `attrs.href`, `rel`, `target` | `<a href="https://example.com" rel="noopener noreferrer" target="_blank">link</a>` |

**Multiple Marks**: Applied in order (strong + em = `<strong><em>text</em></strong>`)

## Conversion Examples

### Example 1: Simple Paragraph

**Input (ADF)**:
```json
{
  "type": "doc",
  "version": 1,
  "content": [
    {
      "type": "paragraph",
      "content": [
        {"type": "text", "text": "Hello, world!"}
      ]
    }
  ]
}
```

**Output (HTML)**:
```html
<p>Hello, world!</p>
```

### Example 2: Bold and Italic Text

**Input (ADF)**:
```json
{
  "type": "doc",
  "version": 1,
  "content": [
    {
      "type": "paragraph",
      "content": [
        {"type": "text", "text": "This is "},
        {"type": "text", "text": "bold", "marks": [{"type": "strong"}]},
        {"type": "text", "text": " and "},
        {"type": "text", "text": "italic", "marks": [{"type": "em"}]},
        {"type": "text", "text": "."}
      ]
    }
  ]
}
```

**Output (HTML)**:
```html
<p>This is <strong>bold</strong> and <em>italic</em>.</p>
```

### Example 3: Bullet List

**Input (ADF)**:
```json
{
  "type": "doc",
  "version": 1,
  "content": [
    {
      "type": "bulletList",
      "content": [
        {
          "type": "listItem",
          "content": [
            {
              "type": "paragraph",
              "content": [
                {"type": "text", "text": "First item"}
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
                {"type": "text", "text": "Second item"}
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

**Output (HTML)**:
```html
<ul>
  <li>First item</li>
  <li>Second item</li>
</ul>
```

### Example 4: Link with Text

**Input (ADF)**:
```json
{
  "type": "doc",
  "version": 1,
  "content": [
    {
      "type": "paragraph",
      "content": [
        {"type": "text", "text": "Visit "},
        {
          "type": "text",
          "text": "our docs",
          "marks": [
            {
              "type": "link",
              "attrs": {"href": "https://docs.example.com"}
            }
          ]
        },
        {"type": "text", "text": " for details."}
      ]
    }
  ]
}
```

**Output (HTML)**:
```html
<p>Visit <a href="https://docs.example.com" rel="noopener noreferrer" target="_blank">our docs</a> for details.</p>
```

### Example 5: Code Block

**Input (ADF)**:
```json
{
  "type": "doc",
  "version": 1,
  "content": [
    {
      "type": "codeBlock",
      "attrs": {"language": "python"},
      "content": [
        {"type": "text", "text": "def hello():\n    print('Hello')"}
      ]
    }
  ]
}
```

**Output (HTML)**:
```html
<pre><code class="language-python">def hello():
    print('Hello')</code></pre>
```

### Example 6: Heading

**Input (ADF)**:
```json
{
  "type": "doc",
  "version": 1,
  "content": [
    {
      "type": "heading",
      "attrs": {"level": 2},
      "content": [
        {"type": "text", "text": "Section Title"}
      ]
    }
  ]
}
```

**Output (HTML)**:
```html
<h2>Section Title</h2>
```

### Example 7: Combined Marks (Bold + Italic)

**Input (ADF)**:
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
          "text": "important text",
          "marks": [
            {"type": "strong"},
            {"type": "em"}
          ]
        }
      ]
    }
  ]
}
```

**Output (HTML)**:
```html
<p><strong><em>important text</em></strong></p>
```

## Edge Cases

### Edge Case 1: Empty Document

**Input**: `{"type": "doc", "version": 1, "content": []}`
**Output**: `""`

### Edge Case 2: Empty Paragraph

**Input**: `{"type": "paragraph", "content": []}`
**Output**: `""` (skip empty paragraphs)

### Edge Case 3: Unknown Node Type

**Input**: `{"type": "unknownNode", "content": [...]}`
**Output**: Process children, ignore unknown wrapper

### Edge Case 4: Malformed ADF (Missing Fields)

**Input**: `{"type": "paragraph"}` (no content field)
**Output**: `""` (graceful fallback)

### Edge Case 5: Deeply Nested Lists

**Input**: List with 3+ levels of nesting
**Output**: Preserve nesting structure with proper HTML

### Edge Case 6: Malicious Link URL

**Input**: `{"type": "link", "attrs": {"href": "javascript:alert(1)"}}`
**Output**: Strip link or use safe fallback URL (sanitizer handles this)

### Edge Case 7: Very Long Text

**Input**: Text node with 10,000+ characters
**Output**: Preserve full text (no truncation)

## Sanitization Contract

### Allowlist (Safe Tags)

**Allowed Tags**:
```python
ALLOWED_TAGS = {
    'p', 'br', 'strong', 'em', 'u', 's',
    'ul', 'ol', 'li',
    'code', 'pre',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'blockquote',
    'a'
}
```

**Disallowed Tags** (stripped):
- `<script>`, `<iframe>`, `<object>`, `<embed>`
- `<style>`, `<link>`
- `<form>`, `<input>`, `<button>`
- Any other tag not in allowlist

### Allowlist (Safe Attributes)

**Per-Tag Attributes**:
```python
ALLOWED_ATTRS = {
    'a': ['href', 'rel', 'target'],
    'code': ['class'],  # For language class
}
```

**Disallowed Attributes** (stripped):
- Event handlers: `onclick`, `onerror`, `onload`, etc.
- Inline styles: `style` attribute
- Dangerous attributes: `formaction`, `data-*` (unless explicitly allowed)

### URL Validation

**Allowed Protocols**:
- `http://`
- `https://`
- Relative URLs (converted to absolute if needed)

**Blocked Protocols**:
- `javascript:`
- `data:`
- `vbscript:`
- `file:`

### Security Enhancements

**Link Security**:
- All links get `rel="noopener noreferrer"`
- All links get `target="_blank"`
- Prevents tabnapping and referrer leakage

## Test Cases

### Test Suite: ADF Conversion

```python
def test_adf_to_html_empty_doc():
    adf = {"type": "doc", "version": 1, "content": []}
    assert _adf_to_html(adf) == ""

def test_adf_to_html_simple_paragraph():
    adf = {
        "type": "doc",
        "version": 1,
        "content": [
            {"type": "paragraph", "content": [
                {"type": "text", "text": "Hello"}
            ]}
        ]
    }
    assert _adf_to_html(adf) == "<p>Hello</p>"

def test_adf_to_html_bold_text():
    adf = {
        "type": "doc",
        "version": 1,
        "content": [
            {"type": "paragraph", "content": [
                {"type": "text", "text": "bold", "marks": [{"type": "strong"}]}
            ]}
        ]
    }
    assert _adf_to_html(adf) == "<p><strong>bold</strong></p>"

def test_adf_to_html_bullet_list():
    adf = {
        "type": "doc",
        "version": 1,
        "content": [
            {"type": "bulletList", "content": [
                {"type": "listItem", "content": [
                    {"type": "paragraph", "content": [
                        {"type": "text", "text": "Item 1"}
                    ]}
                ]}
            ]}
        ]
    }
    assert _adf_to_html(adf) == "<ul><li>Item 1</li></ul>"

def test_adf_to_html_link():
    adf = {
        "type": "doc",
        "version": 1,
        "content": [
            {"type": "paragraph", "content": [
                {"type": "text", "text": "link", "marks": [
                    {"type": "link", "attrs": {"href": "https://example.com"}}
                ]}
            ]}
        ]
    }
    result = _adf_to_html(adf)
    assert 'href="https://example.com"' in result
    assert 'rel="noopener noreferrer"' in result
    assert 'target="_blank"' in result

def test_adf_to_html_unknown_node_type():
    adf = {
        "type": "doc",
        "version": 1,
        "content": [
            {"type": "unknownType", "content": [
                {"type": "text", "text": "fallback text"}
            ]}
        ]
    }
    # Should gracefully handle unknown types
    result = _adf_to_html(adf)
    assert "fallback text" in result or result == ""
```

### Test Suite: HTML Sanitization

```python
def test_sanitize_removes_script_tags():
    html = "<p>Safe</p><script>alert(1)</script>"
    assert sanitize_html(html) == "<p>Safe</p>"

def test_sanitize_removes_event_handlers():
    html = '<p onclick="alert(1)">Text</p>'
    assert sanitize_html(html) == "<p>Text</p>"

def test_sanitize_blocks_javascript_urls():
    html = '<a href="javascript:alert(1)">Click</a>'
    result = sanitize_html(html)
    assert "javascript:" not in result

def test_sanitize_allows_safe_tags():
    html = "<p><strong>Bold</strong> and <em>italic</em></p>"
    assert sanitize_html(html) == html

def test_sanitize_adds_link_security_attrs():
    html = '<a href="https://example.com">Link</a>'
    result = sanitize_html(html)
    assert 'rel="noopener noreferrer"' in result
    assert 'target="_blank"' in result
```

## Performance Requirements

**Conversion Time**:
- Simple description (<1KB): <10ms
- Medium description (1-5KB): <50ms
- Large description (5-20KB): <200ms

**Memory Usage**:
- Linear with input size O(n)
- No exponential memory growth
- Garbage collected after conversion

## Versioning

**Contract Version**: 1.0
**Last Updated**: January 21, 2026
**Breaking Changes**: None (initial version)

**Future Versions**:
- 1.1: Add support for tables, media nodes (if needed)
- 2.0: Change sanitization rules (would be breaking)

## Conclusion

This contract provides a complete specification for ADF-to-HTML conversion with XSS prevention. All implementers must adhere to this contract to ensure consistent and secure behavior.
