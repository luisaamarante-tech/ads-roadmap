# API Contracts - Epic Likes and Multi-Module Selection

This document outlines the expected API contracts for the Epic Likes and Multi-Module Selection features.

## Updated RoadmapItem Response

The `RoadmapItem` interface will include a new `likes` field:

```json
{
  "id": "NEXUS-123",
  "title": "Advanced Flow Builder",
  "description": "A new visual flow builder with drag-and-drop capabilities",
  "status": "NOW",
  "module": "Flows",
  "moduleId": "flows",
  "releaseYear": 2026,
  "releaseQuarter": "Q2",
  "releaseMonth": 6,
  "images": [
    "https://example.com/image1.png",
    "https://example.com/image2.png"
  ],
  "documentationUrl": "https://docs.example.com/flows",
  "likes": 42,
  "lastSyncedAt": "2026-01-20T10:30:00Z"
}
```

### New Field

- **`likes`** (integer, required): The number of likes this epic has received. Defaults to 0 if the JIRA custom field is not configured or empty.

## New Endpoint: Like an Epic

### Request

```
POST /api/v1/roadmap/items/{itemId}/like
```

**Path Parameters:**
- `itemId` (string, required): The JIRA issue key (e.g., "NEXUS-123")

**Request Body:** None (or empty JSON object `{}`)

**Headers:**
- `Content-Type: application/json`

### Response

**Success (200 OK):**

```json
{
  "id": "NEXUS-123",
  "likes": 43,
  "success": true
}
```

**Error (400 Bad Request):**

```json
{
  "error": "Invalid item ID",
  "success": false
}
```

**Error (404 Not Found):**

```json
{
  "error": "Roadmap item not found",
  "success": false
}
```

**Error (500 Internal Server Error):**

```json
{
  "error": "Failed to update like count in JIRA",
  "success": false
}
```

**Error (503 Service Unavailable):**

```json
{
  "error": "JIRA API is currently unavailable",
  "success": false
}
```

## Updated Endpoint: Get Roadmap Items with Multi-Module Filter

### Request

```
GET /api/v1/roadmap/items?status=NOW&year=2026&quarter=Q2&module=flows&module=integrations
```

**Query Parameters:**
- `status` (string, optional): Filter by delivery status (DELIVERED, NOW, NEXT, FUTURE)
- `year` (integer, optional): Filter by release year
- `quarter` (string, optional): Filter by release quarter (Q1, Q2, Q3, Q4)
- `module` (string, optional, **repeatable**): Filter by one or more module IDs. Can be specified multiple times for multi-select.

### Response

**Success (200 OK):**

```json
{
  "items": [
    {
      "id": "NEXUS-123",
      "title": "Advanced Flow Builder",
      "status": "NOW",
      "module": "Flows",
      "moduleId": "flows",
      "likes": 42,
      ...
    },
    {
      "id": "NEXUS-456",
      "title": "Webhook Integrations",
      "status": "NOW",
      "module": "Integrations",
      "moduleId": "integrations",
      "likes": 28,
      ...
    }
  ],
  "total": 2,
  "lastSyncedAt": "2026-01-20T10:30:00Z",
  "isStale": false
}
```

## Frontend Type Updates

### TypeScript Interface: RoadmapItem

```typescript
export interface RoadmapItem {
  id: string;
  title: string;
  description: string;
  status: DeliveryStatus;
  module: string;
  moduleId: string;
  releaseYear: number;
  releaseQuarter: Quarter;
  releaseMonth?: number | null;
  images: string[];
  documentationUrl?: string | null;
  likes: number; // NEW FIELD
  lastSyncedAt: string;
}
```

### TypeScript Interface: RoadmapFilters

```typescript
export interface RoadmapFilters {
  status?: DeliveryStatus;
  year?: number;
  quarter?: Quarter;
  module?: string | string[]; // UPDATED: Can now be a single string or array of strings
}
```

### TypeScript Interface: LikeResponse

```typescript
export interface LikeResponse {
  id: string;
  likes: number;
  success: boolean;
  error?: string;
}
```

## URL Query Parameter Format

When multiple modules are selected, the URL should encode them as repeated query parameters:

```
https://roadmap.example.com/?status=NOW&module=flows&module=integrations&module=analytics
```

This follows the standard URL encoding for array parameters and is compatible with most web frameworks and browsers.
