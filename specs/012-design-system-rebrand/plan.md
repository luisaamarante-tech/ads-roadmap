# Implementation Plan: Design System Update & Brand Rename

**Branch**: `012-design-system-rebrand` | **Date**: 2026-04-06 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/012-design-system-rebrand/spec.md`

## Summary

Update `@weni/unnnic-system` from `3.12.6-alpha` to `3.25.3`, adopting the new **Inter** typography and revised **teal** color palette, then replace all four user-visible occurrences of "Weni" with "VTEX Agentic CX". The change is pure frontend and touches 14 files (1 HTML, 12 Vue/TS, 1 package manifest). No backend work, no data model, no API contracts.

## Technical Context

**Language/Version**: TypeScript 5.3 / Vue 3.4
**Primary Dependencies**: `@weni/unnnic-system` (upgrade: `3.12.6-alpha` → `3.25.3`), Vite 5, Vue Router 4
**Storage**: N/A (no data storage involved)
**Testing**: Vitest 1.x + `@vue/test-utils` 2.4 — 80% coverage threshold enforced for statements, branches, functions, and lines
**Target Platform**: Web (SPA served via Netlify)
**Project Type**: Web application (frontend-only change)
**Performance Goals**: No change — visual update only
**Constraints**: No breaking changes to user-accessible URLs, no data loss (localStorage key `weni-roadmap-liked-items` must not change)
**Scale/Scope**: 14 files, ~60 text/CSS edits, ~2h estimated implementation time

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|---|---|---|
| I. Clean Code & Readability | ✅ Pass | Changes are mechanical text/CSS replacements; no logic added |
| II. Code Style Standards (Frontend) | ✅ Pass | Must run Prettier → ESLint → Stylelint after edits |
| II. No trailing whitespace | ✅ Pass | Auto-fixed by Prettier |
| III. Naming Conventions | ✅ Pass | No new names introduced |
| IV. Testing (80% coverage) | ✅ Pass | CSS/text changes don't reduce coverage; must re-run after package upgrade |
| V. Semantic HTML | ✅ Pass | No HTML structure changes |
| VI. Pre-Commit Compliance | ✅ Pass | Standard pre-commit workflow applies |
| Design System Compliance | ✅ Pass | **This feature IS the design system update** |

**No violations. No complexity justification table needed.**

## Project Structure

### Documentation (this feature)

```text
specs/012-design-system-rebrand/
├── plan.md              ← this file
├── research.md          ← Phase 0 complete
├── checklists/
│   └── requirements.md  ← spec quality checklist
└── tasks.md             ← Phase 2 output (/speckit.tasks command — not created by /speckit.plan)
```

### Source Code (affected files only)

```text
frontend/
├── index.html                              ← brand rename: <title>
├── package.json                            ← no code change; npm install upgrades to 3.25.3
└── src/
    ├── App.vue                             ← font-family fallback: Lato → Inter
    ├── views/
    │   └── RoadmapView.vue                 ← brand rename (hero + footer) + 1 color fallback
    └── components/
        ├── RoadmapCard.vue                 ← 14 color fallback updates
        ├── RoadmapFilters.vue              ← 9 color fallback updates
        ├── ShareButton.vue                 ← 9 color fallback updates
        ├── RoadmapTabs.vue                 ← 4 color fallback updates
        ├── RoadmapEmptyState.vue           ← 3 color fallback updates
        ├── MagicSearchBar.vue              ← 2 color fallback updates
        ├── ImageCarouselModal.vue          ← 2 color fallback updates
        ├── RoadmapCardList.vue             ← 1 color fallback update
        ├── RoadmapFeatureRequestForm.vue   ← brand rename: help text
        └── CanvasMode/
            ├── CanvasEmptyState.vue        ← 1 color fallback update
            └── CanvasExitButton.vue        ← 1 color fallback update
```

**Structure Decision**: Single web application (frontend-only). No backend directory involved.

---

## Phase 0: Research

✅ **Complete** — see [research.md](./research.md)

All unknowns resolved. Key findings:

- **Font**: `Lato` → `Inter, sans-serif`. Inter is loaded automatically by the new package's `dist/style.css` via Google Fonts `@import`. The only application code to change is the fallback in `App.vue`.
- **Colors**: The new palette uses a 1–13 scale for teal; `weni-*` tokens are kept as deprecated aliases. The CSS custom properties `--unnnic-color-weni-*` are **never defined** in the dist (neither old nor new), so the browser always uses the hardcoded fallback hex. Only the fallback values need updating.
- **Package**: No `package.json` edit needed; a fresh `npm install` pulls `3.25.3` via `"latest"`.
- **Brand**: 4 user-visible text occurrences across 3 files.

---

## Phase 1: Design & Contracts

*No data model or API contracts apply to this feature (pure UI/CSS change).*

### Color Token Migration Reference

The following table is the authoritative mapping used when updating `var(--unnnic-color-weni-NNN, <fallback>)` declarations. Replace only the fallback hex value; leave the CSS variable name unchanged.

| CSS variable | Old fallback hex (any variant) | New fallback hex | Source (new palette) |
|---|---|---|---|
| `--unnnic-color-weni-50` | `#e6f8f8` | `#E9FAF8` | teal-1 |
| `--unnnic-color-weni-500` | `#00bfbf` / `#009e96` / `#00a8a8` | `#10B6AF` | teal-7 |
| `--unnnic-color-weni-600` | `#00a8a8` / `#009e96` | `#01A29B` | teal-8 (primary brand accent) |
| `--unnnic-color-weni-700` | `#008f8f` | `#017873` | teal-10 |

> **Lowercase hex convention**: the codebase uses lowercase hex values (`#01a29b`, not `#01A29B`). Apply the new values in lowercase to stay consistent.

### Typography Migration Reference

| Location | Current value | New value |
|---|---|---|
| `App.vue` — `font-family` fallback | `'Lato'` | `'Inter'` |

No other typography changes are needed in application code. The Unnnic dist updates component-internal styles automatically.

### Brand Rename Reference

| File | What to change |
|---|---|
| `frontend/index.html` | `<title>Weni Roadmap</title>` → `<title>VTEX Agentic CX Roadmap</title>` |
| `frontend/src/views/RoadmapView.vue` | `<span class="roadmap-page__brand">Weni</span>` → `<span class="roadmap-page__brand">VTEX Agentic CX</span>` |
| `frontend/src/views/RoadmapView.vue` | `© {{ new Date().getFullYear() }} Weni. All rights reserved.` → `© {{ new Date().getFullYear() }} VTEX Agentic CX. All rights reserved.` |
| `frontend/src/components/RoadmapFeatureRequestForm.vue` | `Weni Roadmap` → `VTEX Agentic CX Roadmap` |

### Implementation Sequence

**Step 1 — Upgrade package**
```bash
cd frontend && npm install
```
Verify the installed version:
```bash
node -e "console.log(require('./node_modules/@weni/unnnic-system/package.json').version)"
# Expected: 3.25.3
```

**Step 2 — Update App.vue font-family**

In `frontend/src/App.vue`, change the `font-family` rule inside `.app`:
```css
/* before */
font-family: var(--unnnic-font-family, 'Lato'), -apple-system, ...

/* after */
font-family: var(--unnnic-font-family, 'Inter'), -apple-system, ...
```

**Step 3 — Update color fallback hex values**

For each of the 11 Vue files listed above, find every occurrence of `var(--unnnic-color-weni-NNN, <hex>)` and replace the fallback hex using the mapping table. No other changes to those files.

**Step 4 — Apply brand rename**

Apply the four text replacements from the Brand Rename Reference table above.

**Step 5 — Quality checks**
```bash
cd frontend
npm run format          # Prettier
npm run lint -- --fix   # ESLint auto-fix
npm run lint:check      # Verify no ESLint errors
npm run stylelint:check # Verify CSS rules
npm test                # Run tests + coverage
```

**Step 6 — Visual verification**
```bash
npm run dev
```
Open http://localhost:5173 and verify:
- Page title reads "VTEX Agentic CX Roadmap" in browser tab
- Hero heading reads "Roadmap of VTEX Agentic CX"
- Footer reads "© [year] VTEX Agentic CX. All rights reserved."
- Interactive elements (buttons, active tabs, card highlights) use the new teal (#01a29b)
- Typography renders in Inter (check browser devtools → Computed → font-family)
- Feature request modal text does not mention "Weni"

### Quickstart for Implementer

See [quickstart.md](./quickstart.md) for a concise step-by-step dev setup guide.
