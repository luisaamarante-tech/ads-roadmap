# Phase 0: Research & Design Decisions

**Feature**: Epic Viewer Enhancements
**Date**: January 21, 2026
**Purpose**: Document research findings and design decisions for image carousel and share functionality

## Design Decisions

### Decision 1: Modal Implementation Approach

**Context**: Need to implement a modal overlay for viewing enlarged images with navigation.

**Decision**: Create custom Vue component extending Unnnic modal patterns rather than using third-party carousel library.

**Rationale**:
- **Design System Consistency**: Unnnic Design System is the single source of truth; custom component ensures visual consistency
- **Bundle Size**: Third-party libraries (like vue3-carousel) add 20-50KB; custom implementation ~5KB
- **Maintenance**: Fewer dependencies reduces security vulnerabilities and version conflicts
- **Flexibility**: Full control over keyboard navigation, loading states, and mobile behavior
- **Existing Patterns**: RoadmapCard already implements custom modal patterns successfully

**Alternatives Considered**:
1. **vue3-carousel** - Rejected: Adds unnecessary features (autoplay, infinite scroll) and styling conflicts with Unnnic
2. **Unnnic Modal Component** - Partially adopted: Will use as base structure but extend for image-specific needs
3. **Native `<dialog>` element** - Rejected: Limited browser support (Safari 15.4+), loses Unnnic styling

**Implementation Notes**:
- Use `<Teleport>` to render modal at document root for proper z-index stacking
- Implement focus trap to prevent keyboard navigation outside modal
- Use CSS transforms for smooth animations (<300ms requirement)

---

### Decision 2: Image Navigation Pattern

**Context**: Users need to navigate between multiple images within the modal.

**Decision**: Implement left/right arrow buttons with keyboard shortcuts (Left/Right arrows, ESC to close).

**Rationale**:
- **Familiarity**: Left/right arrows are universal UX pattern (Google Images, Instagram, Lightbox)
- **Accessibility**: Keyboard shortcuts essential for users who cannot use mouse
- **Mobile Support**: Touch/swipe gestures out of scope but buttons work on mobile
- **Cognitive Load**: Simple, predictable navigation reduces user confusion

**Alternatives Considered**:
1. **Thumbnail Strip** - Rejected: Adds visual complexity (violates "clean and simple" requirement), poor mobile UX
2. **Dots/Pagination Indicators** - Rejected: Less direct than arrows, harder to predict position
3. **Swipe Gestures Only** - Rejected: Excludes desktop users, harder to discover

**Implementation Notes**:
- Hide arrows when only 1 image exists
- Wrap navigation: last image → first image when clicking "next"
- Show current position: "2 of 5" near arrows for context
- Debounce rapid clicks to prevent animation conflicts

---

### Decision 3: Clipboard API Strategy

**Context**: Need to copy shareable link to clipboard across various browsers with varying API support.

**Decision**: Use modern Clipboard API (`navigator.clipboard.writeText`) with graceful fallback to manual copy.

**Rationale**:
- **Modern Standard**: Clipboard API supported in 95%+ of modern browsers (Chrome 66+, Firefox 63+, Safari 13.1+)
- **User Experience**: Async API avoids blocking UI during copy operation
- **Security**: Requires secure context (HTTPS), aligns with production requirements
- **Fallback Coverage**: Manual fallback handles remaining 5% (legacy browsers, permission denied)

**Alternatives Considered**:
1. **`document.execCommand('copy')`** - Rejected: Deprecated, synchronous, requires temporary DOM manipulation
2. **Copy-to-clipboard library** - Rejected: Adds dependency for simple operation we can implement directly
3. **No fallback** - Rejected: Violates requirement FR-021 (fallback method required)

**Implementation Notes**:
- Create `useClipboard` composable for reusable logic
- Fallback: Show input field with pre-selected URL for manual Cmd+C/Ctrl+C
- Handle permission errors gracefully with user-friendly messages
- Test with mocked `navigator.clipboard` in Vitest

**Browser Compatibility**:
```typescript
// Target browsers (as per constitution: modern browsers)
- Chrome 90+ ✅ (Clipboard API since 66)
- Firefox 88+ ✅ (Clipboard API since 63)  
- Safari 14+ ✅ (Clipboard API since 13.1)
- Edge 90+ ✅ (Clipboard API since 79)
```

---

### Decision 4: URL Parameter Structure for Shared Links

**Context**: Need to design URL format for shareable links that directly opens a specific epic.

**Decision**: Use single query parameter `?epic=[EPIC-ID]` appended to existing roadmap URL.

**Rationale**:
- **Simplicity**: Clean, memorable URLs (e.g., `/roadmap?epic=WENI-123`)
- **Consistency**: Aligns with existing filter parameters (`?year=2026&quarter=Q1&module=flows`)
- **SEO Friendly**: Query parameters preserve page identity for search engines
- **Existing Infrastructure**: Vue Router already configured for query parameter handling
- **Forward Compatible**: Easy to add additional parameters later if needed

**Alternatives Considered**:
1. **Path parameter** (`/roadmap/epic/WENI-123`) - Rejected: Requires router reconfiguration, breaks existing filter URLs
2. **Hash fragment** (`/roadmap#epic=WENI-123`) - Rejected: Doesn't trigger router navigation, poor analytics tracking
3. **Encode all state** (`?epic=WENI-123&tab=now&year=2026`) - Rejected: Violates requirement to clear filters (FR-022)

**Implementation Notes**:
- Parse `route.query.epic` in `RoadmapView.onMounted`
- If epic parameter exists: clear all filters, fetch all items, find and expand matching epic
- Handle invalid epic IDs gracefully: show toast notification, don't crash page
- Remove epic parameter from URL after expanding to avoid confusion on page refresh

---

### Decision 5: State Management for Modal

**Context**: Need to manage modal open/closed state and current image index.

**Decision**: Use component-local reactive refs with Vue 3 composition API, no external state management.

**Rationale**:
- **Simplicity**: Modal state is UI-only, doesn't need persistence or global access
- **Performance**: Local state avoids unnecessary re-renders of unrelated components
- **Existing Patterns**: RoadmapCard already uses local `isExpanded` ref successfully
- **No Store Needed**: Feature doesn't use Vuex/Pinia; introducing for this would violate YAGNI principle

**Alternatives Considered**:
1. **Pinia Store** - Rejected: Overkill for transient UI state, adds unnecessary complexity
2. **Provide/Inject** - Rejected: Modal and card are directly related, no deep component tree
3. **Emit Events to Parent** - Rejected: Creates unnecessary coupling, makes testing harder

**Implementation Notes**:
```typescript
// In RoadmapCard.vue
const showImageModal = ref(false);
const currentImageIndex = ref(0);

function onImageClick(index: number): void {
  currentImageIndex.value = index;
  showImageModal.value = true;
}

// In ImageCarouselModal.vue
const props = defineProps<{
  images: string[];
  currentIndex: number;
  epicTitle: string;
}>();

const localIndex = ref(props.currentIndex);
```

---

### Decision 6: Loading States and Error Handling

**Context**: Need to handle slow image loading and broken image URLs.

**Decision**: Show loading spinner overlay on modal image, replace broken images with placeholder + error message.

**Rationale**:
- **User Feedback**: Loading states prevent confusion during slow network
- **Graceful Degradation**: Broken images shouldn't break entire modal
- **Accessibility**: Alt text on broken images provides context for screen readers
- **Performance**: Lazy loading images reduces initial page load

**Alternatives Considered**:
1. **Preload all images** - Rejected: Wastes bandwidth, slows modal open time
2. **Show broken image icon only** - Rejected: Poor UX, doesn't explain problem
3. **Hide broken images** - Rejected: Confuses users about image count

**Implementation Notes**:
```typescript
// Image component states
const imageStates = ref<Record<number, 'loading' | 'loaded' | 'error'>>({});

function onImageLoad(index: number): void {
  imageStates.value[index] = 'loaded';
}

function onImageError(index: number): void {
  imageStates.value[index] = 'error';
  console.error(`Failed to load image ${index}`);
}
```

- Use `loading="lazy"` for offscreen images
- Show Unnnic spinner component during load
- Display Unnnic alert for errors with "Image failed to load" message

---

### Decision 7: Keyboard Navigation Implementation

**Context**: Must support keyboard shortcuts (ESC, arrow keys) for accessibility.

**Decision**: Extract keyboard logic into `useKeyboardNavigation` composable with event listeners in modal lifecycle.

**Rationale**:
- **Reusability**: Composable can be tested independently and reused in future modals
- **Separation of Concerns**: Keeps keyboard logic separate from rendering logic
- **Testability**: Easy to mock keyboard events in Vitest
- **Cleanup**: Lifecycle hooks ensure event listeners are properly removed

**Alternatives Considered**:
1. **Inline event handlers** - Rejected: Harder to test, duplicates logic if adding more modals
2. **Global keyboard service** - Rejected: Overkill for single feature, harder to scope events
3. **Third-party library** - Rejected: Simple enough to implement directly

**Implementation Notes**:
```typescript
// composables/useKeyboardNavigation.ts
export function useKeyboardNavigation(callbacks: {
  onEscape?: () => void;
  onArrowLeft?: () => void;
  onArrowRight?: () => void;
}) {
  function handleKeydown(event: KeyboardEvent): void {
    if (event.key === 'Escape' && callbacks.onEscape) {
      callbacks.onEscape();
    } else if (event.key === 'ArrowLeft' && callbacks.onArrowLeft) {
      event.preventDefault();
      callbacks.onArrowLeft();
    } else if (event.key === 'ArrowRight' && callbacks.onArrowRight) {
      event.preventDefault();
      callbacks.onArrowRight();
    }
  }

  onMounted(() => {
    window.addEventListener('keydown', handleKeydown);
  });

  onUnmounted(() => {
    window.removeEventListener('keydown', handleKeydown);
  });
}
```

---

### Decision 8: Share Button Placement

**Context**: Share button should appear in both card view and expanded view per specification.

**Decision**: Create reusable `ShareButton` component, render in both RoadmapCard header and expanded content.

**Rationale**:
- **DRY Principle**: Single component avoids code duplication
- **Consistency**: Same visual appearance and behavior in both locations
- **Maintainability**: Bug fixes and improvements apply to both placements
- **Testing**: Test once, works everywhere

**Alternatives Considered**:
1. **Duplicate code in two places** - Rejected: Violates DRY, harder to maintain
2. **Single button that moves** - Rejected: Confusing animation, complicates state management
3. **Context menu instead of button** - Rejected: Lower discoverability, non-standard pattern

**Implementation Notes**:
```vue
<!-- In RoadmapCard.vue header -->
<ShareButton
  :epic-id="item.id"
  size="small"
  variant="ghost"
  class="roadmap-card__share-btn"
/>

<!-- In RoadmapCard.vue expanded content -->
<ShareButton
  :epic-id="item.id"
  size="medium"
  variant="outlined"
  class="roadmap-card__share-btn--expanded"
/>
```

---

## Best Practices Integration

### Vue 3 Composition API
- **Ref vs Reactive**: Use `ref()` for primitives, `reactive()` for objects needing deep reactivity
- **Computed Properties**: Derive modal visibility, button states from refs (avoid duplicate state)
- **Lifecycle Hooks**: Use `onMounted` for event listeners, `onUnmounted` for cleanup
- **Props vs Emits**: Props for data down, emits for events up (e.g., `@close`, `@imageChange`)

### TypeScript Best Practices
- **Strict Mode**: Enable strict null checks, no implicit any
- **Type Definitions**: Export interfaces for props, emits, and public API
- **Type Guards**: Use for runtime checks (e.g., `if (typeof epicId === 'string')`)
- **Avoid Any**: Use `unknown` with type guards or specific union types

### Testing Strategy (80% Coverage)
- **Component Tests**: Mount with stubs, simulate user interactions, verify DOM changes
- **Composable Tests**: Call directly, mock browser APIs (clipboard, keyboard events)
- **Edge Cases**: Test empty images array, broken URLs, permission denied scenarios
- **Accessibility**: Verify ARIA labels, keyboard navigation, focus management

### Performance Optimization
- **Lazy Loading**: Use `loading="lazy"` on images to defer offscreen loads
- **Debouncing**: Debounce rapid navigation clicks (300ms) to prevent animation stutter
- **Teleport**: Render modal at root to avoid z-index conflicts with deep nested components
- **Cleanup**: Remove event listeners and timers in `onUnmounted` to prevent memory leaks

### Accessibility (WCAG 2.1 AA)
- **Keyboard Navigation**: All interactive elements accessible via Tab, Enter, ESC
- **Screen Readers**: Use ARIA labels, alt text, and semantic HTML
- **Focus Management**: Trap focus within modal, restore focus on close
- **Color Contrast**: Ensure backdrop, buttons, text meet 4.5:1 contrast ratio

---

## Technical Risks & Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Clipboard API permission denied | Users can't copy link | Medium | Provide fallback input field for manual copy |
| Large images cause modal slowness | Poor UX on slow connections | Medium | Show loading spinner, use browser lazy loading |
| Broken image URLs from JIRA | Modal shows errors | Low | Gracefully handle with placeholder + error message |
| Keyboard shortcuts conflict with browser | Navigation doesn't work | Low | Use `preventDefault()` on arrow keys in modal context |
| Modal z-index conflicts | Modal hidden behind other UI | Low | Use `<Teleport>` to render at document root |
| URL parameter state conflicts | Filters break when sharing | Low | Clear filters when epic parameter detected (per spec) |

---

## Open Questions

**None** - All design decisions resolved. Ready to proceed to Phase 1 (Data Models & Contracts).
