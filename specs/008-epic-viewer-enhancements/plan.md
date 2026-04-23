# Implementation Plan: Epic Viewer Enhancements

**Branch**: `008-epic-viewer-enhancements` | **Date**: January 21, 2026 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/008-epic-viewer-enhancements/spec.md`

## Summary

This feature enhances the epic viewing experience with two key capabilities:
1. **Image Carousel Modal**: Users can click on epic images to view them in an enlarged modal with navigation between multiple images
2. **Share Epic Functionality**: Users can generate and copy shareable links to specific epics that automatically open the epic when visited

**Technical Approach**: Frontend-only enhancement using Vue 3 composition API. Image modal implemented as a reusable component with keyboard navigation support. Share functionality leverages existing URL query parameter system and Clipboard API with fallback support.

## Technical Context

**Language/Version**: TypeScript 5.3, Vue 3.4
**Primary Dependencies**: 
- Vue Router 4.2 (URL handling for shared links)
- @weni/unnnic-system (design system components for modals and buttons)
- Clipboard API (browser native, with fallback for unsupported browsers)

**Storage**: LocalStorage (for tracking user interactions if needed, already used for likes)
**Testing**: Vitest 1.6 with @vue/test-utils 2.4, JSDom 24.0 for component testing
**Target Platform**: Modern web browsers (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+)
**Project Type**: Web application (Vue frontend + Python backend, this feature is frontend-only)
**Performance Goals**: 
- Modal open/close animation completes in <300ms
- Image loading with lazy loading support
- Clipboard copy operation completes in <100ms
- Zero layout shift during image carousel navigation

**Constraints**: 
- Must use Unnnic Design System components where available
- Must maintain 80% test coverage across all metrics (statements, branches, functions, lines)
- Must support keyboard navigation (ESC, arrow keys)
- Must work with existing image URLs from JIRA attachments
- Must preserve current URL filter state when possible

**Scale/Scope**: 
- 2 new Vue components (ImageCarouselModal, ShareButton)
- Modifications to 2 existing components (RoadmapCard, RoadmapView)
- URL routing enhancement for epic parameter handling
- ~400-500 lines of new code total
- Full unit test coverage with mock components

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Clean Code & Readability ✅
- **Status**: PASS
- **Rationale**: Feature adds clear, single-responsibility components (ImageCarouselModal for viewing, ShareButton for sharing). Code will be self-documenting with expressive naming.

### Code Style Standards ✅
- **Status**: PASS
- **Rationale**: Will follow existing Vue/TypeScript standards in codebase:
  - 2-space indentation, semicolons, single quotes
  - ESLint with eslint-config-prettier as last config
  - Prettier for formatting
  - No `any` types, use `unknown` with type guards
  - Imperative mood for function documentation

### Naming Conventions ✅
- **Status**: PASS
- **Rationale**: Will follow established patterns:
  - PascalCase for components: `ImageCarouselModal`, `ShareButton`
  - camelCase for functions/variables
  - BEM methodology for CSS: `.image-carousel__navigation`, `.share-button--copied`
  - Event handlers with `on` prefix: `onImageClick`, `onShareClick`

### Testing & Quality Assurance ✅
- **Status**: PASS
- **Rationale**: Will achieve 80% coverage across all metrics:
  - Unit tests for ImageCarouselModal (open, close, navigation, keyboard)
  - Unit tests for ShareButton (copy, fallback, confirmation)
  - Unit tests for URL parameter handling in RoadmapView
  - Mock browser APIs: Clipboard, keyboard events
  - Test both happy path and error scenarios

### Semantic HTML & Accessibility ✅
- **Status**: PASS
- **Rationale**: 
  - Modal will use semantic `dialog` role or `<dialog>` element
  - Proper ARIA labels for navigation buttons
  - Keyboard navigation support (ESC, arrows, Tab)
  - Focus management when modal opens/closes
  - Alt text for images from epic titles

### Pre-Commit Compliance ✅
- **Status**: PASS
- **Rationale**: Will run standard pre-commit workflow:
  1. `npm run format` (Prettier)
  2. `npm run lint -- --fix` (ESLint auto-fix)
  3. `npm run lint:check` (verify no errors)
  4. `npm run stylelint:check` (CSS validation)
  5. `npm test` (verify 80% coverage)

### Design System Compliance ✅
- **Status**: PASS
- **Rationale**: Will use Unnnic components where available:
  - Modal backdrop and structure from Unnnic patterns
  - Share button using Unnnic button styles
  - Icons following Unnnic icon system
  - Colors using Unnnic CSS variables
  - Spacing using Unnnic spacing tokens

**Overall Gate Status**: ✅ **PASS** - All constitution principles satisfied. No violations require justification.

## Project Structure

### Documentation (this feature)

```text
specs/008-epic-viewer-enhancements/
├── plan.md              # This file
├── research.md          # Phase 0 output (design decisions)
├── data-model.md        # Phase 1 output (component state models)
├── quickstart.md        # Phase 1 output (implementation guide)
├── contracts/           # Phase 1 output (component APIs)
│   ├── ImageCarouselModal.contract.md
│   ├── ShareButton.contract.md
│   └── URLParameters.contract.md
└── checklists/
    └── requirements.md  # Already created (spec validation)
```

### Source Code (repository root)

```text
frontend/
├── src/
│   ├── components/
│   │   ├── RoadmapCard.vue                    # MODIFIED: Add click handlers for images and share button
│   │   ├── ImageCarouselModal.vue             # NEW: Modal for viewing enlarged images
│   │   └── ShareButton.vue                    # NEW: Reusable share button component
│   ├── views/
│   │   └── RoadmapView.vue                    # MODIFIED: Handle epic URL parameter, auto-expand epic
│   ├── composables/
│   │   ├── useClipboard.ts                    # NEW: Composable for clipboard operations with fallback
│   │   └── useKeyboardNavigation.ts           # NEW: Composable for keyboard event handling
│   └── types/
│       └── roadmap.ts                         # MODIFIED: Add types for share/modal state if needed
└── tests/
    ├── components/
    │   ├── RoadmapCard.spec.ts                # MODIFIED: Add tests for new click handlers
    │   ├── ImageCarouselModal.spec.ts         # NEW: Full test suite for modal
    │   └── ShareButton.spec.ts                # NEW: Full test suite for share button
    ├── composables/
    │   ├── useClipboard.spec.ts               # NEW: Test clipboard logic with mocks
    │   └── useKeyboardNavigation.spec.ts      # NEW: Test keyboard event handling
    └── views/
        └── RoadmapView.spec.ts                # MODIFIED: Add tests for epic parameter handling
```

**Structure Decision**: Follows existing web application structure with frontend-only changes. New components are added to `components/` following established naming patterns. Composables extracted for reusable logic (clipboard, keyboard) following Vue 3 composition API best practices. No backend changes required as feature uses existing data and URLs.

## Complexity Tracking

> **No violations - table not needed**

All constitution checks passed without requiring additional complexity or violations.
