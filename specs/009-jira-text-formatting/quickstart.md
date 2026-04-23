# Quickstart: JIRA Text Formatting Integration

**Feature**: 009-jira-text-formatting
**Date**: January 21, 2026
**Audience**: Developers implementing or testing the feature

## Overview

This guide demonstrates how to use the JIRA text formatting feature, including backend conversion, frontend rendering, and testing approaches.

## Prerequisites

- Python 3.11+ with dependencies installed
- Node.js 18+ with npm
- Running backend server with JIRA configuration
- Access to JIRA Cloud with at least one epic

## Backend Integration

### 1. Using ADF to HTML Conversion

The `JiraClient` class automatically converts ADF descriptions to HTML during sync:

```python
# backend/app/services/jira_client.py

from app.services.jira_client import JiraClient
from app.services.html_sanitizer import HTMLSanitizer

# Initialize client
client = JiraClient()

# Fetch public epics (conversion happens automatically)
roadmap_items = client.fetch_public_roadmap_items()

# Each item has HTML description
for item in roadmap_items:
    print(f"Epic: {item.title}")
    print(f"Description (HTML): {item.description}")
    # Description is now sanitized HTML, ready for display
```

### 2. Manual Conversion (for testing)

Convert ADF to HTML directly:

```python
from app.services.jira_client import JiraClient

client = JiraClient()

# Sample ADF from JIRA
adf_input = {
    "type": "doc",
    "version": 1,
    "content": [
        {
            "type": "paragraph",
            "content": [
                {"type": "text", "text": "This is "},
                {"type": "text", "text": "bold", "marks": [{"type": "strong"}]},
                {"type": "text", "text": " text."}
            ]
        }
    ]
}

# Convert to HTML
html_output = client._adf_to_html(adf_input)
print(html_output)
# Output: <p>This is <strong>bold</strong> text.</p>
```

### 3. HTML Sanitization

The sanitizer runs automatically during conversion, but can be used standalone:

```python
from app.services.html_sanitizer import HTMLSanitizer

sanitizer = HTMLSanitizer()

# Potentially unsafe HTML
unsafe_html = '<p>Safe text</p><script>alert("XSS")</script>'

# Sanitize
safe_html = sanitizer.sanitize(unsafe_html)
print(safe_html)
# Output: <p>Safe text</p>
# (script tag removed)

# Links get security attributes
unsafe_link = '<a href="https://example.com">Link</a>'
safe_link = sanitizer.sanitize(unsafe_link)
print(safe_link)
# Output: <a href="https://example.com" rel="noopener noreferrer" target="_blank">Link</a>
```

### 4. Testing Backend Conversion

Run unit tests for ADF conversion:

```bash
cd backend

# Run conversion tests
pytest tests/unit/test_jira_client.py::test_adf_to_html_* -v

# Run sanitization tests
pytest tests/unit/test_html_sanitizer.py -v

# Run with coverage
pytest --cov=app/services tests/unit/test_jira_client.py tests/unit/test_html_sanitizer.py
```

## Frontend Integration

### 1. Display Formatted Description

The `RoadmapCard` component uses `v-html` to render formatted descriptions:

```vue
<!-- frontend/src/components/RoadmapCard.vue -->
<template>
  <article class="roadmap-card">
    <header class="roadmap-card__header">
      <h3 class="roadmap-card__title">{{ item.title }}</h3>
    </header>

    <div v-if="isExpanded" class="roadmap-card__content">
      <!-- v-html renders the sanitized HTML from backend -->
      <div 
        class="roadmap-card__description" 
        v-html="item.description"
      ></div>
    </div>
  </article>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import type { RoadmapItem } from '@/types/roadmap';

interface Props {
  item: RoadmapItem;
}

const props = defineProps<Props>();
const isExpanded = ref(false);
</script>

<style scoped>
/* Style formatted content using :deep() selector */
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
  transition: color 0.2s ease;
}

.roadmap-card__description :deep(a:hover) {
  color: var(--unnnic-color-weni-700, #008f8f);
}

.roadmap-card__description :deep(ul),
.roadmap-card__description :deep(ol) {
  margin: 12px 0;
  padding-left: 24px;
}

.roadmap-card__description :deep(li) {
  margin: 6px 0;
}

.roadmap-card__description :deep(code) {
  background: var(--unnnic-color-neutral-soft, #f5f5f5);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 0.9em;
}

.roadmap-card__description :deep(pre) {
  background: var(--unnnic-color-neutral-soft, #f5f5f5);
  padding: 12px;
  border-radius: 8px;
  overflow-x: auto;
}

.roadmap-card__description :deep(pre code) {
  background: none;
  padding: 0;
}
</style>
```

### 2. Type Definition

The `RoadmapItem` type remains unchanged (description is still a string):

```typescript
// frontend/src/types/roadmap.ts

export interface RoadmapItem {
  id: string;
  title: string;
  description: string; // Now contains HTML instead of plain text
  status: DeliveryStatus;
  module: string;
  moduleId: string;
  releaseYear: number;
  releaseQuarter: Quarter;
  releaseMonth: number | null;
  images: string[];
  documentationUrl: string | null;
  likes: number;
  lastSyncedAt: string;
}
```

### 3. Testing Frontend Rendering

Test the component with formatted HTML:

```typescript
// frontend/tests/components/RoadmapCard.spec.ts

import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import RoadmapCard from '@/components/RoadmapCard.vue';
import type { RoadmapItem } from '@/types/roadmap';

describe('RoadmapCard - Formatted Description', () => {
  const mockItem: RoadmapItem = {
    id: 'PROJ-123',
    title: 'Test Feature',
    description: '<p>This is <strong>bold</strong> and <em>italic</em> text.</p>',
    status: 'NOW',
    module: 'Test Module',
    moduleId: 'test-module',
    releaseYear: 2026,
    releaseQuarter: 'Q1',
    releaseMonth: 1,
    images: [],
    documentationUrl: null,
    likes: 0,
    lastSyncedAt: '2026-01-21T00:00:00Z',
  };

  it('renders formatted HTML description', () => {
    const wrapper = mount(RoadmapCard, {
      props: {
        item: mockItem,
        autoExpand: true, // Start expanded
      },
    });

    const description = wrapper.find('.roadmap-card__description');
    
    // Check HTML was rendered
    expect(description.html()).toContain('<strong>bold</strong>');
    expect(description.html()).toContain('<em>italic</em>');
  });

  it('renders links with security attributes', () => {
    const itemWithLink: RoadmapItem = {
      ...mockItem,
      description: '<p>Visit <a href="https://example.com" rel="noopener noreferrer" target="_blank">our docs</a></p>',
    };

    const wrapper = mount(RoadmapCard, {
      props: {
        item: itemWithLink,
        autoExpand: true,
      },
    });

    const link = wrapper.find('.roadmap-card__description a');
    expect(link.attributes('href')).toBe('https://example.com');
    expect(link.attributes('rel')).toBe('noopener noreferrer');
    expect(link.attributes('target')).toBe('_blank');
  });

  it('handles plain text descriptions (backward compatibility)', () => {
    const itemWithPlainText: RoadmapItem = {
      ...mockItem,
      description: 'This is plain text without formatting.',
    };

    const wrapper = mount(RoadmapCard, {
      props: {
        item: itemWithPlainText,
        autoExpand: true,
      },
    });

    const description = wrapper.find('.roadmap-card__description');
    expect(description.text()).toBe('This is plain text without formatting.');
  });
});
```

## End-to-End Testing

### 1. Create JIRA Epic with Formatting

1. Go to your JIRA project
2. Create a new Epic
3. In the description, add formatted text:
   ```
   This feature adds *authentication* support.

   Features:
   - Email login
   - Password reset
   - OAuth2 integration

   See [documentation](https://docs.example.com) for details.
   ```
4. Mark the epic as public (set the public roadmap field)

### 2. Sync and Verify Backend

```bash
# Trigger JIRA sync
curl -X POST http://localhost:5000/api/roadmap/sync

# Fetch roadmap data
curl http://localhost:5000/api/roadmap/items | jq '.items[] | select(.id=="PROJ-123") | .description'

# Expected output (HTML):
# "<p>This feature adds <strong>authentication</strong> support.</p>
#  <p>Features:</p>
#  <ul>
#    <li>Email login</li>
#    <li>Password reset</li>
#    <li>OAuth2 integration</li>
#  </ul>
#  <p>See <a href=\"https://docs.example.com\" rel=\"noopener noreferrer\" target=\"_blank\">documentation</a> for details.</p>"
```

### 3. Verify Frontend Display

1. Open the roadmap in browser: `http://localhost:5173/`
2. Find the epic you created
3. Expand the epic card
4. Verify formatting displays correctly:
   - Bold text appears bold
   - List displays with bullets
   - Link is clickable and styled
   - Spacing looks natural

### 4. Test Mobile Display

1. Open browser dev tools (F12)
2. Toggle device toolbar (responsive mode)
3. Select mobile device (iPhone, Android)
4. Verify formatting remains readable on small screen

## Common Issues & Solutions

### Issue 1: Formatting Not Appearing

**Symptom**: Description displays as plain text with HTML tags visible

**Cause**: Using `{{ item.description }}` instead of `v-html`

**Solution**:
```vue
<!-- Wrong -->
<p>{{ item.description }}</p>

<!-- Correct -->
<p v-html="item.description"></p>
```

### Issue 2: Styles Not Applying to Formatted Content

**Symptom**: Formatted HTML renders but looks unstyled

**Cause**: Missing `:deep()` selector for scoped styles

**Solution**:
```css
/* Wrong - won't work with scoped styles */
.roadmap-card__description strong {
  font-weight: bold;
}

/* Correct - use :deep() selector */
.roadmap-card__description :deep(strong) {
  font-weight: var(--unnnic-font-weight-bold, 600);
}
```

### Issue 3: XSS Warning in Console

**Symptom**: Browser logs security warning about unsafe HTML

**Cause**: Content not properly sanitized by backend

**Solution**: Verify backend sanitizer is running:
```python
# In jira_client.py, ensure sanitization happens:
def _extract_description(self, description_field) -> str:
    html = self._adf_to_html(description_field)
    return HTMLSanitizer().sanitize(html)  # Must sanitize!
```

### Issue 4: Links Not Opening in New Tab

**Symptom**: Clicking links replaces current page instead of opening new tab

**Cause**: Missing `target="_blank"` attribute

**Solution**: Sanitizer should add this automatically:
```python
# In html_sanitizer.py:
if tag == 'a':
    attrs['target'] = '_blank'
    attrs['rel'] = 'noopener noreferrer'
```

## Performance Testing

### Backend Performance

Measure ADF conversion time:

```python
import time
from app.services.jira_client import JiraClient

client = JiraClient()

# Sample large ADF (1000+ words)
large_adf = {...}  # Your test ADF

start = time.time()
html = client._adf_to_html(large_adf)
duration_ms = (time.time() - start) * 1000

print(f"Conversion time: {duration_ms:.2f}ms")
# Should be < 100ms for typical descriptions
```

### Frontend Performance

Measure rendering time:

```typescript
// In browser console
const start = performance.now();
// Expand epic with long formatted description
const duration = performance.now() - start;
console.log(`Render time: ${duration.toFixed(2)}ms`);
// Should be < 50ms for typical descriptions
```

## Rollback Procedure

If issues arise in production:

1. **Backend Rollback**:
   ```bash
   git revert <commit-hash>
   # Redeploy backend
   # Cache will naturally refresh with plain text
   ```

2. **Frontend Rollback**:
   ```bash
   git revert <commit-hash>
   # Redeploy frontend
   # Plain text descriptions will display normally
   ```

3. **Manual Cache Clear** (if needed):
   ```bash
   # Connect to Redis
   redis-cli FLUSHDB
   # Trigger fresh sync
   curl -X POST http://localhost:5000/api/roadmap/sync
   ```

## Next Steps

- Review [contracts/adf-conversion-spec.md](./contracts/adf-conversion-spec.md) for detailed conversion rules
- Check [research.md](./research.md) for ADF format details
- See [data-model.md](./data-model.md) for data structure changes
- Run full test suite: `pytest` (backend) and `npm test` (frontend)

## Support

For questions or issues:
- Review this quickstart
- Check test files for examples
- Consult ADF specification: https://developer.atlassian.com/cloud/jira/platform/apis/document/structure/
- Ask team lead or tech lead
