/**
 * Vitest Configuration
 * Constitution: "Frontend MUST have unit tests using Vitest with minimum 80% coverage"
 */

import { defineConfig } from 'vitest/config';
import vue from '@vitejs/plugin-vue';
import { fileURLToPath, URL } from 'node:url';

export default defineConfig({
  plugins: [vue()],

  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },

  test: {
    // Environment: jsdom for Vue component testing
    environment: 'jsdom',

    // Globals: Enable describe, it, expect without imports
    globals: true,

    // Load test environment variables
    env: {
      VITE_WEBCHAT_CHANNEL_UUID: 'test-channel-uuid',
      VITE_WEBCHAT_SOCKET_URL: 'https://websocket.weni.ai',
      VITE_WEBCHAT_HOST: 'https://flows.weni.ai',
      VITE_API_URL: 'http://localhost:5001/api/v1',
    },

    // Test file patterns
    include: ['tests/**/*.spec.ts', 'tests/**/*.test.ts'],
    exclude: ['node_modules', 'dist'],

    // Setup files for test utilities
    setupFiles: ['./tests/setup.ts'],

    // Coverage configuration
    // Constitution: "minimum 80% code coverage"
    coverage: {
      provider: 'v8',
      reporter: ['text', 'text-summary', 'lcov', 'html'],
      reportsDirectory: './coverage',
      include: ['src/**/*.{ts,vue}'],
      exclude: [
        'node_modules/',
        'tests/',
        'src/main.ts',
        'src/App.vue', // App wrapper - tested via E2E
        'src/router/**', // Router config - tested via E2E
        'src/views/**', // Views - tested via E2E
        '**/*.d.ts',
        '**/*.spec.ts',
        '**/*.test.ts',
      ],
      thresholds: {
        lines: 80,
        functions: 80,
        branches: 80,
        statements: 80,
      },
    },

    // Reporter configuration
    reporters: ['default'],

    // Watch mode off for CI
    watch: false,

    // Timeout for slow tests
    testTimeout: 10000,
  },
});
