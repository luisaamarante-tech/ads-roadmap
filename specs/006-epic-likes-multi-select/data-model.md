# Data Model: Epic Likes and Multi-Module Selection

**Feature**: Epic Likes and Multi-Module Selection  
**Date**: 2026-01-20  
**Status**: Design Complete

## Overview

This document defines the data structures and relationships for the Epic Likes and Multi-Module Selection features. All entities are derived from functional requirements in the feature specification.

## Core Entities

### 1. RoadmapItem (Updated)

Represents a single roadmap entry derived from a JIRA Epic, now including like count.

**Location**: `backend/app/models/roadmap.py`

**Fields**:

| Field | Type | Required | Description | Validation | Source |
|-------|------|----------|-------------|------------|--------|
| `id` | `str` | Yes | JIRA issue key | Format: `[A-Z]+-\d+` | JIRA `key` |
| `title` | `str` | Yes | Epic title | Max 255 chars | JIRA `summary` or custom field |
| `description` | `str` | Yes | Epic description | Max 5000 chars | JIRA custom field |
| `status` | `DeliveryStatus` | Yes | Delivery status | Enum: DELIVERED, NOW, NEXT, FUTURE | JIRA custom field |
| `module` | `str` | Yes | Product module name | Non-empty string | JIRA custom field |
| `module_id` | `str` | Yes | URL-safe module slug | Slugified from `module` | Derived |
| `release_year` | `int` | Yes | Release year | >= 2020 | JIRA custom field |
| `release_quarter` | `Quarter` | Yes | Release quarter | Enum: Q1, Q2, Q3, Q4 | JIRA custom field |
| `release_month` | `int` | No | Release month | 1-12 or null | JIRA custom field |
| `images` | `list[str]` | Yes | Image URLs | Max 4 items, valid URLs | JIRA custom fields |
| `documentation_url` | `str` | No | Documentation link | Valid URL or null | JIRA custom field |
| `likes` | `int` | Yes | Like count | >= 0, default 0 | **NEW**: JIRA custom field |
| `last_synced_at` | `datetime` | Yes | Last sync timestamp | ISO 8601 format | System generated |

**New Field Details**:
- **`likes`**: Integer representing the number of times users have liked this epic
  - Stored in JIRA custom field "Roadmap Likes" (mapped per project)
  - Default value: 0 (if field missing or not configured)
  - Validation: Non-negative integer only
  - Updated via `POST /api/v1/roadmap/items/{id}/like` endpoint

**State Transitions**: None (likes are additive, no state machine)

**Relationships**:
- Belongs to one Module (via `module_id`)
- Referenced by LikeAction (via `id`)

**Example**:

```python
RoadmapItem(
    id="NEXUS-123",
    title="Advanced Flow Builder",
    description="A new visual flow builder...",
    status=DeliveryStatus.NOW,
    module="Flows",
    module_id="flows",
    release_year=2026,
    release_quarter=Quarter.Q2,
    release_month=6,
    images=["https://example.com/img1.png"],
    documentation_url="https://docs.example.com/flows",
    likes=42,  # NEW FIELD
    last_synced_at=datetime(2026, 1, 20, 10, 30, 0)
)
```

**Serialization** (`to_dict` method):

```python
{
    "id": "NEXUS-123",
    "title": "Advanced Flow Builder",
    "description": "A new visual flow builder...",
    "status": "NOW",
    "module": "Flows",
    "moduleId": "flows",
    "releaseYear": 2026,
    "releaseQuarter": "Q2",
    "releaseMonth": 6,
    "images": ["https://example.com/img1.png"],
    "documentationUrl": "https://docs.example.com/flows",
    "likes": 42,  # NEW FIELD
    "lastSyncedAt": "2026-01-20T10:30:00Z"
}
```

---

### 2. ProjectFieldConfiguration (Updated)

Custom field mapping for a JIRA project, now including likes field.

**Location**: `backend/app/models/custom_field.py`

**Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `public_roadmap` | `str` | Yes | Field marking epic as public |
| `roadmap_status` | `str` | Yes | Delivery status field |
| `module` | `str` | Yes | Module/area field |
| `release_year` | `str` | Yes | Release year field |
| `release_quarter` | `str` | Yes | Release quarter field |
| `release_month` | `str` | Yes | Release month field |
| `documentation_url` | `str` | Yes | Documentation URL field |
| `roadmap_title` | `str` | Yes | Public title field |
| `roadmap_description` | `str` | Yes | Public description field |
| `roadmap_image_url_1` | `str` | Yes | First image URL field |
| `roadmap_image_url_2` | `str` | Yes | Second image URL field |
| `roadmap_image_url_3` | `str` | Yes | Third image URL field |
| `roadmap_image_url_4` | `str` | Yes | Fourth image URL field |
| `roadmap_likes` | `str` | Yes | **NEW**: Like count field |

**New Field**:
- **`roadmap_likes`**: Custom field ID for storing like counts
  - Format: `customfield_\d{5,}` (e.g., "customfield_14929")
  - Type in JIRA: Number field
  - Required in schema (all projects must configure)
  - Used by `JiraClient` to extract/update like counts

**Validation**:

```python
def validate_all_fields_set(self) -> bool:
    """Check that all fields have valid custom field IDs."""
    pattern = re.compile(r"^customfield_\d{5,}$")
    for field_id in asdict(self).values():
        if not pattern.match(field_id):
            return False
    return True
```

**Example**:

```python
ProjectFieldConfiguration(
    public_roadmap="customfield_14699",
    roadmap_status="customfield_14698",
    module="customfield_14622",
    release_year="customfield_14623",
    release_quarter="customfield_14624",
    release_month="customfield_14625",
    documentation_url="customfield_14626",
    roadmap_title="customfield_14697",
    roadmap_description="customfield_14696",
    roadmap_image_url_1="customfield_14695",
    roadmap_image_url_2="customfield_14694",
    roadmap_image_url_3="customfield_14693",
    roadmap_image_url_4="customfield_14692",
    roadmap_likes="customfield_14929"  # NEW FIELD
)
```

---

### 3. RoadmapFilters (Updated)

Filter criteria for querying roadmap items, now supporting multiple modules.

**Location**: `frontend/src/types/roadmap.ts` (TypeScript), backend route params (Python)

**Fields**:

| Field | Type | Required | Description | Validation |
|-------|------|----------|-------------|------------|
| `status` | `DeliveryStatus` | No | Filter by delivery status | Enum value or undefined |
| `year` | `int` | No | Filter by release year | >= 2020 or undefined |
| `quarter` | `Quarter` | No | Filter by release quarter | Enum value or undefined |
| `module` | `str \| str[]` | No | **UPDATED**: Filter by one or more modules | String or array of strings |

**Changed Field**:
- **`module`**: Previously `str` (single module), now `str | str[]` (single or multiple)
  - Frontend: Can be `undefined`, single string, or array of strings
  - Backend: Parsed as `List[str]` from repeated query params
  - URL format: `?module=flows` or `?module=flows&module=integrations`
  - Empty/undefined means "show all modules"

**Backend Type** (FastAPI):

```python
from typing import Optional, List
from fastapi import Query

@app.get("/roadmap/items")
async def get_items(
    status: Optional[DeliveryStatus] = None,
    year: Optional[int] = None,
    quarter: Optional[Quarter] = None,
    module: Optional[List[str]] = Query(None)  # UPDATED: List instead of str
):
    filters = RoadmapFilters(
        status=status,
        year=year,
        quarter=quarter,
        module=module
    )
    ...
```

**Frontend Type** (TypeScript):

```typescript
export interface RoadmapFilters {
  status?: DeliveryStatus;
  year?: number;
  quarter?: Quarter;
  module?: string | string[];  // UPDATED: Can be single or array
}
```

**Filtering Logic**:

```python
def matches_filters(
    self,
    status: Optional[str] = None,
    year: Optional[int] = None,
    quarter: Optional[str] = None,
    module: Optional[List[str]] = None,  # UPDATED: Now accepts list
) -> bool:
    """Check if item matches the given filters."""
    if status and self.status.value != status:
        return False
    if year and self.release_year != year:
        return False
    if quarter and self.release_quarter.value != quarter:
        return False
    # UPDATED: Check if module_id is in the list of modules
    if module and self.module_id not in module:
        return False
    return True
```

---

### 4. LikeResponse (New)

Response structure for like action API endpoint.

**Location**: `frontend/src/types/roadmap.ts` (TypeScript), backend route response (Python)

**Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | `str` | Yes | JIRA issue key of liked item |
| `likes` | `int` | Yes | Updated like count |
| `success` | `bool` | Yes | Whether operation succeeded |
| `error` | `str` | No | Error message if failed |

**TypeScript Interface**:

```typescript
export interface LikeResponse {
  id: string;
  likes: number;
  success: boolean;
  error?: string;
}
```

**Python Model** (response):

```python
from pydantic import BaseModel

class LikeResponse(BaseModel):
    id: str
    likes: int
    success: bool
    error: Optional[str] = None
```

**Success Example**:

```json
{
  "id": "NEXUS-123",
  "likes": 43,
  "success": true
}
```

**Error Example**:

```json
{
  "id": "NEXUS-123",
  "likes": 42,
  "success": false,
  "error": "JIRA API unavailable"
}
```

---

## Data Flow Diagrams

### Like Action Flow

```
User (Frontend)
    |
    | 1. Click like button
    v
RoadmapCard.vue
    |
    | 2. Optimistic update (likes++)
    | 3. Call likeEpic(itemId)
    v
roadmapService.ts
    |
    | 4. POST /api/v1/roadmap/items/{id}/like
    v
Backend (FastAPI)
    |
    | 5. Validate item exists
    | 6. Get current like count from JIRA
    v
JiraClient
    |
    | 7. PUT /rest/api/3/issue/{key} with likes++
    v
JIRA API
    |
    | 8. Update custom field
    | 9. Return success
    v
Backend
    |
    | 10. Return LikeResponse
    v
Frontend
    |
    | 11. Reconcile UI with server count
    v
User sees updated count
```

### Multi-Module Filter Flow

```
User (Frontend)
    |
    | 1. Select multiple modules
    v
RoadmapFilters.vue
    |
    | 2. Emit update:modelValue with module array
    v
RoadmapView.vue
    |
    | 3. Update filters state: { module: ['flows', 'integrations'] }
    | 4. Update URL: ?module=flows&module=integrations
    | 5. Call handleFetchItems()
    v
roadmapService.ts
    |
    | 6. GET /api/v1/roadmap/items?module=flows&module=integrations
    v
Backend (FastAPI)
    |
    | 7. Parse module as List[str]
    | 8. Filter cached items
    v
Filtered RoadmapItem[]
    |
    | 9. Return JSON response
    v
Frontend
    |
    | 10. Update items state
    v
RoadmapCardList displays filtered items
```

---

## Validation Rules

### Like Count Validation

**Backend**:
- Must be non-negative integer: `likes >= 0`
- Cannot exceed maximum integer value (2^31 - 1)
- Default to 0 if JIRA field missing or null

**JIRA Field Configuration**:
- Field type: Number (integer)
- Default value: 0
- Allow negative: No
- Required: No (to support existing epics)

### Module Filter Validation

**Backend**:
- Each module ID must match pattern: `^[a-z0-9-]+$` (URL-safe slug)
- Maximum 10 modules per request (prevent abuse)
- Unknown module IDs are ignored (return empty results)

**Frontend**:
- Module selections stored as Set to prevent duplicates
- URL encoding handles special characters automatically

---

## Migration Strategy

### Existing Data

**Current State**:
- ~500 existing epics across 6 projects
- No `likes` field in RoadmapItem
- Single `module` string in filters

**Migration Steps**:

1. **Schema Update** (Non-breaking):
   - Add `roadmap_likes` to `jira_projects.schema.json` as required field
   - Update all project configurations in `jira_projects.json` with placeholder field IDs

2. **Backend Model Update** (Non-breaking):
   - Add `likes: int = 0` to `RoadmapItem` dataclass with default value
   - Update `to_dict()` to include `likes` field
   - Update `JiraClient._extract_roadmap_item()` to handle missing field gracefully

3. **JIRA Field Creation** (Manual):
   - Create "Roadmap Likes" number field in each JIRA project
   - Update `jira_projects.json` with actual custom field IDs
   - Run CLI tool to verify mappings

4. **Frontend Update** (Non-breaking):
   - Add `likes: number` to `RoadmapItem` interface (TypeScript allows missing fields from server)
   - Update components to display/handle likes
   - Gracefully handle `likes: undefined` from server (show as 0)

5. **Data Backfill** (Post-deployment):
   - Next sync cycle will populate `likes: 0` for all existing epics
   - No manual backfill needed (defaults to 0)

**Rollback Plan**:
- Remove `likes` field from API responses (clients ignore unknown fields)
- No database to clean up (JIRA fields remain but unused)

---

## Performance Considerations

### Like Count Storage

- **JIRA API call cost**: 1 request per like action (acceptable for low frequency)
- **Sync overhead**: No additional overhead (included in existing field fetch)
- **Cache impact**: Negligible (4 bytes per epic)

### Multi-Module Filtering

- **Client-side filtering**: O(n) where n = total epics (~500)
- **No backend query overhead**: Filters applied to cached data
- **URL parameter size**: ~20 bytes per module (10 modules = ~200 bytes)

---

## Summary

**Total Changes**:
- 1 new field added to existing entity (`RoadmapItem.likes`)
- 1 existing field updated (`RoadmapFilters.module` from string to array)
- 1 new response model (`LikeResponse`)
- 1 new configuration field (`ProjectFieldConfiguration.roadmap_likes`)

**Data Integrity**:
- All data stored in JIRA (no local persistence)
- Default values ensure backward compatibility
- Validation rules prevent invalid states

**Ready for Implementation**: All data structures defined and validated.
