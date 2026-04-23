# Implementation Plan: Roadmap Feature Request

**Branch**: `007-roadmap-feature-request` | **Date**: 2026-01-21 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/007-roadmap-feature-request/spec.md`

## Summary

Add a **Request Feature** entry point to the roadmap page. Submissions create a Jira issue routed to the correct backlog based on the selected Module, enforce a `[FEATURE-REQUEST]` title prefix, and notify leaders in Slack (`#weni-product-tech-squad-leaders`).

**Technical approach (high level)**:
- **Frontend**: Add a modal form using Unnnic components; call a new backend endpoint with an idempotency key.
- **Backend**: Add a public POST endpoint that validates input, routes to Jira via explicit module routing config, creates the issue, and posts a Slack notification.
- **Safety**: Rate limiting + idempotency + lightweight bot mitigation to protect Jira/Slack from abuse.

## Technical Context

**Language/Version**: Python 3.11 (backend), TypeScript + Vue 3 (frontend)
**Primary Dependencies**:
  - Backend: Flask 3.x, Flask-Caching, Flask-CORS, Flask-Limiter, Requests
  - Frontend: Vue 3, Unnnic Design System, Axios
**Storage**: No database. Flask-Caching (Redis optional) + existing file fallback for roadmap cache; use cache for short-lived idempotency and Slack retry state.
**Testing**: pytest (backend), Vitest (frontend)
**Target Platform**: Web (responsive)
**Project Type**: Web application (frontend + backend)
**Performance Goals**: Feature request submission completes in < 3 seconds under normal conditions
**Constraints**: Public endpoint must be abuse-resistant; no leakage of private Jira data; Slack notification should not block user success when Jira creation succeeds
**Scale/Scope**: Low-to-moderate submission volume; must be safe under bursts and retries

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Clean Code & Readability**: Keep handlers thin; route logic and integrations live in services; single responsibility per function.
- **Code Style Standards**: No trailing whitespace; follow PEP 8/Black/Flake8; follow frontend lint rules (2-space indentation, semicolons, single quotes).
- **Testing & Coverage**: Add unit tests for routing/idempotency/Jira payload building and Slack notifier behavior (mock external calls).
- **Accessibility**: Modal and form controls must be accessible; semantic structure; Unnnic components preferred.

✅ **Pre-Design Check**: PASSED  
✅ **Post-Design Check**: PASSED (design artifacts produced and remain consistent with constitution)

## Project Structure

### Documentation (this feature)

```text
specs/007-roadmap-feature-request/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── openapi.yaml
└── tasks.md
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── __init__.py                  # Flask app factory (add limiter init if missing)
│   ├── config.py                    # Add Slack + routing config settings
│   ├── routes/
│   │   ├── __init__.py
│   │   └── roadmap.py               # Add feature-request endpoints to existing blueprint
│   ├── services/
│   │   ├── jira_client.py           # Add create-issue method + ADF builder helper
│   │   ├── cache_service.py         # Reuse cache for idempotency (new helpers)
│   │   └── slack_service.py         # NEW: send webhook notifications
│   └── models/
│       └── roadmap.py               # Keep public roadmap models; feature requests stay request/DTO-level
├── config/
│   ├── jira_projects.json
│   └── feature_request_routing.json # NEW: moduleId → Jira project mapping
└── tests/
    ├── unit/
    │   ├── test_feature_request_routing.py
    │   ├── test_feature_request_idempotency.py
    │   └── test_slack_service.py
    └── integration/
        └── test_feature_request_routes.py

frontend/
├── src/
│   ├── components/
│   │   ├── RoadmapView.vue               # Add "Request Feature" entry point
│   │   └── RoadmapFeatureRequestForm.vue # NEW: modal + form
│   ├── services/
│   │   └── roadmapService.ts             # Add createFeatureRequest + getRequestableModules
│   └── types/
│       └── roadmap.ts                    # Add request/response types
└── tests/
    ├── components/
    │   └── RoadmapFeatureRequestForm.spec.ts
    └── services/
        └── roadmapService.spec.ts
```

**Structure Decision**: Web application with separate `frontend/` (Vue) and `backend/` (Flask). New functionality follows existing blueprint/service patterns.

## API Endpoints → Backend Routes

| Endpoint | Route Handler | Purpose |
|----------|---------------|---------|
| `GET /api/v1/roadmap/feature-request/modules` | `routes/roadmap.py::get_feature_request_modules()` | Populate the Module dropdown with routable modules |
| `POST /api/v1/roadmap/feature-requests` | `routes/roadmap.py::create_feature_request()` | Validate, create Jira issue, notify Slack |

## Component Mapping (Frontend → Unnnic)

| UI Element | Unnnic Component(s) | Purpose |
|-----------|----------------------|---------|
| Request Feature button | `<unnnic-button>` | Entry point on roadmap page |
| Modal/Drawer | `<unnnic-modal>` (or closest Unnnic equivalent) | Contain the request form |
| Module select | `<unnnic-select-smart>` | Required module selection |
| Title input | `<unnnic-input>` | Required title |
| Description input | `<unnnic-textarea>` | Required description |
| Email input | `<unnnic-input>` | Required contact email |
| Feedback | `<unnnic-toast>` / `<unnnic-alert>` | Success/error states |

## Implementation Phases

### Phase 1: Backend (routing + integrations) (P1)

- Add routing config loader and validation for `moduleId`
- Implement idempotency using cache + `Idempotency-Key`
- Implement Jira issue creation (summary prefix + ADF description)
- Implement Slack webhook notifier to `#weni-product-tech-squad-leaders`
- Add rate limiting (Flask-Limiter) and honeypot validation
- Add unit + integration tests (mock Jira/Slack calls)

### Phase 2: Frontend (form UX) (P1)

- Add “Request Feature” button to roadmap view
- Add modal form component with required fields and validation
- Call new API with idempotency key; show success with Jira issue reference
- Add frontend tests for service + component behavior

### Phase 3: Reliability & Hardening (P2)

- Add retries/backoff for Slack notification and record failures for follow-up
- Improve error taxonomy and user-facing messages (still keeping public-safe output)

## Key Design Decisions

- **Dynamic routing**: Module → Jira project mapping is automatically built by analyzing existing roadmap items. Each module's issue ID prefix (e.g., "NEXUS-123") determines the target project. New modules appear automatically without configuration.
- **ADF for Jira description**: consistent with Jira Cloud v3 expectations and existing parsing logic.
- **Idempotency-first**: prevents duplicate Jira issues from retries and accidental resubmits.
- **Webhook-based Slack**: least privilege and simplest operations for a single channel.

## Complexity Tracking

No constitution violations requiring justification.
