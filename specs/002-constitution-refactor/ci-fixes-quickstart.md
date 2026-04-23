# CI/CD Fixes - Quickstart Guide

**Created**: 2025-12-26
**Related Plan**: [CI Fixes Plan](./ci-fixes-plan.md)

## Quick Summary

Three fixes needed to pass CI/CD pipeline:

1. ✅ **Frontend Dependencies**: Upgrade typescript-eslint to 8.x
2. ⚠️ **Backend Formatting**: Run Black on 20 files
3. ⚠️ **Commit Message**: Amend to follow Conventional Commits

## Fix 1: Frontend Dependencies (DONE)

### What Changed
- Updated `typescript-eslint` from `^7.5.0` to `^8.0.0` in `package.json`
- This version supports ESLint 9.x

### Commands to Run
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run lint:check  # Verify it works
```

## Fix 2: Backend Formatting (TODO)

### What Needs Formatting
20 Python files need Black formatting. Run this command:

```bash
cd backend

# Activate virtual environment
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Run Black formatter
black app/ tests/

# Verify formatting
black --check app/ tests/

# Run tests to ensure no regressions
pytest
```

### If Black is Not Installed
```bash
cd backend
source venv/bin/activate
pip install black>=24.3.0
black app/ tests/
```

## Fix 3: Commit Message (TODO)

### Current Commit Message (INVALID)
```
Implement refactoring based on Weni code conventions and best practices
```

### Fixed Commit Message (VALID)
Use one of these options:

#### Option A: Amend the Last Commit
```bash
git commit --amend -m "refactor(constitution): implement code quality standards

- Add pre-commit hooks (Black, ESLint, Prettier, Stylelint)
- Refactor all Vue components to BEM methodology
- Write unit tests for backend (80%+ coverage)
- Write component tests for frontend (80%+ coverage)
- Integrate Unnnic Design System tokens
- Improve semantic HTML and accessibility
- Add CI/CD pipeline with GitHub Actions"
```

#### Option B: Create a New Fix Commit
```bash
git add .
git commit -m "fix(ci): resolve CI/CD pipeline failures

- Upgrade typescript-eslint to 8.x for ESLint 9 compatibility
- Format all backend files with Black formatter
- Update documentation with CI/CD troubleshooting"
```

## Verify Everything Works

### 1. Test Locally
```bash
# Backend
cd backend
black --check app/ tests/
isort --check-only app/ tests/
flake8 app/ tests/
pytest --cov=app --cov-report=term-missing

# Frontend
cd frontend
npm run lint:check
npm run format:check
npm run stylelint:check
npm run type-check
npm run test:coverage
```

### 2. Run Pre-commit Hooks
```bash
# From repo root
pre-commit run --all-files
```

### 3. Push and Monitor CI
```bash
git push origin 002-constitution-refactor
# Then check GitHub Actions: https://github.com/{owner}/{repo}/actions
```

## Expected CI Results

After these fixes, all CI jobs should pass:

✅ **Backend Job**
- Black formatting check: ✅ PASS
- isort import ordering: ✅ PASS
- Flake8 linting: ✅ PASS
- Tests with 80% coverage: ✅ PASS

✅ **Frontend Job**
- npm ci (dependency install): ✅ PASS
- ESLint check: ✅ PASS
- Prettier check: ✅ PASS
- Stylelint check: ✅ PASS
- Type check: ✅ PASS
- Tests with 80% coverage: ✅ PASS

✅ **Commitlint Job**
- Commit message validation: ✅ PASS

✅ **Build Job**
- Frontend build: ✅ PASS
- Docker image builds: ✅ PASS

## Troubleshooting

### Frontend: ESLint Still Failing
```bash
cd frontend
npm run lint  # Auto-fix issues
npm run format  # Auto-format code
```

### Backend: Black Formatting Issues
Black is opinionated - it will auto-fix everything:
```bash
black backend/app/ backend/tests/
```

### Commit Message: Multiple Commits Need Fixing
```bash
# Interactive rebase to fix last 5 commits
git rebase -i HEAD~5

# Change 'pick' to 'reword' for commits to fix
# Save and close editor
# Fix each commit message in the following prompts
```

## Quick Reference: Conventional Commits Format

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Common Types**:
- `feat`: New feature
- `fix`: Bug fix
- `refactor`: Code restructuring
- `style`: Formatting changes
- `test`: Adding/updating tests
- `docs`: Documentation only
- `chore`: Maintenance tasks
- `ci`: CI/CD changes

**Example**:
```
feat(filters): add quarter filter

Added quarter filter buttons (Q1-Q4) to RoadmapFilters component.
Users can now filter roadmap items by fiscal quarter.

Closes #123
```

## Files Changed by This Fix

- ✅ `frontend/package.json` - Updated typescript-eslint version
- ⚠️ 20 backend Python files - Need Black formatting
- ⚠️ Git commit message - Needs amendment

## Next Steps

1. Run `cd frontend && npm install` to resolve dependencies
2. Run `cd backend && black app/ tests/` to format code
3. Amend commit message using one of the options above
4. Push changes and verify CI passes

---

**Need Help?** Check the detailed [CI Fixes Plan](./ci-fixes-plan.md)
