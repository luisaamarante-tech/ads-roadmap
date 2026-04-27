/**
 * Centralized environment configuration
 * All environment variables should be accessed through this module
 */

interface WindowConfigs {
  [key: string]: string | undefined;
}

declare global {
  interface Window {
    configs?: WindowConfigs;
  }
}

/**
 * Generic function to get environment variable from multiple sources
 * Priority: window.configs > import.meta.env
 */
function getEnv(name: string): string | undefined {
  return window?.configs?.[name] || import.meta.env[name];
}

/**
 * Get boolean environment variable
 */
function getBoolEnv(name: string, defaultValue = false): boolean {
  const value = getEnv(name);
  if (value === undefined) return defaultValue;
  return value === 'true' || value === '1';
}

/**
 * Centralized environment configuration object
 */
export const env = {
  // API Configuration
  apiUrl: getEnv('VITE_API_URL') || '/api/v1',
  baseUrl: import.meta.env.BASE_URL,

  // Auth Configuration
  authUsername: getEnv('VITE_AUTH_USERNAME') || '',
  authPassword: getEnv('VITE_AUTH_PASSWORD') || '',

  // WebChat Configuration
  webChat: {
    socketUrl: getEnv('VITE_WEBCHAT_SOCKET_URL') || 'https://websocket.weni.ai',
    host: getEnv('VITE_WEBCHAT_HOST') || 'https://flows.weni.ai',
    channelUuid: getEnv('VITE_WEBCHAT_CHANNEL_UUID') || '',
  },

  // Voice Mode Configuration
  voiceMode: {
    enabled: getBoolEnv('VITE_VOICE_MODE_ENABLED', false),
    apiKey: getEnv('VITE_ELEVENLABS_API_KEY') || '',
    voiceId: getEnv('VITE_ELEVENLABS_VOICE_ID') || 'pFZP5JQG7iQjIQuC4Bku',
    languageCode: getEnv('VITE_VOICE_MODE_LANGUAGE_CODE'),
  },
} as const;

/**
 * Legacy function for backward compatibility
 * @deprecated Use the env object instead
 */
export default function getEnvLegacy(name: string): string | undefined {
  return getEnv(name);
}
