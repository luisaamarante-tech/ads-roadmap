# Feature Specification: Canvas Mode with Conversational Search

**Feature Branch**: `010-canvas-conversational-search`
**Created**: 2026-01-22
**Status**: Draft
**Input**: User description: "Canvas Mode with Conversational Search for Roadmap"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Enter Canvas Search Mode (Priority: P1)

As a user, I want to initiate a conversational search so that I can discover roadmap items through natural language queries instead of manually filtering.

**Why this priority**: This is the core entry point to the feature. Without the ability to enter canvas mode, no other functionality is accessible. It's the foundational UX that enables all subsequent interactions.

**Independent Test**: Can be fully tested by clicking the search trigger and verifying the screen splits into two panels (WebChat left, empty results right). Delivers immediate value by providing the conversational interface.

**Acceptance Scenarios**:

1. **Given** I am viewing the normal roadmap view, **When** I click the search/canvas trigger button, **Then** the screen smoothly transitions to a split-panel layout with WebChat on the left (40%) and results panel on the right (60%)
2. **Given** canvas mode is activating, **When** the transition begins, **Then** all existing filter UI elements (year, quarter, module dropdowns) are hidden with a smooth fade animation
3. **Given** canvas mode is active, **When** I view the interface, **Then** the WebChat is embedded and fully functional on the left panel
4. **Given** canvas mode is active and no search has been performed, **When** I view the right panel, **Then** I see an inviting empty state prompting me to ask a question

---

### User Story 2 - Receive and Display Search Results (Priority: P1)

As a user, I want to see roadmap items filtered in real-time based on the AI agent's responses so that I can discover relevant features through conversation.

**Why this priority**: This is the core value proposition of the feature - connecting conversational AI to roadmap filtering. Without this, canvas mode is just an embedded chat with no roadmap integration.

**Independent Test**: Can be tested by sending a message and verifying that when the agent responds with a `[[SEARCH_RESULT]]` block, the right panel immediately displays only the matching roadmap items.

**Acceptance Scenarios**:

1. **Given** canvas mode is active and I send a search query like "show me AI features", **When** the agent responds with a message containing `[[SEARCH_RESULT]]` block with IDs, **Then** the right panel immediately displays only the roadmap items matching those IDs
2. **Given** the agent is typing/streaming a response, **When** the `[[SEARCH_RESULT]]` block is detected (even mid-stream), **Then** the roadmap filtering happens instantly without waiting for the full message
3. **Given** a `[[SEARCH_RESULT]]` block contains IDs like `EXPERI-2434, ENGAGE-4388`, **When** parsing the block, **Then** each ID is extracted and matched against roadmap item IDs to filter the display
4. **Given** some IDs in the `[[SEARCH_RESULT]]` don't match any roadmap items, **When** filtering occurs, **Then** only valid matching items are shown (no errors for missing IDs)

---

### User Story 3 - Maintain Search Context Across Conversation (Priority: P2)

As a user, I want the search results to persist based on the most recent agent response so that I can continue my conversation without losing context.

**Why this priority**: Important for UX but not core functionality. Users can still use the feature without this - they just wouldn't have context persistence.

**Independent Test**: Can be tested by having a conversation, refreshing or navigating away, and verifying that upon returning to canvas mode, the last `[[SEARCH_RESULT]]` is reapplied.

**Acceptance Scenarios**:

1. **Given** I receive a `[[SEARCH_RESULT]]` and then send a follow-up question, **When** the agent responds WITHOUT a new `[[SEARCH_RESULT]]`, **Then** the previous search results remain displayed
2. **Given** I receive multiple messages with `[[SEARCH_RESULT]]` blocks, **When** viewing results, **Then** only the MOST RECENT `[[SEARCH_RESULT]]` determines the filtered items
3. **Given** I re-enter canvas mode after previously exiting, **When** WebChat loads history, **Then** the roadmap is filtered based on the last `[[SEARCH_RESULT]]` in the conversation history

---

### User Story 4 - Exit Canvas Mode (Priority: P2)

As a user, I want to explicitly exit canvas mode so that I can return to the normal roadmap view with traditional filters.

**Why this priority**: Essential for complete UX flow but depends on canvas mode being entered first. Users need a clear way to return to normal browsing.

**Independent Test**: Can be tested by clicking the exit button and verifying smooth transition back to normal view with filters restored.

**Acceptance Scenarios**:

1. **Given** canvas mode is active, **When** I click the explicit "Exit Canvas" or close button, **Then** the screen smoothly transitions back to the normal single-panel roadmap view
2. **Given** I am exiting canvas mode, **When** the transition completes, **Then** all filter UI elements (year, quarter, module) are restored and visible
3. **Given** I exit canvas mode, **When** viewing the normal roadmap, **Then** the roadmap items show ALL items (no search filter applied), respecting only the traditional filters
4. **Given** I exit and re-enter canvas mode, **When** entering again, **Then** the previous conversation history is preserved in WebChat

---

### User Story 5 - Visual Polish and Animations (Priority: P3)

As a user, I want smooth, professional animations when transitioning between modes so that the experience feels polished and seamless.

**Why this priority**: Polish and delight factor. Feature works without animations, but they significantly improve perceived quality.

**Independent Test**: Can be tested by triggering mode transitions and observing animation smoothness, timing, and visual coherence.

**Acceptance Scenarios**:

1. **Given** I am entering canvas mode, **When** the transition occurs, **Then** the animation takes 300-400ms with smooth easing (ease-out or cubic-bezier)
2. **Given** I am exiting canvas mode, **When** the transition occurs, **Then** elements fade/slide back with matching animation timing
3. **Given** search results are being filtered, **When** items appear, **Then** they fade in with subtle stagger animation (not jarring instant appearance)
4. **Given** the empty state is displayed, **When** viewing it, **Then** the prompt to search is visually appealing with subtle animation (pulsing icon, etc.)

---

### Edge Cases

- What happens when WebSocket connection to webchat-service fails?
  - Display connection error in WebChat (handled by WebChat itself), right panel shows "Waiting for connection..." state
- What happens when `[[SEARCH_RESULT]]` contains invalid/malformed IDs?
  - Silently skip invalid IDs, only display items with valid matches
- What happens when `[[SEARCH_RESULT]]` contains zero IDs?
  - Show empty state with message "No matching items found for this query"
- What happens when user resizes browser window in canvas mode?
  - Panels should be responsive; on mobile (<768px), consider stacked layout or priority to chat
- What happens when roadmap data hasn't loaded yet but search results arrive?
  - Store the filter IDs, apply them once roadmap data is available

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST embed Weni WebChat in the left panel without custom message rendering
- **FR-002**: System MUST listen to WebSocket messages from webchat-service backend
- **FR-003**: System MUST parse messages for `[[SEARCH_RESULT]]` blocks with the exact format:
  ```
  [[SEARCH_RESULT]]
  - ID1
  - ID2
  - ID3
  [[/SEARCH_RESULT]]
  ```
- **FR-004**: System MUST filter roadmap items in real-time when `[[SEARCH_RESULT]]` is detected
- **FR-005**: System MUST hide traditional filter UI (year, quarter, module) when in canvas mode
- **FR-006**: System MUST provide explicit exit mechanism to return to normal view
- **FR-007**: System MUST restore filter UI visibility when exiting canvas mode
- **FR-008**: System MUST maintain the most recent `[[SEARCH_RESULT]]` filter across conversation turns
- **FR-009**: System MUST handle incomplete/streaming `[[SEARCH_RESULT]]` blocks by buffering until complete
- **FR-010**: System MUST apply CSS overrides to position WebChat appropriately in the left panel

### Non-Functional Requirements

- **NFR-001**: Mode transitions MUST complete within 400ms for smooth UX
- **NFR-002**: Search result filtering MUST be instantaneous (<50ms) after parsing
- **NFR-003**: WebSocket message parsing MUST NOT block the UI thread
- **NFR-004**: System MUST gracefully degrade if WebSocket connection is unavailable

### Key Entities

- **CanvasMode**: State object representing canvas mode status (active/inactive, last search IDs)
- **SearchResult**: Parsed result from `[[SEARCH_RESULT]]` block containing array of item IDs
- **WebChatConfig**: Configuration for embedding WebChat with appropriate CSS overrides

## Technical Approach

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        RoadmapView.vue                          │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    Canvas Mode Container                   │  │
│  │  ┌─────────────────┐    ┌──────────────────────────────┐  │  │
│  │  │   Left Panel    │    │        Right Panel           │  │  │
│  │  │   (WebChat)     │    │   (Filtered Roadmap Items)   │  │  │
│  │  │                 │    │                              │  │  │
│  │  │  ┌───────────┐  │    │  ┌────────────────────────┐  │  │  │
│  │  │  │ Embedded  │  │    │  │  RoadmapCardList      │  │  │  │
│  │  │  │ Weni      │  │    │  │  (filtered by IDs)    │  │  │  │
│  │  │  │ WebChat   │  │    │  │                        │  │  │  │
│  │  │  │ (iframe)  │  │    │  └────────────────────────┘  │  │  │
│  │  │  └───────────┘  │    │                              │  │  │
│  │  └─────────────────┘    └──────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### WebSocket Integration Strategy

The WebChat already manages its own WebSocket connection to webchat-service. We need to:

1. **Listen to WebSocket messages**: Intercept messages from the webchat-service WebSocket that WebChat uses
2. **Parse for hidden tags**: Extract `[[SEARCH_RESULT]]` blocks from message content
3. **Do NOT modify WebChat**: The WebChat handles all user-facing messaging; we only observe

### Message Parsing Implementation

```typescript
// Example parser for [[SEARCH_RESULT]] blocks
interface SearchResultBlock {
  ids: string[];
  raw: string;
}

function parseSearchResults(messageText: string): SearchResultBlock | null {
  const regex = /\[\[SEARCH_RESULT\]\]([\s\S]*?)\[\[\/SEARCH_RESULT\]\]/;
  const match = messageText.match(regex);

  if (!match) return null;

  const content = match[1];
  const ids = content
    .split('\n')
    .map(line => line.replace(/^-\s*/, '').trim())
    .filter(id => id.length > 0);

  return { ids, raw: match[0] };
}
```

### Component Structure

```
frontend/src/
├── components/
│   ├── CanvasMode/
│   │   ├── CanvasContainer.vue      # Main canvas layout wrapper
│   │   ├── CanvasSearchResults.vue  # Right panel with filtered results
│   │   └── CanvasEmptyState.vue     # Empty state with search prompt
│   └── ...existing components
├── composables/
│   └── useCanvasSearch.ts           # Canvas mode state & WebSocket parsing
└── utils/
    └── searchResultParser.ts        # [[SEARCH_RESULT]] block parser
```

### CSS Overrides for WebChat

The WebChat widget needs CSS overrides to position it in the left panel:

```css
/* Override WebChat positioning in canvas mode */
.canvas-mode .weni-widget {
  position: relative !important;
  width: 100% !important;
  height: 100% !important;
  bottom: unset !important;
  right: unset !important;
}

.canvas-mode .weni-widget aside {
  width: 100% !important;
  height: 100% !important;
}
```

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can enter canvas mode within 1 click from normal roadmap view
- **SC-002**: Search results appear in <100ms after `[[SEARCH_RESULT]]` is detected in agent response
- **SC-003**: Mode transitions complete smoothly without visual glitches or layout jumps
- **SC-004**: 100% of valid `[[SEARCH_RESULT]]` blocks are correctly parsed and applied
- **SC-005**: Users can exit canvas mode and return to normal filters with 1 click
- **SC-006**: WebChat conversation history is preserved across mode transitions
- **SC-007**: Feature works correctly on desktop browsers (Chrome, Firefox, Safari, Edge)

### Acceptance Testing Checklist

- [ ] Canvas mode can be entered via UI trigger
- [ ] WebChat loads and is functional in left panel
- [ ] Traditional filters are hidden in canvas mode
- [ ] `[[SEARCH_RESULT]]` blocks are correctly parsed
- [ ] Roadmap items filter based on parsed IDs
- [ ] Empty state shows when no search results
- [ ] Exit button returns to normal view
- [ ] Filters are restored on exit
- [ ] Animations are smooth and professional
- [ ] Responsive behavior on different screen sizes
