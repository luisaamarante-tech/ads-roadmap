# Research: Roadmap Feature Request

**Feature**: [Roadmap Feature Request](./spec.md)  
**Branch**: `007-roadmap-feature-request`  
**Date**: 2026-01-21

## Summary of Technical Decisions

This feature adds a public write path (feature requests) to an otherwise read-only roadmap API. The main risks are abuse/spam and safe handling of external integrations (Jira + Slack).

## Decisions

### 1) Jira issue creation format (description)

**Decision**: Create the Jira issue via Jira Cloud REST API v3 and send the issue `description` using Atlassian Document Format (ADF).

**Rationale**:
- The backend already uses Jira REST API v3 endpoints and parses ADF for roadmap epic descriptions.
- ADF is the most compatible way to provide rich text and structured content in modern Jira Cloud.

**Alternatives considered**:
- Send a plain string description: may be rejected or inconsistently rendered depending on Jira API version and instance settings.
- Use Jira REST API v2 for simpler string fields: would introduce mixed API versions in the same client and additional maintenance.

---

### 2) Module → Jira backlog routing source of truth

**Decision**: Add a dedicated routing configuration file to map Roadmap Module (by `moduleId`) to a Jira destination (at minimum Jira `projectKey`, optionally issue type name).

**Rationale**:
- The current roadmap “modules” are derived from Jira data and do not reliably imply which Jira project/board should receive new issues.
- A configuration-based mapping is explicit, auditable, and avoids incorrect routing in production.

**Alternatives considered**:
- Infer routing from existing roadmap items (e.g., pick the most frequent project key for a module): error-prone and changes over time.
- Free-text module input: would produce inconsistent data and unpredictable routing.

---

### 3) Slack notification mechanism

**Decision**: Send Slack notifications using an Incoming Webhook configured for the `#weni-product-tech-squad-leaders` channel.

**Rationale**:
- Lowest operational complexity and least privilege (no full bot token required).
- Fits the use case: a single channel notification with a predictable message format.

**Alternatives considered**:
- Slack Web API (`chat.postMessage`) with a bot token: more setup and permissions; useful if later we need interactive workflows.

---

### 4) Idempotency and duplicate prevention

**Decision**: Support an `Idempotency-Key` request header and use the existing caching layer to prevent duplicate issue creation on retries/double-submits.

**Rationale**:
- Public web submissions frequently retry (network issues, double click).
- Cache-backed idempotency is consistent with the existing architecture (no database).

**Alternatives considered**:
- Rely only on UI disabling the submit button: insufficient and not robust against refresh/retry.
- Hash-based dedupe only (payload hash): can block legitimate repeated requests and is hard to tune without user-facing ids.

---

### 5) Abuse prevention for a public write endpoint

**Decision**: Apply strict rate limits on the feature-request endpoint and add a lightweight bot mitigation (honeypot field). Keep room to add CAPTCHA later if needed.

**Rationale**:
- Creating Jira issues is a high-impact action; abuse would spam product backlogs and Slack.
- A rate limiter is already present as a dependency; honeypot is low-effort and effective against basic bots.

**Alternatives considered**:
- Require authentication: would block legitimate public users and adds user management scope.
- CAPTCHA immediately: increases UX friction and requires third-party configuration.

---

### 6) Slack failure handling

**Decision**: Do not fail the user submission when Jira issue creation succeeds but Slack notification fails. Attempt limited retries and record failures for follow-up and/or background retry.

**Rationale**:
- User value is the created Jira issue; Slack is a notification side-effect.
- The spec explicitly calls out this edge case; we should preserve “success” for the requester while still ensuring leaders get notified eventually.

**Alternatives considered**:
- Treat Slack as mandatory and return an error: creates confusing UX and encourages resubmission duplicates.

