# Quickstart: Design System Update & Brand Rename

**Branch**: `012-design-system-rebrand`

## Prerequisites

- Node.js ≥ 18
- Repository cloned and on branch `012-design-system-rebrand`

## Setup

```bash
cd frontend
npm install
```

This upgrades `@weni/unnnic-system` to `3.25.3` (the `"latest"` tag). Confirm:

```bash
node -e "console.log(require('./node_modules/@weni/unnnic-system/package.json').version)"
# 3.25.3
```

## Dev Server

```bash
npm run dev
# → http://localhost:5173
```

## Key Files to Edit

| File | Change type |
|------|-------------|
| `frontend/index.html` | Brand rename — `<title>` |
| `frontend/src/App.vue` | Font family fallback: `'Lato'` → `'Inter'` |
| `frontend/src/views/RoadmapView.vue` | Brand rename + 1 color fallback |
| `frontend/src/components/RoadmapCard.vue` | 14 color fallbacks |
| `frontend/src/components/RoadmapFilters.vue` | 9 color fallbacks |
| `frontend/src/components/ShareButton.vue` | 9 color fallbacks |
| `frontend/src/components/RoadmapTabs.vue` | 4 color fallbacks |
| `frontend/src/components/RoadmapEmptyState.vue` | 3 color fallbacks |
| `frontend/src/components/MagicSearchBar.vue` | 2 color fallbacks |
| `frontend/src/components/ImageCarouselModal.vue` | 2 color fallbacks |
| `frontend/src/components/RoadmapCardList.vue` | 1 color fallback |
| `frontend/src/components/RoadmapFeatureRequestForm.vue` | Brand rename |
| `frontend/src/components/CanvasMode/CanvasEmptyState.vue` | 1 color fallback |
| `frontend/src/components/CanvasMode/CanvasExitButton.vue` | 1 color fallback |

## Color Fallback Replacement Map

Search-and-replace these exact hex values (lowercase):

| CSS variable | Replace old hex | With new hex |
|---|---|---|
| `--unnnic-color-weni-50` | `#e6f8f8` | `#e9faf8` |
| `--unnnic-color-weni-500` | `#00bfbf` | `#10b6af` |
| `--unnnic-color-weni-500` | `#009e96` | `#10b6af` |
| `--unnnic-color-weni-500` | `#00a8a8` | `#10b6af` (check context — also used for weni-600) |
| `--unnnic-color-weni-600` | `#00a8a8` | `#01a29b` |
| `--unnnic-color-weni-700` | `#008f8f` | `#017873` |

> Tip: Use IDE find-and-replace **per variable name** (not just hex), since `#00a8a8` appears for both `weni-500` and `weni-600` in some files. Always replace the fallback of the matching `var(--unnnic-color-weni-NNN, ...)` call.

## Pre-Commit Checklist

```bash
cd frontend
npm run format          # Prettier
npm run lint -- --fix   # ESLint
npm run lint:check      # Verify clean
npm run stylelint:check # CSS lint
npm test                # Tests + 80% coverage
```

## Visual Verification Checklist

After `npm run dev`, check http://localhost:5173:

- [ ] Browser tab: "VTEX Agentic CX Roadmap"
- [ ] Hero heading: "Roadmap of VTEX Agentic CX"
- [ ] Footer: "© [year] VTEX Agentic CX. All rights reserved."
- [ ] Body font: Inter (devtools → Computed → font-family)
- [ ] Active tab underline: `#01a29b` teal
- [ ] Like button active state: `#01a29b` teal
- [ ] Card border on hover: `#01a29b` teal
- [ ] Feature request modal: no "Weni" text visible
