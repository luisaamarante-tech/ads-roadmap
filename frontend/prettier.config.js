/**
 * Prettier Configuration
 * Constitution: "Frontend MUST use ESLint, Prettier, and Stylelint for consistent code quality"
 */

export default {
  // Constitution: "Always use semicolons at statement ends"
  semi: true,

  // Constitution: "Use single quotes for strings"
  singleQuote: true,

  // Constitution: "Use 2-space indentation"
  tabWidth: 2,

  // Constitution: "Use trailing commas in multiline structures"
  trailingComma: 'all',

  // Constitution: "Use spaces inside object braces: { foo: bar }"
  bracketSpacing: true,

  // Constitution: "Use parentheses around single arrow function parameters"
  arrowParens: 'always',

  // Vue-specific settings
  vueIndentScriptAndStyle: false,

  // Line width
  printWidth: 80,

  // End of line
  endOfLine: 'lf',
};
