# Quickstart: Roadmap Feature Request

**Feature Branch**: `007-roadmap-feature-request`  
**Date**: 2026-01-21

## Goal

Enable users to submit feature requests from the roadmap page, which will:

- Create a Jira issue with the `[FEATURE-REQUEST]` prefix
- Notify leaders in Slack (`#weni-product-tech-squad-leaders`)

## Prerequisites

- Jira credentials configured for the backend (existing roadmap sync already requires these)
- A Slack Incoming Webhook configured to post to `#weni-product-tech-squad-leaders`

## Backend Configuration

### Environment variables

Add/confirm the following environment variables for the backend container/process:

- `JIRA_BASE_URL`
- `JIRA_EMAIL`
- `JIRA_API_TOKEN`
- `SLACK_FEATURE_REQUEST_WEBHOOK_URL` (new)

### Module routing (automatic)

**No manual configuration needed!** Module routing is **fully dynamic**:

- The system analyzes existing roadmap items in the cache
- For each module (e.g., "Agent Builder", "Human Support"), it extracts the Jira project from issue IDs
- Example: Module "Agent Builder" has items like "NEXUS-4130" → routes to NEXUS project
- New modules added to Jira appear automatically without config changes

The routing logic is in `backend/app/services/feature_request_routing_loader.py` and rebuilds on each request using cached roadmap data.

## Running locally

### Docker Compose

1. Export required environment variables (including `SLACK_FEATURE_REQUEST_WEBHOOK_URL`)
2. Start services:

```bash
docker-compose up --build
```

### Smoke test

- Open the frontend roadmap page.
- Click **Request Feature**.
- Submit a request with a routable Module.
- Confirm:
  - A Jira issue is created with `[FEATURE-REQUEST]` prefix.
  - A message is posted to `#weni-product-tech-squad-leaders`.

