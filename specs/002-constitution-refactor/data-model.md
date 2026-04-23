# Data Model: Constitution Compliance Refactor

**Feature**: 002-constitution-refactor
**Date**: 2025-12-26
**Purpose**: Define configuration entities and their relationships

---

## Overview

This feature introduces configuration files rather than database entities. The "data model" describes the structure and relationships between configuration files that enforce constitution compliance.

---

## Configuration Entities

### 1. Pre-commit Configuration

**Entity**: `.pre-commit-config.yaml`
**Location**: Repository root
**Purpose**: Defines hooks that run before each commit

```yaml
# Schema
repos:
  - repo: string          # Repository URL or 'local'
    rev: string           # Version tag
    hooks:
      - id: string        # Hook identifier
        name: string      # Display name (optional)
        entry: string     # Command to run (for local hooks)
        language: string  # Hook language
        files: string     # Regex pattern for files (optional)
        args: string[]    # Additional arguments (optional)
```

**Relationships**:
- References `pyproject.toml` for Black/Flake8 configuration
- References `frontend/eslint.config.js` for ESLint execution
- Triggers pytest and vitest test suites

**Validation Rules**:
- MUST include Black hook (Python formatting)
- MUST include Flake8 hook (Python linting)
- MUST include ESLint hook (JS/TS linting)
- MUST include test execution hooks

---

### 2. Python Project Configuration

**Entity**: `pyproject.toml`
**Location**: `backend/pyproject.toml`
**Purpose**: Centralizes Python tool configuration

```toml
# Schema
[tool.black]
line-length = integer          # Max line length (default: 88)
target-version = string[]      # Python versions
include = string               # File pattern
extend-exclude = string        # Exclusion pattern

[tool.flake8]
max-line-length = integer
extend-ignore = string[]       # Error codes to ignore
exclude = string[]             # Directories to skip

[tool.isort]
profile = string               # Preset (e.g., "black")
known_first_party = string[]   # Local package names
sections = string[]            # Import section order

[tool.pytest.ini_options]
testpaths = string[]           # Test directories
addopts = string               # Default arguments
python_files = string[]        # Test file patterns

[tool.coverage.run]
source = string[]              # Modules to measure
omit = string[]                # Paths to exclude
```

**Relationships**:
- Read by Black, Flake8, isort, pytest
- Referenced by `.pre-commit-config.yaml`
- Coverage thresholds used by CI pipeline

**Validation Rules**:
- `line-length` MUST be 88 (Black default, compatible with Flake8)
- `target-version` MUST include py311
- Coverage threshold MUST be ≥80%

---

### 3. ESLint Configuration

**Entity**: `eslint.config.js`
**Location**: `frontend/eslint.config.js`
**Purpose**: JavaScript/TypeScript linting rules

```javascript
// Schema (flat config array)
export default [
  {
    files: string[],           // Glob patterns
    ignores: string[],         // Exclusions
    languageOptions: {
      parser: object,          // Parser module
      parserOptions: object,   // Parser settings
      globals: object,         // Global variables
    },
    plugins: object,           // ESLint plugins
    rules: {
      [ruleName]: 'off' | 'warn' | 'error' | [severity, options]
    }
  }
];
```

**Relationships**:
- Extends TypeScript ESLint and Vue plugin configs
- Used by pre-commit and npm scripts
- Must align with Prettier formatting

**Validation Rules**:
- MUST include `semi: ['error', 'always']`
- MUST include `quotes: ['error', 'single']`
- MUST include Vue 3 plugin configuration

---

### 4. Prettier Configuration

**Entity**: `prettier.config.js`
**Location**: `frontend/prettier.config.js`
**Purpose**: Code formatting rules

```javascript
// Schema
export default {
  semi: boolean,               // Semicolons at end
  singleQuote: boolean,        // Single vs double quotes
  tabWidth: number,            // Indentation spaces
  trailingComma: 'none' | 'es5' | 'all',
  bracketSpacing: boolean,     // Spaces in objects
  arrowParens: 'avoid' | 'always',
  vueIndentScriptAndStyle: boolean,
};
```

**Relationships**:
- Must not conflict with ESLint rules
- Applied by pre-commit and npm scripts

**Validation Rules**:
- `semi` MUST be `true` (constitution requirement)
- `singleQuote` MUST be `true` (constitution requirement)
- `tabWidth` MUST be `2` (constitution requirement)

---

### 5. Stylelint Configuration

**Entity**: `stylelint.config.js`
**Location**: `frontend/stylelint.config.js`
**Purpose**: CSS linting with BEM enforcement

```javascript
// Schema
export default {
  extends: string[],           // Base configurations
  plugins: string[],           // Additional plugins
  rules: {
    [ruleName]: value | [severity, options]
  },
  overrides: [{
    files: string[],
    rules: object
  }]
};
```

**Relationships**:
- BEM plugin validates class naming
- Used by pre-commit and npm scripts
- Applies to Vue SFC `<style>` blocks

**Validation Rules**:
- MUST extend `stylelint-config-standard`
- MUST include BEM pattern plugin
- MUST validate `.block__element--modifier` format

---

### 6. Vitest Configuration

**Entity**: `vitest.config.ts`
**Location**: `frontend/vitest.config.ts`
**Purpose**: Frontend test runner configuration

```typescript
// Schema
export default defineConfig({
  plugins: Plugin[],
  test: {
    environment: 'jsdom' | 'happy-dom' | 'node',
    globals: boolean,
    include: string[],
    exclude: string[],
    coverage: {
      provider: 'v8' | 'istanbul',
      reporter: string[],
      exclude: string[],
      thresholds: {
        lines: number,
        functions: number,
        branches: number,
        statements: number,
      }
    }
  }
});
```

**Relationships**:
- Uses Vite config as base
- Coverage thresholds checked by CI
- Test files in `tests/` directory

**Validation Rules**:
- `environment` MUST be `jsdom` for Vue components
- All `thresholds` MUST be ≥80%
- MUST include Vue plugin

---

### 7. GitHub Actions Workflow

**Entity**: `ci.yml`
**Location**: `.github/workflows/ci.yml`
**Purpose**: Continuous integration pipeline

```yaml
# Schema
name: string
on:
  push:
    branches: string[]
  pull_request:
    branches: string[]

jobs:
  [job-name]:
    runs-on: string
    defaults:
      run:
        working-directory: string
    steps:
      - uses: string           # Action reference
        with: object           # Action inputs
      - run: string            # Shell command
```

**Relationships**:
- Runs all pre-commit checks in clean environment
- Uploads coverage reports
- Fails on coverage below threshold

**Validation Rules**:
- MUST trigger on push and pull_request
- MUST run Black, Flake8, ESLint checks
- MUST run tests with coverage validation
- MUST fail on coverage <80%

---

## Entity Relationship Diagram

```
┌─────────────────────────────────────┐
│       .pre-commit-config.yaml       │
│   (Repository Root - Entry Point)   │
└──────────────┬──────────────────────┘
               │ triggers
               ▼
    ┌──────────┴──────────┐
    │                     │
    ▼                     ▼
┌───────────┐      ┌──────────────┐
│  Backend  │      │   Frontend   │
└─────┬─────┘      └──────┬───────┘
      │                   │
      ▼                   ▼
┌───────────────┐  ┌──────────────────┐
│pyproject.toml │  │ eslint.config.js │
│ - Black       │  │ prettier.config  │
│ - Flake8      │  │ stylelint.config │
│ - isort       │  │ vitest.config.ts │
│ - pytest      │  └────────┬─────────┘
└───────┬───────┘           │
        │                   │
        ▼                   ▼
┌───────────────────────────────────┐
│        .github/workflows/ci.yml   │
│   (Validates all configurations)  │
└───────────────────────────────────┘
```

---

## State Transitions

### Pre-commit Hook States

```
IDLE ─────────────────────────────────────────────────────────────►
       │                                                           │
       │ git commit                                                │
       ▼                                                           │
┌─────────────┐   pass   ┌─────────────┐   pass   ┌────────────┐  │
│ Black/Format│─────────►│ Flake8/Lint │─────────►│ pytest/test│──┤
└─────────────┘          └─────────────┘          └────────────┘  │
       │ fail                 │ fail                   │ fail     │
       ▼                      ▼                        ▼          │
┌──────────────────────────────────────────────────────────────┐  │
│                     COMMIT BLOCKED                           │  │
│            (Developer must fix issues)                       │  │
└──────────────────────────────────────────────────────────────┘  │
                                                                   │
                                                      ◄────────────┘
                                                      COMMIT SUCCEEDS
```

### CI Pipeline States

```
┌──────────┐
│ PR/Push  │
└────┬─────┘
     │
     ▼
┌────────────────┐
│ Checkout Code  │
└────────┬───────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌──────┐  ┌──────────┐
│Backend│ │ Frontend │
└───┬───┘ └────┬─────┘
    │          │
    ▼          ▼
┌───────┐  ┌───────┐
│Linting│  │Linting│
└───┬───┘  └───┬───┘
    │          │
    ▼          ▼
┌───────┐  ┌───────┐
│ Tests │  │ Tests │
└───┬───┘  └───┬───┘
    │          │
    └────┬─────┘
         │
         ▼
    ┌─────────┐
    │ Coverage│
    │  ≥80%?  │
    └────┬────┘
    yes/ \no
       /   \
      ▼     ▼
   ✅ PASS  ❌ FAIL
```

---

## Configuration Dependencies

| File | Depends On | Used By |
|------|------------|---------|
| `.pre-commit-config.yaml` | pyproject.toml, eslint.config.js | git hooks |
| `pyproject.toml` | requirements.txt | Black, Flake8, pytest |
| `eslint.config.js` | package.json | pre-commit, npm scripts |
| `prettier.config.js` | - | pre-commit, npm scripts |
| `stylelint.config.js` | package.json | pre-commit, npm scripts |
| `vitest.config.ts` | vite.config.ts, package.json | npm scripts, CI |
| `.github/workflows/ci.yml` | All above | GitHub Actions |
