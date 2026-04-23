/**
 * Vitest Configuration Contract
 * Location: /frontend/vitest.config.ts
 * Purpose: Frontend test runner configuration
 * Constitution: "Frontend MUST have unit tests using Vitest (or equivalent) with minimum 80% coverage"
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
    // ==========================================================================
    // Environment: jsdom for Vue component testing
    // ==========================================================================
    environment: 'jsdom',

    // ==========================================================================
    // Globals: Enable describe, it, expect without imports
    // ==========================================================================
    globals: true,

    // ==========================================================================
    // Test file patterns
    // ==========================================================================
    include: ['tests/**/*.spec.ts', 'tests/**/*.test.ts'],
    exclude: ['node_modules', 'dist'],

    // ==========================================================================
    // Setup files for test utilities
    // ==========================================================================
    setupFiles: ['./tests/setup.ts'],

    // ==========================================================================
    // Coverage configuration
    // Constitution: "minimum 80% code coverage"
    // ==========================================================================
    coverage: {
      // Use V8 coverage provider (faster than istanbul)
      provider: 'v8',

      // Report formats
      reporter: ['text', 'text-summary', 'lcov', 'html'],

      // Coverage directory
      reportsDirectory: './coverage',

      // Include/exclude patterns
      include: ['src/**/*.{ts,vue}'],
      exclude: [
        'node_modules/',
        'tests/',
        'src/main.ts',
        '**/*.d.ts',
        '**/*.spec.ts',
        '**/*.test.ts',
      ],

      // =======================================================================
      // Thresholds: MUST be >= 80% per Constitution
      // =======================================================================
      thresholds: {
        lines: 80,
        functions: 80,
        branches: 80,
        statements: 80,
      },

      // Fail if thresholds not met
      // Note: Enforced in CI, not locally by default
    },

    // ==========================================================================
    // Reporter configuration
    // ==========================================================================
    reporters: ['default', 'html'],

    // ==========================================================================
    // Watch mode configuration
    // ==========================================================================
    watch: false,

    // ==========================================================================
    // Timeout for slow tests
    // ==========================================================================
    testTimeout: 10000,
  },
});

