# Feature Specification: Design System Update and Brand Rename

**Feature Branch**: `012-design-system-rebrand`
**Created**: 2026-04-06
**Status**: Draft
**Input**: User description: "Update the Design System based on the new version of https://unnnic.stg.cloud.weni.ai/ (main changes: typography and colors) and rebrand from Weni to VTEX Agentic CX in front-facing text."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Updated visual identity on the roadmap page (Priority: P1)

A visitor opens the public roadmap and immediately sees the new brand identity: the page title reads "VTEX Agentic CX Roadmap", the footer shows the correct company name, and the overall visual style (colors, typography) reflects the updated Unnnic design system.

**Why this priority**: This is the most visible change. A mismatched brand name or out-of-date color scheme directly undermines trust and brand perception for every user who visits the page.

**Independent Test**: Can be fully tested by loading the roadmap home page and visually verifying the title, footer, typography, and primary color tokens against the updated design guidelines.

**Acceptance Scenarios**:

1. **Given** the roadmap page is loaded, **When** a visitor reads the page header, **Then** the title reads "Roadmap of VTEX Agentic CX" — not "Weni".
2. **Given** the roadmap page is loaded, **When** a visitor reads the footer, **Then** the copyright text reads "© [year] VTEX Agentic CX. All rights reserved."
3. **Given** the roadmap page is loaded, **When** a visitor inspects text elements, **Then** headings, body copy, and labels follow the updated Unnnic typography scale (font family, weights, and sizes defined by the new design system version).
4. **Given** the roadmap page is loaded, **When** a visitor inspects interactive elements (buttons, active tabs, card borders, like counters), **Then** all primary brand color accents use the updated color palette tokens from the new design system — no legacy `weni` color tokens are applied.

---

### User Story 2 - Feature request form uses updated brand name (Priority: P2)

A visitor opens the feature request modal to submit an idea. The helper text and any descriptive copy inside the form no longer reference "Weni" — they reference "VTEX Agentic CX Roadmap".

**Why this priority**: The feature request form is the main conversion touchpoint. Stale branding there creates confusion about which product the user is interacting with.

**Independent Test**: Can be fully tested by opening the feature request modal and verifying all visible text uses the new brand name.

**Acceptance Scenarios**:

1. **Given** the feature request modal is open, **When** a visitor reads the introductory text, **Then** it references "VTEX Agentic CX Roadmap", not "Weni Roadmap".

---

### User Story 3 - Browser tab title reflects new brand (Priority: P3)

A visitor opens the roadmap in a browser. The browser tab and any bookmarked title show "VTEX Agentic CX Roadmap" instead of "Weni Roadmap".

**Why this priority**: The page `<title>` is the first text a user sees in search results and bookmarks. It should match the updated brand name, but its impact on the live experience is secondary to the visible page content.

**Independent Test**: Can be fully tested by checking the browser tab title after loading the roadmap page.

**Acceptance Scenarios**:

1. **Given** the roadmap page is loaded, **When** a visitor looks at the browser tab, **Then** the tab title reads "VTEX Agentic CX Roadmap".

---

### Edge Cases

- What happens if the updated Unnnic package introduces breaking changes to component APIs? The visual regression must be caught before deployment and individual components verified.
- How does the system handle screens that were using `weni` color tokens as fallback hex values in CSS? The fallback values must also be updated to match new teal palette hex codes.
- What if a user has the roadmap bookmarked or cached? The updated title appears on the next fresh load — no special handling required beyond normal cache headers.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The page `<title>` MUST read "VTEX Agentic CX Roadmap".
- **FR-002**: The roadmap hero heading MUST display "Roadmap of VTEX Agentic CX" (no occurrence of "Weni" in user-visible text).
- **FR-003**: The page footer copyright MUST read "© [year] VTEX Agentic CX. All rights reserved."
- **FR-004**: The feature request form introductory text MUST reference "VTEX Agentic CX Roadmap" instead of "Weni Roadmap".
- **FR-005**: The Unnnic design system package MUST be updated to the latest stable release that delivers the new typography and color tokens shown at https://unnnic.stg.cloud.weni.ai/.
- **FR-006**: All CSS custom property references to legacy `--unnnic-color-weni-*` tokens MUST be replaced with the equivalent tokens from the updated color palette (the new palette uses `teal` as the primary brand color family).
- **FR-007**: Typography across the application MUST adopt the font family, weights, and scale defined by the new Unnnic version.
- **FR-008**: Internal identifiers (CSS class names used for the embedded webchat widget, localStorage keys, import package names, source file comments) MUST NOT be changed as part of this work — only user-facing text is in scope for the brand rename.

### Assumptions

- The new Unnnic design system replaces `weni` color tokens with `teal` color tokens for the primary brand palette; the spec assumes a direct correspondence between `weni-NNN` and `teal-NNN` shade numbers unless the migration guide states otherwise.
- The font family change (if any) is handled by updating the Unnnic package and its distributed stylesheet; no custom font loading code is expected to be needed in the application.
- "VTEX Agentic CX" is the complete replacement brand name wherever "Weni" appeared in user-facing text; no other brand name variants are used.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Zero occurrences of the word "Weni" appear in user-visible text across all screens of the deployed roadmap application.
- **SC-002**: All interactive elements (buttons, active tabs, card highlights, like counters, filter pills) visually match the primary brand color defined in the updated Unnnic color palette, with no legacy teal or weni hex overrides remaining.
- **SC-003**: The typography of headings, body text, and labels visually matches the type scale documented in the updated Unnnic Storybook.
- **SC-004**: The application renders without visual regressions on desktop and mobile — all components display correctly after the package upgrade.
- **SC-005**: The entire set of brand rename and design system changes is delivered as a single, independently deployable update with no functional regressions in filtering, search, epic expansion, or feature request submission.
