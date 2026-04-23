# CI/CD Fixes - Data Model

**Created**: 2025-12-26
**Related**: [CI Fixes Plan](./ci-fixes-plan.md)

This document defines the entities for tracking CI/CD pipeline fixes.

## Entities

### CIIssue

Represents a CI/CD pipeline failure that needs fixing.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | string | Yes | Unique identifier (e.g., "frontend-eslint-conflict") |
| title | string | Yes | Short description of the issue |
| category | enum | Yes | Type: "dependency", "formatting", "commit-message", "test" |
| severity | enum | Yes | Priority: "critical", "high", "medium", "low" |
| status | enum | Yes | State: "identified", "planned", "fixing", "testing", "resolved" |
| affectedJob | string | Yes | CI job name (e.g., "frontend", "backend", "commitlint") |
| errorMessage | string | No | Raw error message from CI logs |
| rootCause | string | Yes | Analysis of why it failed |
| solution | string | Yes | How to fix it |
| filesAffected | string[] | No | List of files that need changes |
| commandsToFix | string[] | No | Commands to run to resolve |
| verificationSteps | string[] | No | Steps to verify fix worked |
| resolvedAt | datetime | No | When the issue was resolved |

### DependencyConflict

Represents a dependency version conflict (extends CIIssue).

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| packageName | string | Yes | Name of the conflicting package |
| currentVersion | string | Yes | Currently installed version |
| requiredVersion | string | Yes | Version required by another package |
| conflictingPackage | string | Yes | Package causing the conflict |
| resolutionStrategy | enum | Yes | "upgrade", "downgrade", "peer-deps", "alternative" |
| newVersion | string | No | Version to install as fix |

### FormattingIssue

Represents code formatting violations (extends CIIssue).

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| formatter | string | Yes | Tool name (e.g., "Black", "Prettier") |
| filesCount | integer | Yes | Number of files needing formatting |
| fileList | string[] | Yes | Full list of affected files |
| autoFixable | boolean | Yes | Can formatter auto-fix? |
| fixCommand | string | Yes | Command to run formatter |

### CommitMessageIssue

Represents commit message validation failures (extends CIIssue).

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| commitSha | string | Yes | Git commit SHA |
| currentMessage | string | Yes | Current (invalid) commit message |
| violations | string[] | Yes | List of validation errors |
| suggestedMessage | string | Yes | Properly formatted message |
| requiresRebase | boolean | Yes | Needs git rebase to fix? |
| affectsMultipleCommits | boolean | Yes | Issue in multiple commits? |

## Enumeration Types

### IssueCategory
- `dependency`: Package version conflicts
- `formatting`: Code style violations
- `commit-message`: Commit message format issues
- `test`: Test failures
- `build`: Build failures
- `linting`: Static analysis errors

### IssueSeverity
- `critical`: Blocks all CI jobs, prevents merge
- `high`: Blocks specific critical job
- `medium`: Non-blocking but should fix
- `low`: Optional improvement

### IssueStatus
- `identified`: Issue discovered in CI logs
- `planned`: Fix strategy documented
- `fixing`: Currently implementing fix
- `testing`: Verifying fix locally
- `resolved`: Fix pushed and CI passing

### ResolutionStrategy
- `upgrade`: Upgrade package to newer version
- `downgrade`: Downgrade package to older version
- `peer-deps`: Use --legacy-peer-deps flag
- `alternative`: Switch to alternative package
- `patch`: Create patch file for dependency

## Current Issues (Instance Data)

### Issue 1: Frontend ESLint Dependency Conflict

```yaml
id: frontend-eslint-typescript-conflict
title: typescript-eslint 7.x incompatible with ESLint 9.x
category: dependency
severity: critical
status: resolved
affectedJob: frontend
rootCause: typescript-eslint@7.18.0 requires eslint@^8.56.0, but eslint@9.39.2 is installed
solution: Upgrade typescript-eslint to 8.x which supports ESLint 9.x
filesAffected:
  - frontend/package.json
commandsToFix:
  - cd frontend
  - npm install typescript-eslint@^8.0.0
  - npm install
verificationSteps:
  - npm run lint:check
  - npm run type-check
resolvedAt: 2025-12-26T14:30:00Z

# DependencyConflict fields
packageName: typescript-eslint
currentVersion: ^7.5.0
requiredVersion: ">=8.0.0"
conflictingPackage: eslint@9.39.2
resolutionStrategy: upgrade
newVersion: ^8.0.0
```

### Issue 2: Backend Black Formatting

```yaml
id: backend-black-formatting
title: 20 Python files need Black formatting
category: formatting
severity: high
status: fixing
affectedJob: backend
rootCause: Files created/modified without running Black formatter
solution: Run black backend/app/ backend/tests/
filesAffected:
  - backend/app/__init__.py
  - backend/app/config.py
  - backend/app/models/__init__.py
  - backend/app/models/roadmap.py
  - backend/app/routes/__init__.py
  - backend/app/routes/health.py
  - backend/app/routes/roadmap.py
  - backend/app/services/__init__.py
  - backend/app/services/cache_service.py
  - backend/app/services/jira_client.py
  - backend/app/services/sync_service.py
  - backend/tests/__init__.py
  - backend/tests/conftest.py
  - backend/tests/unit/__init__.py
  - backend/tests/unit/test_models.py
  - backend/tests/unit/test_cache_service.py
  - backend/tests/unit/test_jira_client.py
  - backend/tests/unit/test_sync_service.py
  - backend/tests/integration/__init__.py
  - backend/tests/integration/test_routes.py
commandsToFix:
  - cd backend
  - source venv/bin/activate
  - black app/ tests/
verificationSteps:
  - black --check app/ tests/
  - pytest

# FormattingIssue fields
formatter: Black
filesCount: 20
fileList: [see filesAffected above]
autoFixable: true
fixCommand: black app/ tests/
```

### Issue 3: Commit Message Format

```yaml
id: commit-message-non-conventional
title: Commit message doesn't follow Conventional Commits
category: commit-message
severity: high
status: planned
affectedJob: commitlint
rootCause: Missing type prefix and proper formatting
solution: Amend commit with proper conventional format
filesAffected: []
commandsToFix:
  - 'git commit --amend -m "refactor(constitution): implement code quality standards"'
verificationSteps:
  - npx commitlint --from HEAD~1 --to HEAD
  - git log -1

# CommitMessageIssue fields
commitSha: 01c2a8a97ac77cfef5d40d0b3c8f324fb262f614
currentMessage: "Implement refactoring based on Weni code conventions and best practices"
violations:
  - "subject may not be empty [subject-empty]"
  - "type may not be empty [type-empty]"
suggestedMessage: |
  refactor(constitution): implement code quality standards

  - Add pre-commit hooks (Black, ESLint, Prettier, Stylelint)
  - Refactor all Vue components to BEM methodology
  - Write unit tests for backend (80%+ coverage)
  - Write component tests for frontend (80%+ coverage)
  - Integrate Unnnic Design System tokens
  - Improve semantic HTML and accessibility
  - Add CI/CD pipeline with GitHub Actions
requiresRebase: false
affectsMultipleCommits: false
```

## Relationships

```
CIIssue (1) ──► (0..1) DependencyConflict
CIIssue (1) ──► (0..1) FormattingIssue
CIIssue (1) ──► (0..1) CommitMessageIssue
```

## Validation Rules

1. **CIIssue**:
   - `id` must be kebab-case
   - `status` transitions: identified → planned → fixing → testing → resolved
   - `resolvedAt` required when status = "resolved"

2. **DependencyConflict**:
   - `newVersion` required when resolutionStrategy = "upgrade" or "downgrade"
   - `currentVersion` and `requiredVersion` must be valid semver

3. **FormattingIssue**:
   - `filesCount` must match length of `fileList`
   - `autoFixable` = true requires `fixCommand`

4. **CommitMessageIssue**:
   - `suggestedMessage` must pass commitlint validation
   - `commitSha` must be valid git SHA

## State Transitions

### Issue Lifecycle

```
identified
    ↓
planned (have solution)
    ↓
fixing (implementing)
    ↓
testing (verifying locally)
    ↓
resolved (CI passing)
```

### Valid Transitions
- identified → planned
- planned → fixing
- fixing → testing
- testing → resolved
- testing → fixing (if verification fails)
- Any state → identified (if issue reoccurs)
