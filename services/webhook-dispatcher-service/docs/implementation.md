# webhook-dispatcher-service

## Service overview and purpose
A standalone service that dispatches outbound webhooks for platform events (e.g., project updates, media uploads, job status changes). It receives event payloads from the main app/orchestrators and delivers them to subscribed external URLs with signing, observability, and delivery logs.

## Technical requirements and dependencies
- Language: Python 3.11+
- Framework: FastAPI (HTTP control) with MCP tool exposure for orchestrators
- HTTP client: httpx with timeouts and per-target headers
- Signing: HMAC (SHA256) signature support via shared secret
- Queue (optional): Celery/Redis for large fan-outs (retries disabled by default per platform policy)
- Storage: Persist delivery logs to PayloadCMS collection (webhookDeliveries) or internal lightweight store

## API endpoints and interfaces
- HTTP:
  - POST `/dispatch` { event, payload, targets[], headers?, signatureKeyId? } → { dispatchId, results[] }
  - GET `/dispatch/{dispatchId}` → status and per-target results
  - GET `/health` → { ok: true }
- MCP tools:
  - `webhook.dispatch(event, payload, targets?, headers?)` → per-target results
- Headers & signing:
  - `X-Webhook-Event`, `X-Webhook-Timestamp`, `X-Webhook-Signature` (HMAC SHA256 over canonical string)

## Database schema (if applicable)
Initial phase can persist via CMS collection `webhookDeliveries`:
- { dispatchId, event, targets: [{ url, status, code, durationMs, error? }], createdAt }

## Integration points with the main PayloadCMS application
- Subscriptions stored in CMS (e.g., collection `webhookSubscriptions`)
- Main app/orchestrator posts events to this service
- Delivery logs written back to CMS for auditability

## Step-by-step implementation guide
1. Implement FastAPI `/dispatch` with validation and canonical signature builder
2. Implement httpx client with sane defaults (timeouts, redirects off)
3. If fan-out > N, enqueue Celery tasks (no automatic retries per platform policy)
4. Record results; write delivery logs to CMS collection
5. Expose MCP tool `webhook.dispatch` for internal orchestrations

## Testing strategy
- Unit: signature generation/verification, header building
- Integration: dispatch to a local mock receiver; validate headers and payload
- Error-path: DNS failure, TLS error, 4xx/5xx mapping to structured results

## Deployment considerations
- Stateless API; scale horizontally
- Secrets for HMAC keys via env vars; rotate via `signatureKeyId`
- No automatic retries; consider idempotency keys on caller side

