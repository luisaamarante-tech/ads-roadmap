/**
 * Stylelint Configuration
 * Constitution: "Use BEM methodology for CSS classes: .block__element--modifier"
 */

export default {
  extends: ['stylelint-config-standard', 'stylelint-config-recommended-vue'],
  plugins: ['stylelint-selector-bem-pattern'],
  rules: {
    // BEM pattern enforcement
    'plugin/selector-bem-pattern': {
      preset: 'bem',
      componentName: '[A-Z]+',
      componentSelectors: {
        initial:
          '^\\.{componentName}(?:__[a-z]+(?:-[a-z]+)*)?(?:--[a-z]+(?:-[a-z]+)*)?$',
      },
    },

    // Allow class pattern flexibility during migration
    'selector-class-pattern': null,

    // Allow custom properties
    'custom-property-pattern': null,

    // Vue-specific adjustments
    'at-rule-no-unknown': [
      true,
      {
        ignoreAtRules: [
          'tailwind',
          'apply',
          'variants',
          'responsive',
          'screen',
        ],
      },
    ],

    // Declaration order (optional but helpful)
    'declaration-empty-line-before': null,
  },
  overrides: [
    {
      files: ['**/*.vue'],
      customSyntax: 'postcss-html',
    },
  ],
};
