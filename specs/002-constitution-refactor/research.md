# Research: Constitution Compliance Refactor

**Feature**: 002-constitution-refactor
**Date**: 2025-12-26
**Purpose**: Document tooling decisions, best practices, and implementation patterns

---

## 1. Pre-commit Hooks Configuration

### Decision
Use `pre-commit` framework with hooks for Black, Flake8, ESLint, Prettier, and Stylelint.

### Rationale
- Industry standard for Python projects
- Supports polyglot repositories (Python + Node.js)
- Runs locally before commits reach CI, catching issues early
- Constitution mandates: "Pre-commit hooks MUST run: linters (Black, Flake8, ESLint), formatters, and unit tests"

### Alternatives Considered
| Alternative | Rejected Because |
|-------------|------------------|
| Husky (Node.js) | Would require separate config for Python, pre-commit handles both |
| Git hooks directly | Hard to share/version, pre-commit provides reproducibility |
| CI-only validation | Too late in cycle, constitution requires pre-commit |

### Configuration Pattern
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.3.0
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
        additional_dependencies: [flake8-docstrings]

  - repo: local
    hooks:
      - id: eslint
        name: ESLint
        entry: npm run lint --prefix frontend
        language: system
        files: ^frontend/.*\.(vue|ts|js)$
        pass_filenames: false
```

---

## 2. Python Linting & Formatting

### Decision
Use Black for formatting and Flake8 for linting with pyproject.toml configuration.

### Rationale
- Black is opinionated and eliminates style debates
- Flake8 catches logical errors and enforces PEP 8
- pyproject.toml consolidates Python tool config (PEP 517/518 standard)
- Constitution: "Run Black and Flake8 via pre-commit hooks"

### Configuration Pattern
```toml
# pyproject.toml
[tool.black]
line-length = 88
target-version = ['py311']
include = '\.pyi?$'
extend-exclude = '''
/(
  venv
  | __pycache__
)/
'''

[tool.flake8]
max-line-length = 88
extend-ignore = ["E203", "E501", "W503"]
exclude = ["venv", "__pycache__", ".git"]
```

### Import Ordering
Use `isort` for PEP 8 import grouping:
```toml
[tool.isort]
profile = "black"
known_first_party = ["app"]
sections = ["FUTURE", "STDLIB", "THIRDPARTY", "FIRSTPARTY", "LOCALFOLDER"]
```

---

## 3. Frontend Linting (ESLint + Prettier + Stylelint)

### Decision
Use ESLint flat config (new standard), Prettier for formatting, Stylelint for CSS with BEM plugin.

### Rationale
- ESLint 9+ uses flat config by default
- Prettier handles formatting, ESLint handles logic/rules
- Stylelint with BEM plugin enforces naming methodology
- Constitution: "Frontend MUST use ESLint, Prettier, and Stylelint"

### Alternatives Considered
| Alternative | Rejected Because |
|-------------|------------------|
| ESLint legacy config (.eslintrc) | Deprecated, flat config is future |
| Biome | Less Vue 3 ecosystem support |
| Only Prettier | Doesn't catch logic issues |

### Configuration Pattern

```javascript
// eslint.config.js (flat config)
import eslint from '@eslint/js';
import tseslint from 'typescript-eslint';
import pluginVue from 'eslint-plugin-vue';

export default [
  eslint.configs.recommended,
  ...tseslint.configs.recommended,
  ...pluginVue.configs['flat/recommended'],
  {
    rules: {
      'semi': ['error', 'always'],
      'quotes': ['error', 'single'],
      'vue/multi-word-component-names': 'off',
    }
  }
];
```

```javascript
// prettier.config.js
export default {
  semi: true,
  singleQuote: true,
  tabWidth: 2,
  trailingComma: 'all',
  bracketSpacing: true,
  arrowParens: 'always',
  vueIndentScriptAndStyle: false,
};
```

```javascript
// stylelint.config.js
export default {
  extends: ['stylelint-config-standard', 'stylelint-config-recommended-vue'],
  plugins: ['stylelint-selector-bem-pattern'],
  rules: {
    'plugin/selector-bem-pattern': {
      preset: 'bem',
      componentName: '[A-Z]+',
      componentSelectors: {
        initial: '^\\.{componentName}(?:__[a-z]+(?:-[a-z]+)*)?(?:--[a-z]+(?:-[a-z]+)*)?$'
      }
    }
  }
};
```

---

## 4. Testing Framework Selection

### Backend: pytest + pytest-cov

#### Decision
Use pytest with pytest-cov for coverage, already in requirements.txt.

#### Rationale
- pytest is industry standard for Python
- pytest-cov integrates coverage.py seamlessly
- Constitution: "minimum 80% code coverage"

#### Configuration Pattern
```toml
# pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
addopts = "--cov=app --cov-report=term-missing --cov-fail-under=80"

[tool.coverage.run]
source = ["app"]
omit = ["*/__pycache__/*", "*/tests/*"]
```

### Frontend: Vitest + Vue Test Utils

#### Decision
Use Vitest (Vite-native) with Vue Test Utils for component testing.

#### Rationale
- Vitest is native to Vite ecosystem (already using Vite 5)
- Vue Test Utils is official Vue 3 testing library
- Fast, HMR-compatible test runner
- Constitution: "Frontend MUST have unit tests"

#### Alternatives Considered
| Alternative | Rejected Because |
|-------------|------------------|
| Jest | Requires additional config for Vite, slower |
| Cypress Component Testing | Heavier, better for E2E |
| Testing Library (only) | Needs underlying runner |

#### Configuration Pattern
```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config';
import vue from '@vitejs/plugin-vue';

export default defineConfig({
  plugins: [vue()],
  test: {
    environment: 'jsdom',
    globals: true,
    coverage: {
      provider: 'v8',
      reporter: ['text', 'lcov'],
      exclude: ['node_modules/', 'tests/'],
      thresholds: {
        lines: 80,
        functions: 80,
        branches: 80,
        statements: 80,
      },
    },
  },
});
```

---

## 5. BEM Methodology Implementation

### Decision
Adopt strict BEM naming: `.block__element--modifier` pattern.

### Rationale
- Constitution: "Use BEM methodology for CSS classes"
- Provides predictable, maintainable CSS structure
- Avoids specificity wars and naming collisions

### Current Classes → BEM Conversion

| Current Class | BEM Equivalent |
|---------------|----------------|
| `.roadmap-card` | `.roadmap-card` (block) |
| `.card-header` | `.roadmap-card__header` (element) |
| `.card-title` | `.roadmap-card__title` (element) |
| `.expanded` | `.roadmap-card--expanded` (modifier) |
| `.filter-select` | `.roadmap-filters__select` (element) |
| `.quarter-btn.active` | `.roadmap-filters__quarter-btn--active` |

### Implementation Pattern
```css
/* Block */
.roadmap-card { }

/* Elements */
.roadmap-card__header { }
.roadmap-card__title { }
.roadmap-card__content { }
.roadmap-card__meta { }

/* Modifiers */
.roadmap-card--expanded { }
.roadmap-card--loading { }
```

---

## 6. Unnnic Design System Integration

### Decision
Replace custom UI components with @weni/unnnic-system equivalents.

### Rationale
- Constitution: "Use Unnnic components for all UI elements"
- Already installed as dependency (`@weni/unnnic-system: latest`)
- Ensures brand consistency across Weni products

### Component Mapping

| Current Implementation | Unnnic Replacement |
|-----------------------|-------------------|
| Custom `<button class="retry-button">` | `<UnnnicButton>` |
| Custom `<button class="read-more-button">` | `<UnnnicButton type="secondary">` |
| Custom `<select class="filter-select">` | `<UnnnicSelectSmart>` |
| Custom `<button class="quarter-btn">` | `<UnnnicButtonGroup>` or `<UnnnicButton>` |
| Custom tabs | `<UnnnicTab>` |
| Custom loading skeleton | `<UnnnicSkeletonLoading>` |

### Design Token Usage
```css
/* Use Unnnic CSS variables */
.roadmap-card {
  background: var(--unnnic-color-background-snow);
  border: 1px solid var(--unnnic-color-neutral-soft);
  border-radius: var(--unnnic-border-radius-sm);
  padding: var(--unnnic-spacing-stack-md);
}

.roadmap-card:hover {
  border-color: var(--unnnic-color-weni-500);
}
```

### Integration Steps
1. Import Unnnic CSS in main.ts: `import '@weni/unnnic-system/dist/style.css'`
2. Register components globally or import per-component
3. Replace custom components incrementally
4. Remove custom CSS that duplicates Unnnic tokens

---

## 7. GitHub Actions CI Pipeline

### Decision
Use GitHub Actions with matrix strategy for parallel backend/frontend jobs.

### Rationale
- Native to GitHub, no external CI service needed
- Matrix strategy runs Python and Node.js checks in parallel
- Constitution: "CI pipeline MUST validate all tests and linting on push/PR"

### Configuration Pattern
```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r backend/requirements.txt
      - run: pip install black flake8 isort
      - run: black --check backend/
      - run: flake8 backend/
      - run: pytest backend/tests --cov=backend/app --cov-fail-under=80

  frontend:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: frontend
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
      - run: npm ci
      - run: npm run lint
      - run: npm run test:coverage
```

---

## 8. Conventional Commits Enforcement

### Decision
Use commitlint with husky for commit message validation.

### Rationale
- Constitution: "Use Conventional Commits format: `<type>(<scope>): <description>`"
- Enables automated changelog generation
- Provides consistent commit history

### Configuration
```javascript
// commitlint.config.js
export default {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'header-max-length': [2, 'always', 50],
    'type-enum': [
      2,
      'always',
      ['feat', 'fix', 'docs', 'style', 'refactor', 'test', 'chore']
    ]
  }
};
```

---

## Summary of Decisions

| Area | Tool/Approach | Status |
|------|---------------|--------|
| Pre-commit | pre-commit framework | ✅ Decided |
| Python formatting | Black | ✅ Decided |
| Python linting | Flake8 + isort | ✅ Decided |
| Python testing | pytest + pytest-cov | ✅ Decided |
| JS/TS linting | ESLint (flat config) | ✅ Decided |
| JS/TS formatting | Prettier | ✅ Decided |
| CSS linting | Stylelint + BEM plugin | ✅ Decided |
| Frontend testing | Vitest + Vue Test Utils | ✅ Decided |
| CSS methodology | BEM | ✅ Decided |
| Design system | Unnnic | ✅ Decided |
| CI/CD | GitHub Actions | ✅ Decided |
| Commit format | Conventional Commits | ✅ Decided |

All NEEDS CLARIFICATION items have been resolved through research.
