# Platform Secrets & Startup Matrix

## Overview

Centralized reference for runtime domains, required secrets, and baseline startup commands across the Auto-Movie mono-repo. Domain values mirror `docs/Domain-configs.md` when available; ports are listed for local use. Secrets include any variable that would expose credentials, API keys, tokens, or connection strings.

### Installation Attempt Snapshot (2025-02-14)
- ✅ `pnpm install --dir /var/www/movie-generation-platform/apps/auto-movie`
- ⚠️ Python dependencies for services remain pending because the host Python lacks `pip`/`ensurepip` (`python3 -m pip` and `python3 -m ensurepip` both fail). Installing `python3-pip` or using service-specific virtual environments will be required before running Python services.

> **Note:** Start commands below assume environment files are populated with production-ready values and prerequisites (MongoDB, Redis, Neo4j, FFmpeg, etc.) are available.

## Component Reference

### Auto-Movie App (`apps/auto-movie`)
- **Runtime:** Node.js 20.x with pnpm
- **Domains:** `localhost:3010` · `auto-movie.ngrok.pro` · `auto-movie.ft.tc`
- **Secrets:** `DATABASE_URI`, `PAYLOAD_SECRET`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `OPENROUTER_API_KEY`, `FAL_KEY`, `ELEVENLABS_API_KEY`, `JINA_API_KEY`, `CELERY_TASK_API_KEY`, `BRAIN_SERVICE_API_KEY`, `NEXTAUTH_SECRET`
- **Key Config:** `PAYLOAD_PUBLIC_SERVER_URL`, `R2_BUCKET_NAME`, `R2_ENDPOINT`, `R2_PUBLIC_URL`, `NEXT_PUBLIC_TASK_SERVICE_URL`, `NEXT_PUBLIC_BRAIN_SERVICE_URL`, `NEXT_PUBLIC_AGENTS_SERVICE_URL`, `OPENROUTER_DEFAULT_MODEL`
- **Install:** `pnpm install --dir apps/auto-movie` ✅
- **Run (dev):** `pnpm --dir apps/auto-movie dev`
- **Run (prod):** `pnpm --dir apps/auto-movie start`

### Celery Task API & Workers (`services/celery-redis`)
- **Runtime:** Python 3.11 (FastAPI + Celery)
- **Domains:** `localhost:8001` · `tasks.ngrok.pro` · `tasks.ft.tc`
- **Secrets:** `REDIS_URL`, `API_KEY`, `PAYLOAD_API_KEY`, `R2_ACCESS_KEY`, `R2_SECRET_KEY`, optional `CUDA_VISIBLE_DEVICES`
- **Key Config:** `API_HOST`, `API_PORT`, `AUTO_MOVIE_APP_URL`, `WEBHOOK_BASE_URL`, `BRAIN_SERVICE_BASE_URL`, `MAX_RETRY_ATTEMPTS`, `ENABLE_METRICS`
- **Install:** `python3 -m pip install -r services/celery-redis/requirements.txt` ⚠️ blocked (pip missing)
- **Run (API):** `uvicorn app.api:app --host 0.0.0.0 --port 8001`
- **Run (Workers):** `celery -A app.worker worker --loglevel=INFO`

### LangGraph Orchestrator (`services/langgraph-orchestrator`)
- **Runtime:** Python 3.11
- **Domains:** `localhost:8003` · `agents.ngrok.pro` · `agents.ft.tc`
- **Secrets:** `SECRET_KEY`, `API_KEY`, `REDIS_PASSWORD`, `OPENROUTER_API_KEY`
- **Key Config:** `REDIS_HOST`, `REDIS_PORT`, `AUTO_MOVIE_BASE_URL`, `BRAIN_SERVICE_BASE_URL`, `TASK_SERVICE_BASE_URL`, `MAX_WORKFLOWS`, `OPENROUTER_DEFAULT_MODEL`
- **Install:** `python3 -m pip install -r services/langgraph-orchestrator/requirements.txt` ⚠️ blocked (pip missing)
- **Run:** `python3 services/langgraph-orchestrator/start_server.py`

### Analytics Service (`services/analytics-service`)
- **Runtime:** Python 3.11 (FastAPI)
- **Domains:** Suggested `localhost:8016` · `analytics.ngrok.pro` · `analytics.ft.tc`
- **Secrets:** `PAYLOADCMS_API_KEY`
- **Key Config:** `PAYLOADCMS_URL`, `PORT`, `CORS_ORIGINS`, `ANALYTICS_EVENTS_SLUG`, `ANALYTICS_SUMMARIES_SLUG`
- **Install:** `python3 -m pip install -r services/analytics-service/requirements.txt` ⚠️ pending (pip missing)
- **Run:** `python3 -m src.main`

### MCP Brain Service (`services/mcp-brain-service`)
- **Runtime:** Python 3.11
- **Domains:** `localhost:8002` · `brain.ngrok.pro` · `brain.ft.tc`
- **Secrets:** `NEO4J_PASSWORD`, `JINA_API_KEY`
- **Key Config:** `NEO4J_URI`, `NEO4J_USER`, `CORS_ORIGINS`, `PORT`
- **Install:** `python3 -m pip install -r services/mcp-brain-service/requirements.txt` ⚠️ pending (pip missing)
- **Run:** `python3 -m src.main`

### MCP Story Service (`services/mcp-story-service`)
- **Runtime:** Python 3.11 (Poetry)
- **Domains:** `localhost:8010` · `story.ngrok.pro` · `story.ft.tc`
- **Secrets:** `REDIS_PASSWORD`, `SECRET_KEY`
- **Key Config:** `REDIS_HOST`, `REDIS_PORT`, `REDIS_DB`, `PROMETHEUS_PORT`, `BRAIN_SERVICE_BASE_URL`
- **Install:** `poetry install` (after installing Poetry) ⚠️ pending (pip/poetry unavailable)
- **Run:** `poetry run python -m src.mcp.server`

### MCP Story Bible Service (`services/mcp-story-bible-service`)
- **Runtime:** Python 3.11
- **Domains:** `localhost:8015` · `story-bible.ngrok.pro` · `story-bible.ft.tc`
- **Secrets:** `PAYLOADCMS_API_KEY`
- **Key Config:** `PAYLOADCMS_API_URL`, `BRAIN_SERVICE_URL`, `BRAIN_SERVICE_WS_URL`, `ALLOWED_ORIGINS`, `METRICS_PORT`
- **Install:** `python3 -m pip install -r services/mcp-story-bible-service/requirements.txt` ⚠️ pending
- **Run:** `python3 -m src.main`

### MCP Story Architect Service (`services/mcp-story-architect-service`)
- **Runtime:** Python 3.11
- **Domains:** Suggested `localhost:8017` · `story-architect.ngrok.pro` · `story-architect.ft.tc`
- **Secrets:** `PAYLOAD_API_SECRET`, `OPENAI_API_KEY`, optional override LLM keys
- **Key Config:** `PAYLOAD_API_URL`, `OPENAI_MODEL`, `METRICS_PORT`, `ENABLE_TRACING`
- **Install:** `python3 -m pip install -r services/mcp-story-architect-service/requirements.txt` ⚠️ pending
- **Run:** `python3 src/main.py`

### MCP Series Creator Service (`services/mcp-series-creator-service`)
- **Runtime:** Python 3.11
- **Domains:** Suggested `localhost:8018` · `series.ngrok.pro` · `series.ft.tc`
- **Secrets:** `PAYLOAD_API_SECRET`, `OPENAI_API_KEY`, optional override provider keys
- **Key Config:** `PAYLOAD_API_URL`, `OPENAI_MODEL`, `METRICS_PORT`, `SANITIZE_LOGS`
- **Install:** `python3 -m pip install -r services/mcp-series-creator-service/requirements.txt` ⚠️ pending
- **Run:** `python3 src/main.py`

### MCP Character Service (`services/mcp-character-service`)
- **Runtime:** Python 3.11
- **Domains:** `localhost:8011` · `character.ngrok.pro` · `character.ft.tc`
- **Secrets:** `DATABASE_URL`, `REDIS_URL`, `SECRET_KEY`, `PAYLOAD_CMS_API_KEY`, `LLM_API_KEY`
- **Key Config:** `PROMETHEUS_PORT`, `MAX_CONCURRENT_REQUESTS`, `ENABLE_PAYLOAD_INTEGRATION`, `ENABLE_LLM_INTEGRATION`
- **Install:** `python3 -m pip install -r services/mcp-character-service/requirements.txt` ⚠️ pending
- **Run:** `python3 -m src.main`

### MCP Visual Design Service (`services/mcp-visual-design-service`)
- **Runtime:** Python 3.11
- **Domains:** `localhost:8004` · `visual.ngrok.pro` · `visual.ft.tc`
- **Secrets:** `FAL_API_KEY`, `OPENROUTER_API_KEY`, `PAYLOADCMS_API_KEY`
- **Key Config:** `PAYLOADCMS_API_URL`, `REDIS_URL`, `PAYLOADCMS_WEBSOCKET_URL`, `LOG_LEVEL`
- **Install:** `python3 -m pip install -r services/mcp-visual-design-service/requirements.txt` ⚠️ pending
- **Run:** `python3 src/main.py` (or `docker compose up`)

### MCP 3D Asset Service (`services/mcp-3d-asset-service`)
- **Runtime:** Python 3.11
- **Domains:** `localhost:8014` · `asset.ngrok.pro` · `asset.ft.tc`
- **Secrets:** `PAYLOADCMS_API_KEY`
- **Key Config:** `PAYLOADCMS_URL`, `LOG_LEVEL`, optional `ASSIMP_CLI_PATH`, `BLENDER_CLI_PATH`
- **Install:** `python3 -m pip install -r services/mcp-3d-asset-service/requirements.txt` ⚠️ pending
- **Run:** `python3 -m src.main`

- **Runtime:** Python 3.11
- **Domains:** `localhost:8013` · `audio.ngrok-free.dev` · `story-architect.ft.tc` *(per current Domain-configs; reassign to a dedicated audio domain to avoid clashes with Story Architect)*
- **Secrets:** `ELEVENLABS_API_KEY` (or other TTS provider keys), any music/SFX provider credentials
- **Key Config:** `PAYLOADCMS` endpoints, FFmpeg/SoX paths when added
- **Install:** `python3 -m pip install -r services/mcp-audio-service/requirements.txt` ⚠️ pending
- **Run:** `python3 -m src.main`

### MCP Final QC Service (`services/mcp-final-qc-service`)
- **Runtime:** Python 3.11
- **Domains:** Suggested `localhost:8019` · `final-qc.ngrok.pro` · `final-qc.ft.tc`
- **Secrets:** `SECRET_KEY`, `PAYLOAD_CMS_API_KEY`
- **Key Config:** `MCP_SERVER_PORT`, `FFMPEG_PATH`, `FFPROBE_PATH`, `PROMETHEUS_PORT`, `ENABLE_PREVIEW_GENERATION`
- **Install:** `python3 -m pip install -r services/mcp-final-qc-service/requirements.txt` ⚠️ pending
- **Run:** `python3 -m src.main`

### MCP Video Generation Service (`services/mcp-video-generation-service`)
- **Runtime:** Python 3.11
- **Domains:** Suggested `localhost:8020` · `video-gen.ngrok.pro` · `video-gen.ft.tc`
- **Secrets:** `FAL_API_KEY`, optional `ELEVENLABS_API_KEY`
- **Key Config:** `FAL_IMAGE_TO_VIDEO`, `FAL_TEXT_TO_VIDEO`, shared image model identifiers
- **Install:** `python3 -m pip install -r services/mcp-video-generation-service/requirements.txt` ⚠️ pending
- **Run:** `python3 -m src.mcp_server`

### MCP Video Processing Service (`services/mcp-video-processing-service`)
- **Runtime:** Python 3.11 + Celery
- **Domains:** Suggested `localhost:8021` · `video-processing.ngrok.pro` · `video-processing.ft.tc`
- **Secrets:** PayloadCMS API key, Redis credentials for Celery
- **Key Config:** FFmpeg paths, Celery broker URLs, job metadata collections
- **Install:** `python3 -m pip install -r services/mcp-video-processing-service/requirements.txt` ⚠️ pending
- **Run (API):** `uvicorn src.api:app --host 0.0.0.0 --port 8021`
- **Run (Workers):** `celery -A src.tasks worker --loglevel=INFO`

### MCP Video Editor Service (`services/mcp-video-editor-service`)
- **Runtime:** Python 3.11
- **Domains:** Suggested `localhost:8022` · `video-editor.ngrok.pro` · `video-editor.ft.tc`
- **Secrets:** `PAYLOAD_CMS_API_KEY`
- **Key Config:** `PAYLOAD_CMS_URL`, `FFMPEG_PATH`, `FFPROBE_PATH`, `VIDEO_EDITOR_TEMP_DIR`
- **Install:** `python3 -m pip install -r services/mcp-video-editor-service/requirements.txt` ⚠️ pending
- **Run:** `python3 -m src.main`

### MCP Distribution Service (`services/mcp-distribution-service`)
- **Runtime:** Python 3.11
- **Domains:** Suggested `localhost:8023` · `distribution.ngrok.pro` · `distribution.ft.tc`
- **Secrets:** `PAYLOADCMS_API_KEY`
- **Key Config:** `PAYLOADCMS_URL`, `PAYLOAD_PUBLIC_SERVER_URL`, `DISTRIBUTION_SKIP_CHECKSUM`
- **Install:** `python3 -m pip install -r services/mcp-distribution-service/requirements.txt` ⚠️ pending
- **Run:** `python3 -m src.mcp_server`

### MCP Media Transcoding Service (`services/mcp-media-transcoding-service`)
- **Runtime:** Python 3.11 + Celery
- **Domains:** Suggested `localhost:8024` · `transcode.ngrok.pro` · `transcode.ft.tc`
- **Secrets:** PayloadCMS API key, Redis credentials
- **Key Config:** Target presets, FFmpeg availability, job status collections
- **Install:** `python3 -m pip install -r services/mcp-media-transcoding-service/requirements.txt` ⚠️ pending
- **Run (API):** `uvicorn src.api:app --host 0.0.0.0 --port 8024`
- **Run (Workers):** `celery -A src.tasks worker --loglevel=INFO`

### Export Service (`services/export-service`)
- **Runtime:** Python 3.11 + Celery
- **Domains:** Suggested `localhost:8025` · `export.ngrok.pro` · `export.ft.tc`
- **Secrets:** PayloadCMS API key, downstream video/transcoding service tokens if applicable
- **Key Config:** Worker queues, temp storage paths, integration service URLs
- **Install:** `python3 -m pip install -r services/export-service/requirements.txt` ⚠️ pending
- **Run (API):** `uvicorn src.api:app --host 0.0.0.0 --port 8025`
- **Run (Workers):** `celery -A src.tasks worker --loglevel=INFO`

### Webhook Dispatcher Service (`services/webhook-dispatcher-service`)
- **Runtime:** Python 3.11
- **Domains:** Suggested `localhost:8026` · `webhooks.ngrok.pro` · `webhooks.ft.tc`
- **Secrets:** HMAC signing secrets per target (`WEBHOOK_SIGNING_SECRET_*` pattern), PayloadCMS API key if persisting logs
- **Key Config:** Default timeout values, max target fan-out, CMS collection slugs for deliveries
- **Install:** `python3 -m pip install -r services/webhook-dispatcher-service/requirements.txt` ⚠️ pending
- **Run:** `python3 -m src.main`

## Next Steps
1. Install `python3-pip` (or platform-specific equivalent) so service dependencies can be set up inside per-service virtual environments.
2. Populate `.env` files for each component with the secrets listed above and align domain names with `docs/Domain-configs.md` after resolving port conflicts (8015 duplication).
3. Once dependencies are satisfied, start each service in the order: data stores → core services (`brain`, `celery`) → orchestrator (`langgraph`) → domain-specific MCP services → Auto-Movie UI.
