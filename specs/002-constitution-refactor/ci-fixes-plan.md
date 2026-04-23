# CI/CD Fixes Implementation Plan

**Branch**: `002-constitution-refactor` | **Date**: 2025-12-26
**Parent Plan**: [Constitution Refactor Plan](./plan.md)

## Summary

Fix three critical CI/CD pipeline failures identified during the initial implementation:

1. **Frontend Dependency Conflict**: ESLint 9 is incompatible with typescript-eslint 7.x (requires ESLint 8.x)
2. **Backend Code Formatting**: 20 backend files need Black formatting to pass CI checks
3. **Commit Message Format**: Recent commits don't follow Conventional Commits standard

## Technical Context

**Language/Version**: Node.js 20 (frontend), Python 3.11+ (backend)
**Primary Tools**:
- Frontend: ESLint 8.x (downgrade from 9.x), typescript-eslint 8.x (upgrade from 7.x)
- Backend: Black 24.3.0 (already installed)
- Git: Conventional Commits format

**Target Platform**: GitHub Actions CI/CD
**Project Type**: Dependency version fix + code formatting
**Constraints**:
- Must maintain constitution compliance
- Cannot break existing functionality
- Must pass all CI checks

## Issues Analysis

### Issue 1: Frontend ESLint Version Conflict

**Problem**: typescript-eslint@7.18.0 requires eslint@^8.56.0, but we have eslint@9.39.2

**Root Cause**: ESLint 9 was released recently and typescript-eslint 7.x doesn't support it yet

**Solution**:
- Option A: Downgrade ESLint to 8.x (stable, well-tested)
- Option B: Upgrade typescript-eslint to 8.x (supports ESLint 9)

**Chosen**: Option B - Upgrade typescript-eslint to 8.x for better long-term compatibility

### Issue 2: Backend Black Formatting

**Problem**: 20 Python files fail Black formatting checks

**Root Cause**: Files were created/modified without running Black formatter

**Affected Files**:
- `backend/app/__init__.py`
- `backend/app/config.py`
- `backend/app/models/__init__.py`
- `backend/app/models/roadmap.py`
- `backend/app/routes/__init__.py`
- `backend/app/routes/health.py`
- `backend/app/routes/roadmap.py`
- `backend/app/services/__init__.py`
- `backend/app/services/cache_service.py`
- `backend/app/services/jira_client.py`
- `backend/app/services/sync_service.py`
- `backend/tests/__init__.py`
- `backend/tests/conftest.py`
- `backend/tests/unit/__init__.py`
- `backend/tests/unit/test_models.py`
- `backend/tests/unit/test_cache_service.py`
- `backend/tests/unit/test_jira_client.py`
- `backend/tests/unit/test_sync_service.py`
- `backend/tests/integration/__init__.py`
- `backend/tests/integration/test_routes.py`

**Solution**: Run `black backend/` to auto-format all files

### Issue 3: Commit Message Format

**Problem**: Commit "Implement refactoring based on Weni code conventions and best practices" doesn't follow Conventional Commits

**Root Cause**: Missing type prefix (feat/fix/refactor/etc.)

**Solution**: Use `git commit --amend` to fix the message or create a new commit with proper format

**Proper Format**:
```
refactor(constitution): implement code quality standards

- Add pre-commit hooks with Black, ESLint, Prettier
- Refactor all components to BEM methodology
- Add 80%+ test coverage
- Integrate Unnnic Design System
- Improve semantic HTML and accessibility
```

## Implementation Phases

### Phase 1: Fix Frontend Dependencies

1. Update `frontend/package.json`:
   - Change `typescript-eslint` from `^7.5.0` to `^8.0.0`
   - Keep `eslint` at `^9.0.0`
   - Update related ESLint plugins if needed

2. Run `npm install` to resolve dependencies

3. Verify ESLint still works: `npm run lint`

### Phase 2: Format Backend Code

1. Activate backend virtual environment
2. Run `black backend/app/ backend/tests/`
3. Verify formatting: `black --check backend/`
4. Run tests to ensure no regressions: `pytest`

### Phase 3: Fix Commit Message

1. Amend the commit message using:
   ```bash
   git commit --amend -m "refactor(constitution): implement code quality standards

   - Add pre-commit hooks with Black, ESLint, Prettier
   - Refactor all components to BEM methodology
   - Add 80%+ test coverage
   - Integrate Unnnic Design System
   - Improve semantic HTML and accessibility"
   ```

2. Or create a new commit with fixes:
   ```bash
   git add .
   git commit -m "fix(ci): resolve CI/CD pipeline failures

   - Upgrade typescript-eslint to 8.x for ESLint 9 compatibility
   - Format all backend files with Black
   - Fix commit message to follow Conventional Commits"
   ```

### Phase 4: Verify CI/CD

1. Push changes to remote branch
2. Monitor GitHub Actions workflow
3. Verify all jobs pass:
   - Backend: Black, isort, Flake8, tests
   - Frontend: ESLint, Prettier, Stylelint, tests
   - Commitlint: message format validation

## Constitution Check

*GATE: Must pass before implementation*

| Principle | Current State | Compliant | Action Required |
|-----------|---------------|-----------|-----------------|
| **Code Style Standards** | CI failing on formatting | ❌ No | Run Black formatter |
| **Testing & Quality** | Tests may fail after deps update | ⚠️ Verify | Test after changes |
| **Commit Standards** | Non-conventional commit message | ❌ No | Amend or new commit |

**Gate Status**: ⚠️ BLOCKED - Must fix formatting and commit message before CI passes

## Expected Outcomes

1. **Frontend Dependencies Resolved**: `npm ci` completes successfully
2. **Backend Formatting Passes**: All Black checks pass
3. **Commit Messages Valid**: All commits follow Conventional Commits format
4. **CI Pipeline Green**: All GitHub Actions jobs pass

## Rollback Plan

If issues persist:
1. **Frontend**: Revert to ESLint 8.x and typescript-eslint 7.x (stable combination)
2. **Backend**: Check if Black introduced breaking changes (unlikely)
3. **Commits**: Use `git rebase -i` to fix multiple commits if needed
