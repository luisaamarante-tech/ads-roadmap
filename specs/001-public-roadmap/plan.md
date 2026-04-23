# Implementation Plan: Weni Public Roadmap

**Branch**: `001-public-roadmap` | **Date**: December 22, 2025 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-public-roadmap/spec.md`

## Summary

Build a public roadmap page for Weni customers and stakeholders to view upcoming and delivered features. The page displays items organized by status tabs (Delivered/Now/Next/Future) with time and module filtering. Data is sourced from JIRA epics via a secure backend that syncs and caches publicly-flagged items.

**Technical Approach**:
- **Frontend**: Vue.js 3 with Weni Design System (Unnnic) components
- **Backend**: Flask/Python with APScheduler for JIRA sync
- **Data Flow**: JIRA → Backend Sync → Cache → API → Frontend

## Technical Context

**Language/Version**: Python 3.11 (backend), TypeScript/Vue.js 3 (frontend)
**Primary Dependencies**:
  - Backend: Flask 3.x, Flask-Caching, Flask-CORS, Flask-Limiter, APScheduler, Requests
  - Frontend: Vue.js 3, Unnnic (Weni Design System), Axios
**Storage**: Flask-Caching (Redis or filesystem) - no database required
**Testing**: pytest (backend), Vitest (frontend)
**Target Platform**: Web (responsive desktop + mobile)
**Project Type**: Web application (frontend + backend)
**Performance Goals**: Page load < 3 seconds, API response < 500ms
**Constraints**: JIRA sync frequency 5 minutes, zero information leakage from non-public epics
**Scale/Scope**: Read-only public page, ~100 roadmap items, moderate traffic

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

The project constitution is a template with no specific gates defined. No violations to report.

✅ **Pre-Design Check**: PASSED (no constitution constraints)
✅ **Post-Design Check**: PASSED (no constitution constraints)

## Project Structure

### Documentation (this feature)

```text
specs/001-public-roadmap/
├── spec.md              # Feature specification
├── plan.md              # This file (implementation plan)
├── research.md          # Technology research and decisions
├── data-model.md        # Entity definitions and data flow
├── quickstart.md        # Developer setup guide
├── contracts/           # API contracts
│   └── openapi.yaml     # OpenAPI 3.0 specification
└── checklists/
    └── requirements.md  # Specification quality checklist
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── __init__.py           # Flask app factory
│   ├── config.py             # Configuration management
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── roadmap.py        # Roadmap API endpoints
│   │   └── health.py         # Health check endpoint
│   ├── services/
│   │   ├── __init__.py
│   │   ├── jira_client.py    # JIRA API client
│   │   ├── sync_service.py   # Data sync logic
│   │   └── cache_service.py  # Cache management
│   └── models/
│       ├── __init__.py
│       └── roadmap.py        # Data classes
├── tests/
│   ├── conftest.py
│   ├── test_routes.py
│   ├── test_sync.py
│   └── test_jira_client.py
├── requirements.txt
├── .env.example
├── Dockerfile
└── run.py

frontend/
├── src/
│   ├── components/
│   │   ├── RoadmapTabs.vue           # Status tab navigation
│   │   ├── RoadmapFilters.vue        # Year/Quarter/Module filters
│   │   ├── RoadmapCard.vue           # Expandable item card
│   │   ├── RoadmapCardList.vue       # List of cards with count
│   │   ├── RoadmapImageGallery.vue   # Image carousel (up to 4)
│   │   └── RoadmapEmptyState.vue     # Empty/loading states
│   ├── views/
│   │   └── RoadmapView.vue           # Main roadmap page
│   ├── services/
│   │   └── roadmapService.ts         # API client
│   ├── types/
│   │   └── roadmap.ts                # TypeScript interfaces
│   ├── App.vue
│   ├── main.ts
│   └── router/
│       └── index.ts
├── tests/
│   └── components/
│       └── RoadmapCard.spec.ts
├── .env.example
├── package.json
├── tsconfig.json
└── vite.config.ts
```

**Structure Decision**: Web application with separate frontend and backend. Frontend is a Vue.js SPA. Backend is a simple Flask API with background sync job. No database - all data cached from JIRA.

## Component Mapping

### Frontend Components → Unnnic Design System

| Custom Component | Unnnic Components Used | Purpose |
|------------------|------------------------|---------|
| `RoadmapTabs.vue` | `<unnnic-tabs>` | Status navigation (Delivered/Now/Next/Future) |
| `RoadmapFilters.vue` | `<unnnic-select-smart>`, `<unnnic-segmented-control>` | Year dropdown, Quarter buttons, Module filter |
| `RoadmapCard.vue` | `<unnnic-accordion>`, `<unnnic-card>`, `<unnnic-tag>` | Expandable item with module badge |
| `RoadmapImageGallery.vue` | `<unnnic-carousel>` | Feature screenshots (1-4 images) |
| `RoadmapEmptyState.vue` | `<unnnic-alert>`, `<unnnic-skeleton>` | Empty state and loading skeleton |
| `RoadmapCardList.vue` | Native Vue + CSS Grid | Container for cards with item count |

### API Endpoints → Backend Routes

| Endpoint | Route Handler | Purpose |
|----------|---------------|---------|
| `GET /api/v1/roadmap/items` | `routes/roadmap.py::get_items()` | List items with filters |
| `GET /api/v1/roadmap/items/{id}` | `routes/roadmap.py::get_item()` | Single item details |
| `GET /api/v1/roadmap/modules` | `routes/roadmap.py::get_modules()` | Available module filters |
| `GET /api/v1/roadmap/stats` | `routes/roadmap.py::get_stats()` | Item counts by status |
| `GET /api/v1/health` | `routes/health.py::health_check()` | Sync status and health |

## Implementation Phases

### Phase 1: Backend Core (P1 - Foundation)

1. **Flask app scaffold** with configuration
2. **JIRA client** for API authentication and epic fetching
3. **Sync service** with field extraction and validation
4. **Cache layer** for storing transformed data
5. **API routes** for roadmap items and modules

**Deliverables**: Working backend that syncs from JIRA and serves cached data

### Phase 2: Frontend Core (P1 - Core UI)

1. **Vue.js project** with Unnnic integration
2. **RoadmapTabs** component for status navigation
3. **RoadmapCard** expandable card component
4. **RoadmapCardList** with item count display
5. **API service** and state management

**Deliverables**: Working roadmap page with tabs and expandable cards

### Phase 3: Filtering & Polish (P2 - Enhanced UX)

1. **RoadmapFilters** component (year, quarter, module)
2. **RoadmapImageGallery** with carousel
3. **Empty states** and loading skeletons
4. **Mobile responsive** adjustments

**Deliverables**: Complete roadmap page with all filtering and polish

### Phase 4: Production Readiness (P1 - Security)

1. **Rate limiting** and CORS configuration
2. **Audit logging** for sync operations
3. **Docker containerization**
4. **Environment configuration** for production

**Deliverables**: Production-ready deployment package

## Key Design Decisions

### 1. No Database Required

**Decision**: Use in-memory/file caching instead of a database.

**Rationale**:
- Data is read-only and fully cacheable
- Source of truth is JIRA (not this system)
- Simplifies deployment and operations
- ~100 items fit easily in memory

### 2. Background Sync vs Real-time

**Decision**: Sync every 5 minutes via APScheduler.

**Rationale**:
- Decouples frontend performance from JIRA API
- Ensures availability during JIRA outages
- 5-minute delay acceptable per requirements (SC-003)
- Simpler than webhook-based real-time sync

### 3. Field Allowlist Security

**Decision**: Explicitly allowlist JIRA fields to extract.

**Rationale**:
- Prevents accidental data leakage (FR-011)
- Only specified fields ever leave JIRA
- Easy to audit what data is exposed

### 4. Status-Based Navigation

**Decision**: Primary navigation via status tabs (like Synerise).

**Rationale**:
- Clear mental model: "What's delivered? What's next?"
- Matches user expectations from reference design
- Works well with Unnnic Tabs component

## Dependencies

### Backend

```
flask>=3.0.0
flask-cors>=4.0.0
flask-caching>=2.0.0
flask-limiter>=3.5.0
apscheduler>=3.10.0
requests>=2.31.0
python-dotenv>=1.0.0
gunicorn>=21.0.0
pytest>=7.4.0
```

### Frontend

```json
{
  "dependencies": {
    "vue": "^3.4.0",
    "@weni/unnnic-system": "latest",
    "axios": "^1.6.0",
    "vue-router": "^4.2.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^4.5.0",
    "typescript": "^5.3.0",
    "vite": "^5.0.0",
    "vitest": "^1.0.0"
  }
}
```

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| JIRA API changes | Version-lock API calls, monitor deprecation notices |
| Custom field ID changes | Configuration-based field mapping, admin verification tool |
| Image availability | Proxy images through backend, fallback placeholder |
| Cache corruption | File-based fallback, health check endpoint |
| Rate limit abuse | Flask-Limiter, IP-based rate limiting |

## Success Metrics (from Spec)

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Page load time | < 3 seconds | Frontend performance monitoring |
| Data leakage | 0 incidents | Security audit, field allowlist |
| Sync latency | < 5 minutes | Backend metrics |
| Availability | 99.9% | Health endpoint monitoring |
| Mobile support | 100% | Browser testing |

## Related Artifacts

- [Specification](./spec.md) - Feature requirements
- [Research](./research.md) - Technology decisions
- [Data Model](./data-model.md) - Entity definitions
- [API Contract](./contracts/openapi.yaml) - OpenAPI specification
- [Quickstart](./quickstart.md) - Developer setup guide
