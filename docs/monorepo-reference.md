# Movie Generation Platform Monorepo Reference

## Purpose & Scope
- Provide a single, up-to-date entry point for current and future contributors.
- Summarize architecture, services, workflows, and resources without duplicating detailed docs.
- Highlight ownership expectations so the document remains accurate as the platform evolves.

## High-Level Architecture Overview
- Centralized **mcp-brain-service** exposes AI/ML capabilities (embeddings, semantic search, knowledge graph).
- Downstream services connect to the brain over MCP WebSocket for consistent AI interactions.
- Key dependencies managed by the brain service: Jina v4 embeddings API, Neo4j graph database.
- Orchestration handled by **langgraph-orchestrator**; UI delivered by **apps/auto-movie**; background jobs routed through **celery-task-service**.

```mermaid
flowchart LR
    subgraph Brain["mcp-brain-service (Port 8002)"]
        Jina[Jina v4 API]
        Neo4j[(Neo4j DB)]
    end
    Orchestrator[langgraph-orchestrator (Port 8003)] -->|MCP WebSocket| Brain
    AutoMovie[apps/auto-movie (Port 3010)] -->|REST / MCP| Brain
    Celery[celery-task-service (Port 8001)] -->|MCP WebSocket| Brain
    External[(External Clients)] --> AutoMovie
```

## Service & App Catalog

| Path | Component | Role & Capabilities | Tech Stack | Reference Source(s) |
| --- | --- | --- | --- | --- |
| `services/mcp-brain-service` | Brain Service | Central AI hub: embeddings, semantic search, knowledge graph | Python, FastAPI, Jina v4, Neo4j | [`docs/architecture/brain-service.md`](./architecture/brain-service.md) · [`docs/api/brain-service-api.md`](./api/brain-service-api.md) · [`docs/fixing-docs/jina-fix-implementation-plan.md`](./fixing-docs/jina-fix-implementation-plan.md#implementation-status) |
| `services/langgraph-orchestrator` | Workflow Orchestrator | Coordinates agents and workflows via LangGraph | Python, LangGraph | [`docs/fixing-docs/jina-fix-implementation-plan.md`](./fixing-docs/jina-fix-implementation-plan.md#implementation-status) (Phase 2 marked complete – verify with submodule README) |
| `services/celery-redis` | Task Service | Background task queue for asynchronous jobs | Python, Celery, Redis | [`docs/fixing-docs/jina-fix-implementation-plan.md`](./fixing-docs/jina-fix-implementation-plan.md#implementation-status) (Phase 4 marked complete) |
| `services/mcp-story-service` | Story Service | Generates narrative beats and scripts | Python | Consult service-specific README within submodule for latest status |
| `services/mcp-character-service` | Character Service | Manages character definitions and traits | Python | Consult service-specific README within submodule for latest status |
| Additional services (`analytics-service`, `export-service`, `mcp-3d-asset-service`, `mcp-audio-service`, `mcp-media-transcoding-service`, `mcp-video-processing-service`, `mcp-visual-design-service`, `webhook-dispatcher-service`) | Supporting media pipelines and integrations | Mixed stacks per submodule | Review respective submodule READMEs |
| `apps/auto-movie` | Frontend | User interface for movie generation workflow | Next.js, React, TypeScript | [`docs/auto-movie-feature-list.md`](./auto-movie-feature-list.md) (Last updated 2025-09-28) |

> For submodule repository URLs and initialization scripts see [`repo-map.json`](../repo-map.json) and [`scripts/`](../scripts/).

## Environment & Setup Essentials
1. **Prerequisites:** Docker & Docker Compose, Python 3.11+, Node.js 18+, Neo4j instance (local or Docker).
2. **Repository Setup:**
   ```bash
   git clone --recursive <repo>
   cd movie-generation-platform
   git submodule update --init --recursive
   ```
3. **Environment Variables:**
   - Brain service `.env`: `JINA_API_KEY`, `JINA_API_URL`, `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`, `MCP_SERVER_PORT`.
   - Orchestrator `.env`: `BRAIN_SERVICE_BASE_URL`, `BRAIN_SERVICE_WS_URL`.
   - Frontend `.env.local`: `NEXT_PUBLIC_BRAIN_SERVICE_URL`.
4. **Startup Sequence:** Bring up brain service first, then orchestrator, celery service, and finally the frontend.

## Development Workflows
- **Common Commands:** `npm run build`, `npm run test`, `npm run lint`, `npm run typecheck` (run within relevant submodule).
- **Submodule Management:** Use helper scripts (`scripts/add-submodules.ps1` or `.sh`) after editing `repo-map.json`, or manage manually via `git submodule add` and `git submodule update --init --recursive`.
- **Branching & Updates:** Commit changes inside submodules, then update pointers in this monorepo (`git add <submodule>` -> commit on master).
- **Testing Expectations:** Follow TDD where possible; ensure brain service tests/linting pass before relying services are updated.

## Operational Status & Roadmap Snapshot
- **Brain & Orchestrator:** [`docs/fixing-docs/jina-fix-implementation-plan.md`](./fixing-docs/jina-fix-implementation-plan.md) records all architecture phases as complete as of 2025-01-28. Confirm with submodule READMEs before planning follow-up work.
- **Frontend:** [`docs/auto-movie-feature-list.md`](./auto-movie-feature-list.md) (updated 2025-09-28) shows Phase 1 complete and Phase 2 enhancements in progress.
- **Historical Progress:** [`README.md`](../README.md) retains a 35% overall progress table—treat as historical context until reconciled with newer sources.
- **Action:** When planning new work, rely on the most recently updated service-specific docs and update this reference accordingly.

## Key References & Further Reading
- [`README.md`](../README.md) – Monorepo overview and setup basics; verify progress metrics against newer sources.
- [`docs/architecture/brain-service.md`](./architecture/brain-service.md) – Brain service architecture (stable reference).
- [`docs/api/brain-service-api.md`](./api/brain-service-api.md) – MCP tool and API definitions.
- [`docs/troubleshooting/README.md`](./troubleshooting/README.md) – Entry point to troubleshooting guides (integration issues guide is actively maintained).
- [`docs/fixing-docs/jina-fix-implementation-plan.md`](./fixing-docs/jina-fix-implementation-plan.md) – Architecture phase log; last completion entry dated 2025-01-28.
- [`docs/auto-movie-feature-list.md`](./auto-movie-feature-list.md) – Frontend roadmap; last updated 2025-09-28 with Phase 2 in progress.

## Maintenance Notes
- **Ownership:** Core maintainers should review this document whenever major architectural or workflow changes merge.
- **Cadence:** Revalidate at milestone completions or quarterly, whichever comes first.
- **Process:** Update summaries and cross-links; ensure status indicators mirror authoritative sources (e.g., `README.md`).
