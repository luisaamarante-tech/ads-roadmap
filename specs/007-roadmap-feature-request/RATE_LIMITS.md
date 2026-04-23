# Rate Limiting Behavior: Feature Request API

## Current Rate Limits (Per IP Address)

| Endpoint | Limit | Window |
|----------|-------|--------|
| `POST /feature-requests` | 3 requests | per minute |
| `POST /feature-requests` | 10 requests | per hour |
| `GET /feature-request/modules` | 30 requests | per minute |

## What Happens When Limits Are Exceeded?

### Scenario 1: User submits 4th request in same minute

**Backend Response**:
```json
{
  "error": "RATE_LIMIT_EXCEEDED",
  "message": "Too many requests. Please wait and try again. Limits: 3 per minute, 10 per hour."
}
```
**HTTP Status**: `429 Too Many Requests`

**Frontend Display**:
```
Too many requests. You can submit up to 3 requests per minute and 10 per hour. 
Please wait and try again.
```

### Scenario 2: User submits 11th request in same hour

**Same as above** - 429 error with rate limit message.

### Scenario 3: User tries to bypass with duplicate clicks

**Backend Response** (via idempotency):
```json
{
  "success": true,
  "issueKey": "NEXUS-123",
  "issueUrl": "https://...",
  "leaderNotificationStatus": "SENT",
  "message": "Feature request submitted successfully"
}
```
**HTTP Status**: `200 OK` (cached response, no new Jira issue created)

The user sees success, but **no duplicate issue is created** - they get the same issue key from the first request.

## Additional Protection Layers

### 1. Form-Level Protection
- Submit button disabled during submission
- All inputs disabled during submission
- Shows "Submitting..." text
- Prevents accidental double-clicks

### 2. Idempotency (1 hour cache)
- Same `Idempotency-Key` returns cached response
- Prevents duplicates from:
  - Browser refresh + resubmit
  - Network retry
  - User clicking submit multiple times

### 3. Honeypot Field
- Hidden `website` field must be empty
- Bots that auto-fill forms get rejected immediately

### 4. Payload Size Limit
- Maximum 50KB per request
- Prevents memory exhaustion attacks

### 5. Input Sanitization
- Removes control characters
- Limits consecutive newlines
- Escapes special characters for Slack

## User Experience

**Normal user** (1-2 requests per session):
- ✅ Works perfectly
- ✅ Clear confirmation with Jira issue link
- ✅ Can retry if needed (idempotency protects against duplicates)

**Abusive user** (trying to spam):
- ⚠️ 4th request in a minute → Blocked with clear message
- ⚠️ 11th request in an hour → Blocked with clear message
- ⚠️ Must wait for rate limit window to reset

**Bot/scraper**:
- ❌ Honeypot field detection → Rejected silently
- ❌ Rate limits prevent mass submissions
- ❌ No way to bypass (IP-based tracking)

## Monitoring

Check backend logs for abuse patterns:
```bash
grep "Feature request rejected" backend.log
grep "RATE_LIMIT_EXCEEDED" backend.log
```
