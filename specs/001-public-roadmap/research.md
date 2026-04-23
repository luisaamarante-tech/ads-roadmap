# Research: Weni Public Roadmap

**Feature Branch**: `001-public-roadmap`
**Date**: December 22, 2025

## 1. Weni Design System (Unnnic) Components

### Decision
Use the [Weni Design System (Unnnic)](https://unnnic.stg.cloud.weni.ai/) Vue.js component library for all UI components.

### Key Components to Use

| Component | Purpose | Location in Design System |
|-----------|---------|---------------------------|
| **Tabs** | Status navigation (Delivered/Now/Next/Future) | Navigation > Tabs |
| **SegmentedControl** | Quarter selector (Q1/Q2/Q3/Q4) | Navigation > SegmentedControl |
| **SelectSmart** | Year dropdown, Module/Area filter | Select > SelectSmart |
| **Accordion** | Expandable roadmap item cards | Accordion > Accordion |
| **Card** | Container for each roadmap item | Data Display > Card |
| **Tag / Chip** | Module/product badges | Data Display > Tag, Chip |
| **Carousel** | Image gallery for feature screenshots | Data Display > Carousel |
| **Button** | "Read More" link buttons | Form > Button |
| **Skeleton** | Loading states | Example > Skeleton |
| **PageHeader** | Page title and description | Layout > PageHeader |
| **Icon** | Various icons throughout | Misc > Icon |
| **Alert** | Empty state, error messages | Feedback > Alert |

### Rationale
- Pre-built, tested components reduce development time
- Consistent with Weni's existing products
- Responsive design built-in
- Accessible components following best practices

### Alternatives Considered
- Custom CSS components: Rejected - unnecessary duplication of effort
- Tailwind CSS: Rejected - doesn't match Weni's design language

---

## 2. JIRA Cloud REST API Integration

### Decision
Use JIRA Cloud REST API v3 with API token authentication for fetching epic data.

### Authentication Pattern
```
Authorization: Basic {base64(email:api_token)}
```

API tokens are created at: https://id.atlassian.com/manage-profile/security/api-tokens

### Key API Endpoints

| Endpoint | Purpose |
|----------|---------|
| `GET /rest/api/3/search` | Search for epics using JQL |
| `GET /rest/api/3/issue/{issueIdOrKey}` | Get single issue details |
| `GET /rest/api/3/field` | Get all custom field definitions |

### JQL Query Pattern
```jql
issuetype = Epic AND "Public Roadmap" = true AND project = {PROJECT_KEY}
```

### Custom Field Mapping Strategy

JIRA custom fields have IDs like `customfield_10001`. The backend must:
1. Fetch field definitions via `/rest/api/3/field` to map readable names to IDs
2. Store this mapping in configuration
3. Use the mapped IDs when parsing issue responses

### Required Custom Fields in JIRA

| Field Name | Type | Purpose |
|------------|------|---------|
| Public Roadmap | Checkbox | Flag to show on roadmap |
| Roadmap Status | Select (Delivered/Now/Next/Future) | Status tab placement |
| Release Month | Select (1-12) | Time filtering |
| Release Quarter | Select (Q1-Q4) | Time filtering |
| Release Year | Number | Time filtering |
| Module/Product | Select | Category filtering |
| Documentation Link | URL | "Read More" button |
| Roadmap Images | Attachment field | Up to 4 images |

### Rationale
- REST API v3 is the current, supported version
- API token auth is simpler than OAuth for server-to-server communication
- JQL provides powerful filtering capabilities
- Custom fields allow Product Managers to control visibility in JIRA

### Alternatives Considered
- OAuth 2.0 (3LO): Rejected - adds complexity for server-to-server use case
- JIRA Webhooks: Considered for real-time sync but adds complexity; polling is sufficient for 5-minute sync requirement
- GraphQL API: Not available for JIRA Cloud

---

## 3. Flask Backend Architecture

### Decision
Simple Flask application with the following structure:
- Flask for HTTP routing
- APScheduler for periodic JIRA sync
- Flask-Caching with Redis/file cache for data persistence
- Flask-CORS for cross-origin requests
- Flask-Limiter for rate limiting

### Dependencies
```
flask>=3.0.0
flask-cors>=4.0.0
flask-caching>=2.0.0
flask-limiter>=3.5.0
apscheduler>=3.10.0
requests>=2.31.0
python-dotenv>=1.0.0
gunicorn>=21.0.0
```

### Sync Strategy
1. Background job runs every 5 minutes (configurable)
2. Fetches all public epics from JIRA
3. Transforms and validates data
4. Stores in cache (replaces previous data)
5. API serves cached data (never hits JIRA directly for requests)

### Rationale
- Flask is lightweight and suitable for simple APIs
- APScheduler integrates well with Flask for background jobs
- File-based cache works for single-instance deployments; Redis for multi-instance
- Request-time caching ensures availability during JIRA outages

### Alternatives Considered
- Django: Rejected - overkill for a simple caching API
- FastAPI: Good alternative but Flask is more widely known
- Celery: Rejected - APScheduler is simpler for single-instance deployments

---

## 4. Data Caching Strategy

### Decision
Two-layer caching approach:
1. **Primary Cache**: In-memory/Redis cache of transformed roadmap data
2. **Fallback Cache**: Persistent file storage for JIRA outage scenarios

### Cache Invalidation
- Cache refreshed every sync cycle (5 minutes)
- No cache invalidation from frontend
- Stale data indicator if last sync > 10 minutes ago

### Rationale
- Ensures roadmap availability even during JIRA outages
- Reduces JIRA API calls
- Simplifies frontend (always reads from cache)

---

## 5. Security Considerations

### Decision
Implement strict data filtering at the sync layer.

### Security Measures

| Measure | Implementation |
|---------|----------------|
| Field allowlist | Only sync specified fields; ignore all others |
| No JIRA credentials in frontend | All JIRA auth stays in backend |
| Rate limiting | 100 requests/minute per IP |
| CORS | Restrict to known frontend domains |
| Audit logging | Log all sync operations with timestamps |

### Sensitive Data Handling
- JIRA credentials stored in environment variables only
- Never log JIRA API tokens
- Never expose raw JIRA issue data to frontend

### Rationale
- Defense in depth approach
- Minimizes attack surface
- Complies with requirement FR-011 (no data leakage)

---

## 6. Frontend Architecture

### Decision
Vue.js 3 with Composition API and the Unnnic component library.

### State Management
- Use Vue 3's built-in `reactive()` and `ref()` for local state
- No Vuex/Pinia needed for this read-only page

### API Integration
- Axios for HTTP requests
- Single `roadmapService.js` for all API calls

### Rationale
- Composition API is the modern Vue pattern
- Simple read-only page doesn't need complex state management
- Matches Weni's existing Vue.js ecosystem

---

## 7. Deployment Considerations

### Decision
Containerized deployment with Docker.

### Container Strategy
- Single Dockerfile for backend (Flask + sync worker)
- Frontend can be static files served via Nginx or embedded in existing Weni app

### Environment Variables
```
JIRA_BASE_URL=https://your-domain.atlassian.net
JIRA_EMAIL=service-account@company.com
JIRA_API_TOKEN=secret-token
JIRA_PROJECT_KEY=PROJ
SYNC_INTERVAL_MINUTES=5
CACHE_TYPE=redis  # or 'filesystem'
REDIS_URL=redis://localhost:6379/0
ALLOWED_ORIGINS=https://roadmap.weni.ai
```

### Rationale
- Docker ensures consistent deployments
- Environment variables follow 12-factor app principles
- Supports both simple and scalable deployments

---

## Summary of Technology Stack

| Layer | Technology | Version |
|-------|------------|---------|
| Frontend | Vue.js | 3.x |
| UI Components | Unnnic (Weni Design System) | Latest |
| Backend | Flask | 3.x |
| Python | Python | 3.11+ |
| Cache | Flask-Caching (Redis/File) | 2.x |
| Scheduler | APScheduler | 3.x |
| HTTP Client | Requests | 2.x |
| JIRA API | Atlassian REST API v3 | v3 |
