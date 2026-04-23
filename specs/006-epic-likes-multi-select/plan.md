# Implementation Plan: Epic Likes and Multi-Module Selection

**Branch**: `006-epic-likes-multi-select` | **Date**: 2026-01-20 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/006-epic-likes-multi-select/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

This feature adds two independent capabilities to the Weni Public Roadmap:

1. **Epic Likes**: Users can like roadmap epics to express interest, with like counts stored in JIRA custom fields and displayed on epic cards. No database storage—JIRA is the source of truth.

2. **Multi-Module Selection**: Users can select multiple product modules simultaneously to filter epics across different product areas, replacing the current single-module selection.

**Technical Approach**: Extend existing backend JIRA sync service to retrieve/update a new "Roadmap Likes" custom field, add a new API endpoint for like actions, update frontend components to display like counts and handle multi-module filtering via updated query parameters.

## Technical Context

**Language/Version**: Backend: Python 3.14 | Frontend: TypeScript 5.x with Vue 3
**Primary Dependencies**: Backend: FastAPI, requests (JIRA API), pytest | Frontend: Vue 3, Axios, Vite, Vitest
**Storage**: JIRA custom fields (no local database)
**Testing**: Backend: pytest with 80% coverage minimum | Frontend: Vitest with component tests
**Target Platform**: Web application (backend: Linux server via Render, frontend: Netlify CDN)
**Project Type**: Web (backend + frontend)
**Performance Goals**: 
- Like count retrieval: < 2 seconds on page load
- Like action: < 3 seconds for JIRA update
- Multi-module filtering: < 1 second for up to 500 epics
**Constraints**: 
- No local database (JIRA is the single source of truth)
- JIRA API rate limits: ~10 requests/second
- Stateless backend (no session storage)
- Must maintain backward compatibility with existing projects
**Scale/Scope**: 
- ~6 JIRA projects currently configured
- ~500 epics maximum across all projects
- Support up to 10 concurrent module selections

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Compliance Review

| Principle | Status | Notes |
|-----------|--------|-------|
| **I. Clean Code & Readability** | ✅ PASS | Feature extends existing service patterns without introducing new complexity |
| **II. Code Style Standards** | ✅ PASS | Will follow PEP 8 (backend) and Vue/TypeScript conventions (frontend) with existing linters |
| **III. Naming Conventions** | ✅ PASS | Backend: `snake_case`, Frontend: `camelCase` for functions, `PascalCase` for components, BEM for CSS |
| **IV. Testing & Quality Assurance** | ✅ PASS | Unit tests required for new service methods, API endpoints, and Vue components. Target 80%+ coverage |
| **V. Semantic HTML & Accessibility** | ✅ PASS | Like button will use semantic `<button>` with proper ARIA labels, multi-select uses semantic `<select>` or checkboxes |
| **Backend Standards** | ✅ PASS | New API endpoint follows existing FastAPI patterns, pre-commit hooks in place |
| **Frontend Standards** | ✅ PASS | Component structure follows existing patterns (components/, services/, types/) |
| **Design System Compliance** | ✅ PASS | Like button will use Unnnic button styles, filter UI uses existing Unnnic components |

### Gate Result

**STATUS: ✅ PASS** - All constitution principles satisfied. No violations to justify.

- No new architectural patterns introduced
- Extends existing JIRA client and sync service
- Follows established API endpoint conventions
- Reuses existing filter infrastructure
- No database or state management additions

## Project Structure

### Documentation (this feature)

```text
specs/006-epic-likes-multi-select/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   ├── api-contracts.md
│   └── jira-projects-schema-update.json
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── models/
│   │   ├── roadmap.py              # UPDATE: Add likes field to RoadmapItem
│   │   └── custom_field.py         # UPDATE: Add roadmap_likes to ProjectFieldConfiguration
│   ├── services/
│   │   ├── jira_client.py          # UPDATE: Extract likes field, add update_likes method
│   │   ├── sync_service.py         # UPDATE: Sync likes during normal sync cycle
│   │   └── config_loader.py        # UPDATE: Add roadmap_likes to ProjectFieldMapping
│   ├── routes/
│   │   └── roadmap.py              # NEW: Add POST /items/{id}/like endpoint
│   │                               # UPDATE: Handle multiple module query params
│   └── config.py                   # No changes (uses jira_projects.json)
├── config/
│   ├── jira_projects.json          # UPDATE: Add roadmap_likes field for all projects
│   └── jira_projects.schema.json  # UPDATE: Add roadmap_likes to required fields
└── tests/
    ├── unit/
    │   ├── test_roadmap_model.py   # UPDATE: Test likes field
    │   ├── test_jira_client.py     # UPDATE: Test likes extraction/update
    │   └── test_roadmap_routes.py  # NEW: Test like endpoint
    └── integration/
        └── test_sync_service.py    # UPDATE: Test likes sync

frontend/
├── src/
│   ├── types/
│   │   └── roadmap.ts              # UPDATE: Add likes field, update RoadmapFilters
│   ├── components/
│   │   ├── RoadmapCard.vue         # UPDATE: Add like button and count display
│   │   └── RoadmapFilters.vue      # UPDATE: Multi-select for modules
│   ├── services/
│   │   └── roadmapService.ts       # NEW: Add likeEpic method
│   │                               # UPDATE: Support module array in filters
│   └── views/
│       └── RoadmapView.vue         # UPDATE: Handle multi-module in filters state
└── tests/
    ├── components/
    │   ├── RoadmapCard.test.ts     # UPDATE: Test like button interaction
    │   └── RoadmapFilters.test.ts  # UPDATE: Test multi-select behavior
    └── services/
        └── roadmapService.test.ts  # NEW: Test likeEpic API call
```

**Structure Decision**: This is a web application with existing backend (Python/FastAPI) and frontend (Vue 3/TypeScript) projects. The feature extends existing modules without introducing new architectural layers. Backend changes are primarily in the services layer (JIRA client, sync service) and routes (new endpoint). Frontend changes focus on existing components (RoadmapCard, RoadmapFilters) with minimal service layer additions.

## Complexity Tracking

No complexity violations—all constitution gates passed without justification needed.

## Phase 0: Research & Technology Decisions

See [research.md](./research.md) for detailed research findings.

### Key Decisions

1. **Like Storage in JIRA**: Use JIRA number custom field type to store integer like counts
2. **Like Increment Strategy**: Direct JIRA API update with optimistic UI update and rollback on error
3. **Multi-Module Query Format**: Use repeated `module` query parameters following standard web conventions
4. **Debouncing Strategy**: Frontend debouncing with 500ms delay to prevent rapid-click issues
5. **Missing Field Handling**: Default to 0 likes, disable like button if field not configured

## Phase 1: Design Artifacts

### Data Model

See [data-model.md](./data-model.md) for complete entity definitions and relationships.

**Summary**:
- `RoadmapItem` model gains `likes: int` field
- `ProjectFieldConfiguration` gains `roadmap_likes: str` field mapping
- `RoadmapFilters` interface updated to accept `module: str | str[]`

### Contracts

See [contracts/](./contracts/) directory for API specifications.

**Summary**:
- New endpoint: `POST /api/v1/roadmap/items/{itemId}/like`
- Updated endpoint: `GET /api/v1/roadmap/items` supports multiple `module` params
- Updated TypeScript interfaces with `likes` field

### Quickstart

See [quickstart.md](./quickstart.md) for setup and development instructions.

## Implementation Notes

### Backend Implementation Order

1. Update `jira_projects.schema.json` to add `roadmap_likes` as required field
2. Update `ProjectFieldMapping` and `ProjectFieldConfiguration` dataclasses
3. Update `JiraClient` to extract likes field from JIRA epics
4. Add `JiraClient.update_epic_likes(issue_key, new_count)` method
5. Update `SyncService` to include likes in sync cycle
6. Add `POST /api/v1/roadmap/items/{id}/like` endpoint in `routes/roadmap.py`
7. Update `matches_filters` method to handle module as list
8. Write unit tests for all new/modified methods

### Frontend Implementation Order

1. Update `roadmap.ts` types to include `likes: number` in `RoadmapItem`
2. Update `RoadmapFilters` interface to support `module?: string | string[]`
3. Add `likeEpic(itemId: string)` method to `roadmapService.ts`
4. Update `RoadmapCard.vue` to display like count and like button
5. Add click handler with debouncing and optimistic updates
6. Update `RoadmapFilters.vue` to support multi-select (checkboxes or multi-select dropdown)
7. Update `RoadmapView.vue` to handle module array in filter state
8. Update URL query parameter serialization for multiple modules
9. Write component tests for like button and multi-select interactions

### Configuration Updates

Each JIRA project in `config/jira_projects.json` must add:

```json
"roadmap_likes": "customfield_XXXXX"
```

The CLI tool (`app/cli/jira_setup.py`) should be updated to include "Roadmap Likes" in the interactive field mapping flow.

### Testing Strategy

**Backend**:
- Unit test `RoadmapItem.to_dict()` includes `likes` field
- Unit test `JiraClient._extract_roadmap_item()` handles missing likes field
- Unit test `JiraClient.update_epic_likes()` makes correct API call
- Integration test full sync cycle includes likes
- API test `POST /like` endpoint with success/error scenarios
- API test multi-module filtering with 0, 1, and multiple modules

**Frontend**:
- Component test like button renders with correct count
- Component test like button click triggers API call
- Component test like button shows loading state during update
- Component test like button handles errors gracefully
- Component test multi-select allows selecting/deselecting modules
- Component test multi-select updates URL parameters
- Service test `likeEpic` calls correct endpoint

### Migration Considerations

**Breaking Changes**: None—feature is additive

**Backward Compatibility**:
- Projects without `roadmap_likes` field configured will show 0 likes (read-only)
- Existing single-module filter URLs continue to work
- New multi-module URLs are forward-compatible

**Rollback Plan**:
- Remove `likes` field from API responses (non-breaking for clients)
- Hide like button in frontend via feature flag if needed
- Restore single-module filter UI

## Post-Phase 1 Constitution Re-check

**STATUS: ✅ PASS** - Design artifacts maintain compliance with all constitution principles.

- Data model changes are minimal and follow existing patterns
- API contracts use standard REST conventions
- No new architectural complexity introduced
- Testing strategy meets 80% coverage requirements
- Frontend components follow BEM naming and Vue 3 Composition API patterns

## Next Steps

This plan is complete. To continue:

1. **Review this plan** and all generated artifacts (research.md, data-model.md, contracts/, quickstart.md)
2. **Run `/speckit.tasks`** to break this plan into granular implementation tasks
3. **Begin implementation** following the task order and testing strategy defined above
