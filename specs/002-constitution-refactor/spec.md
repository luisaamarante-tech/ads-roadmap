# Feature Specification: Constitution Compliance Refactor

**Feature Branch**: `002-constitution-refactor`
**Created**: 2025-12-26
**Status**: Draft
**Input**: User description: "Refactor project to align with constitution.md standards"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Developer Contributes Clean, Tested Code (Priority: P1)

A developer working on the Weni Roadmap project needs to contribute code that meets quality standards. The codebase provides pre-configured linting, formatting, and testing tools that automatically validate contributions before they can be merged. The developer can focus on building features knowing the tooling catches style violations and missing tests.

**Why this priority**: Testing and code quality are the foundation of maintainable software. Without these in place, technical debt accumulates and future development slows. The constitution mandates 80% test coverage and pre-commit validation.

**Independent Test**: Can be fully tested by running `git commit` and verifying that linters, formatters, and tests execute automatically, blocking commits with violations.

**Acceptance Scenarios**:

1. **Given** a developer has made Python code changes, **When** they attempt to commit, **Then** Black formats the code, Flake8 checks for style violations, and unit tests run automatically
2. **Given** a developer has made frontend code changes, **When** they attempt to commit, **Then** ESLint, Prettier, and Stylelint validate the code, and tests run automatically
3. **Given** a commit has passing linters and tests, **When** the developer pushes to remote, **Then** CI pipeline validates all checks in a clean environment
4. **Given** test coverage drops below 80%, **When** the developer attempts to merge, **Then** the CI pipeline fails with a clear coverage report

---

### User Story 2 - Codebase Follows Naming Conventions Consistently (Priority: P2)

The codebase uses consistent naming patterns across all files, making it navigable and understandable for any team member. Backend code follows PEP 8 conventions and frontend code follows established Vue/TypeScript patterns with BEM methodology for CSS.

**Why this priority**: Consistent naming reduces cognitive load and makes the codebase accessible to new developers. This directly supports the "Clean Code & Readability" principle.

**Independent Test**: Can be fully tested by running static analysis tools and reviewing code samples for convention compliance.

**Acceptance Scenarios**:

1. **Given** any Python file in the backend, **When** reviewed by Flake8, **Then** all names follow PEP 8 (snake_case for functions/variables, PascalCase for classes)
2. **Given** any Vue component, **When** reviewed, **Then** it uses camelCase for variables/functions, PascalCase for component names
3. **Given** any CSS in components, **When** reviewed, **Then** classes follow BEM methodology (.block__element--modifier)
4. **Given** any event handler in Vue, **When** reviewed, **Then** it uses "on" prefix (e.g., onUserClick) and state updates use "handle" prefix (e.g., handleSubmit)

---

### User Story 3 - Frontend Uses Unnnic Design System (Priority: P3)

The frontend application uses Weni's Unnnic Design System for all UI components, ensuring visual consistency with other Weni products and reducing custom component maintenance burden.

**Why this priority**: Design system compliance ensures brand consistency and reduces development effort by leveraging pre-built, tested components. The constitution mandates Unnnic as the single source of truth.

**Independent Test**: Can be fully tested by auditing components for Unnnic usage and visually comparing against the design system reference.

**Acceptance Scenarios**:

1. **Given** a button is needed in the UI, **When** implemented, **Then** UnnnicButton component is used instead of custom button styling
2. **Given** form inputs are needed, **When** implemented, **Then** Unnnic input components are used
3. **Given** color or spacing is applied, **When** inspected, **Then** Unnnic design tokens (CSS variables) are used
4. **Given** the application is rendered, **When** compared to unnnic.stg.cloud.weni.ai, **Then** components match the design system visual patterns

---

### User Story 4 - HTML is Semantic and Accessible (Priority: P3)

The frontend uses semantic HTML elements appropriately, improving accessibility for assistive technologies and SEO performance. Screen readers can navigate the content logically.

**Why this priority**: Semantic HTML is a fundamental web standard that improves accessibility and maintainability. The constitution lists this as a non-negotiable requirement.

**Independent Test**: Can be fully tested by running accessibility audits (Lighthouse, axe) and reviewing HTML structure.

**Acceptance Scenarios**:

1. **Given** the roadmap page loads, **When** inspected, **Then** it uses semantic tags (header, main, nav, section, article, footer) appropriately
2. **Given** headings exist on the page, **When** inspected, **Then** they follow proper hierarchy (h1 → h2 → h3) without skipping levels
3. **Given** interactive elements exist, **When** accessed via keyboard, **Then** they are focusable and have appropriate ARIA labels
4. **Given** an accessibility audit runs, **When** completed, **Then** no critical semantic HTML violations are reported

---

### Edge Cases

- What happens when Unnnic components don't exist for a needed UI pattern?
  - Extend existing Unnnic components through composition, document the gap, and report to design system team
- How are third-party library conflicts with linting rules handled?
  - Configure ESLint/Stylelint to ignore specific third-party code patterns via configuration rules
- What happens when legacy code cannot immediately meet 80% coverage?
  - Prioritize new code coverage, create a backlog for legacy coverage, enforce coverage only on changed files initially

## Requirements *(mandatory)*

### Functional Requirements

#### Backend Requirements

- **FR-001**: Backend MUST have pre-commit hooks configured running Black (formatter), Flake8 (linter), and pytest (tests)
- **FR-002**: Backend MUST achieve minimum 80% code coverage with unit tests
- **FR-003**: Backend unit tests MUST NOT depend on external services (JIRA, Redis)—all dependencies MUST be mocked
- **FR-004**: Backend code MUST use type annotations for all function signatures and variables
- **FR-005**: Backend imports MUST be grouped: (1) standard library, (2) third-party, (3) local—separated by blank lines

#### Frontend Requirements

- **FR-006**: Frontend MUST have ESLint, Prettier, and Stylelint configured and enforced via pre-commit
- **FR-007**: Frontend MUST have unit tests using Vitest (or equivalent) with minimum 80% coverage
- **FR-008**: Frontend CSS classes MUST follow BEM methodology (.block__element--modifier)
- **FR-009**: Frontend MUST use Unnnic Design System components for all standard UI elements (buttons, inputs, cards, modals)
- **FR-010**: Frontend MUST use Unnnic design tokens (CSS variables) for colors, spacing, and typography
- **FR-011**: Frontend MUST use 2-space indentation, semicolons at statement ends, and single quotes for strings
- **FR-012**: Frontend event handlers MUST be prefixed with "on" (e.g., onUserClick), state updates with "handle"

#### HTML & Accessibility Requirements

- **FR-013**: Frontend MUST use semantic HTML tags (header, nav, main, section, article, aside, footer) appropriately
- **FR-014**: Frontend MUST maintain proper heading hierarchy (h1 → h2 → h3) without skipping levels
- **FR-015**: Frontend MUST NOT use excessive div nesting when semantic alternatives exist
- **FR-016**: Frontend MUST NOT use inline styles—all styling via external stylesheets or scoped component styles

#### CI/CD Requirements

- **FR-017**: CI pipeline MUST validate all pre-commit checks (linting, formatting, tests) on every push and PR
- **FR-018**: CI pipeline MUST fail when test coverage drops below 80%
- **FR-019**: All PRs MUST follow Conventional Commits format: `<type>(<scope>): <description>`

### Key Entities

- **Pre-commit Configuration**: Defines which tools run before commits are accepted (Black, Flake8, ESLint, Prettier, Stylelint, pytest, Vitest)
- **Coverage Report**: Tracks percentage of code covered by tests, stored per module and overall
- **Design Token**: CSS variable from Unnnic design system (colors, spacing, typography)
- **BEM Class**: CSS class following Block__Element--Modifier naming pattern

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All commits pass pre-commit validation (linting, formatting, basic tests) in under 30 seconds
- **SC-002**: Backend test coverage reaches minimum 80% as reported by pytest-cov
- **SC-003**: Frontend test coverage reaches minimum 80% as reported by Vitest coverage
- **SC-004**: Zero Flake8 errors or warnings in backend code
- **SC-005**: Zero ESLint, Prettier, or Stylelint errors in frontend code
- **SC-006**: Lighthouse accessibility score of 90+ on the roadmap page
- **SC-007**: 100% of new UI components use Unnnic Design System instead of custom implementations
- **SC-008**: All CSS classes in components follow BEM methodology (verifiable via regex pattern matching)
- **SC-009**: All commits in this feature branch follow Conventional Commits format
- **SC-010**: CI pipeline runs all validations and provides pass/fail status within 5 minutes
