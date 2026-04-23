/**
 * ESLint Configuration Contract
 * Location: /frontend/eslint.config.js
 * Purpose: JavaScript/TypeScript linting rules
 * Constitution: "Frontend MUST use ESLint, Prettier, and Stylelint for consistent code quality"
 */

import eslint from '@eslint/js';
import tseslint from 'typescript-eslint';
import pluginVue from 'eslint-plugin-vue';
import eslintConfigPrettier from 'eslint-config-prettier';

export default [
  // Base ESLint recommended rules
  eslint.configs.recommended,

  // TypeScript ESLint recommended rules
  ...tseslint.configs.recommended,

  // Vue 3 recommended rules
  ...pluginVue.configs['flat/recommended'],

  // Prettier compatibility (disables conflicting rules)
  eslintConfigPrettier,

  // Project-specific configuration
  {
    files: ['**/*.{js,ts,vue}'],
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: 'module',
      globals: {
        window: 'readonly',
        document: 'readonly',
        console: 'readonly',
      },
      parserOptions: {
        parser: tseslint.parser,
      },
    },
    rules: {
      // =======================================================================
      // Constitution: "Always use semicolons at statement ends"
      // =======================================================================
      'semi': ['error', 'always'],

      // =======================================================================
      // Constitution: "Use single quotes for strings (except HTML attributes)"
      // =======================================================================
      'quotes': ['error', 'single', { avoidEscape: true }],

      // =======================================================================
      // Constitution: "Use spaces inside object braces: { foo: bar }"
      // =======================================================================
      'object-curly-spacing': ['error', 'always'],

      // =======================================================================
      // Constitution: "Use parentheses around single arrow function parameters"
      // =======================================================================
      'arrow-parens': ['error', 'always'],

      // =======================================================================
      // Constitution: "Use trailing commas in multiline structures"
      // =======================================================================
      'comma-dangle': ['error', 'always-multiline'],

      // =======================================================================
      // Constitution: "Use 2-space indentation"
      // =======================================================================
      'indent': ['error', 2, { SwitchCase: 1 }],

      // =======================================================================
      // Constitution: "Use camelCase for variables and functions"
      // =======================================================================
      'camelcase': ['error', { properties: 'never' }],

      // =======================================================================
      // Constitution: "Prefix event handlers with on"
      // Note: Enforced via code review, not easily automated
      // =======================================================================

      // TypeScript specific
      '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
      '@typescript-eslint/explicit-function-return-type': 'off',
      '@typescript-eslint/no-explicit-any': 'warn',

      // Vue specific
      'vue/multi-word-component-names': 'off', // Allow single-word names like "App"
      'vue/html-indent': ['error', 2],
      'vue/script-indent': ['error', 2, { baseIndent: 0 }],
      'vue/max-attributes-per-line': ['error', {
        singleline: 3,
        multiline: 1,
      }],
      // =======================================================================
      // Constitution: "For multi-attribute elements, place one attribute per line"
      // =======================================================================
      'vue/first-attribute-linebreak': ['error', {
        singleline: 'ignore',
        multiline: 'below',
      }],
      'vue/html-closing-bracket-newline': ['error', {
        singleline: 'never',
        multiline: 'always',
      }],
    },
  },

  // Ignore patterns
  {
    ignores: [
      'node_modules/**',
      'dist/**',
      'coverage/**',
      '*.config.js',
      '*.config.ts',
    ],
  },
];

