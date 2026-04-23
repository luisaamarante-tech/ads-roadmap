# Contract: URL Parameters for Shared Epic Links

**Feature**: Shared Epic Links
**Purpose**: Define URL structure and routing behavior for direct epic navigation
**Scope**: RoadmapView.vue modifications

## URL Structure

### Base URL Pattern

```
{origin}/roadmap?epic={epicId}[&other-params]

Examples:
✅ https://roadmap.weni.ai/roadmap?epic=WENI-123
✅ http://localhost:5173/roadmap?epic=FLOWS-456
✅ https://roadmap.weni.ai/roadmap?epic=ENGAGE-789
```

### Query Parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `epic` | string | Yes | JIRA issue key (PROJECT-NUMBER format) | `WENI-123` |
| `year` | number | No | Filter year (cleared by epic param) | `2026` |
| `quarter` | string | No | Filter quarter (cleared by epic param) | `Q1` |
| `module` | string[] | No | Filter modules (cleared by epic param) | `flows`, `inteligence` |

### Parameter Precedence

**Rule**: When `epic` parameter is present, all filter parameters are ignored and cleared.

**Rationale**: Per specification requirement FR-022, filters must be cleared to ensure the shared epic is visible.

```typescript
// Priority handling
if (route.query.epic) {
  // Clear all filters
  filters.value = {};
  
  // Process epic link
  await handleSharedEpicLink(route.query.epic);
  
  // Remove epic parameter after processing
  router.replace({ query: {} });
}
```

## Routing Behavior

### Scenario 1: Opening Shared Link (New Tab)

**Input URL**: `https://roadmap.weni.ai/roadmap?epic=WENI-123`

**Flow**:
```
1. Page loads, RoadmapView mounts
2. onMounted() checks route.query.epic → found
3. Set sharedEpicId = 'WENI-123'
4. Clear all filters: filters.value = {}
5. Fetch ALL roadmap items (no filter params)
6. Search items for epic with id='WENI-123'
   ├─ Found: Expand epic card, scroll into view
   └─ Not found: Show error toast
7. Remove 'epic' param from URL: router.replace({ query: {} })
8. User can now interact normally with filters
```

**Expected Result**:
- Epic WENI-123 is displayed expanded
- All filters are cleared
- URL is clean: `/roadmap` (no epic param)
- User can apply filters normally after

### Scenario 2: Opening Shared Link (Existing Tab with Filters)

**Initial State**: User viewing `/roadmap?year=2026&quarter=Q1&module=flows`

**User Action**: Clicks shared link `https://roadmap.weni.ai/roadmap?epic=WENI-456`

**Flow**:
```
1. Router navigates to new URL
2. Route guard/watcher detects query change
3. Detect epic parameter presence
4. Override current filters: filters.value = {}
5. Fetch ALL items (ignore previous filters)
6. Find and expand epic WENI-456
7. Remove epic parameter
8. User's previous filters are lost (by design)
```

**Expected Result**:
- Epic WENI-456 is displayed expanded
- Previous filters (2026, Q1, flows) are cleared
- URL becomes `/roadmap`
- User must reapply filters if desired

### Scenario 3: Invalid Epic ID

**Input URL**: `https://roadmap.weni.ai/roadmap?epic=INVALID-999`

**Flow**:
```
1. Parse epic parameter: 'INVALID-999'
2. Fetch all items
3. Search for epic with id='INVALID-999'
4. Not found
5. Show error toast: "Epic INVALID-999 not found or no longer available"
6. Remove epic parameter from URL
7. Display empty roadmap or default view
```

**Expected Result**:
- User sees error notification
- URL is cleared: `/roadmap`
- Page does not crash or show blank screen

### Scenario 4: Malformed Epic Parameter

**Input URL**: `https://roadmap.weni.ai/roadmap?epic=`

**Flow**:
```
1. Parse epic parameter: empty string
2. Detect invalid format
3. Ignore epic parameter (treat as no parameter)
4. Load roadmap normally with default/current filters
5. No error shown (graceful degradation)
```

**Expected Result**:
- Normal roadmap view loads
- No epic expansion
- No error message

## Implementation Contract

### RoadmapView.vue Modifications

#### New State

```typescript
const sharedEpicId = ref<string | null>(null);
const isProcessingSharedEpic = ref(false);
```

#### New Computed

```typescript
const hasSharedEpicParam = computed(() => {
  return !!route.query.epic && typeof route.query.epic === 'string';
});
```

#### New Functions

```typescript
/**
 * Handle shared epic link on mount and route changes.
 * Clears filters, fetches all items, finds and expands epic.
 */
async function handleSharedEpicLink(): Promise<void> {
  const epicId = route.query.epic;
  
  if (!epicId || typeof epicId !== 'string') {
    return;
  }
  
  isProcessingSharedEpic.value = true;
  sharedEpicId.value = epicId;
  
  try {
    // Clear all filters to ensure epic is visible
    filters.value = {};
    
    // Fetch all items without filters
    await handleFetchItems();
    
    // Find and expand the epic
    const expanded = expandEpicById(epicId);
    
    if (!expanded) {
      // Epic not found - show error
      error.value = `Epic ${epicId} not found or no longer available.`;
    }
  } catch (e) {
    console.error('Failed to process shared epic link:', e);
    error.value = 'Failed to load shared epic. Please try again.';
  } finally {
    // Clean up: remove epic parameter from URL
    router.replace({ query: {} });
    sharedEpicId.value = null;
    isProcessingSharedEpic.value = false;
  }
}

/**
 * Find epic in items array and expand it.
 * Returns true if epic found and expanded.
 */
function expandEpicById(epicId: string): boolean {
  const epicIndex = items.value.findIndex((item) => item.id === epicId);
  
  if (epicIndex === -1) {
    return false;
  }
  
  // Find the RoadmapCard component for this epic
  // This requires ref array on RoadmapCardList
  const cardComponent = cardListRef.value?.getCardByIndex(epicIndex);
  
  if (cardComponent) {
    // Programmatically expand the card
    cardComponent.isExpanded = true;
    
    // Scroll card into view
    nextTick(() => {
      cardComponent.$el.scrollIntoView({
        behavior: 'smooth',
        block: 'center',
      });
    });
    
    return true;
  }
  
  return false;
}
```

#### Modified onMounted

```typescript
onMounted(async () => {
  // Check for shared epic link FIRST
  if (hasSharedEpicParam.value) {
    await handleSharedEpicLink();
    return; // Don't load normal filters
  }
  
  // Normal flow: parse filters from URL
  parseFiltersFromURL();
  handleFetchItems();
  handleFetchStats();
  handleFetchModules();
});
```

#### Watch for Route Changes

```typescript
watch(
  () => route.query.epic,
  (newEpicId) => {
    if (newEpicId && typeof newEpicId === 'string') {
      handleSharedEpicLink();
    }
  }
);
```

### RoadmapCardList.vue Modifications

**Add ref array to expose card components**:

```typescript
// In RoadmapCardList.vue
const cardRefs = ref<InstanceType<typeof RoadmapCard>[]>([]);

function getCardByIndex(index: number) {
  return cardRefs.value[index];
}

defineExpose({
  getCardByIndex,
});
```

```vue
<!-- Template -->
<RoadmapCard
  v-for="(item, index) in items"
  :key="item.id"
  :ref="(el) => (cardRefs[index] = el)"
  :item="item"
/>
```

### RoadmapCard.vue Modifications

**Expose isExpanded state**:

```typescript
// In RoadmapCard.vue
defineExpose({
  isExpanded,
});
```

## URL Cleanup Strategy

### When to Remove Epic Parameter

**Timing**: Immediately after epic is found and expanded (or error is shown)

**Rationale**: 
- Prevents confusion if user refreshes page (epic would disappear)
- Allows user to apply filters normally after viewing shared epic
- Clean URL in browser history

**Implementation**:

```typescript
// After successful epic expansion
router.replace({ 
  query: {}, // Remove all query params
  // OR preserve other params if any:
  // query: { ...route.query, epic: undefined }
});
```

## Error Messages

### User-Facing Messages

```typescript
const ERROR_MESSAGES = {
  EPIC_NOT_FOUND: (epicId: string) => 
    `Epic ${epicId} not found. It may have been removed or you don't have access.`,
  
  LOAD_FAILED: 
    'Failed to load the shared epic. Please check your connection and try again.',
  
  INVALID_FORMAT: (epicId: string) =>
    `Invalid epic ID format: ${epicId}. Expected format: PROJECT-123`,
};
```

### Console Logging

```typescript
// Log for debugging
console.info('[SharedEpic] Processing link:', epicId);
console.warn('[SharedEpic] Epic not found:', epicId);
console.error('[SharedEpic] Failed to load:', error);
```

## Accessibility

### ARIA Live Regions

```vue
<div
  role="status"
  aria-live="polite"
  aria-atomic="true"
  class="sr-only"
>
  {{ ariaStatusMessage }}
</div>
```

```typescript
const ariaStatusMessage = computed(() => {
  if (isProcessingSharedEpic.value) {
    return `Loading shared epic ${sharedEpicId.value}`;
  }
  if (error.value) {
    return `Error: ${error.value}`;
  }
  return '';
});
```

### Focus Management

```typescript
// After expanding epic, move focus to epic title
nextTick(() => {
  const epicTitle = document.querySelector(
    `[data-epic-id="${epicId}"] .roadmap-card__title`
  );
  if (epicTitle instanceof HTMLElement) {
    epicTitle.focus();
    epicTitle.setAttribute('tabindex', '-1'); // Make programmatically focusable
  }
});
```

## Testing Contract

### Unit Tests (RoadmapView)

```typescript
describe('RoadmapView - Shared Epic Links', () => {
  it('should detect epic parameter in URL on mount', () => { });
  it('should clear filters when epic parameter present', () => { });
  it('should fetch all items without filters', () => { });
  it('should expand epic when found in items', () => { });
  it('should scroll to expanded epic', () => { });
  it('should remove epic parameter after processing', () => { });
  it('should show error when epic not found', () => { });
  it('should handle malformed epic parameter gracefully', () => { });
  it('should handle empty epic parameter', () => { });
  it('should override existing filters when epic param present', () => { });
});
```

### Integration Tests

```typescript
describe('Shared Epic Link - E2E Flow', () => {
  it('should open shared link and expand epic', async () => {
    // 1. Navigate to shared link
    await router.push('/roadmap?epic=WENI-123');
    await nextTick();
    
    // 2. Verify filters cleared
    expect(filters.value).toEqual({});
    
    // 3. Verify items fetched
    expect(handleFetchItems).toHaveBeenCalledWith({});
    
    // 4. Verify epic expanded
    const epicCard = wrapper.find('[data-epic-id="WENI-123"]');
    expect(epicCard.classes()).toContain('roadmap-card--expanded');
    
    // 5. Verify URL cleaned
    expect(route.query.epic).toBeUndefined();
  });
});
```

## Performance Considerations

- **Debounce route watchers**: Prevent multiple handleSharedEpicLink calls if route changes rapidly
- **Cancel in-flight requests**: If new epic link clicked while processing previous one
- **Cache items**: Don't refetch if items already loaded (unless filters changed)
- **Lazy scroll**: Use IntersectionObserver to detect when epic is in view (don't force scroll if already visible)

## Security Considerations

- **No authorization**: Epic visibility determined by backend API (if epic not in response, it's not accessible)
- **No sensitive data in URL**: Only epic ID (public identifier) in URL parameter
- **XSS prevention**: Sanitize epic ID before displaying in error messages (use Vue's text interpolation, not v-html)
- **Rate limiting**: Backend should rate-limit epic access to prevent scraping

## Browser Compatibility

- Vue Router 4.2+ (supports query parameter reactivity)
- Modern browsers with History API (pushState/replaceState)
- All target browsers (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+) support required APIs

## Known Limitations

1. Epic must be in currently loaded dataset (not across different tabs/statuses)
2. No deep linking to specific tab (always shows default DELIVERED tab)
3. Cannot preserve user's filter state after viewing shared epic (by design)
4. Shared link only works if epic is still published in JIRA
5. No analytics tracking built-in (parent must track via events)
