# Deployment Server Requirements

## Overview

This guide captures the runtime, infrastructure, and process-management requirements for deploying the movie-generation platform directly on an Ubuntu server. It replaces the original Coolify-based plan and assumes a single-host deployment that reverse-proxies traffic through `nginx` and supervises long-running services with `pm2`. Port assignments must remain aligned with [`docs/Domain-configs.md`](./Domain-configs.md); any mismatches called out below should be resolved before go-live.

## Base Operating System & Packages

- Use Ubuntu 22.04 LTS (or newer) with regular security updates (`sudo unattended-upgrade` recommended).
- Core packages:
  ```bash
  sudo apt update && sudo apt install -y build-essential git curl unzip \
       python3.11 python3.11-venv python3-pip pkg-config libssl-dev \
       ffmpeg nginx redis-server
  ```
- Optional but recommended: `ufw` (firewall), `fail2ban`, `logrotate`, `htop`, `certbot` (`python3-certbot-nginx`) for TLS, and NVIDIA drivers / CUDA where GPU workloads are required.

## Language Runtimes & Global Tooling

| Component | Required Version | Install Notes |
|-----------|-----------------|---------------|
| Node.js   | 20.x LTS (>=18.20.2) | Install via Nodesource or NVM; required by `apps/auto-movie` and pm2 supervisor. |
| pnpm      | 9.x or 10.x | `npm install -g pnpm` after Node installation. |
| PM2       | Latest | `npm install -g pm2`; used to manage both Node and Python processes. |
| Python    | 3.11 | Matches `pyproject.toml` requirements across Python services. |
| pip / venv | Latest | Use per-service virtual environments under `/srv/services/<name>/.venv`. |
| Poetry (optional) | If reusing existing lockfiles; otherwise `pip install -r requirements.txt` is sufficient. |

> **Note:** PM2 can supervise Python services by setting `interpreter: "/usr/bin/python3"` in the ecosystem file. For GPU tasks install CUDA/cuDNN packages that match the deployed PyTorch builds (see `services/celery-redis/requirements.txt`).

## Shared Infrastructure Services

| Service | Default Port(s) | Used By | Notes |
|---------|-----------------|---------|-------|
| MongoDB Community (>=6.0) | `27017` | Auto-Movie PayloadCMS, MCP services persisting project metadata | Single instance can serve all workloads; enable authentication and backups. |
| Redis 7.x | `6379` (+ optional `9100` exporter) | Celery task queue, LangGraph orchestrator, caching layers | Deploy as a single shared instance; enable persistence (AOF) for durability. |
| PostgreSQL 15+ | `5432` | `mcp-character-service` (and any other asyncpg clients) | Create separate DB/user per service. |
| Neo4j 5.x | `7474` (HTTP), `7687` (Bolt) | `mcp-brain-service` | Production bolt connections should stay internal; expose HTTPS UI only if secured. |
| Prometheus (optional) | `9090` | Metrics scraping for Celery, LangGraph, MCP services | Useful if consolidating observability on the same host. |
| Grafana (optional) | `3001` | Visualization dashboards | Configure behind nginx and secure with SSO/basic auth. |
| Redis Insight / Mongo Express (optional) | `8101`, `8102` | Ops tooling | Deploy behind admin-only network segments. |

All shared data services can run on the same VM for MVP, but consider managed offerings (Atlas, Redis Enterprise, Aura) for resilience.

### Current Host Installation Snapshot (Last verified 2025-02-14)

| Component | Installed Version | Verification Command |
|-----------|------------------|----------------------|
| MongoDB Community | 7.0.24 | `mongod --version` |
| Neo4j | 5.26.12 | `neo4j --version` |
| FFmpeg | 6.1.1-3ubuntu5 | `ffmpeg -version` |
| Redis Server | 7.0.15 | `redis-server --version` |

> All core data/processing services above are present on the target Ubuntu host and respond with the versions listed when the commands are executed as the deployment user.

## Application & Agent Services

### Core Platform Processes

| Service | Repo Path | Runtime | Default Port | Critical Dependencies |
|---------|-----------|---------|--------------|-----------------------|
| Auto-Movie App (Next.js + PayloadCMS) | `apps/auto-movie` | Node.js 20 + pnpm | 3010 (serves 3000 internally) | MongoDB, Cloudflare R2 (S3 API), Celery Task API (8001), Brain (8002). |
| Celery Task API | `services/celery-redis` (`uvicorn` server) | Python 3.11 | 8001 | Redis (queue/result), MongoDB (metadata), S3/R2, GPU, FFmpeg. |
| Celery Workers & Beat | `services/celery-redis` (`celery` processes) | Python 3.11 | n/a (background) | Redis, GPU drivers (torch optional). |
| MCP Brain Service | `services/mcp-brain-service` | Python 3.11 | 8002 | Neo4j, Jina API, Redis (optional caching). |
| LangGraph Orchestrator | `services/langgraph-orchestrator` | Python 3.11 | 8003 | Redis, optional MQTT broker, integration with MCP agents. |
| Analytics Service | `services/analytics-service` | Python 3.11 | 8016 (per docs) | PayloadCMS API, Redis (optional), HTTP outbound. |

### Domain & Media MCP Services

| Service | Repo Path | Runtime | Port (current default) | Notes |
|---------|-----------|---------|------------------------|-------|
| Story MCP | `services/mcp-story-service` | Python 3.11 | 8010 | Provides story analysis via MCP. |
| Character MCP | `services/mcp-character-service` | Python 3.11 | 8011 | Requires PostgreSQL (`DATABASE_URL`) + Redis; exposes Prometheus metrics on 8012. |
| Visual Design MCP | `services/mcp-visual-design-service` | Python 3.11 | 8004 | Needs FAL + OpenRouter credentials; optional Redis for caching. |
| 3D Asset MCP | `services/mcp-3d-asset-service` | Python 3.11 | 8014 | Depends on PayloadCMS API & asset storage. |
| Story Bible MCP | `services/mcp-story-bible-service` | Python 3.11 | 8015 | Uses PayloadCMS + external LLM providers. |
| Story Architect MCP | `services/mcp-story-architect-service` | Python 3.11 | (configure, default metrics 8081) | Ensure unique service port before deployment; relies on OpenAI + PayloadCMS. |
| Visual QA / Final QC MCP | `services/mcp-final-qc-service` | Python 3.11 | **8015 (conflicts)** | Reassign to free port (e.g., 8017) before launch. |
| Distribution MCP | `services/mcp-distribution-service` | Python 3.11 | configure (default 8020 suggested) | Handles content release workflows. |
| Series Creator MCP | `services/mcp-series-creator-service` | Python 3.11 | configure | Needs OpenAI/OpenRouter credentials. |
| Video Generation MCP | `services/mcp-video-generation-service` | Python 3.11 | configure | Requires GPU toolchain, S3 storage, FFmpeg. |
| Video Editor MCP | `services/mcp-video-editor-service` | Python 3.11 | configure (runs as MCP WebSocket server) | Requires FFmpeg binaries and PayloadCMS API key. |
| Story Architect Support Services | `services/mcp-story-architect-service` | Python 3.11 | configure | Shares dependencies with Payload + LLMs. |

> **Port alignment:** Update either the MCP Story Bible or Final QC service to resolve the shared `8015` default. Capture the final mapping in both this document and `docs/Domain-configs.md` once the decision is made.

## PM2-Based Process Management

1. **Install & bootstrap PM2**
   ```bash
   sudo npm install -g pm2
   pm2 update
   ```
2. **Create `/srv/ecosystem.config.cjs` (example):**
   ```javascript
   module.exports = {
     apps: [
       {
         name: "auto-movie",
         script: "pnpm",
         args: "start",
         cwd: "/srv/apps/auto-movie",
         interpreter: "/usr/bin/env",
         env: { PORT: "3000" }
       },
       {
         name: "celery-api",
         script: "uvicorn",
         args: "app.api:app --host 0.0.0.0 --port 8001",
         interpreter: "/usr/bin/python3",
         cwd: "/srv/services/celery-redis",
         env: { ENVIRONMENT: "production" }
       },
       {
         name: "celery-worker",
         script: "celery",
         args: "-A app.worker worker --loglevel=INFO",
         interpreter: "/usr/bin/python3",
         cwd: "/srv/services/celery-redis"
       },
       {
         name: "brain-service",
         script: "uvicorn",
         args: "app.main:app --host 0.0.0.0 --port 8002",
         interpreter: "/usr/bin/python3",
         cwd: "/srv/services/mcp-brain-service"
       }
     ]
   };
   ```
   Add additional MCP services following the same pattern (unique `name`, `cwd`, and arguments).
3. **Start & persist processes**
   ```bash
   pm2 start /srv/ecosystem.config.cjs
   pm2 save
   pm2 startup systemd -u deploy && sudo env PATH=$PATH pm2 startup systemd -u deploy --hp /home/deploy
   ```
4. **Integrate logs**: configure `pm2 logrotate` (`pm2 install pm2-logrotate`) and forward to central logging if available.

## Nginx Reverse Proxy & TLS

1. Install nginx: `sudo apt install -y nginx` (already included above).
2. Sample server block (`/etc/nginx/sites-available/auto-movie`):
   ```nginx
   server {
     listen 80;
     server_name auto-movie.ft.tc;

     location / {
       proxy_pass http://127.0.0.1:3010;
       proxy_set_header Host $host;
       proxy_set_header X-Real-IP $remote_addr;
       proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
       proxy_set_header X-Forwarded-Proto $scheme;
     }
   }
   ```
   Duplicate the server block for each public service (e.g., `tasks.ft.tc → 127.0.0.1:8001`, `brain.ft.tc → 127.0.0.1:8002`, `agents.ft.tc → 127.0.0.1:8003`). Keep the port list synchronized with `Domain-configs.md`.
3. Enable the sites and reload nginx:
   ```bash
   sudo ln -s /etc/nginx/sites-available/auto-movie /etc/nginx/sites-enabled/
   sudo nginx -t && sudo systemctl reload nginx
   ```
4. Issue TLS certificates with certbot:
   ```bash
   sudo certbot --nginx -d auto-movie.ft.tc -d tasks.ft.tc -d brain.ft.tc
   ```
5. Harden nginx (HSTS, rate limiting) once certificates are active.

## Deployment Checklist

- [ ] Assign a dedicated Linux user (e.g., `deploy`) and store code under `/srv/apps` and `/srv/services` with correct permissions.
- [ ] Provision MongoDB, Redis, PostgreSQL, and Neo4j with secure credentials; rotate secrets into `.env` files.
- [ ] Install Node.js, pnpm, Python 3.11 toolchain, and PM2 globally.
- [ ] Create per-service virtual environments and install dependencies (`pip install -r requirements.txt`).
- [ ] Configure PM2 ecosystem entries for every service (API, workers, MCP servers) and persist with `pm2 save`.
- [ ] Configure nginx server blocks for each public domain; obtain TLS via certbot.
- [ ] Verify port assignments against [`docs/Domain-configs.md`](./Domain-configs.md) and resolve conflicts (e.g., Story Bible vs Final QC both default to 8015).
- [ ] Enable monitoring endpoints (Prometheus/Grafana or external APM) and configure alerting.
- [ ] Document GPU driver versions and FFmpeg builds if video generation/processing runs on the same host.
- [ ] Run platform acceptance tests (`pnpm test`, service-specific pytest suites) after deployment.

## Notes on Port Resolution

| Port | Documented Usage (`Domain-configs.md`) | Observed Default in Service Code | Action |
|------|----------------------------------------|----------------------------------|--------|
| 8010 | Story MCP | Story MCP | ✅ identical |
| 8011 | Character MCP | Character MCP | ✅ identical |
| 8012 | Visual MCP (docs) | Character MCP Prometheus metrics | Decide final owner; consider shifting metrics to 9112. |
| 8014 | Asset MCP | Asset MCP | ✅ identical |
| 8015 | Story Bible MCP | Final QC MCP (`services/mcp-final-qc-service/src/config.py`) | **Resolve conflict** before production. |
| 8016 | _Not listed_ | Analytics Service docs | Add to Domain-configs.md if service will be public. |
| 8004 | _Not listed_ | Visual Design MCP config | Add to Domain-configs.md for completeness. |

Update `Domain-configs.md` after finalizing these assignments so reverse proxies and PM2 entries stay consistent.
