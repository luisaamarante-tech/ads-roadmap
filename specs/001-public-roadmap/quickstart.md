# Quickstart: Weni Public Roadmap

**Feature Branch**: `001-public-roadmap`
**Date**: December 22, 2025

## Prerequisites

### JIRA Setup (One-time)

1. **Create custom fields in JIRA** for your project:
   - `Public Roadmap` (Checkbox) - Flag to show on public roadmap
   - `Roadmap Status` (Select: Delivered/Now/Next/Future) - Status tab placement
   - `Release Year` (Number) - Target year
   - `Release Quarter` (Select: Q1/Q2/Q3/Q4) - Target quarter
   - `Release Month` (Select: 1-12) - Target month (optional)
   - `Module/Product` (Select) - Product area
   - `Documentation Link` (URL) - Link for "Read More"

2. **Create a JIRA API token**:
   - Go to https://id.atlassian.com/manage-profile/security/api-tokens
   - Create a new API token for the service account

3. **Note the custom field IDs**:
   - Go to JIRA Admin → Issues → Custom Fields
   - Copy the field IDs (e.g., `customfield_10001`)

### Development Environment

- Python 3.11+
- Node.js 18+
- Redis (optional, for caching)

---

## Backend Setup

### 1. Create project structure

```bash
mkdir -p weni-roadmap-backend/{app,tests}
cd weni-roadmap-backend
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
```

### 3. Install dependencies

```bash
pip install flask flask-cors flask-caching flask-limiter apscheduler requests python-dotenv gunicorn
pip freeze > requirements.txt
```

### 4. Create `.env` file

```bash
cat > .env << 'EOF'
# JIRA Configuration
JIRA_BASE_URL=https://your-domain.atlassian.net
JIRA_EMAIL=service-account@company.com
JIRA_API_TOKEN=your-api-token
JIRA_PROJECT_KEY=PROJ

# Custom Field IDs (update with your actual IDs)
JIRA_FIELD_PUBLIC_ROADMAP=customfield_10001
JIRA_FIELD_ROADMAP_STATUS=customfield_10002
JIRA_FIELD_MODULE=customfield_10003
JIRA_FIELD_RELEASE_YEAR=customfield_10004
JIRA_FIELD_RELEASE_QUARTER=customfield_10005
JIRA_FIELD_RELEASE_MONTH=customfield_10006
JIRA_FIELD_DOCUMENTATION_URL=customfield_10007

# Sync Configuration
SYNC_INTERVAL_MINUTES=5

# Cache Configuration
CACHE_TYPE=simple  # Use 'redis' in production
REDIS_URL=redis://localhost:6379/0

# CORS
ALLOWED_ORIGINS=http://localhost:8080,http://localhost:3000

# Rate Limiting
RATE_LIMIT=100 per minute
EOF
```

### 5. Create basic Flask app

```python
# app/__init__.py
from flask import Flask
from flask_cors import CORS
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

cache = Cache()
limiter = Limiter(key_func=get_remote_address)

def create_app():
    app = Flask(__name__)

    # Configuration
    app.config.from_prefixed_env()

    # Initialize extensions
    CORS(app, origins=app.config.get('ALLOWED_ORIGINS', '*').split(','))
    cache.init_app(app, config={'CACHE_TYPE': app.config.get('CACHE_TYPE', 'simple')})
    limiter.init_app(app)

    # Register blueprints
    from app.routes import roadmap_bp, health_bp
    app.register_blueprint(roadmap_bp, url_prefix='/api/v1/roadmap')
    app.register_blueprint(health_bp, url_prefix='/api/v1')

    return app
```

### 6. Run the backend

```bash
flask run --port 5000
```

---

## Frontend Setup

### 1. Create Vue.js project

```bash
npm create vue@latest weni-roadmap-frontend
cd weni-roadmap-frontend
```

Select options:
- TypeScript: Yes
- Vue Router: Yes (for /roadmap route)
- Pinia: No (not needed for this simple page)

### 2. Install Unnnic (Weni Design System)

```bash
npm install @weni/unnnic-system
```

### 3. Configure Unnnic in main.ts

```typescript
// src/main.ts
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import Unnnic from '@weni/unnnic-system'
import '@weni/unnnic-system/dist/style.css'

const app = createApp(App)
app.use(router)
app.use(Unnnic)
app.mount('#app')
```

### 4. Create roadmap service

```typescript
// src/services/roadmapService.ts
import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:5000/api/v1'

export interface RoadmapItem {
  id: string
  title: string
  description: string
  status: 'DELIVERED' | 'NOW' | 'NEXT' | 'FUTURE'
  module: string
  moduleId: string
  releaseYear: number
  releaseQuarter: 'Q1' | 'Q2' | 'Q3' | 'Q4'
  releaseMonth?: number
  images: string[]
  documentationUrl?: string
}

export interface RoadmapFilters {
  status?: string
  year?: number
  quarter?: string
  module?: string
}

export async function getRoadmapItems(filters: RoadmapFilters = {}) {
  const { data } = await axios.get(`${API_BASE}/roadmap/items`, { params: filters })
  return data
}

export async function getModules() {
  const { data } = await axios.get(`${API_BASE}/roadmap/modules`)
  return data.modules
}

export async function getStats(filters: RoadmapFilters = {}) {
  const { data } = await axios.get(`${API_BASE}/roadmap/stats`, { params: filters })
  return data
}
```

### 5. Create environment file

```bash
# .env.development
VITE_API_URL=http://localhost:5000/api/v1
```

### 6. Run the frontend

```bash
npm run dev
```

---

## Quick Test

### 1. Test backend health

```bash
curl http://localhost:5000/api/v1/health
```

Expected response:
```json
{
  "status": "healthy",
  "lastSyncAt": null,
  "lastSyncStatus": null,
  "itemCount": 0
}
```

### 2. Trigger manual sync (dev only)

```bash
curl -X POST http://localhost:5000/api/v1/admin/sync
```

### 3. Fetch roadmap items

```bash
curl http://localhost:5000/api/v1/roadmap/items?status=DELIVERED
```

---

## Key Files Reference

### Backend Structure

```
weni-roadmap-backend/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── routes.py             # API routes
│   ├── services/
│   │   ├── jira_service.py   # JIRA API client
│   │   └── sync_service.py   # Data sync logic
│   └── models.py             # Data classes
├── tests/
│   ├── test_routes.py
│   └── test_sync.py
├── .env
├── requirements.txt
└── run.py
```

### Frontend Structure

```
weni-roadmap-frontend/
├── src/
│   ├── components/
│   │   ├── RoadmapTabs.vue       # Status tabs
│   │   ├── RoadmapFilters.vue    # Year/Quarter/Module filters
│   │   ├── RoadmapCard.vue       # Expandable item card
│   │   └── RoadmapImageGallery.vue
│   ├── views/
│   │   └── RoadmapView.vue       # Main roadmap page
│   ├── services/
│   │   └── roadmapService.ts     # API client
│   ├── App.vue
│   └── main.ts
├── .env.development
└── package.json
```

---

## Common Issues

### CORS Errors

Ensure `ALLOWED_ORIGINS` in backend `.env` includes your frontend URL.

### JIRA Authentication Fails

1. Verify API token is correct
2. Ensure service account email matches
3. Check project permissions

### Custom Fields Not Found

1. Verify field IDs in JIRA Admin → Custom Fields
2. Ensure fields are added to your project's screen scheme

### No Items Showing

1. Check that epics have `Public Roadmap` checkbox enabled
2. Verify all required fields are filled
3. Check backend logs for validation errors

---

## Next Steps

1. **Customize styling**: Adjust Unnnic component props to match design
2. **Add image handling**: Set up image proxy for JIRA attachments
3. **Configure caching**: Switch to Redis for production
4. **Set up monitoring**: Add logging and health checks
5. **Deploy**: Containerize and deploy to your infrastructure
