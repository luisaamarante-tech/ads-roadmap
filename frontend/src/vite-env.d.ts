/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL?: string;
  readonly BASE_URL: string;
  // WebChat configuration
  readonly VITE_WEBCHAT_SOCKET_URL?: string;
  readonly VITE_WEBCHAT_HOST?: string;
  readonly VITE_WEBCHAT_CHANNEL_UUID?: string;
  // Voice Mode configuration
  readonly VITE_VOICE_MODE_ENABLED?: string;
  readonly VITE_ELEVENLABS_API_KEY?: string;
  readonly VITE_ELEVENLABS_VOICE_ID?: string;
  readonly VITE_VOICE_MODE_LANGUAGE_CODE?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
