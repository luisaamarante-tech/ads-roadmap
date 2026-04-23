# Data Model: Roadmap Feature Request

**Feature**: [Roadmap Feature Request](./spec.md)  
**Branch**: `007-roadmap-feature-request`  
**Date**: 2026-01-21

## Entities

### 1) FeatureRequest

Represents a single feature request submission originating from the roadmap page.

**Fields**

- **idempotencyKey** (string, required): Client-provided key used to prevent duplicates.
- **moduleId** (string, required): URL-safe module identifier chosen by the user (matches roadmap module `id`).
- **moduleName** (string, optional): Display name for logging/notifications (when available).
- **title** (string, required): User-provided short summary (used to build the Jira issue summary).
- **description** (string, required): User-provided details and context.
- **contactEmail** (string, required): Email used for follow-up.
- **submittedAt** (timestamp, required): When the backend accepted the submission.
- **requestContext** (object, optional): Non-sensitive context for triage (e.g., page URL, app version).
- **clientMeta** (object, optional): Lightweight metadata (e.g., user agent, language). Avoid storing sensitive data.

**Validation rules**

- `moduleId`: must be a known, routable module (see `FeatureRequestRoutingRule`).
- `title`: trimmed, non-empty; enforce a max length to keep Jira summary readable.
- `description`: trimmed, non-empty; enforce a max length.
- `contactEmail`: must match a basic email format check.
- `idempotencyKey`: required; max length; treat as opaque.

---

### 2) FeatureRequestRoutingRule

Defines how a selected module maps to a Jira backlog destination.

**Fields**

- **moduleId** (string, required): Module identifier (slug).
- **jiraProjectKey** (string, required): Jira project key where the issue will be created.
- **jiraIssueTypeName** (string, optional): Issue type name to use (defaults to "Task").
- **labels** (list of string, optional): Optional labels to apply (e.g., `feature-request`).

**Source of truth**

- **Dynamically generated** by analyzing existing roadmap items in the cache.
- For each module, the system extracts the Jira project from the issue ID prefix.
- Example: Module "Agent Builder" with items "NEXUS-4130", "NEXUS-4306" → routes to NEXUS.
- This ensures new modules appear automatically without manual configuration.

---

### 3) JiraIssueReference

Represents the created Jira issue returned to the requester and used for Slack notifications.

**Fields**

- **key** (string, required): Jira issue key (e.g., `NEXUS-123`).
- **url** (string, optional): Human-friendly browse URL.
- **createdAt** (timestamp, required): When Jira confirmed creation.

---

### 4) SlackNotification

Represents an attempt to notify leaders about a new request.

**Fields**

- **channel** (string, required): `#weni-product-tech-squad-leaders`.
- **messageSummary** (string, required): Rendered human-readable summary.
- **status** (enum, required): `PENDING` | `SENT` | `FAILED`.
- **attemptCount** (integer, required)
- **lastAttemptAt** (timestamp, optional)
- **lastError** (string, optional)

**Storage**

- No database required. For reliability, pending/failed notifications can be retained short-term in cache for retry.

## State Transitions

1. **RECEIVED** → **VALIDATED**
2. **VALIDATED** → **JIRA_CREATED** (or **FAILED**)
3. **JIRA_CREATED** → **SLACK_SENT** (or **SLACK_FAILED** → retry → **SLACK_SENT** / **SLACK_FAILED**)

## Notes on Data Persistence

- The system does not need to persist FeatureRequests long-term to deliver value; the Jira issue is the system of record.
- Short-term cache persistence is required for idempotency and to support retrying Slack notifications without creating duplicate Jira issues.

