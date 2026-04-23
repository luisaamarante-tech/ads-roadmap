# Quickstart: Epic Likes and Multi-Module Selection

**Feature**: Epic Likes and Multi-Module Selection  
**Date**: 2026-01-20  
**For**: Developers implementing this feature

## Overview

This guide provides step-by-step instructions to set up, develop, and test the Epic Likes and Multi-Module Selection features. Follow these steps in order for the smoothest development experience.

## Prerequisites

### System Requirements

- Python 3.14+ (backend)
- Node.js 18+ (frontend)
- Git
- Access to JIRA with admin permissions (to create custom field)

### Repository Access

```bash
# Clone and navigate to repo
git clone git@github.com:weni-ai/weni-roadmap.git
cd weni-roadmap

# Checkout feature branch
git checkout 006-epic-likes-multi-select
```

### Environment Setup

**Backend**:

```bash
cd backend

# Create virtual environment
python3.14 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Configure JIRA credentials in .env
JIRA_BASE_URL=https://your-instance.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-api-token
```

**Frontend**:

```bash
cd frontend

# Install dependencies
npm install

# Copy environment template (if exists)
cp .env.example .env

# Configure API URL (optional, defaults to /api/v1)
VITE_API_URL=http://localhost:8000/api/v1
```

---

## JIRA Configuration

### Step 1: Create Custom Field

1. Log in to JIRA with admin permissions
2. Navigate to **Settings** → **Issues** → **Custom fields**
3. Click **Create custom field**
4. Select **Number** as field type
5. Name the field: `Roadmap Likes`
6. Add description: "Number of likes this epic has received on the public roadmap"
7. Configure field:
   - **Default value**: 0
   - **Allow negative values**: No
   - **Required**: No
8. Associate with screen(s) used by Epic issue type
9. Note the custom field ID (format: `customfield_XXXXX`)

### Step 2: Update Configuration

**Backend Configuration**:

Edit `backend/config/jira_projects.json` and add the `roadmap_likes` field for each project:

```json
{
  "version": "1.0",
  "projects": {
    "NEXUS": {
      "public_roadmap": "customfield_14699",
      "roadmap_status": "customfield_14698",
      "module": "customfield_14622",
      "release_year": "customfield_14623",
      "release_quarter": "customfield_14624",
      "release_month": "customfield_14625",
      "documentation_url": "customfield_14626",
      "roadmap_title": "customfield_14697",
      "roadmap_description": "customfield_14696",
      "roadmap_image_url_1": "customfield_14695",
      "roadmap_image_url_2": "customfield_14694",
      "roadmap_image_url_3": "customfield_14693",
      "roadmap_image_url_4": "customfield_14692",
      "roadmap_likes": "customfield_XXXXX"  // ADD THIS LINE with your field ID
    },
    // Repeat for EXPERI, ENGAGE, MDI, ENGINE, CLOUDW
  }
}
```

**Validate Configuration**:

```bash
cd backend

# Run validation script
python -m app.cli.jira_setup validate

# Expected output: "✓ All field mappings are valid"
```

---

## Development Setup

### Backend Development

**Run the backend server**:

```bash
cd backend
source venv/bin/activate  # If not already activated

# Run development server with auto-reload
uvicorn app:app --reload --host 0.0.0.0 --port 8000

# Expected output:
# INFO:     Uvicorn running on http://0.0.0.0:8000
# INFO:     Application startup complete.
```

**Run tests**:

```bash
# Run all tests with coverage
pytest --cov=app --cov-report=html --cov-report=term

# Run specific test file
pytest tests/unit/test_roadmap_model.py -v

# Run tests matching pattern
pytest -k "test_likes" -v
```

**Linting and formatting**:

```bash
# Format code with Black
black app/ tests/

# Check with Flake8
flake8 app/ tests/

# Type checking (if using mypy)
mypy app/
```

### Frontend Development

**Run the frontend dev server**:

```bash
cd frontend

# Start development server
npm run dev

# Expected output:
# VITE v4.x.x  ready in XXX ms
# ➜  Local:   http://localhost:5173/
# ➜  Network: use --host to expose
```

**Run tests**:

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage

# Run specific test file
npm test RoadmapCard.test.ts
```

**Linting and formatting**:

```bash
# Lint code
npm run lint

# Fix linting issues
npm run lint:fix

# Format code with Prettier
npm run format

# Check styles with Stylelint
npm run stylelint
```

---

## Implementation Workflow

### Phase 1: Backend - Like Count Retrieval

**Files to modify**:

1. **Update schema**: `backend/config/jira_projects.schema.json`

```json
{
  "required": [
    // ... existing fields ...
    "roadmap_likes"  // ADD THIS
  ],
  "properties": {
    // ... existing properties ...
    "roadmap_likes": {
      "type": "string",
      "pattern": "^customfield_\\d{5,}$",
      "description": "Custom field ID for storing like counts"
    }
  }
}
```

2. **Update data models**: `backend/app/models/custom_field.py`

```python
@dataclass
class ProjectFieldConfiguration:
    # ... existing fields ...
    roadmap_likes: str  # ADD THIS
```

3. **Update RoadmapItem**: `backend/app/models/roadmap.py`

```python
@dataclass
class RoadmapItem:
    # ... existing fields ...
    likes: int = 0  # ADD THIS with default value
    
    def to_dict(self) -> dict:
        return {
            # ... existing fields ...
            "likes": self.likes,  # ADD THIS
        }
```

4. **Update JIRA client**: `backend/app/services/jira_client.py`

```python
def _extract_roadmap_item(self, issue: dict, project_key: str) -> RoadmapItem:
    # ... existing extraction logic ...
    
    # Extract likes (NEW)
    likes_field = project_fields.get("roadmap_likes")
    likes = issue["fields"].get(likes_field, 0) or 0
    
    return RoadmapItem(
        # ... existing parameters ...
        likes=likes,  # ADD THIS
    )
```

**Test**:

```bash
# Run backend server
cd backend
uvicorn app:app --reload

# In another terminal, test retrieval
curl http://localhost:8000/api/v1/roadmap/items | jq '.[0].likes'
# Expected: 0 (or actual count if set in JIRA)
```

### Phase 2: Backend - Like Action Endpoint

**File to modify**: `backend/app/routes/roadmap.py`

```python
from typing import List
from fastapi import APIRouter, HTTPException, Query

@router.post("/items/{item_id}/like")
async def like_item(item_id: str) -> dict:
    """
    Increment the like count for a roadmap item.
    
    Args:
        item_id: JIRA issue key (e.g., "NEXUS-123")
        
    Returns:
        LikeResponse with updated count
    """
    try:
        # Get current item to verify it exists
        items = cache_service.get_all_items()
        item = next((i for i in items if i.id == item_id), None)
        
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        
        # Update likes in JIRA
        new_count = jira_client.update_epic_likes(item_id, item.likes + 1)
        
        # Invalidate cache to trigger re-sync
        cache_service.invalidate()
        
        return {
            "id": item_id,
            "likes": new_count,
            "success": True
        }
    except Exception as e:
        logger.error(f"Failed to like item {item_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

**Add JIRA update method**: `backend/app/services/jira_client.py`

```python
def update_epic_likes(self, issue_key: str, new_count: int) -> int:
    """
    Update the like count for an epic in JIRA.
    
    Args:
        issue_key: JIRA issue key (e.g., "NEXUS-123")
        new_count: New like count value
        
    Returns:
        Updated like count
    """
    # Get project key from issue key (e.g., "NEXUS" from "NEXUS-123")
    project_key = issue_key.split("-")[0]
    project_fields = self.config.get_project_custom_fields(project_key)
    
    if not project_fields or "roadmap_likes" not in project_fields:
        raise ValueError(f"roadmap_likes field not configured for project {project_key}")
    
    likes_field = project_fields["roadmap_likes"]
    
    # Update via JIRA API
    url = f"{self.base_url}/rest/api/3/issue/{issue_key}"
    payload = {
        "fields": {
            likes_field: new_count
        }
    }
    
    response = requests.put(
        url,
        headers=self._get_headers(),
        json=payload,
        timeout=10
    )
    
    if response.status_code != 204:
        raise Exception(f"JIRA API error: {response.status_code} - {response.text}")
    
    return new_count
```

**Test**:

```bash
# Test like endpoint
curl -X POST http://localhost:8000/api/v1/roadmap/items/NEXUS-123/like | jq
# Expected: { "id": "NEXUS-123", "likes": 1, "success": true }

# Verify in JIRA that the field was updated
```

### Phase 3: Backend - Multi-Module Filtering

**File to modify**: `backend/app/routes/roadmap.py`

```python
@router.get("/items")
async def get_items(
    status: Optional[str] = None,
    year: Optional[int] = None,
    quarter: Optional[str] = None,
    module: Optional[List[str]] = Query(None),  # UPDATED: Now accepts list
) -> dict:
    """Get roadmap items with optional filters."""
    items = cache_service.get_all_items()
    
    # Apply filters
    if status or year or quarter or module:
        items = [
            item for item in items
            if item.matches_filters(status, year, quarter, module)  # Pass module list
        ]
    
    return {
        "items": [item.to_dict() for item in items],
        "total": len(items),
        # ... metadata ...
    }
```

**Update filtering logic**: `backend/app/models/roadmap.py`

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
    # UPDATED: Check if module_id is in the list
    if module and self.module_id not in module:
        return False
    return True
```

**Test**:

```bash
# Test single module (backward compatible)
curl "http://localhost:8000/api/v1/roadmap/items?module=flows" | jq '.total'

# Test multiple modules
curl "http://localhost:8000/api/v1/roadmap/items?module=flows&module=integrations" | jq '.total'
```

### Phase 4: Frontend - Like Button UI

**File to modify**: `frontend/src/types/roadmap.ts`

```typescript
export interface RoadmapItem {
  // ... existing fields ...
  likes: number;  // ADD THIS
}

export interface LikeResponse {  // ADD THIS
  id: string;
  likes: number;
  success: boolean;
  error?: string;
}
```

**File to modify**: `frontend/src/services/roadmapService.ts`

```typescript
export async function likeEpic(itemId: string): Promise<LikeResponse> {
  const response = await api.post<LikeResponse>(
    `/roadmap/items/${itemId}/like`
  );
  return response.data;
}
```

**File to modify**: `frontend/src/components/RoadmapCard.vue`

```vue
<script setup lang="ts">
import { ref } from 'vue';
import type { RoadmapItem } from '@/types/roadmap';
import { likeEpic } from '@/services/roadmapService';

interface Props {
  item: RoadmapItem;
}

const props = defineProps<Props>();
const emit = defineEmits<{
  'like-updated': [itemId: string, newCount: number];
}>();

const localLikes = ref(props.item.likes);
const likePending = ref(false);
const likeError = ref<string | null>(null);

async function onLikeClick(event: Event): Promise<void> {
  event.stopPropagation();
  
  if (likePending.value) return;
  
  likePending.value = true;
  likeError.value = null;
  
  // Optimistic update
  const previousCount = localLikes.value;
  localLikes.value++;
  
  try {
    const response = await likeEpic(props.item.id);
    localLikes.value = response.likes;  // Reconcile with server
    emit('like-updated', props.item.id, response.likes);
  } catch (error) {
    // Rollback on error
    localLikes.value = previousCount;
    likeError.value = 'Failed to like epic. Please try again.';
    console.error('Like error:', error);
  } finally {
    likePending.value = false;
  }
}
</script>

<template>
  <article class="roadmap-card">
    <!-- Existing card header -->
    <header class="roadmap-card__header">
      <!-- ... existing content ... -->
      
      <!-- Like button (NEW) -->
      <button
        class="roadmap-card__like-btn"
        :disabled="likePending"
        :aria-label="`Like this epic (${localLikes} likes)`"
        @click="onLikeClick"
      >
        <svg class="roadmap-card__like-icon" width="20" height="20" viewBox="0 0 20 20">
          <path d="M10 17.5l-1.5-1.35C4.4 12.36 2 10.28 2 7.5 2 5.5 3.5 4 5.5 4c1.54 0 3.04.99 3.57 2.36h1.87C11.46 4.99 12.96 4 14.5 4 16.5 4 18 5.5 18 7.5c0 2.78-2.4 4.86-6.5 8.65L10 17.5z" />
        </svg>
        <span class="roadmap-card__like-count">{{ localLikes }}</span>
      </button>
    </header>
    
    <!-- Error message -->
    <div v-if="likeError" class="roadmap-card__error">
      {{ likeError }}
    </div>
    
    <!-- ... rest of card content ... -->
  </article>
</template>

<style scoped>
.roadmap-card__like-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  background: var(--unnnic-color-background-snow, #fff);
  border: 1px solid var(--unnnic-color-neutral-soft, #e8e8e8);
  border-radius: var(--unnnic-border-radius-sm, 6px);
  cursor: pointer;
  transition: all 0.2s ease;
}

.roadmap-card__like-btn:hover:not(:disabled) {
  border-color: var(--unnnic-color-weni-600, #00a8a8);
  background: rgb(0 168 168 / 5%);
}

.roadmap-card__like-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.roadmap-card__like-icon {
  fill: var(--unnnic-color-neutral-cloudy, #67738b);
}

.roadmap-card__like-btn:hover:not(:disabled) .roadmap-card__like-icon {
  fill: var(--unnnic-color-weni-600, #00a8a8);
}

.roadmap-card__like-count {
  font-size: var(--unnnic-font-size-body-sm, 12px);
  font-weight: var(--unnnic-font-weight-medium, 500);
  color: var(--unnnic-color-neutral-dark, #4a4a4a);
}

.roadmap-card__error {
  margin-top: 8px;
  padding: 8px;
  background: rgb(255 0 0 / 10%);
  border-radius: 4px;
  color: var(--unnnic-color-feedback-red, #d32f2f);
  font-size: 12px;
}
</style>
```

**Test in browser**:

```bash
# Start frontend dev server
cd frontend
npm run dev

# Open http://localhost:5173
# Click a like button and verify:
# 1. Count increments immediately (optimistic)
# 2. Network request shows in DevTools
# 3. Count reconciles with server response
```

### Phase 5: Frontend - Multi-Select Filter

**File to modify**: `frontend/src/types/roadmap.ts`

```typescript
export interface RoadmapFilters {
  status?: DeliveryStatus;
  year?: number;
  quarter?: Quarter;
  module?: string | string[];  // UPDATED: Can be array
}
```

**File to modify**: `frontend/src/components/RoadmapFilters.vue`

```vue
<script setup lang="ts">
import { computed } from 'vue';
import type { Module, RoadmapFilters } from '@/types/roadmap';

interface Props {
  modelValue: RoadmapFilters;
  modules: Module[];
}

const props = defineProps<Props>();
const emit = defineEmits<{
  'update:modelValue': [value: RoadmapFilters];
}>();

const selectedModules = computed({
  get: () => {
    const module = props.modelValue.module;
    if (!module) return [];
    return Array.isArray(module) ? module : [module];
  },
  set: (value: string[]) => {
    emit('update:modelValue', {
      ...props.modelValue,
      module: value.length === 0 ? undefined : value,
    });
  },
});

function onModuleToggle(moduleId: string): void {
  const current = new Set(selectedModules.value);
  if (current.has(moduleId)) {
    current.delete(moduleId);
  } else {
    current.add(moduleId);
  }
  selectedModules.value = Array.from(current);
}
</script>

<template>
  <div class="filters">
    <!-- ... existing year and quarter filters ... -->
    
    <!-- Multi-select module filter (UPDATED) -->
    <div class="filters__group">
      <span class="filters__label">Modules</span>
      <div class="filters__module-list">
        <label
          v-for="mod in modules"
          :key="mod.id"
          class="filters__module-option"
        >
          <input
            type="checkbox"
            :checked="selectedModules.includes(mod.id)"
            @change="onModuleToggle(mod.id)"
          />
          <span>{{ mod.name }} ({{ mod.itemCount }})</span>
        </label>
      </div>
    </div>
  </div>
</template>

<style scoped>
.filters__module-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.filters__module-option {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.filters__module-option input[type="checkbox"] {
  cursor: pointer;
}
</style>
```

**Test in browser**:

```bash
# 1. Select multiple modules
# 2. Verify URL updates: ?module=flows&module=integrations
# 3. Verify filtered items display
# 4. Deselect a module and verify update
# 5. Share URL with friend and verify they see same filters
```

---

## Testing Checklist

### Backend Tests

- [ ] `test_roadmap_model.py`: Test `RoadmapItem` includes `likes` field
- [ ] `test_roadmap_model.py`: Test `to_dict()` serializes `likes`
- [ ] `test_roadmap_model.py`: Test `matches_filters` with module list
- [ ] `test_jira_client.py`: Test likes extraction from JIRA
- [ ] `test_jira_client.py`: Test `update_epic_likes` method
- [ ] `test_jira_client.py`: Test missing likes field defaults to 0
- [ ] `test_roadmap_routes.py`: Test `POST /items/{id}/like` success
- [ ] `test_roadmap_routes.py`: Test like endpoint with invalid ID
- [ ] `test_roadmap_routes.py`: Test multi-module filtering
- [ ] `test_sync_service.py`: Test sync includes likes

### Frontend Tests

- [ ] `RoadmapCard.test.ts`: Test like button renders
- [ ] `RoadmapCard.test.ts`: Test like button click increments count
- [ ] `RoadmapCard.test.ts`: Test like button shows loading state
- [ ] `RoadmapCard.test.ts`: Test like button error handling
- [ ] `RoadmapFilters.test.ts`: Test module multi-select renders
- [ ] `RoadmapFilters.test.ts`: Test selecting multiple modules
- [ ] `RoadmapFilters.test.ts`: Test deselecting modules
- [ ] `roadmapService.test.ts`: Test `likeEpic` API call

### Integration Tests

- [ ] End-to-end: Like an epic and verify JIRA field updates
- [ ] End-to-end: Filter by multiple modules and verify results
- [ ] End-to-end: Share multi-module URL and verify recipient sees same view

---

## Troubleshooting

### "Field not configured" error

**Symptom**: API returns 400 error when liking an epic

**Solution**:
1. Verify `roadmap_likes` field exists in `jira_projects.json` for the project
2. Verify custom field ID is correct in JIRA
3. Run `python -m app.cli.jira_setup validate` to check configuration

### Likes not syncing from JIRA

**Symptom**: Like count always shows 0

**Solution**:
1. Check JIRA field has a value set
2. Verify field ID in configuration matches JIRA
3. Check backend logs for sync errors
4. Manually trigger sync: `curl http://localhost:8000/api/v1/roadmap/sync`

### Multi-select not filtering correctly

**Symptom**: Selecting modules shows no results or wrong results

**Solution**:
1. Check browser console for JavaScript errors
2. Verify URL parameters are formatted correctly: `?module=flows&module=integrations`
3. Check backend logs to see what filters were received
4. Verify module IDs match those returned by `/api/v1/roadmap/modules`

---

## Deployment

### Production Checklist

- [ ] All tests passing (80%+ coverage)
- [ ] Linters pass (Black, Flake8, ESLint, Prettier)
- [ ] "Roadmap Likes" custom field created in all JIRA projects
- [ ] `jira_projects.json` updated with all field IDs
- [ ] Environment variables set in production (Render, Netlify)
- [ ] Smoke test: Like an epic and verify in JIRA
- [ ] Smoke test: Filter by multiple modules
- [ ] Documentation updated (if applicable)

### Rollback Plan

If issues arise in production:

1. **Frontend**: Revert feature flag or redeploy previous version
2. **Backend**: Remove `/like` endpoint or return 503
3. **JIRA fields**: No action needed (data preserved for future retry)

---

## Next Steps

After completing this quickstart:

1. Review [tasks.md](./tasks.md) for detailed implementation tasks
2. Create PR with incremental changes (don't implement everything at once)
3. Request code review from team
4. Deploy to staging environment for QA testing
5. Monitor production metrics after deployment

## Support

- Slack: #weni-roadmap-dev
- Documentation: See `/docs` directory
- Constitution: `.specify/memory/constitution.md`
