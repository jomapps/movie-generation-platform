# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

This is a **Movie Generation Platform** built as a monorepo containing multiple independent services and applications organized via Git submodules. The platform combines AI-powered content generation services with a modern web application for creating and managing movie production workflows.

## Architecture

### Monorepo Structure
The repository uses **Git submodules** to maintain clean separation between services while enabling coordination:
- `apps/auto-movie/` - Next.js/Payload CMS frontend application 
- `services/` - Backend microservices (Python/FastAPI)
  - `celery-redis/` - Task processing service (Celery + Redis)
  - `langgraph-orchestrator/` - Workflow orchestration service
  - `mcp-*-service/` - Model Context Protocol services (brain, character, story)

### Technology Stack
- **Frontend**: Next.js 15, React 19, PayloadCMS 3.x, TailwindCSS, TypeScript
- **Backend Services**: Python 3.11+, FastAPI, Celery, Redis
- **Infrastructure**: Docker/Docker Compose, Prometheus monitoring
- **Testing**: PyTest (Python), Playwright + Vitest (TypeScript)
- **AI Integration**: MCP (Model Context Protocol) for AI services

### Service Communication
- Services communicate via HTTP APIs and Celery task queues
- MCP services provide AI capabilities through structured tool interfaces
- Redis handles task queue management and caching
- Each service exposes health checks and metrics endpoints

## Common Development Commands

### Repository Management
```powershell
# Initialize all submodules (recommended on Windows)
pwsh scripts/add-submodules.ps1

# Update all submodules to latest
git submodule foreach --recursive git pull origin $(git rev-parse --abbrev-ref HEAD)

# Sync submodule configurations
git submodule sync --recursive
git submodule update --init --recursive
```

### Frontend (auto-movie app)
```bash
# Navigate to frontend
cd apps/auto-movie

# Install dependencies
pnpm install

# Development server (runs on port 3010)
pnpm dev

# Build for production
pnpm build

# Run tests
pnpm test              # Run all tests
pnpm test:e2e          # Playwright E2E tests
pnpm test:int          # Integration tests with Vitest

# Code quality
pnpm lint              # ESLint
```

### Python Services (celery-redis, langgraph-orchestrator, mcp-* services)
```bash
# Navigate to any Python service
cd services/celery-redis  # or other service

# Install dependencies
pip install -e .
pip install -e .[dev]     # Include dev dependencies

# Run service locally
python -m app.main        # FastAPI service

# Run with Docker
docker-compose up         # Development
docker-compose -f docker-compose.prod.yml up  # Production

# Testing
pytest                    # All tests
pytest -m unit           # Unit tests only
pytest -m integration    # Integration tests only
pytest -m contract       # Contract tests only

# Code quality
black .                   # Format code
flake8                   # Lint code
mypy .                   # Type checking
```

### Testing Individual Components
```bash
# Test single service
cd services/mcp-story-service
pytest tests/unit/test_genre_analyzer.py::test_specific_function

# Test specific areas
pytest -m "integration and not slow"    # Fast integration tests
pytest -k "character"                   # Tests containing "character"
pytest --maxfail=1                      # Stop on first failure
```

## Key Integration Points

### Byterover MCP Integration
This project integrates with Byterover MCP tools for enhanced AI development workflows. When working with this codebase:

1. **Knowledge Management**: Use `byterover-retrieve-knowledge` to access project context before major tasks
2. **Module Updates**: Call `byterover-update-modules` when modifying service architectures or APIs
3. **Plan Persistence**: Always use `byterover-save-implementation-plan` for approved development plans

### Service Dependencies
- The `celery-redis` service must be running for task processing
- MCP services require proper configuration of their respective AI model endpoints
- The frontend depends on backend APIs being available (usually port 8001+ for services)

### Configuration Management
- Each service uses environment variables for configuration
- Development configs are in `docker-compose.yml` files
- Production deployments use separate compose files (`.prod.yml`, `.coolify.yml`)

### Monitoring and Observability
- Services expose Prometheus metrics on `/metrics` endpoints
- Structured logging via `structlog` for all Python services
- Health checks available at `/api/v1/health` for each service

## Development Notes

### Working with Submodules
- Always commit changes within the submodule directory first, then update the parent repo
- The monorepo tracks specific commit SHAs for each submodule
- Use `git status` in the root to see which submodules have uncommitted changes

### Service-First Architecture
- Each service is independently deployable and testable
- Services follow OpenAPI specifications (see `specs/` directories in each service)
- Contract tests ensure API compatibility between services

### AI Service Development
- MCP services use structured tool definitions for AI interactions
- Story, character, and brain services provide complementary AI capabilities
- The orchestrator manages complex workflows across multiple AI services