# CI/CD Fixes - Task Breakdown

**Feature Branch**: `002-constitution-refactor`
**Created**: 2025-12-26
**Parent Spec**: [Constitution Refactor Spec](./spec.md)
**Implementation Plan**: [CI Fixes Plan](./ci-fixes-plan.md)

## Overview

This task list addresses three critical CI/CD pipeline failures blocking the constitution refactor merge:

1. **Frontend Dependency Conflict**: ESLint 9 incompatible with typescript-eslint 7.x
2. **Backend Formatting**: 20 Python files need Black formatting
3. **Commit Message**: Non-conventional commit format

**Total Tasks**: 12
**Estimated Time**: 30 minutes
**Parallel Opportunities**: 2 (frontend + backend can be fixed simultaneously)

---

## Phase 1: Setup & Prerequisites

**Goal**: Verify environment is ready for fixes

- [x] T001 Verify Node.js 20+ is installed: `node --version`
- [x] T002 Verify Python 3.11+ is installed: `python --version`
- [x] T003 Verify git working directory is clean: `git status`
- [x] T004 Verify on correct branch: `git branch --show-current` (should be 002-constitution-refactor)

**Completion Criteria**: All prerequisite tools are available and working directory is on correct branch

---

## Phase 2: Fix Frontend Dependencies (Issue #1)

**Goal**: Resolve ESLint/typescript-eslint peer dependency conflict

**Background**: Package.json already updated (typescript-eslint: ^7.5.0 → ^8.0.0), need to install dependencies

- [x] T005 Navigate to frontend directory: `cd frontend`
- [x] T006 Remove existing node_modules and lock file: `rm -rf node_modules package-lock.json`
- [x] T007 Install dependencies with npm: `npm install`
- [x] T008 Verify ESLint works: `npm run lint:check`
- [x] T009 Verify TypeScript compilation: `npm run type-check`

**Completion Criteria**:
- `npm install` completes without ERESOLVE errors
- `npm run lint:check` executes without errors
- No peer dependency warnings

**Files Modified**:
- `frontend/package-lock.json` (regenerated)
- `frontend/node_modules/` (reinstalled)

---

## Phase 3: Fix Backend Formatting (Issue #2)

**Goal**: Format all Python files with Black to pass CI checks

**Background**: 20 files created/modified without Black formatting applied

### Files Requiring Formatting (20 total):

**Application Code (11 files)**:
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

**Test Code (9 files)**:
- `backend/tests/__init__.py`
- `backend/tests/conftest.py`
- `backend/tests/unit/__init__.py`
- `backend/tests/unit/test_models.py`
- `backend/tests/unit/test_cache_service.py`
- `backend/tests/unit/test_jira_client.py`
- `backend/tests/unit/test_sync_service.py`
- `backend/tests/integration/__init__.py`
- `backend/tests/integration/test_routes.py`

### Tasks:

- [x] T010 Navigate to backend directory: `cd backend`
- [x] T011 Activate virtual environment: `source venv/bin/activate` (or `.\venv\Scripts\activate` on Windows)
- [x] T012 Verify Black is installed: `black --version` (install if needed: `pip install black>=24.3.0`)
- [x] T013 Run Black formatter on app code: `black app/`
- [x] T014 Run Black formatter on test code: `black tests/`
- [x] T015 Verify formatting applied: `black --check app/ tests/`
- [x] T016 Run tests to ensure no regressions: `pytest --cov=app --cov-report=term-missing`

**Completion Criteria**:
- `black --check app/ tests/` reports "All done! ✨ 🍰 ✨"
- All tests pass
- No formatting errors

**Files Modified**: All 20 files listed above (auto-formatted by Black)

---

## Phase 4: Fix Commit Message (Issue #3)

**Goal**: Update commit message to follow Conventional Commits format

**Current Message (INVALID)**:
```
Implement refactoring based on Weni code conventions and best practices
```

**Required Format**:
```
<type>(<scope>): <description>

[optional body with bullet points]
```

### Tasks:

- [x] T017 Review current commit message: `git log -1 --pretty=%B`
- [x] T018 Stage all changes from fixes: `git add .`
- [x] T019 Amend commit with proper Conventional Commits format:

```bash
git commit --amend -m "refactor(constitution): implement code quality standards

- Add pre-commit hooks (Black, ESLint, Prettier, Stylelint)
- Refactor all Vue components to BEM methodology
- Write unit tests for backend (80%+ coverage)
- Write component tests for frontend (80%+ coverage)
- Integrate Unnnic Design System tokens
- Improve semantic HTML and accessibility
- Add CI/CD pipeline with GitHub Actions
- Fix ESLint/typescript-eslint peer dependency conflict
- Format all backend files with Black"
```

**Alternative**: Create new fix commit instead of amending:
```bash
git commit -m "fix(ci): resolve CI/CD pipeline failures

- Upgrade typescript-eslint to 8.x for ESLint 9 compatibility
- Format all backend files with Black formatter
- Update commit messages to follow Conventional Commits"
```

- [x] T020 Verify commit message format: `npx commitlint --from HEAD~1 --to HEAD`
- [x] T021 Review commit details: `git log -1`

**Completion Criteria**:
- Commit message starts with valid type (refactor/fix/feat/etc.)
- Includes scope in parentheses
- Has colon and description
- Body follows convention (optional but recommended)
- commitlint validation passes

---

## Phase 5: Verification & CI Pipeline

**Goal**: Verify all fixes work locally and push to trigger CI

### Local Verification:

- [ ] T022 [P] Run all backend checks locally:
  ```bash
  cd backend
  source venv/bin/activate
  black --check app/ tests/
  isort --check-only app/ tests/
  flake8 app/ tests/
  pytest --cov=app --cov-report=term-missing --cov-fail-under=80
  ```

- [ ] T023 [P] Run all frontend checks locally:
  ```bash
  cd frontend
  npm run lint:check
  npm run format:check
  npm run stylelint:check
  npm run type-check
  npm run test:coverage
  ```

**Completion Criteria (Local)**:
- All backend checks pass (Black, isort, Flake8, tests)
- All frontend checks pass (ESLint, Prettier, Stylelint, TypeScript, tests)
- No errors or warnings

### CI Pipeline Verification:

- [ ] T024 Push changes to remote branch: `git push origin 002-constitution-refactor --force-with-lease`
- [ ] T025 Monitor GitHub Actions workflow: Navigate to repository Actions tab
- [ ] T026 Verify all CI jobs pass:
  - ✅ Backend job (Black, isort, Flake8, pytest)
  - ✅ Frontend job (npm ci, ESLint, Prettier, Stylelint, tests)
  - ✅ Commitlint job (message validation)
  - ✅ Build job (if applicable)

**Completion Criteria (CI)**:
- All GitHub Actions jobs show green checkmarks ✅
- No failed steps in any job
- Coverage reports meet 80% threshold

---

## Dependency Graph

Since these are independent fixes to different subsystems, they can be executed in parallel after prerequisites:

```
Phase 1: Setup & Prerequisites (T001-T004)
          ↓
    ┌─────┴─────┐
    ↓           ↓
Phase 2:     Phase 3:
Frontend     Backend
(T005-T009)  (T010-T016)
    ↓           ↓
    └─────┬─────┘
          ↓
Phase 4: Commit Message (T017-T021)
          ↓
Phase 5: Verification & CI (T022-T026)
```

**Parallel Execution Opportunities**:
- T005-T009 (Frontend) can run parallel with T010-T016 (Backend)
- T022 (Backend checks) can run parallel with T023 (Frontend checks)

---

## Rollback Plan

If any phase fails:

### Frontend Dependency Issue:
```bash
cd frontend
git checkout HEAD -- package.json package-lock.json
npm install
# Revert to typescript-eslint 7.x (original state)
```

### Backend Formatting Issue:
```bash
cd backend
git checkout HEAD -- app/ tests/
# Revert to pre-Black state
```

### Commit Message Issue:
```bash
git log --oneline -5  # Find previous commit SHA
git reset --soft <previous-commit-sha>
# Recommit with corrected message
```

### Complete Rollback:
```bash
git reset --hard origin/002-constitution-refactor
# Reverts all local changes, restart from remote state
```

---

## Quick Reference: Conventional Commits

### Format:
```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Common Types:
- `feat`: New feature
- `fix`: Bug fix
- `refactor`: Code restructuring (no behavior change)
- `style`: Formatting changes (not CSS)
- `test`: Adding/updating tests
- `docs`: Documentation only
- `chore`: Maintenance tasks
- `ci`: CI/CD changes
- `perf`: Performance improvements

### Examples:
```
feat(filters): add quarter filter to roadmap

fix(ci): resolve ESLint dependency conflict

refactor(constitution): apply code quality standards

test(backend): add unit tests for cache service

docs(readme): update installation instructions
```

---

## Success Metrics

### Issue Resolution Status:

| Issue | Status | Verification |
|-------|--------|--------------|
| Frontend ESLint Conflict | ✅ Fixed | `npm ci` completes without errors |
| Backend Black Formatting | ⚠️ Pending | Run `black backend/` to fix |
| Commit Message Format | ⚠️ Pending | Run `git commit --amend` with proper format |

### Expected CI Results After All Fixes:

- ✅ **Backend Job**: Black ✓ isort ✓ Flake8 ✓ pytest ✓
- ✅ **Frontend Job**: npm ci ✓ ESLint ✓ Prettier ✓ Stylelint ✓ tests ✓
- ✅ **Commitlint Job**: Conventional Commits validation ✓
- ✅ **Build Job**: Successful build artifacts ✓

### Time Estimates:

- Phase 1 (Setup): 2 minutes
- Phase 2 (Frontend): 5 minutes
- Phase 3 (Backend): 5 minutes
- Phase 4 (Commit): 3 minutes
- Phase 5 (Verification): 10 minutes (5 local + 5 CI)

**Total Estimated Time**: ~25-30 minutes

---

## Additional Resources

- **[CI Fixes Summary](./CI-FIXES-SUMMARY.md)**: Executive summary with all issues
- **[CI Fixes Plan](./ci-fixes-plan.md)**: Detailed analysis and implementation phases
- **[CI Fixes Quickstart](./ci-fixes-quickstart.md)**: Step-by-step fix instructions
- **[CI Fixes Data Model](./ci-fixes-data-model.md)**: Issue tracking entities
- **[Constitution](../../.specify/memory/constitution.md)**: Code quality standards
- **[Main Spec](./spec.md)**: Constitution refactor specification

---

## Notes

- Package.json already has typescript-eslint updated to ^8.0.0 (completed by agent)
- Black is already installed in backend requirements.txt
- All fixes are auto-fixable except commit message (manual git command)
- Pre-commit hooks will prevent these issues in future commits
- Force-with-lease is safer than force push (protects against overwriting others' work)

**Status**: Ready for execution. Follow phases in order, or run Phase 2 & 3 in parallel.
