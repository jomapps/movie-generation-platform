# analytics-service

## Service overview and purpose
Collects and aggregates platform events to produce actionable analytics: project progress, user behavior, AI performance, and resource usage. Provides summaries and simple dashboards data for the UI.

## Technical requirements and dependencies
- Language: Python 3.11+
- Framework: FastAPI + MCP tools for internal queries
- Storage (phase 1): Write raw events to PayloadCMS `analyticsEvents` collection; maintain rolled-up `analyticsSummaries`
- Optional (future): ClickHouse/TimescaleDB for high-volume timeseries

## API endpoints and interfaces
- HTTP:
  - POST `/events` { type, projectId?, sessionId?, userId?, timestamp?, metadata } → { id }
  - GET `/projects/{id}/summary` → { totals, charts }
  - GET `/metrics/ai-performance` → latency/quality aggregates
  - GET `/health` → { ok: true }
- MCP tools:
  - `analytics.record_event`
  - `analytics.get_project_summary`

## Database schema (if applicable)
- analyticsEvents: { type, projectId?, userId?, ts, metadata }
- analyticsSummaries: { projectId, period, metrics: { messages, executions, errors, durations } }

## Integration points with PayloadCMS
- UI/backend send events to `/events`
- Summaries updated periodically or on-demand and stored in CMS
- Data exposed to UI via CMS or directly from this service

## Step-by-step implementation guide
1. Define event schema and validation (Pydantic)
2. Implement `/events` ingestion with basic rate limiting
3. Implement summarization functions and `/projects/{id}/summary`
4. Add MCP tools for orchestrators to query analytics
5. Optimize storage and indexing; plan for external TSDB later

## Testing strategy
- Unit: aggregation logic; edge cases for empty data
- Integration: ingest → summarize → fetch summary
- Load: basic throughput test on `/events`

## Deployment considerations
- Stateless API; horizontal scaling
- Data retention policies; scheduled compaction jobs
- Privacy: avoid storing PII in raw events; use IDs only

