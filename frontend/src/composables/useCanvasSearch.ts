/**
 * Composable for managing canvas search mode state.
 *
 * Handles entering/exiting canvas mode, initializing WebChat in embedded mode,
 * parsing WebChat messages for [[SEARCH_RESULT]] blocks, and filtering roadmap items.
 */

import { ref, computed, onUnmounted } from 'vue';
import type { Ref, ComputedRef } from 'vue';
import type { SearchResult, CanvasConfig } from '@/types/canvas';
import type { WebChatConfig } from '@/types/webchat';
import { parseSearchResults } from '@/utils/searchResultParser';
import { env } from '@/utils/env';

/** Default configuration for canvas mode */
const DEFAULT_CONFIG: CanvasConfig = {
  leftPanelWidth: 40,
  animationDuration: 350,
  autoScrollResults: true,
};

/** WebChat configuration from environment */
const WEBCHAT_CONFIG = {
  socketUrl: env.webChat.socketUrl,
  host: env.webChat.host,
  channelUuid: env.webChat.channelUuid,
};

/** Voice Mode configuration from environment */
const VOICE_MODE_CONFIG = {
  enabled: env.voiceMode.enabled,
  apiKey: env.voiceMode.apiKey,
  voiceId: env.voiceMode.voiceId,
  languageCode: env.voiceMode.languageCode,
};

/** CSS selector for the WebChat container */
const WEBCHAT_CONTAINER_ID = 'weni-webchat-canvas';

/**
 * Return type for useCanvasSearch composable.
 */
export interface UseCanvasSearchReturn {
  /** Whether canvas mode is currently active */
  isCanvasMode: Ref<boolean>;

  /** IDs of roadmap items to display */
  filteredItemIds: Ref<string[]>;

  /** Last parsed search result */
  lastSearchResult: Ref<SearchResult | null>;

  /** Whether we have search results to display */
  hasSearchResults: ComputedRef<boolean>;

  /** Whether waiting for first search (canvas active, no results yet) */
  isWaitingForSearch: ComputedRef<boolean>;

  /** Canvas configuration */
  config: CanvasConfig;

  /** WebChat container ID */
  webchatContainerId: string;

  /** Enter canvas mode, optionally with an initial message to send */
  enterCanvasMode: (initialMessage?: string) => void;

  /** Exit canvas mode */
  exitCanvasMode: () => void;

  /** Clear current search results */
  clearSearchResults: () => void;

  /** Manually process a message (for testing) */
  processMessage: (text: string) => void;

  /** Send a message to WebChat programmatically */
  sendMessage: (message: string) => void;
}

/**
 * Composable for managing canvas search mode.
 *
 * @param customConfig - Optional custom configuration
 * @returns Canvas search state and actions
 *
 * @example
 * const {
 *   isCanvasMode,
 *   filteredItemIds,
 *   enterCanvasMode,
 *   exitCanvasMode,
 *   webchatContainerId,
 * } = useCanvasSearch();
 */
export function useCanvasSearch(
  customConfig?: Partial<CanvasConfig>,
): UseCanvasSearchReturn {
  // Merge configuration
  const config: CanvasConfig = { ...DEFAULT_CONFIG, ...customConfig };

  // State
  const isCanvasMode = ref(false);
  const filteredItemIds = ref<string[]>([]);
  const lastSearchResult = ref<SearchResult | null>(null);

  // Computed
  const hasSearchResults = computed(() => filteredItemIds.value.length > 0);
  const isWaitingForSearch = computed(
    () => isCanvasMode.value && !hasSearchResults.value,
  );

  // Track if WebChat is initialized
  let isWebChatInitialized = false;

  // Pending message to send after WebChat is ready
  let pendingMessage: string | null = null;

  /**
   * Get single-use token for STT (Speech-to-Text) from ElevenLabs.
   * In production, this should be done on your backend to protect your API key.
   *
   * WARNING: Do not expose API keys in production frontend code!
   * Implement a backend endpoint that generates ElevenLabs tokens.
   *
   * Example backend endpoint (Node.js/Express):
   * ```
   * app.get('/api/voice/token', async (req, res) => {
   *   const response = await fetch('https://api.elevenlabs.io/v1/single-use-token/realtime_scribe', {
   *     method: 'POST',
   *     headers: { 'xi-api-key': process.env.ELEVENLABS_API_KEY }
   *   });
   *   const data = await response.json();
   *   res.json({ token: data.token });
   * });
   * ```
   */
  async function getVoiceToken(): Promise<string> {
    if (!VOICE_MODE_CONFIG.apiKey) {
      console.warn(
        '⚠️ Voice Mode: ElevenLabs API key not configured. Set VITE_ELEVENLABS_API_KEY.',
      );
      throw new Error('ElevenLabs API key not configured');
    }

    try {
      // Get a single-use token from ElevenLabs API
      const response = await fetch(
        'https://api.elevenlabs.io/v1/single-use-token/realtime_scribe',
        {
          method: 'POST',
          headers: {
            'xi-api-key': VOICE_MODE_CONFIG.apiKey,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({}),
        },
      );

      if (!response.ok) {
        const errorText = await response.text();
        console.error(
          '[Voice] Token fetch failed:',
          response.status,
          errorText,
        );
        throw new Error(`Failed to get voice token: ${response.status}`);
      }

      const data = await response.json();
      return data.token;
    } catch (error) {
      console.error('[Voice] Failed to get token:', error);
      throw error;
    }
  }

  /**
   * Get API key for TTS (Text-to-Speech).
   * In production, this should be done via a backend proxy endpoint.
   *
   * WARNING: Do not expose API keys in production frontend code!
   */
  function getApiKey(): string {
    if (!VOICE_MODE_CONFIG.apiKey) {
      throw new Error('ElevenLabs API key not configured');
    }
    return VOICE_MODE_CONFIG.apiKey;
  }

  /**
   * Process a block containing [[SEARCH_RESULT]] tags.
   * Called by the WebChat onNewBlock callback.
   */
  function processMessage(text: string): void {
    if (!text || typeof text !== 'string') {
      return;
    }

    const parseResult = parseSearchResults(text);

    if (parseResult.found && parseResult.result) {
      lastSearchResult.value = parseResult.result;
      filteredItemIds.value = parseResult.result.ids;
    }
  }

  /**
   * Handle metadata block from WebChat.
   * This is called by the WebChat onNewBlock callback when
   * a [[TAG]]content[[/TAG]] block is detected.
   */
  function handleNewBlock(block: string): void {
    // Check if it's a SEARCH_RESULT block
    if (block.includes('[[SEARCH_RESULT]]')) {
      processMessage(block);
    }
  }

  /**
   * Initialize WebChat in embedded mode.
   */
  function initializeWebChat(): void {
    if (isWebChatInitialized) return;

    // Check if WebChat library is loaded
    if (!window.WebChat) {
      console.warn('WebChat library not loaded. Retrying in 500ms...');
      setTimeout(initializeWebChat, 500);
      return;
    }

    // Check if channel UUID is configured
    if (!WEBCHAT_CONFIG.channelUuid) {
      console.warn(
        'WebChat channel UUID not configured. Set VITE_WEBCHAT_CHANNEL_UUID.',
      );
      return;
    }

    // Check if container exists
    const container = document.getElementById(WEBCHAT_CONTAINER_ID);
    if (!container) {
      console.warn('WebChat container not found. Retrying in 100ms...');
      setTimeout(initializeWebChat, 100);
      return;
    }

    try {
      // Clear any existing WebChat data before init (both storages)
      [sessionStorage, localStorage].forEach((storage) => {
        const keys = Object.keys(storage).filter(
          (key) =>
            key.toLowerCase().includes('webchat') ||
            key.toLowerCase().includes('weni') ||
            key.toLowerCase().includes('chat'),
        );
        keys.forEach((key) => storage.removeItem(key));
      });

      // Ensure container is empty before init
      container.innerHTML = '';

      const config: WebChatConfig = {
        selector: `#${WEBCHAT_CONTAINER_ID}`,
        socketUrl: WEBCHAT_CONFIG.socketUrl,
        host: WEBCHAT_CONFIG.host,
        channelUuid: WEBCHAT_CONFIG.channelUuid,

        // Enable embedded mode
        embedded: true,

        // CRITICAL: Connect WebSocket immediately on mount (not on demand)
        // This ensures connection is ready when we send the initial message
        connectOn: 'mount',

        // Don't hide widget while connecting - show it immediately
        hideWhenNotConnected: false,

        // Use session storage (clears on tab close)
        storage: 'session',

        // Clear cache on each initialization
        autoClearCache: true,

        // Fill the container
        widgetHeight: '100%',
        widgetWidth: '100%',

        // Appearance
        mainColor: '#00A49F',
        headerBackgroundColor: '#00A49F',
        title: 'Roadmap',
        inputTextFieldHint: 'Ask about the roadmap...',

        // Block detection callback - receives [[TAG]]content[[/TAG]] blocks
        onNewBlock: handleNewBlock,
      };

      // Add voice mode configuration if enabled
      if (VOICE_MODE_CONFIG.enabled && VOICE_MODE_CONFIG.apiKey) {
        config.voiceMode = {
          enabled: true,
          voiceId: VOICE_MODE_CONFIG.voiceId,
          silenceThreshold: 0.5, // seconds
          vadThreshold: 0.3, // Local VAD for barge-in detection (lower = more sensitive)
          sttVadThreshold: 0.5, // ElevenLabs STT VAD threshold (0.3-0.7 recommended)
          enableBargeIn: true, // Allow user to interrupt agent
          autoListen: true, // Auto-listen after agent finishes speaking
          getToken: getVoiceToken, // For STT (single-use token)
          getApiKey: getApiKey, // For TTS (API key)
        };

        // Add language code if specified
        if (VOICE_MODE_CONFIG.languageCode) {
          config.voiceMode.languageCode = VOICE_MODE_CONFIG.languageCode;
        }
      }

      window.WebChat.init(config);

      isWebChatInitialized = true;

      // If there's a pending message, wait for connection and send
      if (pendingMessage) {
        const messageToSend = pendingMessage;
        pendingMessage = null;
        // Wait for WebSocket connection to be established, then send
        waitForConnectionAndSend(messageToSend);
      }
    } catch (error) {
      console.error('Failed to initialize WebChat:', error);
    }
  }

  /**
   * Wait for WebChat connection to be established, then send message.
   * Uses WebChat.onReady() API for proper connection and initialization detection.
   */
  async function waitForConnectionAndSend(message: string): Promise<void> {
    if (!window.WebChat) {
      return;
    }

    try {
      // Wait for connection AND initialization (max 10 seconds)
      if (window.WebChat.onReady) {
        await window.WebChat.onReady(10000);
      }
      sendMessage(message);
    } catch {
      // Try to send anyway - WebChat.send will queue it
      sendMessage(message);
    }
  }

  /**
   * Send a message to WebChat using the vendor API.
   */
  function sendMessage(message: string): void {
    if (!message || typeof message !== 'string') {
      return;
    }

    // If WebChat not initialized yet, store as pending
    if (!isWebChatInitialized) {
      pendingMessage = message;
      return;
    }

    // Check if WebChat is available
    if (!window.WebChat || !window.WebChat.send) {
      pendingMessage = message;
      return;
    }

    try {
      window.WebChat.send({
        text: message,
        metadata: {
          source: 'magic-search-bar',
          page: '/roadmap',
        },
      });
    } catch {
      // Silent fail - message was already added to UI
    }
  }

  /**
   * Destroy WebChat instance completely.
   * Must clean DOM, storage, and internal state to allow re-initialization.
   */
  async function destroyWebChat(): Promise<void> {
    if (!isWebChatInitialized) return;

    // Mark as not initialized immediately to prevent race conditions
    isWebChatInitialized = false;

    try {
      // 1. Call vendor destroy if available - this unmounts React
      if (window.WebChat && window.WebChat.destroy) {
        window.WebChat.destroy();
      }

      // 2. Wait for React to complete unmount before touching DOM
      await new Promise((resolve) => setTimeout(resolve, 100));

      // 3. Clear all WebChat data from storage
      [sessionStorage, localStorage].forEach((storage) => {
        const keys = Object.keys(storage).filter(
          (key) =>
            key.toLowerCase().includes('webchat') ||
            key.toLowerCase().includes('weni') ||
            key.toLowerCase().includes('chat'),
        );
        keys.forEach((key) => storage.removeItem(key));
      });

      // 4. Clean container DOM only after React unmount completes
      const container = document.getElementById(WEBCHAT_CONTAINER_ID);
      if (container) {
        container.innerHTML = '';
      }

      // 5. Also clear any orphaned webchat elements that might be outside container
      document
        .querySelectorAll('.weni-widget, .weni-chat, [class*="weni-"]')
        .forEach((el) => {
          if (!el.closest(`#${WEBCHAT_CONTAINER_ID}`)) {
            el.remove();
          }
        });
    } catch {
      // Ignore cleanup errors - the widget is being destroyed anyway
    }
  }

  /**
   * Enter canvas search mode.
   * @param initialMessage - Optional message to send automatically after WebChat is ready
   */
  function enterCanvasMode(initialMessage?: string): void {
    if (isCanvasMode.value) {
      // If already in canvas mode but received a new message, send it
      if (initialMessage) {
        sendMessage(initialMessage);
      }
      return;
    }

    // Store pending message to send after WebChat initializes
    if (initialMessage) {
      pendingMessage = initialMessage;
    }

    isCanvasMode.value = true;

    // Initialize WebChat after DOM update
    setTimeout(initializeWebChat, 50);
  }

  /**
   * Exit canvas search mode.
   */
  async function exitCanvasMode(): Promise<void> {
    if (!isCanvasMode.value) {
      return;
    }

    isCanvasMode.value = false;

    // Clear pending message
    pendingMessage = null;

    // Destroy WebChat (wait for React to unmount)
    await destroyWebChat();

    // Clear search results
    clearSearchResults();
  }

  /**
   * Clear current search results.
   */
  function clearSearchResults(): void {
    filteredItemIds.value = [];
    lastSearchResult.value = null;
  }

  // Lifecycle hooks
  onUnmounted(() => {
    // Cleanup
    if (isCanvasMode.value) {
      destroyWebChat();
    }
  });

  return {
    isCanvasMode,
    filteredItemIds,
    lastSearchResult,
    hasSearchResults,
    isWaitingForSearch,
    config,
    webchatContainerId: WEBCHAT_CONTAINER_ID,
    enterCanvasMode,
    exitCanvasMode,
    clearSearchResults,
    processMessage,
    sendMessage,
  };
}

export default useCanvasSearch;
