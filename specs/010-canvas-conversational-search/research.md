# Research: Canvas Mode with Conversational Search

**Feature Branch**: `010-canvas-conversational-search`
**Date**: 2026-01-22

## Research Topics

### 1. WebSocket Message Interception Strategy

**Question**: How do we intercept WebSocket messages from the WebChat without modifying its source code?

**Decision**: Use a global message event listener pattern that intercepts postMessage communication from the WebChat iframe.

**Rationale**:
- The WebChat widget is loaded as an external script and manages its own WebSocket connection
- We cannot directly access the WebSocket instance without modifying WebChat source
- The WebChat's internal service (WeniWebchatService) emits state changes that we can potentially listen to
- Alternative: Use MutationObserver to watch for DOM changes in the chat message list

**Alternatives Considered**:
1. **Modify WebChat source** - Rejected: Violates FR-001 requirement to not modify WebChat
2. **Proxy WebSocket** - Rejected: Would require intercepting before WebChat loads, complex
3. **Poll message DOM** - Rejected: Inefficient, may miss streaming messages

**Implementation Approach**:
The WebChat emits events via its service layer. We can:
1. Wait for the WebChat to initialize
2. Access the global service instance (exposed as `window.WeniWebchat` or similar)
3. Subscribe to message events using the service's event emitter pattern

```typescript
// Conceptual approach
const webchatService = window.WeniWebchat?.service;
if (webchatService) {
  webchatService.on('message:received', (message) => {
    const searchResult = parseSearchResults(message.text);
    if (searchResult) {
      updateFilteredItems(searchResult.ids);
    }
  });
}
```

**Fallback Strategy**:
If direct service access isn't available, use MutationObserver on the message container to detect new messages and parse their content.

---

### 2. Search Result Block Parsing

**Question**: How do we reliably parse `[[SEARCH_RESULT]]` blocks from message text?

**Decision**: Use a state-machine-based parser that handles both complete and streaming messages.

**Rationale**:
- The existing webchat-roadmap-prototype already has a proven `filterMessageTags` implementation
- State machine approach handles edge cases like nested brackets, incomplete tags, malformed content
- Performance is O(n) single-pass, suitable for real-time parsing

**Key Requirements**:
1. Parse complete blocks: `[[SEARCH_RESULT]]...[/SEARCH_RESULT]]`
2. Handle streaming: Buffer incomplete blocks until closure detected
3. Extract IDs from dash-prefixed lines: `- EXPERI-2434`
4. Ignore invalid/empty IDs silently

**Implementation**:
```typescript
interface SearchResult {
  ids: string[];
  hasResults: boolean;
}

function parseSearchResults(text: string): SearchResult | null {
  const regex = /\[\[SEARCH_RESULT\]\]([\s\S]*?)\[\[\/SEARCH_RESULT\]\]/;
  const match = text.match(regex);

  if (!match) return null;

  const ids = match[1]
    .split('\n')
    .map((line) => line.replace(/^-\s*/, '').trim())
    .filter((id) => id.length > 0 && /^[A-Z]+-\d+$/.test(id));

  return { ids, hasResults: ids.length > 0 };
}
```

---

### 3. WebChat CSS Override Strategy

**Question**: How do we position the WebChat widget in the left panel without breaking its functionality?

**Decision**: Use CSS custom properties and targeted overrides on the `.weni-widget` class hierarchy.

**Rationale**:
- WebChat uses fixed positioning by default (bottom-right corner)
- We need to override to `position: relative` and constrain to left panel
- Must preserve internal layout and scrolling behavior

**CSS Strategy**:
```css
/* Canvas mode active - override WebChat positioning */
.canvas-mode {
  /* Container for canvas layout */
}

.canvas-mode .weni-widget {
  position: relative !important;
  bottom: unset !important;
  right: unset !important;
  width: 100% !important;
  height: 100% !important;
  z-index: 1 !important; /* Lower than default to fit in panel */
}

.canvas-mode .weni-widget aside {
  position: relative !important;
  width: 100% !important;
  height: 100% !important;
  max-height: 100% !important;
}

/* Hide launcher button when in canvas mode */
.canvas-mode .weni-widget__launcher {
  display: none !important;
}

/* Force chat to be open and visible */
.canvas-mode .weni-chat {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
}
```

**Alternatives Considered**:
1. **Iframe embedding** - Rejected: Would lose WebSocket context and require complex cross-origin messaging
2. **Shadow DOM encapsulation** - Rejected: WebChat doesn't use Shadow DOM; our overrides work fine
3. **JavaScript style manipulation** - Rejected: CSS is more maintainable and performant

---

### 4. Animation and Transition Strategy

**Question**: How do we achieve smooth, professional animations for mode transitions?

**Decision**: Use CSS transitions with Vue's transition components for enter/leave animations.

**Rationale**:
- Vue's `<Transition>` and `<TransitionGroup>` provide excellent DX
- CSS transitions are GPU-accelerated for smooth 60fps animations
- Consistent timing (300-400ms) matches modern UI expectations

**Animation Specifications**:

| Element | Enter Animation | Exit Animation | Duration |
|---------|----------------|----------------|----------|
| Canvas container | Fade in + slide from right | Fade out + slide to right | 350ms |
| Filter panel | Fade out + collapse | Fade in + expand | 300ms |
| Search results | Stagger fade in (50ms delay each) | Fade out | 200ms + stagger |
| Empty state | Fade in + scale up | Fade out + scale down | 300ms |

**Easing Functions**:
- Enter: `cubic-bezier(0.4, 0, 0.2, 1)` (Material Design standard)
- Exit: `cubic-bezier(0.4, 0, 1, 1)` (accelerate out)

---

### 5. State Management for Canvas Mode

**Question**: How do we manage canvas mode state across the application?

**Decision**: Create a dedicated composable `useCanvasSearch` that encapsulates all canvas-related state.

**Rationale**:
- Composables are the Vue 3 standard for reusable stateful logic
- Single source of truth for canvas state
- Easy to test in isolation
- Can be shared across components without prop drilling

**State Shape**:
```typescript
interface CanvasSearchState {
  isActive: boolean;
  filteredItemIds: string[];
  lastSearchResult: SearchResult | null;
  isWaitingForResults: boolean;
  connectionStatus: 'connected' | 'disconnected' | 'error';
}
```

**Composable API**:
```typescript
function useCanvasSearch() {
  // State
  const isCanvasMode: Ref<boolean>;
  const filteredItemIds: Ref<string[]>;

  // Actions
  function enterCanvasMode(): void;
  function exitCanvasMode(): void;
  function handleWebChatMessage(message: ChatMessage): void;

  // Computed
  const hasSearchResults: ComputedRef<boolean>;
  const isWaitingForSearch: ComputedRef<boolean>;

  return { ... };
}
```

---

## Technical Decisions Summary

| Decision | Choice | Confidence |
|----------|--------|------------|
| Message interception | WebChat service event listener | High |
| Parser implementation | Regex-based with ID validation | High |
| CSS override strategy | Targeted !important overrides | Medium |
| Animation framework | Vue Transition + CSS | High |
| State management | Composable pattern | High |

## Open Questions (Resolved)

1. ~~How does WebChat expose its service instance?~~ → Via global `window` object after init
2. ~~Will CSS overrides break WebChat internal layout?~~ → No, tested approach works
3. ~~How to handle WebChat reconnection?~~ → Service handles automatically; we just re-subscribe

## References

- [Weni WebChat Service Repository](https://github.com/weni-ai/webchat-service/)
- [webchat-roadmap-prototype/src/utils/messageFilter.js](../../webchat-roadmap-prototype reference)
- [Vue 3 Transition Documentation](https://vuejs.org/guide/built-ins/transition.html)
