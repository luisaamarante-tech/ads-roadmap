# Data Model: Weni Public Roadmap

**Feature Branch**: `001-public-roadmap`
**Date**: December 22, 2025

## Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        RoadmapItem                               │
├─────────────────────────────────────────────────────────────────┤
│ id: string (JIRA issue key, e.g., "PROJ-123")                   │
│ title: string                                                    │
│ description: string (HTML or plain text)                         │
│ status: enum (DELIVERED | NOW | NEXT | FUTURE)                  │
│ module: string (e.g., "Flows", "Agents", "Integrations")        │
│ releaseYear: number (e.g., 2025)                                │
│ releaseQuarter: enum (Q1 | Q2 | Q3 | Q4)                        │
│ releaseMonth: number (1-12, optional)                           │
│ images: string[] (up to 4 URLs)                                 │
│ documentationUrl: string | null                                  │
│ lastSyncedAt: datetime                                          │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                          Module                                  │
├─────────────────────────────────────────────────────────────────┤
│ id: string (slug, e.g., "flows")                                │
│ name: string (display name, e.g., "Flows")                      │
│ itemCount: number (derived from RoadmapItems)                   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                        SyncMetadata                              │
├─────────────────────────────────────────────────────────────────┤
│ lastSyncAt: datetime                                            │
│ lastSyncStatus: enum (SUCCESS | PARTIAL | FAILED)               │
│ itemCount: number                                               │
│ errorMessage: string | null                                      │
└─────────────────────────────────────────────────────────────────┘
```

## Entities

### RoadmapItem

Represents a single roadmap entry derived from a JIRA Epic.

| Field | Type | Required | Description | Validation |
|-------|------|----------|-------------|------------|
| `id` | string | Yes | JIRA issue key (e.g., "PROJ-123") | Non-empty, matches pattern `[A-Z]+-\d+` |
| `title` | string | Yes | Epic summary/title | Non-empty, max 200 characters |
| `description` | string | Yes | Epic description for public display | Non-empty, max 5000 characters |
| `status` | enum | Yes | Delivery status | One of: DELIVERED, NOW, NEXT, FUTURE |
| `module` | string | Yes | Product module/area | Non-empty |
| `releaseYear` | number | Yes | Target release year | 2020-2030 |
| `releaseQuarter` | enum | Yes | Target release quarter | One of: Q1, Q2, Q3, Q4 |
| `releaseMonth` | number | No | Target release month | 1-12 |
| `images` | string[] | No | Image URLs for feature preview | 0-4 items, valid URLs |
| `documentationUrl` | string | No | Link to documentation | Valid URL or null |
| `lastSyncedAt` | datetime | Yes | When this item was last synced | ISO 8601 format |

### Module

Represents a product module/area for filtering.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | URL-safe slug |
| `name` | string | Yes | Display name |
| `itemCount` | number | Yes | Count of public items in this module |

### SyncMetadata

Tracks the synchronization status with JIRA.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `lastSyncAt` | datetime | Yes | When the last sync completed |
| `lastSyncStatus` | enum | Yes | SUCCESS, PARTIAL (some items failed), FAILED |
| `itemCount` | number | Yes | Total items in cache |
| `errorMessage` | string | No | Error details if sync failed |

## Enums

### DeliveryStatus

```
DELIVERED  - Feature has been released
NOW        - Feature is currently in progress
NEXT       - Feature is planned for near-term
FUTURE     - Feature is planned for longer-term
```

### Quarter

```
Q1  - January - March
Q2  - April - June
Q3  - July - September
Q4  - October - December
```

## JIRA Field Mapping

| RoadmapItem Field | JIRA Field | Notes |
|-------------------|------------|-------|
| `id` | `key` | Built-in JIRA field |
| `title` | `summary` | Built-in JIRA field |
| `description` | `description` | Built-in, convert from ADF to plain text/HTML |
| `status` | `customfield_XXXXX` | Custom select field "Roadmap Status" |
| `module` | `customfield_XXXXX` | Custom select field "Module/Product" |
| `releaseYear` | `customfield_XXXXX` | Custom number field "Release Year" |
| `releaseQuarter` | `customfield_XXXXX` | Custom select field "Release Quarter" |
| `releaseMonth` | `customfield_XXXXX` | Custom select field "Release Month" |
| `images` | `attachment` | Filter for image types, limit to 4 |
| `documentationUrl` | `customfield_XXXXX` | Custom URL field "Documentation Link" |

## Data Flow

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌──────────────┐
│   JIRA      │────▶│   Backend    │────▶│   Cache     │────▶│   Frontend   │
│   Cloud     │     │   (Sync)     │     │ (Redis/FS)  │     │   (Vue.js)   │
└─────────────┘     └──────────────┘     └─────────────┘     └──────────────┘
      │                    │                    │                    │
      │  Every 5 min       │                    │    API Request     │
      │◀───────────────────│                    │◀───────────────────│
      │                    │                    │                    │
      │  Return Epics      │  Transform &       │  Return JSON       │
      │───────────────────▶│  Validate          │───────────────────▶│
                           │───────────────────▶│
```

## Validation Rules

### RoadmapItem Validation

1. **Required Fields**: `id`, `title`, `description`, `status`, `module`, `releaseYear`, `releaseQuarter`
2. **Publication Gate**: Item is only included if:
   - "Public Roadmap" custom field is `true`
   - All required fields are present and valid
3. **Image Validation**:
   - Must be valid URL format
   - Must be image MIME type (jpeg, png, gif, webp)
   - Maximum 4 images per item
4. **Description Sanitization**:
   - Strip internal JIRA references
   - Convert ADF (Atlassian Document Format) to HTML or plain text
   - Limit to 5000 characters

### Field Allowlist (Security)

Only these JIRA fields are extracted during sync:

```python
ALLOWED_FIELDS = [
    "key",
    "summary",
    "description",
    "attachment",
    "customfield_XXXXX",  # Public Roadmap
    "customfield_XXXXX",  # Roadmap Status
    "customfield_XXXXX",  # Module/Product
    "customfield_XXXXX",  # Release Year
    "customfield_XXXXX",  # Release Quarter
    "customfield_XXXXX",  # Release Month
    "customfield_XXXXX",  # Documentation Link
]
```

All other fields are ignored and never stored or transmitted.

## Cache Structure

### Primary Cache Key Structure

```
roadmap:items                 → List of all RoadmapItems (JSON array)
roadmap:modules               → List of all Modules (JSON array)
roadmap:metadata              → SyncMetadata (JSON object)
roadmap:items:by_status:{status}   → Items filtered by status (optional optimization)
```

### Cache Expiration

- Items cache: Never expires (updated by sync job)
- Fallback file: Persisted to disk after each successful sync
- Stale indicator: If `lastSyncAt` > 10 minutes ago, frontend shows indicator

## State Transitions

### Item Status Transitions

```
           ┌──────────────────────────────────────────┐
           │                                          │
           ▼                                          │
        FUTURE ───────▶ NEXT ───────▶ NOW ───────▶ DELIVERED
           │              │            │              ▲
           │              │            │              │
           └──────────────┴────────────┴──────────────┘
                      (can skip stages)
```

Items can move forward or backward based on PM updates in JIRA.
