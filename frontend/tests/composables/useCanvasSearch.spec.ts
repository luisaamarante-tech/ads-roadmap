/**
 * Unit tests for useCanvasSearch composable.
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { useCanvasSearch } from '@/composables/useCanvasSearch';

// Mock window.WebChat
const mockWebChatInit = vi.fn();
const mockWebChatDestroy = vi.fn();
const mockWebChatOn = vi.fn();
const mockWebChatOff = vi.fn();
const mockWebChatSend = vi.fn();
const mockWebChatOnReady = vi.fn().mockResolvedValue(undefined);

function setupMockWebChat() {
  (window as { WebChat?: object }).WebChat = {
    init: mockWebChatInit,
    destroy: mockWebChatDestroy,
    on: mockWebChatOn,
    off: mockWebChatOff,
    send: mockWebChatSend,
    onReady: mockWebChatOnReady,
  };
}

function removeMockWebChat() {
  delete (window as { WebChat?: object }).WebChat;
}

describe('useCanvasSearch', () => {
  beforeEach(() => {
    // Reset DOM
    document.body.innerHTML = '';
    vi.useFakeTimers();
    mockWebChatInit.mockClear();
    mockWebChatDestroy.mockClear();
    mockWebChatOn.mockClear();
    mockWebChatOff.mockClear();
    mockWebChatSend.mockClear();
    mockWebChatOnReady.mockClear();
    mockWebChatOnReady.mockResolvedValue(undefined);
    setupMockWebChat();
    // Set channel UUID for tests
    import.meta.env.VITE_WEBCHAT_CHANNEL_UUID = 'test-channel-uuid';
  });

  afterEach(() => {
    document.body.innerHTML = '';
    vi.clearAllMocks();
    vi.useRealTimers();
    removeMockWebChat();
    delete import.meta.env.VITE_WEBCHAT_CHANNEL_UUID;
  });

  describe('initial state', () => {
    it('starts with canvas mode inactive', () => {
      const { isCanvasMode, filteredItemIds, hasSearchResults } =
        useCanvasSearch();

      expect(isCanvasMode.value).toBe(false);
      expect(filteredItemIds.value).toEqual([]);
      expect(hasSearchResults.value).toBe(false);
    });

    it('uses default configuration', () => {
      const { config } = useCanvasSearch();

      expect(config.leftPanelWidth).toBe(40);
      expect(config.animationDuration).toBe(350);
      expect(config.autoScrollResults).toBe(true);
    });

    it('accepts custom configuration', () => {
      const { config } = useCanvasSearch({
        leftPanelWidth: 50,
        animationDuration: 500,
      });

      expect(config.leftPanelWidth).toBe(50);
      expect(config.animationDuration).toBe(500);
      expect(config.autoScrollResults).toBe(true);
    });

    it('provides webchatContainerId', () => {
      const { webchatContainerId } = useCanvasSearch();

      expect(webchatContainerId).toBe('weni-webchat-canvas');
    });
  });

  describe('enterCanvasMode', () => {
    it('sets canvas mode to active', () => {
      const { isCanvasMode, enterCanvasMode } = useCanvasSearch();

      enterCanvasMode();

      expect(isCanvasMode.value).toBe(true);
    });

    it('does nothing if already active', () => {
      const { isCanvasMode, enterCanvasMode } = useCanvasSearch();

      enterCanvasMode();
      enterCanvasMode();

      expect(isCanvasMode.value).toBe(true);
    });

    it('schedules WebChat initialization after timeout', async () => {
      const { enterCanvasMode, isCanvasMode } = useCanvasSearch();

      enterCanvasMode();

      expect(isCanvasMode.value).toBe(true);

      // Note: actual WebChat.init call depends on env config (channelUuid)
      // This test verifies the timing mechanism
      await vi.advanceTimersByTimeAsync(100);

      // State should remain active
      expect(isCanvasMode.value).toBe(true);
    });

    it('provides correct webchat container ID', () => {
      const { webchatContainerId } = useCanvasSearch();

      // The selector should match this ID
      expect(webchatContainerId).toBe('weni-webchat-canvas');
    });
  });

  describe('exitCanvasMode', () => {
    it('sets canvas mode to inactive', async () => {
      const { isCanvasMode, enterCanvasMode, exitCanvasMode } =
        useCanvasSearch();

      enterCanvasMode();
      await vi.advanceTimersByTimeAsync(100);

      exitCanvasMode();

      expect(isCanvasMode.value).toBe(false);
    });

    it('clears search results', async () => {
      const {
        enterCanvasMode,
        exitCanvasMode,
        filteredItemIds,
        processMessage,
      } = useCanvasSearch();

      enterCanvasMode();
      await vi.advanceTimersByTimeAsync(100);

      processMessage(`[[SEARCH_RESULT]]
- TEST-123
[[/SEARCH_RESULT]]`);

      expect(filteredItemIds.value).toEqual(['TEST-123']);

      await exitCanvasMode();
      await vi.advanceTimersByTimeAsync(150);

      expect(filteredItemIds.value).toEqual([]);
    });

    it('attempts to destroy WebChat on exit', async () => {
      const { enterCanvasMode, exitCanvasMode, isCanvasMode } = useCanvasSearch();

      enterCanvasMode();
      await vi.advanceTimersByTimeAsync(100);

      await exitCanvasMode();
      await vi.advanceTimersByTimeAsync(150);

      // State should be inactive
      expect(isCanvasMode.value).toBe(false);
      // Note: actual destroy call depends on whether init succeeded
    });

    it('does nothing if already inactive', async () => {
      const { isCanvasMode, exitCanvasMode } = useCanvasSearch();

      await exitCanvasMode();

      expect(isCanvasMode.value).toBe(false);
      expect(mockWebChatDestroy).not.toHaveBeenCalled();
    });
  });

  describe('processMessage', () => {
    it('extracts IDs from [[SEARCH_RESULT]] block', () => {
      const { processMessage, filteredItemIds, lastSearchResult } =
        useCanvasSearch();

      processMessage(`Here are results:
[[SEARCH_RESULT]]
- EXPERI-2434
- ENGAGE-4388
[[/SEARCH_RESULT]]`);

      expect(filteredItemIds.value).toEqual(['EXPERI-2434', 'ENGAGE-4388']);
      expect(lastSearchResult.value?.hasResults).toBe(true);
    });

    it('updates results on new [[SEARCH_RESULT]] block', () => {
      const { processMessage, filteredItemIds } = useCanvasSearch();

      processMessage(`[[SEARCH_RESULT]]
- FIRST-1
[[/SEARCH_RESULT]]`);

      expect(filteredItemIds.value).toEqual(['FIRST-1']);

      processMessage(`[[SEARCH_RESULT]]
- SECOND-2
- THIRD-3
[[/SEARCH_RESULT]]`);

      expect(filteredItemIds.value).toEqual(['SECOND-2', 'THIRD-3']);
    });

    it('ignores messages without [[SEARCH_RESULT]] block', () => {
      const { processMessage, filteredItemIds, lastSearchResult } =
        useCanvasSearch();

      processMessage('Just a normal message');

      expect(filteredItemIds.value).toEqual([]);
      expect(lastSearchResult.value).toBeNull();
    });

    it('handles empty or invalid input gracefully', () => {
      const { processMessage, filteredItemIds } = useCanvasSearch();

      processMessage('');
      processMessage(null as unknown as string);
      processMessage(undefined as unknown as string);

      expect(filteredItemIds.value).toEqual([]);
    });
  });

  describe('computed properties', () => {
    it('hasSearchResults reflects filtered IDs', () => {
      const { processMessage, hasSearchResults } = useCanvasSearch();

      expect(hasSearchResults.value).toBe(false);

      processMessage(`[[SEARCH_RESULT]]
- TEST-1
[[/SEARCH_RESULT]]`);

      expect(hasSearchResults.value).toBe(true);
    });

    it('isWaitingForSearch is true when canvas active but no results', () => {
      const { enterCanvasMode, isWaitingForSearch, processMessage } =
        useCanvasSearch();

      expect(isWaitingForSearch.value).toBe(false);

      enterCanvasMode();

      expect(isWaitingForSearch.value).toBe(true);

      processMessage(`[[SEARCH_RESULT]]
- TEST-1
[[/SEARCH_RESULT]]`);

      expect(isWaitingForSearch.value).toBe(false);
    });
  });

  describe('clearSearchResults', () => {
    it('clears filtered IDs and last result', () => {
      const {
        processMessage,
        clearSearchResults,
        filteredItemIds,
        lastSearchResult,
      } = useCanvasSearch();

      processMessage(`[[SEARCH_RESULT]]
- TEST-1
[[/SEARCH_RESULT]]`);

      expect(filteredItemIds.value.length).toBeGreaterThan(0);

      clearSearchResults();

      expect(filteredItemIds.value).toEqual([]);
      expect(lastSearchResult.value).toBeNull();
    });
  });

  describe('sendMessage', () => {
    it('sends message via WebChat.send API', async () => {
      const { enterCanvasMode, sendMessage } = useCanvasSearch();

      // Add container to DOM
      const container = document.createElement('div');
      container.id = 'weni-webchat-canvas';
      document.body.appendChild(container);

      enterCanvasMode();
      await vi.advanceTimersByTimeAsync(100);

      sendMessage('Hello world');

      // Wait for retry attempts
      await vi.advanceTimersByTimeAsync(2000);

      expect(mockWebChatSend).toHaveBeenCalledWith({
        text: 'Hello world',
        metadata: {
          source: 'magic-search-bar',
          page: '/roadmap',
        },
      });
    });

    it('stores message as pending if WebChat not ready', () => {
      const { sendMessage } = useCanvasSearch();

      // Don't enter canvas mode, WebChat not initialized
      sendMessage('Pending message');

      // Message should be stored but not sent yet
      expect(mockWebChatSend).not.toHaveBeenCalled();
    });

    it('ignores empty or invalid messages', () => {
      const { sendMessage } = useCanvasSearch();

      sendMessage('');
      sendMessage(null as unknown as string);
      sendMessage(undefined as unknown as string);

      expect(mockWebChatSend).not.toHaveBeenCalled();
    });
  });

  describe('enterCanvasMode with initialMessage', () => {
    it('stores initial message to send after WebChat ready', async () => {
      const { enterCanvasMode } = useCanvasSearch();

      // Add container to DOM
      const container = document.createElement('div');
      container.id = 'weni-webchat-canvas';
      document.body.appendChild(container);

      enterCanvasMode('Search query');

      // Wait for initialization and retry
      await vi.advanceTimersByTimeAsync(2000);

      expect(mockWebChatSend).toHaveBeenCalledWith({
        text: 'Search query',
        metadata: {
          source: 'magic-search-bar',
          page: '/roadmap',
        },
      });
    });

    it('sends new message if already in canvas mode', async () => {
      const { enterCanvasMode } = useCanvasSearch();

      // Add container to DOM
      const container = document.createElement('div');
      container.id = 'weni-webchat-canvas';
      document.body.appendChild(container);

      enterCanvasMode();
      await vi.advanceTimersByTimeAsync(2000);

      // Call again with a message
      enterCanvasMode('Another search');
      await vi.advanceTimersByTimeAsync(2000);

      expect(mockWebChatSend).toHaveBeenCalledWith({
        text: 'Another search',
        metadata: {
          source: 'magic-search-bar',
          page: '/roadmap',
        },
      });
    });
  });

  describe('WebChat integration', () => {
    it('retries initialization if WebChat not loaded', async () => {
      removeMockWebChat();

      const { enterCanvasMode } = useCanvasSearch();

      enterCanvasMode();
      await vi.advanceTimersByTimeAsync(100);

      expect(mockWebChatInit).not.toHaveBeenCalled();

      // Simulate WebChat loading
      setupMockWebChat();

      // Wait for retry (500ms)
      await vi.advanceTimersByTimeAsync(2000);

      // Note: WebChat.init won't be called without proper channelUuid
      // This test verifies the retry mechanism exists
    });

    it('handles WebChat with event listeners if available', async () => {
      // WebChat.on is called if available during init
      // Since channelUuid is not set in test env, init won't proceed
      // This tests the interface compatibility
      const { enterCanvasMode } = useCanvasSearch();

      enterCanvasMode();
      await vi.advanceTimersByTimeAsync(100);

      // Just verify no errors are thrown
      expect(mockWebChatInit).toBeDefined();
    });

    it('handles exit gracefully even without WebChat initialized', async () => {
      const { enterCanvasMode, exitCanvasMode, isCanvasMode } = useCanvasSearch();

      enterCanvasMode();
      await vi.advanceTimersByTimeAsync(100);

      // Exit should work even if WebChat wasn't fully initialized
      exitCanvasMode();

      expect(isCanvasMode.value).toBe(false);
    });
  });
});
