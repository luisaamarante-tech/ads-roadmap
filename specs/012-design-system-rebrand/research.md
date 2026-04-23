# Research: Design System Update & Brand Rename

**Feature**: `012-design-system-rebrand`
**Date**: 2026-04-06
**Status**: Complete — all unknowns resolved

---

## 1. Package Version Delta

**Decision**: Upgrade `@weni/unnnic-system` from `3.12.6-alpha-teleports.0` (currently installed) to `3.25.3` (current `latest` on npm).

**Rationale**: The `package.json` already declares `"latest"`, so no semver pin change is needed in `package.json`. The working `node_modules` just needs a fresh `npm install` after the update. Version `3.25.3` is the version powering the Storybook at https://unnnic.stg.cloud.weni.ai/.

**Alternatives considered**: Pinning a specific version for stability. Rejected because `"latest"` is the project's stated policy and `3.25.3` is the stable release.

---

## 2. Typography Changes

### 2.1 Font Family: Lato → Inter

**Decision**: Replace `'Lato'` with `'Inter'` everywhere it appears as a hardcoded fallback.

**Rationale**: The new `fonts.scss` in `@weni/unnnic-system@3.25.3` declares:
```scss
$unnnic-font-family: Inter, sans-serif;
```
The previous version used `Lato`. The deprecated `fonts.scss` shipped in the new package includes a Google Fonts `@import` for Inter (optical-size 14–32, weights 400–600), so the font loads automatically when the updated `dist/style.css` is imported. No manual `<link>` tag is needed.

**App.vue impact**: The global font stack currently reads:
```css
font-family: var(--unnnic-font-family, 'Lato'), -apple-system, ...
```
`--unnnic-font-family` is **not** a CSS custom property defined by the dist, so `'Lato'` is always used as fallback. The fallback must be updated to `'Inter'`.

**Alternatives considered**: Adding a `<link>` tag for Inter in `index.html`. Rejected because the new package's `dist/style.css` already loads Inter via `@import` in its deprecated fonts partial.

### 2.2 Font Weight Scale

**Decision**: No application code changes required for font weight; Unnnic components handle this internally.

**Rationale**: The new `fonts.scss` changes bold from `700` to `600` and adds `font-weight-semibold: 600`. The application code does not directly reference SCSS weight tokens—it uses the Unnnic components which pick up the new values automatically after the package upgrade.

### 2.3 Line Height

**Decision**: No application code changes required.

**Rationale**: Line heights changed from pixel-based multipliers (e.g., `calc(2 * 16px)`) to a uniform `1.4` ratio. These are used within Unnnic component styles only. Application CSS that sets its own line heights is unaffected.

### 2.4 Letter Spacing (new tokens)

**Decision**: No application code changes required.

**Rationale**: Letter-spacing tokens are new in `3.25.3` and are applied internally by Unnnic components. Application code does not use these tokens directly.

---

## 3. Color System Changes

### 3.1 Scale Renaming: 50-950 → 1-13

**Decision**: Use the **deprecated alias layer** for backwards compatibility; update only the hardcoded fallback hex values.

**Rationale**: The new `@weni/unnnic-system` ships a `deprecated/colors.scss` that maps old `weni-NNN` SCSS variables to the new `teal-N` scale. The mapping (confirmed from source):

| Old token (SCSS) | Deprecated alias → New primitive | Old hex (fallback in app) | New hex |
|---|---|---|---|
| `$unnnic-color-weni-50` | `teal-1` | `#e6f8f8` | `#E9FAF8` |
| `$unnnic-color-weni-500` | `teal-7` | `#00bfbf` / `#009e96` / `#00a8a8` | `#10B6AF` |
| `$unnnic-color-weni-600` | `teal-8` | `#00a8a8` | `#01A29B` |
| `$unnnic-color-weni-700` | `teal-10` | `#008f8f` | `#017873` |

**Key insight**: `--unnnic-color-weni-*` **are not CSS custom properties** — neither the old nor the new `dist/style.css` defines them as `:root` variables. The application uses `var(--unnnic-color-weni-600, #00a8a8)` but the variable is never set, so the browser **always falls through to the hardcoded hex fallback**. The fix is to update those fallback hex values.

**Alternatives considered**:
1. Migrate token names to the new `teal-N` scale (`var(--unnnic-color-teal-8, #01A29B)`). Rejected: still not CSS custom properties, adds churn with no functional benefit.
2. Define actual CSS custom properties in `App.vue` or a global stylesheet. Deferred: out of scope for this feature; could be a follow-up.

### 3.2 Semantic Color Token Changes

**Decision**: No direct changes needed in application code; Unnnic components pick these up automatically.

**Rationale**: Semantic tokens like `fg-accent`, `bg-accent-strong`, `border-accent-strong` now resolve to `#01A29B` (teal-8) instead of `#00A49F` (old teal-600). These are used by Unnnic UI components internally.

---

## 4. Dependency Compatibility

**Decision**: Proceed with upgrade; Vue 3.4 compatibility confirmed.

**Rationale**: `@weni/unnnic-system@3.25.3` lists `vue: "^3.4.8"` as a peer dependency. The project uses `vue: "^3.4.0"`, which satisfies this range. New transitive dependencies (`reka-ui`, `lucide-vue-next`, `@vueuse/core v14`, etc.) are bundled in the package dist and do not require installation in the application's `node_modules`.

**Risk**: The alpha→stable gap (3.12 → 3.25) is large. Components used in the application must be verified after upgrade. Components in use: `UnnnicButton`, `UnnnicIcon`, `UnnnicInput`, `UnnnicModal`, `UnnnicTag`, `UnnnicTab`, `UnnnicTabItem`, `UnnnicAlert`, `UnnnicTooltip`, `UnnnicCarousel` (approximate list from usage grep).

---

## 5. Brand Rename: Weni → VTEX Agentic CX

**Decision**: Replace "Weni" with "VTEX Agentic CX" in all user-facing text; leave internal identifiers unchanged.

**Rationale**: The scope is intentionally narrow. The four user-visible occurrences are:

| File | Line | Current text | New text |
|---|---|---|---|
| `frontend/index.html` | `<title>` | `Weni Roadmap` | `VTEX Agentic CX Roadmap` |
| `frontend/src/views/RoadmapView.vue` | Hero heading | `Roadmap of Weni` | `Roadmap of VTEX Agentic CX` |
| `frontend/src/views/RoadmapView.vue` | Footer | `© [year] Weni. All rights reserved.` | `© [year] VTEX Agentic CX. All rights reserved.` |
| `frontend/src/components/RoadmapFeatureRequestForm.vue` | Help text | `Weni Roadmap` | `VTEX Agentic CX Roadmap` |

**Explicitly out of scope** (internal identifiers — no change):
- CSS class selectors: `.weni-widget`, `.weni-chat`, `#weni-webchat-canvas`, etc. (webchat widget integration CSS)
- localStorage key: `weni-roadmap-liked-items`
- npm package name: `@weni/unnnic-system`
- Source file comments referring to the project name
- `const WEBCHAT_CONTAINER_ID = 'weni-webchat-canvas'` (runtime ID for the webchat DOM element)
- `key.toLowerCase().includes('weni')` (canvas search key filtering logic)

**Alternatives considered**: Renaming localStorage key. Rejected: would silently reset all users' liked items on deploy with no migration path.

---

## 6. Files Affected (Complete Inventory)

### Brand rename (4 locations in 3 files)
- `frontend/index.html`
- `frontend/src/views/RoadmapView.vue`
- `frontend/src/components/RoadmapFeatureRequestForm.vue`

### Design system — font family (1 file)
- `frontend/src/App.vue` — update font-family fallback

### Design system — color token fallbacks (11 files, 47 occurrences)
- `frontend/src/components/RoadmapCard.vue` (14 occurrences)
- `frontend/src/components/ShareButton.vue` (9 occurrences)
- `frontend/src/components/RoadmapFilters.vue` (9 occurrences)
- `frontend/src/components/RoadmapTabs.vue` (4 occurrences)
- `frontend/src/components/RoadmapEmptyState.vue` (3 occurrences)
- `frontend/src/components/MagicSearchBar.vue` (2 occurrences)
- `frontend/src/components/ImageCarouselModal.vue` (2 occurrences)
- `frontend/src/views/RoadmapView.vue` (1 occurrence)
- `frontend/src/components/RoadmapCardList.vue` (1 occurrence)
- `frontend/src/components/CanvasMode/CanvasExitButton.vue` (1 occurrence)
- `frontend/src/components/CanvasMode/CanvasEmptyState.vue` (1 occurrence)

### Package manifest
- `frontend/package.json` — no code change; `npm install` refreshes to 3.25.3 via `"latest"`

---

## 7. Test Impact Assessment

**Decision**: Existing unit tests are not expected to fail from these changes; coverage thresholds remain achievable.

**Rationale**:
- CSS changes (color fallbacks, font family) are not exercised by unit tests.
- Text content changes are not tested directly in existing unit tests (confirmed: no test snapshots).
- Package upgrade may trigger component API changes that break test mounts — must run `npm test` post-upgrade and fix any failures.
- Stylelint rules to watch: `Expected modern color-function notation` and `Unexpected vendor-prefixed property` — existing code uses `var()` patterns, which are fine.

---

## 8. Rollout Order

1. Upgrade `@weni/unnnic-system` to 3.25.3 (`npm install`)
2. Update `App.vue` font-family fallback (`'Lato'` → `'Inter'`)
3. Update color fallback hex values in all 11 component files
4. Apply brand rename in 3 files (4 text occurrences)
5. Run `npm run format && npm run lint -- --fix && npm run stylelint:check`
6. Run `npm test` — fix any coverage regressions
7. Manual visual verification in browser
