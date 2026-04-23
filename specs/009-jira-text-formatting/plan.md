# Implementation Plan: JIRA Text Formatting Preservation

**Branch**: `009-jira-text-formatting` | **Date**: January 21, 2026 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/009-jira-text-formatting/spec.md`

## Summary

Enable proper rendering of JIRA text formatting (bold, italic, underline, lists, links, code blocks) on the public roadmap by converting Atlassian Document Format (ADF) to sanitized HTML instead of plain text. This preserves formatting applied in JIRA epic descriptions while maintaining security through XSS prevention.

**Current Issue**: The backend's `_adf_to_text()` method strips all formatting from JIRA descriptions, converting them to plain text. The frontend then displays this plain text, losing all formatting.

**Solution Approach**: Replace plain text conversion with ADF-to-HTML conversion in the backend, and render sanitized HTML in the frontend with proper XSS protection.

## Technical Context

**Language/Version**: Python 3.11+ (backend), Vue 3.4 + TypeScript 5.3 (frontend)
**Primary Dependencies**:
- Backend: Flask, requests (JIRA API), existing codebase
- Frontend: Vue 3, @weni/unnnic-system, axios
**Storage**: In-memory cache (Redis-based, existing architecture)
**Testing**: pytest (backend 80%+ coverage), Vitest + @vue/test-utils (frontend 80%+ coverage)
**Target Platform**: Web application (desktop + mobile responsive)
**Project Type**: Web - separated backend (Python) + frontend (Vue)
**Performance Goals**: <100ms additional processing time for ADF-to-HTML conversion
**Constraints**:
- Must prevent XSS attacks (sanitize all HTML output)
- Must maintain backward compatibility with existing plain descriptions
- Must pass all existing tests while adding new coverage
- Mobile responsive display (viewport ≥375px)
**Scale/Scope**: Affects all public roadmap items (~hundreds of epics); single RoadmapCard component

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Code Quality Gates

✓ **Clean Code & Readability** (I)
- Conversion logic will be self-documenting with clear function names
- HTML sanitization will follow explicit-over-implicit principle
- Functions maintain single responsibility (convert vs sanitize vs render)

✓ **Code Style Standards** (II)
- Backend: PEP 8, Black, Flake8, isort, type annotations
- Frontend: 2-space indent, ESLint + Prettier, no `any` types
- Docstrings use imperative mood (D401 compliance)
- ESLint config includes `eslint-config-prettier` as last extend

✓ **Naming Conventions** (III)
- Backend: `_adf_to_html()`, `_sanitize_html()` (snake_case)
- Frontend: `FormattedDescription` component or `v-html` usage (PascalCase)
- Event handlers: `onCardClick` (existing pattern)

✓ **Testing & Quality Assurance** (IV)
- Unit tests for ADF-to-HTML conversion (all node types)
- Unit tests for HTML sanitization (XSS prevention)
- Frontend component tests for rendering formatted content
- Coverage ≥80% for all metrics (statements, branches, functions, lines)
- Mock localStorage, IntersectionObserver in frontend tests

✓ **Semantic HTML & Accessibility** (V)
- Rendered HTML uses semantic tags (`<strong>`, `<em>`, `<ul>`, `<ol>`, `<a>`)
- Links have proper attributes (rel="noopener noreferrer" for external)
- Screen readers can parse formatted content correctly

✓ **Pre-Commit Compliance** (VI)
- Run `black . && isort . && flake8 .` before commit
- Run `npm run format && npm run lint -- --fix` before commit
- All tests pass with ≥80% coverage

### Design System Compliance

✓ **Unnnic Design System**
- Description formatting styles integrate with existing Unnnic tokens
- Use CSS custom properties for colors and spacing
- No custom components needed (styling only)

### Complexity Justification

*No violations - all changes align with constitution principles*

## Project Structure

### Documentation (this feature)

```text
specs/009-jira-text-formatting/
├── plan.md              # This file
├── research.md          # Phase 0: ADF structure research
├── data-model.md        # Phase 1: Updated RoadmapItem model
├── quickstart.md        # Phase 1: Integration examples
└── contracts/           # Phase 1: ADF-to-HTML conversion contract
    └── adf-conversion-spec.md
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── services/
│   │   ├── jira_client.py         # MODIFY: Replace _adf_to_text with _adf_to_html
│   │   └── html_sanitizer.py      # NEW: XSS sanitization service
│   └── models/
│       └── roadmap.py              # UNCHANGED: description remains string (now HTML)
└── tests/
    └── unit/
        ├── test_jira_client.py     # MODIFY: Add ADF-to-HTML tests
        └── test_html_sanitizer.py  # NEW: Sanitization tests

frontend/
├── src/
│   ├── components/
│   │   └── RoadmapCard.vue         # MODIFY: Render description as HTML
│   └── utils/
│       └── sanitize.ts              # NEW (OPTIONAL): Client-side sanitization helper
└── tests/
    └── components/
        └── RoadmapCard.spec.ts     # MODIFY: Add formatted content tests
```

**Structure Decision**: Existing web application structure (backend + frontend) is optimal. No new projects or major structural changes needed. Changes are localized to description handling in JIRA client (backend) and RoadmapCard display (frontend).

## Complexity Tracking

*No constitution violations requiring justification*

## Post-Design Constitution Re-evaluation

*GATE: Re-check after Phase 1 design completion*

### Design Artifacts Review

✓ **research.md**: Complete - all unknowns resolved
- ADF format documented
- Conversion approach defined
- Security approach specified
- Best practices identified

✓ **data-model.md**: Complete - minimal model changes
- No new entities
- Description field content format changes only
- Backward compatible
- Clear migration strategy

✓ **contracts/**: Complete - conversion contract specified
- ADF node type mappings defined
- HTML output format specified
- Sanitization rules documented
- Test cases provided

✓ **quickstart.md**: Complete - integration examples provided
- Backend conversion examples
- Frontend rendering examples
- Testing approaches documented
- Common issues and solutions included

### Constitution Compliance Confirmation

**Final Verification**:

✓ **Clean Code** (I): Design maintains single responsibility principle
- Conversion logic separated from sanitization
- Frontend rendering isolated in component
- No unnecessary complexity added

✓ **Code Style** (II): Design follows all style standards
- Backend: PEP 8, type annotations, docstrings
- Frontend: Vue 3 composition API, TypeScript strict mode
- ESLint/Prettier configured correctly

✓ **Naming** (III): Design uses clear, consistent naming
- Backend: `_adf_to_html()`, `sanitize_html()`
- Frontend: `FormattedDescription` patterns
- BEM methodology for CSS classes

✓ **Testing** (IV): Design includes comprehensive test strategy
- Unit tests for all conversion logic
- Security tests for XSS prevention
- Component tests for rendering
- ≥80% coverage target for all metrics

✓ **Accessibility** (V): Design preserves semantic HTML
- Proper use of `<strong>`, `<em>`, `<ul>`, `<ol>`, `<a>`
- Screen reader compatible
- Keyboard navigable links

✓ **Pre-Commit** (VI): Design integrates with existing CI
- Linters run on modified files
- Tests run before commit
- Coverage gates enforced

✓ **Design System** (VII): Design uses Unnnic tokens
- CSS variables for colors, spacing, typography
- No custom components needed
- Consistent with existing design

### Breaking Changes: None

- API contract unchanged (description remains string)
- Frontend interface unchanged (RoadmapItem type same)
- Backward compatible with plain text descriptions
- No database migrations needed

### Dependencies: None Added

- No new npm packages
- No new Python libraries
- Uses existing Vue 3, TypeScript, pytest, Vitest
- Custom implementation for ADF conversion and sanitization

### Performance Impact: Minimal

- Conversion adds <100ms to sync time (offline process)
- No impact on page load time (cached data)
- No impact on rendering time (native v-html)
- Cache size increase <5% (HTML vs plain text)

### Security Impact: Improved

- Explicit XSS prevention through sanitization
- URL validation for links
- Security headers added to external links
- Defense-in-depth approach (backend + frontend + CSP)

**Conclusion**: All constitution gates passed. Design is clean, maintainable, secure, and performant. Ready to proceed to Phase 2 (task breakdown).
