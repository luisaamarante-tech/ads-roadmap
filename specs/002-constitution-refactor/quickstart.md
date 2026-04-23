# Quickstart: Constitution Compliance Refactor

**Feature**: 002-constitution-refactor
**Purpose**: Step-by-step guide to implement constitution compliance

---

## Prerequisites

- Python 3.11+
- Node.js 20+
- Git with pre-commit installed (`pip install pre-commit`)

---

## Phase 1: Install Pre-commit Hooks

### 1.1 Install pre-commit framework

```bash
# Install pre-commit globally or in virtualenv
pip install pre-commit

# Verify installation
pre-commit --version
```

### 1.2 Create pre-commit configuration

Copy the contract file to the repository root:

```bash
cp specs/002-constitution-refactor/contracts/pre-commit-config.yaml .pre-commit-config.yaml
```

### 1.3 Install the hooks

```bash
# Install hooks into .git/hooks
pre-commit install
pre-commit install --hook-type commit-msg

# Run on all files to verify setup
pre-commit run --all-files
```

---

## Phase 2: Configure Backend Tooling

### 2.1 Create pyproject.toml

Copy the contract file to the backend directory:

```bash
cp specs/002-constitution-refactor/contracts/pyproject.toml backend/pyproject.toml
```

### 2.2 Install development dependencies

```bash
cd backend
pip install black flake8 isort pytest-cov flake8-docstrings flake8-bugbear
```

### 2.3 Create setup.cfg for Flake8

```bash
# backend/setup.cfg
cat > backend/setup.cfg << 'EOF'
[flake8]
max-line-length = 88
extend-ignore = E203, E501, W503
exclude = venv, __pycache__, .git, data
per-file-ignores =
    __init__.py:F401
EOF
```

### 2.4 Verify backend linting works

```bash
cd backend
black --check .
isort --check-only .
flake8 .
```

---

## Phase 3: Configure Frontend Tooling

### 3.1 Install ESLint dependencies

```bash
cd frontend
npm install -D \
  @eslint/js \
  eslint \
  typescript-eslint \
  eslint-plugin-vue \
  eslint-config-prettier
```

### 3.2 Install Prettier

```bash
npm install -D prettier
```

### 3.3 Install Stylelint with BEM plugin

```bash
npm install -D \
  stylelint \
  stylelint-config-standard \
  stylelint-config-recommended-vue \
  stylelint-selector-bem-pattern \
  postcss-html
```

### 3.4 Install Vitest for testing

```bash
npm install -D \
  vitest \
  @vitest/coverage-v8 \
  @vue/test-utils \
  jsdom
```

### 3.5 Copy configuration files

```bash
cp specs/002-constitution-refactor/contracts/eslint.config.js frontend/eslint.config.js
cp specs/002-constitution-refactor/contracts/vitest.config.ts frontend/vitest.config.ts
```

### 3.6 Create Prettier config

```bash
cat > frontend/prettier.config.js << 'EOF'
export default {
  semi: true,
  singleQuote: true,
  tabWidth: 2,
  trailingComma: 'all',
  bracketSpacing: true,
  arrowParens: 'always',
  vueIndentScriptAndStyle: false,
  printWidth: 80,
};
EOF
```

### 3.7 Create Stylelint config

```bash
cat > frontend/stylelint.config.js << 'EOF'
export default {
  extends: [
    'stylelint-config-standard',
    'stylelint-config-recommended-vue',
  ],
  plugins: ['stylelint-selector-bem-pattern'],
  rules: {
    'plugin/selector-bem-pattern': {
      preset: 'bem',
      componentName: '[A-Z]+',
      componentSelectors: {
        initial: '^\\.{componentName}(?:__[a-z]+(?:-[a-z]+)*)?(?:--[a-z]+(?:-[a-z]+)*)?$'
      }
    },
    'selector-class-pattern': null,
  },
  overrides: [
    {
      files: ['**/*.vue'],
      customSyntax: 'postcss-html',
    },
  ],
};
EOF
```

### 3.8 Update package.json scripts

Add these scripts to `frontend/package.json`:

```json
{
  "scripts": {
    "lint": "eslint . --ext .vue,.js,.jsx,.cjs,.mjs,.ts,.tsx --fix",
    "lint:check": "eslint . --ext .vue,.js,.jsx,.cjs,.mjs,.ts,.tsx",
    "format": "prettier --write \"src/**/*.{vue,ts,js,css}\"",
    "format:check": "prettier --check \"src/**/*.{vue,ts,js,css}\"",
    "stylelint": "stylelint \"src/**/*.{vue,css}\" --fix",
    "stylelint:check": "stylelint \"src/**/*.{vue,css}\"",
    "test": "vitest run",
    "test:watch": "vitest",
    "test:coverage": "vitest run --coverage"
  }
}
```

### 3.9 Verify frontend linting works

```bash
cd frontend
npm run lint:check
npm run format:check
npm run stylelint:check
```

---

## Phase 4: Create Test Infrastructure

### 4.1 Backend test structure

```bash
# Create test directories
mkdir -p backend/tests/unit backend/tests/integration

# Create conftest.py for fixtures
cat > backend/tests/conftest.py << 'EOF'
"""Pytest configuration and shared fixtures."""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime

from app import create_app
from app.models import RoadmapItem, Module, SyncMetadata, DeliveryStatus, Quarter


@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app()
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def mock_cache():
    """Mock Flask-Caching instance."""
    cache = MagicMock()
    cache.get.return_value = None
    cache.set.return_value = True
    return cache


@pytest.fixture
def sample_roadmap_item():
    """Sample RoadmapItem for testing."""
    return RoadmapItem(
        id='TEST-123',
        title='Test Feature',
        description='A test feature description',
        status=DeliveryStatus.NOW,
        module='Test Module',
        module_id='test-module',
        release_year=2025,
        release_quarter=Quarter.Q1,
    )


@pytest.fixture
def mock_jira_response():
    """Mock JIRA API response."""
    return {
        'issues': [
            {
                'key': 'TEST-123',
                'fields': {
                    'summary': 'Test Feature',
                    'description': {'type': 'doc', 'content': []},
                }
            }
        ]
    }
EOF
```

### 4.2 Frontend test structure

```bash
# Create test directories
mkdir -p frontend/tests/components frontend/tests/services frontend/mocks

# Create test setup file
cat > frontend/tests/setup.ts << 'EOF'
/**
 * Vitest setup file
 * Configures test environment before tests run
 */

import { config } from '@vue/test-utils';

// Mock Unnnic components globally
config.global.stubs = {
  'UnnnicButton': true,
  'UnnnicInput': true,
  'UnnnicSelectSmart': true,
  'UnnnicTab': true,
};

// Mock IntersectionObserver
global.IntersectionObserver = class {
  constructor() {}
  observe() {}
  unobserve() {}
  disconnect() {}
} as any;
EOF

# Create mock data
cat > frontend/mocks/roadmapData.ts << 'EOF'
/**
 * Mock data for testing
 */

import type { RoadmapItem, Module, RoadmapStats } from '@/types/roadmap';

export const mockRoadmapItems: RoadmapItem[] = [
  {
    id: 'TEST-001',
    title: 'Test Feature One',
    description: 'Description for test feature one',
    status: 'DELIVERED',
    module: 'Test Module',
    moduleId: 'test-module',
    releaseYear: 2025,
    releaseQuarter: 'Q1',
    releaseMonth: null,
    images: [],
    documentationUrl: null,
    lastSyncedAt: '2025-01-01T00:00:00Z',
  },
];

export const mockModules: Module[] = [
  { id: 'test-module', name: 'Test Module', itemCount: 1 },
];

export const mockStats: RoadmapStats = {
  DELIVERED: 1,
  NOW: 0,
  NEXT: 0,
  FUTURE: 0,
};
EOF
```

---

## Phase 5: Setup GitHub Actions CI

### 5.1 Create workflow directory

```bash
mkdir -p .github/workflows
```

### 5.2 Copy CI workflow

```bash
cp specs/002-constitution-refactor/contracts/ci.yml .github/workflows/ci.yml
```

### 5.3 Create commitlint config

```bash
cat > commitlint.config.js << 'EOF'
export default {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'header-max-length': [2, 'always', 50],
    'type-enum': [
      2,
      'always',
      ['feat', 'fix', 'docs', 'style', 'refactor', 'test', 'chore']
    ],
    'scope-case': [2, 'always', 'lower-case'],
    'subject-case': [2, 'always', 'sentence-case'],
  }
};
EOF
```

---

## Phase 6: Verify Everything Works

### 6.1 Run all checks locally

```bash
# Run pre-commit on all files
pre-commit run --all-files

# Backend tests
cd backend
pytest tests/ --cov=app --cov-report=term-missing

# Frontend tests
cd frontend
npm run test:coverage
```

### 6.2 Make a test commit

```bash
# Stage all changes
git add .

# Commit with conventional format
git commit -m "chore(tooling): add pre-commit hooks and linting configuration"
```

If pre-commit fails, fix the issues and try again.

---

## Verification Checklist

| Step | Command | Expected Result |
|------|---------|-----------------|
| Pre-commit installed | `pre-commit --version` | Version displayed |
| Hooks installed | `ls .git/hooks/pre-commit` | File exists |
| Black works | `cd backend && black --check .` | No reformatting needed |
| Flake8 works | `cd backend && flake8 .` | No errors |
| ESLint works | `cd frontend && npm run lint:check` | No errors |
| Prettier works | `cd frontend && npm run format:check` | No differences |
| Stylelint works | `cd frontend && npm run stylelint:check` | No errors |
| Backend tests pass | `cd backend && pytest` | All tests pass |
| Backend coverage ≥80% | Check pytest output | Coverage meets threshold |
| Frontend tests pass | `cd frontend && npm run test` | All tests pass |
| Frontend coverage ≥80% | Check vitest output | Coverage meets threshold |
| Commit works | `git commit` | Pre-commit hooks pass |

---

## Troubleshooting

### Pre-commit hooks not running

```bash
# Reinstall hooks
pre-commit uninstall
pre-commit install
pre-commit install --hook-type commit-msg
```

### ESLint conflicts with Prettier

Ensure `eslint-config-prettier` is installed and is the LAST config in eslint.config.js.

### Stylelint BEM errors

The BEM plugin may flag existing classes. Either:
1. Refactor classes to BEM format
2. Temporarily disable the rule for specific files

### Coverage threshold failures

Increase test coverage before proceeding. Focus on:
1. Critical business logic
2. Edge cases
3. Error handling paths

---

## Next Steps

After completing this quickstart:

1. **Write unit tests** for backend services (see `/specs/002-constitution-refactor/tasks.md`)
2. **Write component tests** for frontend components
3. **Refactor CSS** to BEM methodology
4. **Integrate Unnnic** components
5. **Run accessibility audit** and fix issues
