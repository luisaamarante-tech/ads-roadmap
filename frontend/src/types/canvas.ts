/**
 * Canvas mode TypeScript types for conversational search.
 */

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
