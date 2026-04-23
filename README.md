# VTEX Ads Public Roadmap

A public-facing roadmap page for VTEX Ads customers and stakeholders, displaying upcoming and delivered features synchronized from JIRA Epics.

## Overview

- **Frontend**: Vue.js 3 with TypeScript and Weni Design System (Unnnic)
- **Backend**: Flask with Python 3.11
- **Data Source**: JIRA Cloud API (VTEX Ads project key: `VA`)
- **Hosting**: Vercel (frontend static + backend serverless functions + Cron Jobs for sync)

## Features

- View roadmap items by delivery status (Delivered, Now, Next, Future)
- Filter by year, quarter, and module/product
- Expandable cards with full descriptions and images
- Documentation links for each feature
- Responsive design for all devices
- Automatic sync with JIRA via Vercel Cron Jobs (every 30 min)
- Fallback cache for JIRA outages

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose (optional)

### Local Development

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your JIRA credentials

# Run development server
flask run --port 5000
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Copy environment template
cp .env.example .env

# Run development server
npm run dev
```

The frontend will be available at http://localhost:5173 and will proxy API requests to the backend at http://localhost:5000.

## Vercel Deployment

This project is configured for Vercel with:
- **Frontend**: Static site built from `frontend/` (Vite/Vue)
- **Backend**: Python serverless functions via `api/index.py`
- **Sync**: Vercel Cron Job calling `POST /api/v1/sync` every 30 minutes

### Deploy Steps

1. **Push to GitHub** — connect the repository to Vercel

2. **Set Environment Variables** in Vercel dashboard (`Settings → Environment Variables`):

   | Variable | Required | Description |
   |----------|----------|-------------|
   | `JIRA_BASE_URL` | ✅ | `https://your-domain.atlassian.net` |
   | `JIRA_EMAIL` | ✅ | Service account email |
   | `JIRA_API_TOKEN` | ✅ | JIRA API token (mark as secret) |
   | `REDIS_URL` | ✅ | Upstash or Vercel KV Redis URL |
   | `CACHE_TYPE` | ✅ | `redis` |
   | `CRON_SECRET` | ✅ | Random secret to protect `/api/v1/sync` |
   | `ENABLE_SCHEDULER` | ✅ | `false` (Vercel uses Cron Jobs instead) |
   | `SLACK_FEATURE_REQUEST_WEBHOOK_URL` | — | Optional Slack webhook |

3. **Redis**: Create a free Upstash Redis instance at https://upstash.com and copy the `REDIS_URL`

4. **Deploy** — Vercel will build frontend (`npm run build`) and deploy the Python function

5. **Verify** — check `https://your-app.vercel.app/api/v1/health`

### Cron Job

The `vercel.json` configures a cron job at `*/30 * * * *` (every 30 minutes) calling `POST /api/v1/sync`. Vercel automatically sends `Authorization: Bearer <CRON_SECRET>` — no additional configuration needed.

> **Note**: Vercel Hobby plan supports 1 cron job with a minimum interval of 1 day. For 30-minute syncs you need the **Pro plan**. Alternatively, use a free external cron service like [cron-job.org](https://cron-job.org) to call the sync endpoint.

## JIRA Configuration

The backend synchronizes from JIRA project `VA` (VTEX Ads). Custom field mappings are stored in `backend/config/jira_projects.json`.

### Authentication Setup

Configure these environment variables in `backend/.env`:

| Variable | Example |
|----------|---------|
| `JIRA_BASE_URL` | `https://your-domain.atlassian.net` |
| `JIRA_EMAIL` | `roadmap-sync@vtex.com` |
| `JIRA_API_TOKEN` | `ATATT3xFf...` |

#### Obtaining a JIRA API Token

1. Log in to your Atlassian account
2. Navigate to **Security → API tokens**: https://id.atlassian.com/manage-profile/security/api-tokens
3. Click **Create API token**
4. Name the token (e.g., "VTEX Ads Roadmap Sync")
5. **Copy the token immediately** (you won't be able to view it again)

### Custom Field Requirements

14 custom fields required on JIRA Epics:

| Field Attribute | JIRA Field Type | Required |
|----------------|----------------|----------|
| `public_roadmap` | Checkbox | **Yes** |
| `roadmap_status` | Select List (Single) | **Yes** |
| `module` | Select List (Single) | **Yes** |
| `release_year` | Number | **Yes** |
| `release_quarter` | Select List (Single) | **Yes** |
| `release_month` | Number | **Yes** |
| `documentation_url` | URL | **Yes** |
| `roadmap_title` | Text (255 chars) | **Yes** |
| `roadmap_description` | Paragraph (Rich Text) | **Yes** |
| `roadmap_likes` | Number | **Yes** |
| `roadmap_image_url_1-4` | URL | No |

### Field Mapping with CLI

```bash
cd backend

# List available custom fields
flask jira list-fields VA

# Interactively map fields
flask jira map-fields VA

# Validate configuration
flask jira validate-config VA

# Test sync
flask sync run --once
```

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/v1/health` | Service health check |
| `POST /api/v1/sync` | Trigger JIRA sync (requires `Authorization: Bearer <CRON_SECRET>`) |
| `GET /api/v1/roadmap/items` | List items with filters |
| `GET /api/v1/roadmap/items/{id}` | Get single item |
| `GET /api/v1/roadmap/modules` | List available modules |
| `GET /api/v1/roadmap/stats` | Get item counts by status |

### Query Parameters for `/roadmap/items`

- `status`: DELIVERED, NOW, NEXT, or FUTURE
- `year`: Filter by release year (e.g., 2025)
- `quarter`: Filter by quarter (Q1, Q2, Q3, Q4)
- `module`: Filter by module ID (slug)

## Project Structure

```
vtex-ads-roadmap/
├── api/
│   └── index.py            # Vercel Python function entry point
├── backend/
│   ├── app/
│   │   ├── models/         # Data models (RoadmapItem, Module)
│   │   ├── routes/         # API endpoints (health + sync, roadmap)
│   │   └── services/       # JIRA client, sync, cache
│   ├── config/
│   │   └── jira_projects.json  # JIRA custom field mappings for VA project
│   ├── requirements.txt
│   └── run.py
├── frontend/
│   ├── src/
│   │   ├── components/     # Vue components
│   │   ├── views/          # Page components
│   │   ├── services/       # API client
│   │   └── types/          # TypeScript types
│   ├── .env.example
│   ├── .env.production     # Vercel production: VITE_API_BASE_URL=/api
│   └── package.json
├── vercel.json             # Vercel build + routes + cron config
├── requirements.txt        # Root-level (points to backend/requirements.txt)
└── README.md
```

## Development

### Running Tests

```bash
# Backend (requires 80% coverage)
cd backend
pytest --cov=app --cov-report=term-missing

# Frontend
cd frontend
npm run test:coverage
```

### Linting & Formatting

```bash
# Backend
cd backend
black app/ tests/
isort app/ tests/
flake8 app/ tests/

# Frontend
cd frontend
npm run lint
npm run format
```

## Security

- **No authentication required** for public roadmap access
- JIRA credentials are **server-side only** (never exposed to frontend)
- Only fields marked as public are synced (allowlist-based extraction)
- Rate limiting: 100 requests/minute per IP
- Sync endpoint protected by `CRON_SECRET`
- CORS configured for allowed origins only

## Contributing

1. Create a feature branch from `develop`
2. Make changes following the code quality standards
3. Ensure all tests pass with 80%+ coverage
4. Submit a PR with conventional commit messages

## License

Copyright © 2024 VTEX. All rights reserved.
