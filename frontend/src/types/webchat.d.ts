/**
 * Type declarations for the vendor WebChat library (webchat-audio.umd.js).
 *
 * The WebChat library is loaded globally via a script tag and exposes
 * its API on window.WebChat.
 */

export interface VoiceModeConfig {
  enabled: boolean;
  voiceId?: string;
  languageCode?: string;
  silenceThreshold?: number;
  vadThreshold?: number;
  sttVadThreshold?: number;
  enableBargeIn?: boolean;
  autoListen?: boolean;
  getToken?: () => Promise<string>;
  getApiKey?: () => string;
  texts?: Record<string, unknown>;
}

export interface WebChatConfig {
  selector: string;
  socketUrl: string;
  host: string;
  channelUuid: string;
  embedded?: boolean;
  connectOn?: 'mount' | 'manual' | 'demand';
  hideWhenNotConnected?: boolean;
  storage?: 'local' | 'session';
  autoClearCache?: boolean;
  widgetHeight?: string;
  widgetWidth?: string;
  mainColor?: string;
  headerBackgroundColor?: string;
  title?: string;
  inputTextFieldHint?: string;
  onNewMessage?: (message: WebChatMessage) => void;
  onNewBlock?: (block: string) => void;
  voiceMode?: VoiceModeConfig;
}

export interface WebChatMessage {
  id: string;
  type: string;
  text: string;
  direction: 'incoming' | 'outgoing';
  timestamp: number;
}

export interface WebChatSendOptions {
  text: string;
  metadata?: Record<string, unknown>;
}

export interface WebChatAPI {
  init: (config: WebChatConfig) => void;
  open: () => void;
  close: () => void;
  destroy: () => void;
  send: (message: string | WebChatSendOptions) => void;
  sendMessage: (text: string) => void;
  on: (event: string, callback: (data: unknown) => void) => void;
  off: (event: string, callback: (data: unknown) => void) => void;
  /** Check if WebSocket connection is established */
  isConnected: () => Promise<boolean>;
  /** Wait for WebSocket connection to be established */
  onReady: (timeoutMs?: number) => Promise<void>;
}

declare global {
  interface Window {
    WebChat?: WebChatAPI;
  }
}
