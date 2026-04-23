# Research: Epic Likes and Multi-Module Selection

**Feature**: Epic Likes and Multi-Module Selection  
**Date**: 2026-01-20  
**Researcher**: AI Planning Agent  
**Status**: Complete

## Overview

This document captures research findings and technical decisions for implementing like functionality on roadmap epics and multi-module filtering. All research tasks identified in the Technical Context have been resolved.

## Research Areas

### 1. JIRA Custom Field for Like Storage

**Question**: What is the best JIRA custom field type for storing like counts?

**Decision**: Use **Number** field type (integer)

**Rationale**:
- JIRA Number fields support integers with atomic increment operations
- Field can be updated via REST API with simple PUT/POST operations
- Validation ensures only numeric values are stored
- No need for complex parsing or transformation
- Direct mapping to backend `int` and frontend `number` types

**Alternatives Considered**:
- **Text field**: Rejected due to lack of type safety and need for manual validation
- **Labels**: Rejected as semantically incorrect and hard to aggregate
- **Custom JSON in description**: Rejected as non-standard and fragile

**Implementation Notes**:
- Field name: "Roadmap Likes"
- Default value: 0
- Validation: Non-negative integers only
- API endpoint: `/rest/api/3/issue/{issueIdOrKey}` with field update payload

**References**:
- JIRA Cloud REST API v3 - Update Issue: https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issues/#api-rest-api-3-issue-issueidorkey-put
- JIRA Custom Fields Documentation: https://support.atlassian.com/jira-cloud-administration/docs/edit-a-custom-field/

---

### 2. Like Increment Strategy

**Question**: How should we handle like increments to balance performance, consistency, and user experience?

**Decision**: **Optimistic UI Update with Server Reconciliation**

**Rationale**:
- Provides immediate feedback to users (better UX)
- Reduces perceived latency from 3s to instant
- Handles JIRA API failures gracefully with rollback
- Simple to implement without introducing state management complexity
- Aligns with existing stateless backend architecture

**Implementation Flow**:
1. User clicks like button
2. Frontend immediately increments count in UI (optimistic update)
3. Frontend calls `POST /api/v1/roadmap/items/{id}/like` endpoint
4. Backend increments JIRA field by 1 via JIRA API
5. Backend returns new count
6. Frontend reconciles UI with server response
7. On error: Rollback UI change and show error message

**Alternatives Considered**:
- **Synchronous wait**: Rejected due to poor UX (3s wait)
- **Pessimistic locking**: Rejected as over-engineered for anonymous likes
- **Client-side only**: Rejected as violates "JIRA is the database" requirement
- **Queue-based processing**: Rejected as adds unnecessary complexity

**Edge Case Handling**:
- **Rapid clicks**: Debounce button with 500ms delay to prevent duplicate requests
- **Concurrent updates**: Last-write-wins (acceptable for anonymous likes)
- **API timeout**: Show error, rollback UI, suggest retry
- **Network offline**: Detect and disable like button with message

**References**:
- Optimistic UI Patterns: https://www.apollographql.com/docs/react/performance/optimistic-ui/
- REST API Best Practices for Idempotency: https://restfulapi.net/idempotent-rest-apis/

---

### 3. Multi-Module Query Parameter Format

**Question**: What is the standard way to encode multiple module selections in URL query parameters?

**Decision**: **Repeated Query Parameters** (e.g., `?module=flows&module=integrations`)

**Rationale**:
- Follows HTTP standard for array parameters (RFC 3986)
- Native support in most frameworks (FastAPI, Axios, URLSearchParams)
- Human-readable and bookmarkable URLs
- Compatible with browser history API
- Consistent with existing filter patterns (status, year, quarter)

**URL Examples**:
```
# Single module (backward compatible)
?status=NOW&module=flows

# Multiple modules (new)
?status=NOW&module=flows&module=integrations&module=analytics

# No modules (show all)
?status=NOW
```

**Backend Parsing** (FastAPI):
```python
@app.get("/roadmap/items")
def get_items(module: List[str] = Query(None)):
    # module is None, ["flows"], or ["flows", "integrations", ...]
```

**Frontend Encoding** (URLSearchParams):
```typescript
const params = new URLSearchParams();
modules.forEach(m => params.append('module', m));
// Result: module=flows&module=integrations
```

**Alternatives Considered**:
- **Comma-separated** (`?module=flows,integrations`): Rejected due to URL encoding issues with commas
- **Bracket notation** (`?module[]=flows&module[]=integrations`): Rejected as non-standard and framework-specific
- **JSON in query** (`?module=["flows","integrations"]`): Rejected due to encoding complexity

**References**:
- RFC 3986 (URI): https://datatracker.ietf.org/doc/html/rfc3986#section-3.4
- FastAPI Query Parameters: https://fastapi.tiangolo.com/tutorial/query-params-str-validations/#query-parameter-list-multiple-values
- MDN URLSearchParams: https://developer.mozilla.org/en-US/docs/Web/API/URLSearchParams

---

### 4. Frontend Debouncing Strategy

**Question**: How do we prevent rapid-click issues while maintaining responsiveness?

**Decision**: **Client-side debouncing with 500ms delay + request deduplication**

**Rationale**:
- 500ms is imperceptible to users but prevents double-clicks
- Debouncing at the button level is simpler than global state
- Request deduplication via request IDs prevents duplicate backend calls
- Aligns with existing frontend patterns (no new dependencies)

**Implementation Approach**:
```typescript
const likePending = ref(false);
const debounceTimer = ref<number | null>(null);

function onLikeClick() {
  if (likePending.value) return; // Prevent clicks during request
  
  if (debounceTimer.value) {
    clearTimeout(debounceTimer.value);
  }
  
  debounceTimer.value = setTimeout(async () => {
    likePending.value = true;
    try {
      await likeEpic(item.id);
    } finally {
      likePending.value = false;
    }
  }, 500);
}
```

**Alternatives Considered**:
- **Lodash debounce**: Rejected to avoid adding dependency
- **No debouncing**: Rejected due to UX issues with accidental double-clicks
- **Backend rate limiting**: Rejected as doesn't solve frontend UX problem

**References**:
- Debouncing vs Throttling: https://css-tricks.com/debouncing-throttling-explained-examples/
- Vue 3 Debouncing Patterns: https://vuejs.org/guide/essentials/event-handling.html#event-modifiers

---

### 5. Handling Missing JIRA Custom Fields

**Question**: What should happen when a project doesn't have the "Roadmap Likes" field configured?

**Decision**: **Graceful degradation with default value of 0 and disabled interaction**

**Rationale**:
- Maintains backward compatibility with existing projects
- Avoids breaking the application for projects without likes configured
- Provides clear visual indication (disabled button) when feature unavailable
- Allows gradual rollout across projects
- Follows "fail gracefully" principle

**Implementation**:
- Backend: If `roadmap_likes` not in project config, set `likes = 0` in `RoadmapItem`
- Backend: Return 404 or 400 error if like endpoint called for item without field
- Frontend: Display like count as "0" but disable/hide like button
- Frontend: Show tooltip on hover: "Likes not configured for this project"

**Error Handling Flow**:
1. Backend sync detects missing field mapping → logs warning, continues with `likes=0`
2. Frontend receives `likes=0` for unconfigured project
3. Frontend attempts like action → backend returns 400 "Field not configured"
4. Frontend shows error message: "Likes are not available for this epic"

**Alternatives Considered**:
- **Hard error on missing field**: Rejected as too disruptive
- **Hide like count entirely**: Rejected as inconsistent UI across projects
- **Auto-create field**: Rejected as requires admin permissions and is out of scope

**References**:
- Graceful Degradation Principles: https://developer.mozilla.org/en-US/docs/Glossary/Graceful_degradation
- Feature Flag Patterns: https://martinfowler.com/articles/feature-toggles.html

---

### 6. JIRA API Rate Limiting Considerations

**Question**: How do we ensure like updates don't exceed JIRA API rate limits?

**Decision**: **Client-side throttling + backend request queuing (future enhancement)**

**Rationale**:
- JIRA Cloud typically allows ~10 requests/second per API token
- Current traffic (500 epics, <100 daily visitors) is well below limits
- Frontend debouncing already reduces request volume
- Backend can add queue in future if needed
- Monitoring can detect approaching limits

**Current Implementation**:
- Frontend debouncing (500ms) naturally limits request rate
- Backend implements no special queuing (stateless design)
- Log JIRA API responses to detect 429 (rate limit) errors
- Return user-friendly error message if rate limited

**Future Enhancements** (if needed):
- Implement exponential backoff for 429 responses
- Add Redis-based request queue for burst handling
- Cache recent like counts to reduce read load

**Monitoring**:
- Track JIRA API response times and error rates
- Alert if 429 errors exceed 1% of requests
- Dashboard showing daily like count updates per project

**References**:
- JIRA Cloud Rate Limits: https://developer.atlassian.com/cloud/jira/platform/rate-limiting/
- Exponential Backoff: https://en.wikipedia.org/wiki/Exponential_backoff

---

### 7. Multi-Module UI Component Choice

**Question**: Should we use a multi-select dropdown or checkboxes for module filtering?

**Decision**: **Multi-select dropdown with checkbox-like behavior**

**Rationale**:
- Conserves vertical space (important for filter bar)
- Familiar pattern from existing single-select dropdown
- Unnnic design system provides multi-select component
- Supports "Select All" / "Clear All" actions
- Mobile-friendly with better touch targets than checkboxes

**Implementation**:
- Replace `<select>` with Unnnic multi-select component
- Show selected module count in collapsed state (e.g., "3 modules selected")
- "All Modules" option when none selected
- Sort modules alphabetically with item counts

**Alternatives Considered**:
- **Checkbox list**: Rejected due to vertical space consumption
- **Tag-based selection**: Rejected as less familiar pattern
- **Autocomplete**: Rejected as overkill for ~10 modules

**Accessibility**:
- ARIA labels for screen readers
- Keyboard navigation (arrow keys, space to select)
- Focus indicators on selected items

**References**:
- Unnnic Design System: https://unnnic.stg.cloud.weni.ai/
- Multi-Select Best Practices: https://www.nngroup.com/articles/drop-down-menus/

---

## Technology Stack Validation

### Backend

| Technology | Version | Purpose | Decision |
|------------|---------|---------|----------|
| Python | 3.14 | Backend runtime | ✅ Existing |
| FastAPI | Latest | API framework | ✅ Existing |
| Requests | Latest | JIRA API client | ✅ Existing |
| Pytest | Latest | Testing | ✅ Existing |

**No new backend dependencies required.**

### Frontend

| Technology | Version | Purpose | Decision |
|------------|---------|---------|----------|
| Vue 3 | 3.x | UI framework | ✅ Existing |
| TypeScript | 5.x | Type safety | ✅ Existing |
| Axios | Latest | HTTP client | ✅ Existing |
| Vite | Latest | Build tool | ✅ Existing |
| Vitest | Latest | Testing | ✅ Existing |
| Unnnic | Latest | Design system | ✅ Existing |

**No new frontend dependencies required.**

## Security Considerations

### Like Action Security

**Threat**: Spam/bot-generated likes

**Mitigation**:
- Rate limiting at API gateway level (existing Render infrastructure)
- CORS restrictions to allowed origins only
- Monitor for unusual patterns (same IP, rapid succession)

**Threat**: JIRA API token exposure

**Mitigation**:
- Backend-only access to JIRA credentials (existing pattern)
- Frontend never sees JIRA tokens
- Tokens stored in environment variables, not code

**Threat**: Unauthorized like manipulation

**Mitigation**:
- No authentication required (anonymous likes are acceptable per spec)
- Like counts are public data (no privacy concerns)
- JIRA field permissions restrict write access to service account

### Data Validation

- Backend validates `itemId` format (JIRA issue key pattern)
- Backend validates like count is non-negative integer
- Frontend sanitizes user input (though minimal for this feature)

## Performance Benchmarks

### Expected Metrics

| Operation | Target | Strategy |
|-----------|--------|----------|
| Load page with likes | < 2s | Include likes in existing JIRA sync, no extra calls |
| Like button click (perceived) | Instant | Optimistic UI update |
| Like button click (actual) | < 3s | Single JIRA API call to update field |
| Multi-module filter | < 1s | Client-side filtering of cached data |
| Sync with likes | < 30s | Parallel JIRA API calls (existing pattern) |

### Load Testing Considerations

- Current load: ~100 users/day, peak ~20 concurrent
- Like action load: Estimate 1-5 likes per user session
- JIRA API capacity: 10 req/s = 36,000 req/hour >> expected load

**Conclusion**: No performance concerns at current or 10x scale.

## Accessibility Requirements

### Like Button

- Semantic `<button>` element (not `<div>` with click handler)
- ARIA label: "Like this epic" / "Unlike this epic"
- ARIA pressed state for visual indication
- Keyboard accessible (Enter/Space to activate)
- Focus indicator visible
- Color contrast meets WCAG AA standards

### Multi-Select Filter

- Semantic `<select multiple>` or ARIA combobox pattern
- ARIA labels for screen readers
- Keyboard navigation (Tab, Arrow keys, Space)
- Announced selection count ("3 of 10 modules selected")

## Open Questions (Resolved)

All research questions have been resolved. No blocking unknowns remain.

## Summary

All technical decisions documented and justified. Implementation can proceed with confidence:

1. ✅ Like storage: JIRA Number custom field
2. ✅ Like increment: Optimistic UI with server reconciliation
3. ✅ Multi-module URL: Repeated query parameters
4. ✅ Debouncing: 500ms client-side with request deduplication
5. ✅ Missing fields: Graceful degradation with default 0
6. ✅ Rate limiting: Existing patterns sufficient for current scale
7. ✅ UI component: Multi-select dropdown from Unnnic

No new dependencies, no architecture changes, no security concerns. Ready for Phase 1 design.
