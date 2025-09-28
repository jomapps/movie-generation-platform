# mcp-script-service

## Service overview and purpose
An MCP server that generates screenplay artifacts: loglines, outlines, beat sheets, and scene dialog. It consumes project briefs and constraints to produce structured script outputs for downstream production.

## Technical requirements and dependencies
- Language: Python 3.11+
- Framework: FastAPI + MCP adapter
- LLM providers: OpenRouter models per seeded list
- Storage: PayloadCMS (Projects, Sessions, Documents/Media where applicable)
- Optional: Celery/Redis for long generations

## API endpoints and interfaces
- HTTP:
  - POST `/scripts/logline` { projectId, premise } → { logline }
  - POST `/scripts/outline` { projectId, acts?, tone, constraints } → { outline }
  - POST `/scripts/scene` { projectId, sceneId, synopsis } → { slugline, action, dialog[] }
  - GET `/health` → { ok: true }
- MCP tools:
  - `script.generate_logline`
  - `script.generate_outline`
  - `script.generate_scene`

## Database schema (if applicable)
Leverage PayloadCMS collections; store outputs in a `documents`/`scripts` area or attach to `projects` with fields:
- project.script: { outline, scenes[], lastUpdated }

## Integration points with PayloadCMS
- Writes: store generated text as rich documents linked to the project
- Reads: project metadata, genre, constraints from Projects collection
- Prompt execution records: promptsExecuted collection

## Step-by-step implementation guide
1. Set up endpoints and MCP tools with validation
2. Implement prompt building using platform promptTemplates
3. Call OpenRouter models; map responses to structured JSON
4. Persist results to PayloadCMS and emit progress events
5. Add longer jobs to Celery when needed

## Testing strategy
- Unit: prompt builders and response mappers
- Integration: outline generation happy-path and persistence
- Negative: model error mapping to user-facing messages

## Deployment considerations
- Stateless container; scale horizontally
- Provider keys via environment
- Respect platform’s fixed model list and failure-handling policy

