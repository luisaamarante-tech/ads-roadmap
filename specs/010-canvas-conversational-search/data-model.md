# Data Model: Canvas Mode with Conversational Search

**Feature Branch**: `010-canvas-conversational-search`
**Date**: 2026-01-22

## Entity Overview

This feature introduces client-side state models only. No backend changes or API modifications required.

```
┌─────────────────────────────────────────────────────────────┐
│                    Canvas Search Domain                      │
│                                                              │
│  ┌──────────────────┐     ┌──────────────────────────────┐  │
│  │  CanvasState     │     │     SearchResult             │  │
│  │                  │     │                              │  │
│  │  - isActive      │────▶│  - ids: string[]            │  │
│  │  - filteredIds   │     │  - hasResults: boolean       │  │
│  │  - lastResult    │     │  - timestamp: number         │  │
│  └──────────────────┘     └──────────────────────────────┘  │
│           │                                                  │
│           │ uses                                             │
│           ▼                                                  │
│  ┌──────────────────┐     ┌──────────────────────────────┐  │
│  │  WebChatMessage  │     │     RoadmapItem (existing)   │  │
│  │                  │     │                              │  │
│  │  - type          │     │  - id: string                │  │
│  │  - text          │     │  - title: string             │  │
│  │  - direction     │     │  - description: string       │  │
│  │  - timestamp     │     │  - status: DeliveryStatus    │  │
│  └──────────────────┘     └──────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Type Definitions

### Canvas State Types

**File**: `frontend/src/types/canvas.ts`

```typescript
/**
 * Canvas mode state for conversational search.
 */
export interface CanvasState {
  /** Whether canvas mode is currently active */
  isActive: boolean;

  /** IDs of roadmap items to display (from last search result) */
  filteredItemIds: string[];

  /** Last parsed search result from WebChat */
  lastSearchResult: SearchResult | null;

  /** Timestamp when canvas mode was entered */
  enteredAt: number | null;
}

/**
 * Parsed result from [[SEARCH_RESULT]] block in chat message.
 */
export interface SearchResult {
  /** Array of roadmap item IDs (e.g., "EXPERI-2434", "ENGAGE-4388") */
  ids: string[];

  /** Whether any valid IDs were found */
  hasResults: boolean;

  /** Raw matched text for debugging */
  rawMatch: string;

  /** Timestamp when result was parsed */
  timestamp: number;
}

/**
 * WebChat message structure (subset of what webchat-service provides).
 */
export interface WebChatMessage {
  /** Message type: "text", "image", etc. */
  type: 'text' | 'image' | 'video' | 'audio' | 'document';

  /** Message text content */
  text: string;

  /** Direction: "incoming" (from agent) or "outgoing" (from user) */
  direction: 'incoming' | 'outgoing';

  /** Unix timestamp in milliseconds */
  timestamp: number;

  /** Unique message ID */
  id?: string;
}

/**
 * Canvas mode configuration options.
 */
export interface CanvasConfig {
  /** Left panel width as percentage (default: 40) */
  leftPanelWidth: number;

  /** Animation duration in milliseconds (default: 350) */
  animationDuration: number;

  /** Whether to auto-scroll results on filter change */
  autoScrollResults: boolean;
}

/**
 * Default canvas configuration.
 */
export const DEFAULT_CANVAS_CONFIG: CanvasConfig = {
  leftPanelWidth: 40,
  animationDuration: 350,
  autoScrollResults: true,
};
```

### Parser Types

**File**: `frontend/src/utils/searchResultParser.ts`

```typescript
/**
 * Parser result for [[SEARCH_RESULT]] extraction.
 */
export interface ParseResult {
  /** Whether a valid block was found */
  found: boolean;

  /** Extracted search result (null if not found) */
  result: SearchResult | null;

  /** Text with search result block removed (for display) */
  cleanText: string;
}

/**
 * Streaming parser state for handling chunked messages.
 */
export interface StreamingParserState {
  /** Current parser state */
  state: 'text' | 'tag_opening' | 'tag_content' | 'tag_closing';

  /** Buffer for incomplete tag */
  buffer: string;

  /** Accumulated visible text */
  visibleText: string;

  /** Pending IDs from incomplete block */
  pendingIds: string[];
}
```

## Validation Rules

### Search Result Validation

| Field | Rule | Example |
|-------|------|---------|
| `ids` | Must match pattern `^[A-Z]+-\d+$` | `EXPERI-2434` ✓, `invalid` ✗ |
| `ids` | Duplicates are removed | `[A, A, B]` → `[A, B]` |
| `ids` | Empty strings are filtered | `["", "A"]` → `["A"]` |

### Canvas State Validation

| Field | Rule |
|-------|------|
| `isActive` | Boolean, required |
| `filteredItemIds` | Array of valid IDs, may be empty |
| `lastSearchResult` | Null until first search received |
| `enteredAt` | Null when inactive, timestamp when active |

## State Transitions

### Canvas Mode State Machine

```
                    ┌─────────────────┐
                    │                 │
                    │    INACTIVE     │◀──────────────────────┐
                    │                 │                       │
                    └────────┬────────┘                       │
                             │                                │
                             │ enterCanvasMode()              │
                             ▼                                │
                    ┌─────────────────┐                       │
                    │                 │                       │
                    │     ACTIVE      │                       │
                    │  (no results)   │                       │
                    │                 │                       │
                    └────────┬────────┘                       │
                             │                                │
                             │ [[SEARCH_RESULT]] received     │
                             ▼                                │
                    ┌─────────────────┐                       │
                    │                 │                       │
                    │     ACTIVE      │───────────────────────┤
                    │ (with results)  │  exitCanvasMode()     │
                    │                 │                       │
                    └────────┬────────┘                       │
                             │                                │
                             │ new [[SEARCH_RESULT]]          │
                             │                                │
                             └────────────────────────────────┘
                                        (stays active,
                                         updates results)
```

### State Transition Actions

| Transition | Trigger | Actions |
|------------|---------|---------|
| INACTIVE → ACTIVE | `enterCanvasMode()` | Set `isActive=true`, hide filters, show canvas UI |
| ACTIVE → ACTIVE (updated) | New `[[SEARCH_RESULT]]` | Update `filteredItemIds`, `lastSearchResult` |
| ACTIVE → INACTIVE | `exitCanvasMode()` | Set `isActive=false`, show filters, hide canvas UI |

## Relationships with Existing Models

### Integration with RoadmapItem

The `filteredItemIds` in canvas state maps directly to `RoadmapItem.id`:

```typescript
// Filtering logic in CanvasSearchResults.vue
const filteredItems = computed(() => {
  if (filteredItemIds.value.length === 0) {
    return []; // Show empty state
  }

  return allItems.value.filter((item) =>
    filteredItemIds.value.includes(item.id)
  );
});
```

### Integration with Existing Filters

When canvas mode is active, traditional filters (year, quarter, module) are hidden and ignored. The filtered results come solely from `[[SEARCH_RESULT]]` IDs.

| Mode | Filters Used |
|------|--------------|
| Normal | Year, Quarter, Module, Status |
| Canvas | `[[SEARCH_RESULT]]` IDs only |

## Persistence Strategy

### Session Persistence

Canvas state is ephemeral and tied to the WebChat session:

- **Canvas mode active state**: Not persisted (resets on page refresh)
- **Search results**: Derived from WebChat history (persisted by WebChat)
- **Conversation history**: Managed by WebChat's localStorage

### Recovery on Page Load

When page loads with existing WebChat history:
1. Canvas mode starts as inactive
2. User can enter canvas mode
3. System scans WebChat history for last `[[SEARCH_RESULT]]`
4. If found, applies filter to roadmap items
