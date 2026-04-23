# Implementation Plan: Canvas Mode with Conversational Search

**Branch**: `010-canvas-conversational-search` | **Date**: 2026-01-22 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/010-canvas-conversational-search/spec.md`

## Summary

Implement a canvas-based search mode where users can search the roadmap through natural language conversation with Weni WebChat. The interface splits into two panels: WebChat on the left for conversation, and filtered roadmap results on the right. The system listens to WebSocket messages from webchat-service, parses hidden `[[SEARCH_RESULT]]` blocks, and filters roadmap items in real-time.

## Technical Context

**Language/Version**: TypeScript 5.3+ with Vue 3.4+
**Primary Dependencies**: Vue 3.4, Vue Router 4.2, @weni/unnnic-system, Vite 5
**Storage**: N/A (uses existing roadmap service; no new persistence layer)
**Testing**: Vitest 1.6+ with @vue/test-utils 2.4+, 80% coverage required
**Target Platform**: Web browsers (Chrome, Firefox, Safari, Edge)
**Project Type**: Web application - frontend only (extends existing frontend)
**Performance Goals**: <50ms for search result filtering, <400ms for mode transitions
**Constraints**: No modifications to WebChat source; CSS overrides only; must work with existing WebSocket
**Scale/Scope**: Single-page feature addition to existing roadmap frontend

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Clean Code & Readability | ✓ PASS | Self-descriptive names, single responsibility functions |
| II. Code Style Standards | ✓ PASS | 2-space indent, semicolons, single quotes, BEM CSS |
| III. Naming Conventions | ✓ PASS | camelCase functions, PascalCase components, BEM CSS classes |
| IV. Testing & QA | ✓ PASS | Vitest tests required, 80% coverage threshold |
| V. Semantic HTML & Accessibility | ✓ PASS | Use semantic tags, ARIA attributes for mode transitions |
| VI. Pre-Commit Compliance | ✓ PASS | Will run Prettier → ESLint → Stylelint → Vitest |
| Design System Compliance | ✓ PASS | Use Unnnic components where applicable |

**No violations requiring justification.**

## Project Structure

### Documentation (this feature)

```text
specs/010-canvas-conversational-search/
├── plan.md              # This file
├── research.md          # Phase 0 output: WebSocket integration research
├── data-model.md        # Phase 1 output: Canvas state models
├── quickstart.md        # Phase 1 output: Integration guide
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code (repository root)

```text
frontend/
├── src/
│   ├── components/
│   │   ├── CanvasMode/
│   │   │   ├── CanvasContainer.vue       # Main canvas layout wrapper
│   │   │   ├── CanvasSearchResults.vue   # Right panel with filtered results
│   │   │   ├── CanvasEmptyState.vue      # Empty state with search prompt
│   │   │   └── CanvasExitButton.vue      # Exit button component
│   │   └── ...existing components
│   ├── composables/
│   │   ├── useCanvasSearch.ts            # Canvas mode state & message parsing
│   │   └── ...existing composables
│   ├── utils/
│   │   └── searchResultParser.ts         # [[SEARCH_RESULT]] block parser
│   ├── types/
│   │   └── canvas.ts                     # Canvas mode TypeScript types
│   └── views/
│       └── RoadmapView.vue               # Modified to support canvas mode
└── tests/
    ├── components/
    │   ├── CanvasContainer.spec.ts
    │   ├── CanvasSearchResults.spec.ts
    │   └── CanvasEmptyState.spec.ts
    ├── composables/
    │   └── useCanvasSearch.spec.ts
    └── utils/
        └── searchResultParser.spec.ts
```

**Structure Decision**: Frontend-only changes following existing Vue component organization. New components grouped under `CanvasMode/` folder per constitution guidelines. Utils separated for testability.

## Complexity Tracking

> No violations requiring justification. Feature uses standard Vue patterns within existing architecture.

| Consideration | Decision | Rationale |
|--------------|----------|-----------|
| WebSocket interception | Global event listener on window | WebChat uses global WebSocket; safest non-invasive approach |
| State management | Composable (useCanvasSearch) | Follows existing pattern; no need for Pinia/Vuex for this scope |
| CSS overrides | Scoped global styles | Target `.weni-widget` class; minimal specificity wars |
