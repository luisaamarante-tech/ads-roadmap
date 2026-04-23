# Quickstart: Canvas Mode with Conversational Search

**Feature Branch**: `010-canvas-conversational-search`
**Date**: 2026-01-22

## Overview

This document provides a quick integration guide for the Canvas Mode feature, enabling conversational search for the Weni Roadmap.

## Prerequisites

- Node.js 18+ and npm
- Existing weni-roadmap frontend running
- WebChat widget already integrated (via `index.html` script)

## Quick Setup

### 1. Install Dependencies

No new dependencies required. Feature uses existing Vue 3, TypeScript, and Unnnic Design System.

### 2. Import the Composable

```typescript
// In RoadmapView.vue or any component needing canvas functionality
import { useCanvasSearch } from '@/composables/useCanvasSearch';

const {
  isCanvasMode,
  filteredItemIds,
  hasSearchResults,
  enterCanvasMode,
  exitCanvasMode,
} = useCanvasSearch();
```

### 3. Add Canvas Trigger Button

```vue
<template>
  <!-- Add to navbar or header -->
  <unnnic-button
    type="secondary"
    icon-left="search-1"
    text="AI Search"
    @click="enterCanvasMode"
  />
</template>
```

### 4. Integrate Canvas Container

```vue
<template>
  <div :class="{ 'canvas-mode': isCanvasMode }">
    <!-- Normal view (hidden when canvas active) -->
    <RoadmapFilters v-if="!isCanvasMode" v-model="filters" :modules="modules" />
    <RoadmapCardList v-if="!isCanvasMode" :items="items" :status="activeStatus" />

    <!-- Canvas mode view -->
    <CanvasContainer
      v-if="isCanvasMode"
      :filtered-item-ids="filteredItemIds"
      :all-items="allItems"
      @exit="exitCanvasMode"
    />
  </div>
</template>
```

## Component Usage

### CanvasContainer

Main wrapper component that provides the split-panel layout.

```vue
<CanvasContainer
  :filtered-item-ids="filteredItemIds"
  :all-items="allItems"
  @exit="exitCanvasMode"
/>
```

**Props**:
| Prop | Type | Required | Description |
|------|------|----------|-------------|
| `filteredItemIds` | `string[]` | Yes | IDs from search results |
| `allItems` | `RoadmapItem[]` | Yes | All roadmap items for filtering |

**Events**:
| Event | Payload | Description |
|-------|---------|-------------|
| `exit` | - | Emitted when user clicks exit button |

### CanvasSearchResults

Displays filtered roadmap items in the right panel.

```vue
<CanvasSearchResults
  :items="filteredItems"
  :loading="loading"
/>
```

### CanvasEmptyState

Shown when no search results are available.

```vue
<CanvasEmptyState
  :has-search="hasSearchResults"
/>
```

## Composable API Reference

### useCanvasSearch()

```typescript
interface UseCanvasSearchReturn {
  // State
  isCanvasMode: Ref<boolean>;
  filteredItemIds: Ref<string[]>;
  lastSearchResult: Ref<SearchResult | null>;

  // Computed
  hasSearchResults: ComputedRef<boolean>;
  isWaitingForResults: ComputedRef<boolean>;

  // Actions
  enterCanvasMode: () => void;
  exitCanvasMode: () => void;
  clearSearchResults: () => void;
}
```

**Example Usage**:

```typescript
const {
  isCanvasMode,
  filteredItemIds,
  hasSearchResults,
  enterCanvasMode,
  exitCanvasMode,
} = useCanvasSearch();

// Enter canvas mode
function onSearchButtonClick() {
  enterCanvasMode();
}

// Exit canvas mode
function onExitClick() {
  exitCanvasMode();
}

// Watch for search result changes
watch(filteredItemIds, (newIds) => {
  console.log('Search results updated:', newIds);
});
```

## Parser API Reference

### parseSearchResults(text: string)

Extracts `[[SEARCH_RESULT]]` block from message text.

```typescript
import { parseSearchResults } from '@/utils/searchResultParser';

const message = `Here are some features...
[[SEARCH_RESULT]]
- EXPERI-2434
- ENGAGE-4388
[[/SEARCH_RESULT]]`;

const result = parseSearchResults(message);
// result = { ids: ['EXPERI-2434', 'ENGAGE-4388'], hasResults: true, ... }
```

### cleanMessageText(text: string)

Removes `[[SEARCH_RESULT]]` blocks for display purposes.

```typescript
import { cleanMessageText } from '@/utils/searchResultParser';

const cleanText = cleanMessageText(message);
// cleanText = "Here are some features..."
```

## CSS Customization

### Override Panel Widths

```css
/* Custom panel widths */
.canvas-container {
  --canvas-left-panel-width: 35%;
  --canvas-right-panel-width: 65%;
}
```

### Custom Animation Timing

```css
/* Slower transitions */
.canvas-container {
  --canvas-animation-duration: 500ms;
}

/* Faster transitions */
.canvas-container {
  --canvas-animation-duration: 200ms;
}
```

## Testing

### Unit Test Example

```typescript
import { describe, it, expect } from 'vitest';
import { parseSearchResults } from '@/utils/searchResultParser';

describe('parseSearchResults', () => {
  it('extracts valid IDs from search result block', () => {
    const text = `[[SEARCH_RESULT]]
- EXPERI-2434
- ENGAGE-4388
[[/SEARCH_RESULT]]`;

    const result = parseSearchResults(text);

    expect(result).not.toBeNull();
    expect(result?.ids).toEqual(['EXPERI-2434', 'ENGAGE-4388']);
  });

  it('returns null when no block present', () => {
    const result = parseSearchResults('Just normal text');
    expect(result).toBeNull();
  });
});
```

### Component Test Example

```typescript
import { mount } from '@vue/test-utils';
import { describe, it, expect } from 'vitest';
import CanvasEmptyState from '@/components/CanvasMode/CanvasEmptyState.vue';

describe('CanvasEmptyState', () => {
  it('renders search prompt when no results', () => {
    const wrapper = mount(CanvasEmptyState, {
      props: { hasSearch: false },
    });

    expect(wrapper.text()).toContain('Ask a question');
  });
});
```

## Troubleshooting

### WebChat Not Visible in Canvas Mode

**Problem**: WebChat doesn't appear in the left panel.

**Solution**: Ensure the CSS overrides are loaded and `.canvas-mode` class is applied to the parent container.

```css
/* Verify these styles are present */
.canvas-mode .weni-widget {
  position: relative !important;
}
```

### Search Results Not Updating

**Problem**: `[[SEARCH_RESULT]]` blocks are not being parsed.

**Solution**: Check that the WebChat service event listener is properly connected:

```typescript
// In useCanvasSearch.ts
onMounted(() => {
  // Verify WebChat service is available
  const service = window.WeniWebchat?.service;
  if (!service) {
    console.warn('WebChat service not found');
    return;
  }

  service.on('message:received', handleMessage);
});
```

### Animation Jank

**Problem**: Mode transitions are choppy.

**Solution**: Ensure hardware acceleration is enabled:

```css
.canvas-container {
  transform: translateZ(0);
  will-change: transform, opacity;
}
```

## Integration Checklist

- [ ] Import `useCanvasSearch` composable
- [ ] Add canvas trigger button to UI
- [ ] Integrate `CanvasContainer` component
- [ ] Apply `.canvas-mode` class when active
- [ ] Verify CSS overrides for WebChat positioning
- [ ] Test search result parsing with sample messages
- [ ] Verify exit button returns to normal view
- [ ] Test on multiple browsers (Chrome, Firefox, Safari)
