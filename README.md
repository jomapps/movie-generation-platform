# Movie Generation Platform Monorepo

## Overview

An intelligent movie generation platform built with a centralized brain service architecture. This monorepo aggregates multiple standalone services and apps while maintaining clean separation through submodules, enabling end-to-end AI-powered movie creation workflows.

## 🧠 Centralized Brain Service Architecture

The platform is built around a **centralized brain service** that provides all AI/ML capabilities including embeddings, semantic search, and knowledge graph management. All other services communicate with the brain service via MCP (Model Context Protocol) WebSocket connections.

### Architecture Diagram

```
┌─────────────────────┐    MCP WebSocket    ┌─────────────────────┐
│ langgraph-          │ ──────────────────► │ mcp-brain-service   │
│ orchestrator        │                     │ (Port: 8002)        │
│ (Port: 8003)        │                     │                     │
└─────────────────────┘                     │ ┌─────────────────┐ │
                                            │ │ Jina v4 Embed   │ │
┌─────────────────────┐    MCP WebSocket    │ └─────────────────┘ │
│ auto-movie          │ ──────────────────► │                     │
│ (Port: 3010)        │                     │ ┌─────────────────┐ │
└─────────────────────┘                     │ │ Neo4j Database  │ │
                                            │ │ (Port: 7474)    │ │
┌─────────────────────┐    MCP WebSocket    │ └─────────────────┘ │
│ celery-task-service │ ──────────────────► └─────────────────────┘
│ (Port: 8001)        │
└─────────────────────┘
```

### Key Benefits

- **Single Source of Truth**: Only the brain service connects directly to AI services (Jina) and graph database (Neo4j)
- **Consistent AI/ML**: Centralized embedding generation and semantic search across all services
- **Scalable**: Brain service handles multiple concurrent MCP WebSocket connections
- **Maintainable**: Clear separation of concerns with standardized MCP communication

## Repository Structure

```
.
├── apps/
│   └── auto-movie/                # Next.js frontend app (submodule)
├── services/
│   ├── mcp-brain-service/         # 🧠 CORE: AI/ML brain service (submodule)
│   ├── mcp-story-service/         # Story generation service (submodule)
│   ├── mcp-character-service/     # Character management service (submodule)
│   ├── langgraph-orchestrator/    # Workflow orchestration (submodule)
│   └── celery-redis/              # Task queue service (submodule)
├── docs/
│   ├── architecture/              # Architecture documentation
│   ├── api/                       # API documentation
│   ├── troubleshooting/           # Troubleshooting guides
│   ├── fixing-docs/               # Implementation plans
│   └── thoughts/                  # Design notes
├── scripts/
│   ├── add-submodules.ps1         # PowerShell helper (Windows recommended)
│   └── add-submodules.sh          # Bash helper (requires jq)
└── repo-map.json                  # Configure submodule URLs and paths
```

## 🚀 Quick Start

### Prerequisites

- **Docker & Docker Compose** (recommended)
- **Python 3.11+** for brain service
- **Node.js 18+** for frontend
- **Neo4j** (can run via Docker)

### 1. Clone and Setup

```bash
# Clone with submodules
git clone --recursive <this-mono-repo-url>
cd movie-generation-platform

# Or initialize submodules if already cloned
git submodule update --init --recursive
```

### 2. Start Core Services

```bash
# Start brain service (REQUIRED - other services depend on this)
cd services/mcp-brain-service
docker-compose up -d

# Start other services
cd ../langgraph-orchestrator
docker-compose up -d

cd ../celery-redis
docker-compose up -d

# Start frontend
cd ../../apps/auto-movie
npm install && npm run dev
```

### 3. Verify Setup

```bash
# Check brain service health
curl http://localhost:8002/health

# Check frontend
open http://localhost:3010
```

## 🔧 Development Setup

### Adding External Repositories

**Option A — PowerShell (recommended on Windows):**

```powershell
# 1) Edit repo-map.json and fill in each "url"
# 2) Run the helper script (PowerShell 7+ or Windows PowerShell)
powershell -ExecutionPolicy Bypass -File scripts/add-submodules.ps1
# or
pwsh scripts/add-submodules.ps1
```

**Option B — Bash (requires jq):**

```bash
# 1) Edit repo-map.json and fill in each "url"
# 2) Run the helper script
bash scripts/add-submodules.sh
```

**Option C — Manual (one-by-one):**

```bash
git submodule add -b main <URL_FOR_mcp-brain-service> services/mcp-brain-service
git submodule add -b main <URL_FOR_langgraph-orchestrator> services/langgraph-orchestrator
git submodule add -b main <URL_FOR_mcp-story-service> services/mcp-story-service
git submodule add -b main <URL_FOR_mcp-character-service> services/mcp-character-service
git submodule add -b main <URL_FOR_celery-redis> services/celery-redis
git submodule add -b main <URL_FOR_auto-movie> apps/auto-movie

git submodule update --init --recursive
```

### Environment Configuration

**Brain Service (Required):**
```bash
# services/mcp-brain-service/.env
JINA_API_KEY=your_jina_api_key
JINA_API_URL=https://api.jina.ai/v1/embeddings
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
MCP_SERVER_PORT=8002
```

**Orchestrator:**
```bash
# services/langgraph-orchestrator/.env
BRAIN_SERVICE_BASE_URL=http://localhost:8002
BRAIN_SERVICE_WS_URL=ws://localhost:8002/mcp
```

**Frontend:**
```bash
# apps/auto-movie/.env.local
NEXT_PUBLIC_BRAIN_SERVICE_URL=http://localhost:8002
```

### Working with Submodules

```bash
# Clone this monorepo and initialize submodules
git clone <this-mono-repo-url>
cd movie-generation-platform
git submodule update --init --recursive

# Pull latest changes across all submodules
git submodule foreach --recursive git pull origin $(git rev-parse --abbrev-ref HEAD)

# If you switch branches in the monorepo and want submodules aligned
git submodule sync --recursive
git submodule update --init --recursive

# Update specific submodule
cd services/mcp-brain-service
git pull origin main
cd ../..
git add services/mcp-brain-service
git commit -m "Update brain service submodule"
```

## 📚 Documentation

- **[Brain Service Architecture](docs/architecture/brain-service.md)** - Detailed brain service design
- **[API Documentation](docs/api/)** - Complete API reference
- **[Troubleshooting Guide](docs/troubleshooting/)** - Common issues and solutions
- **[Implementation Plan](docs/fixing-docs/jina-fix-implementation-plan.md)** - Current project status

## 🛠️ MCP Tools Available

The brain service provides 20+ MCP tools for AI operations:

### Core Tools
- `embed_text` - Generate embeddings for text
- `search_by_embedding` - Semantic similarity search
- `store_document` - Store documents with embeddings
- `batch_embed_texts` - Efficient batch embedding

### Knowledge Graph
- `create_relationship` - Link entities in knowledge graph
- `query_graph` - Execute Cypher queries
- `get_node_neighbors` - Explore graph connections

### Workflow Integration
- `store_workflow_data` - Track LangGraph execution
- `store_agent_memory` - Agent conversation memory
- `search_similar_workflows` - Find workflow patterns

### Batch Processing
- `process_document_batch` - Bulk document processing
- `batch_similarity_search` - Multiple queries at once

[See full API documentation](docs/api/brain-service-api.md)

## 🏗️ Service Details

### MCP Brain Service (Port: 8002)
**Role:** Centralized AI/ML hub providing embeddings, semantic search, and knowledge graph
- **Technology:** Python, FastAPI, Neo4j, Jina v4
- **MCP Tools:** 20+ tools for embeddings, search, graph operations
- **Status:** ✅ **Production Ready**

### LangGraph Orchestrator (Port: 8003)
**Role:** Workflow orchestration and agent coordination
- **Technology:** Python, LangGraph, MCP WebSocket client
- **Integration:** Connects to brain service via MCP
- **Status:** 🔄 **75% Complete** (cleanup needed)

### Auto-Movie Frontend (Port: 3010)
**Role:** User interface for movie generation
- **Technology:** Next.js, React, TypeScript
- **Integration:** Needs brain service MCP client
- **Status:** ❌ **Integration Pending**

### Celery Task Service (Port: 8001)
**Role:** Background task processing
- **Technology:** Python, Celery, Redis
- **Integration:** Needs brain service MCP client
- **Status:** ❌ **Integration Pending**

## 📊 Implementation Status

**Overall Progress: 35% Complete**

| Component | Status | Progress |
|-----------|--------|----------|
| MCP Brain Service | ✅ Complete | 100% |
| LangGraph Orchestrator | 🔄 In Progress | 75% |
| Auto-Movie Frontend | ❌ Pending | 0% |
| Celery Task Service | ❌ Pending | 0% |
| Documentation | 🔄 In Progress | 80% |

## 🤝 Contributing

1. **Brain Service First**: Ensure brain service changes are tested and documented
2. **MCP Integration**: All new services must use MCP WebSocket communication
3. **Documentation**: Update relevant docs for any API changes
4. **Testing**: Follow TDD principles with comprehensive test coverage

## 📝 Notes

- Each service/app remains a separate Git repository. Commits to submodules should be done inside the submodule directory and pushed to its own origin.
- This monorepo tracks submodule SHAs. Update the SHA by committing submodule pointer changes in the monorepo after pulling in the submodule.
- The brain service is the foundation - ensure it's running before starting other services.
- All AI/ML operations go through the brain service to maintain consistency.

## 🚀 Next Steps

1. **Complete Phase 2**: Remove Neo4j dependencies from orchestrator
2. **Implement Phase 3**: Create TypeScript MCP client for auto-movie
3. **Implement Phase 4**: Add brain service integration to celery service
4. **Testing**: Comprehensive integration testing across all services
5. **Production**: Deploy with proper monitoring and scaling

## 📞 Support

For issues and questions:
- Check the [troubleshooting guide](docs/troubleshooting/)
- Review the [implementation plan](docs/fixing-docs/jina-fix-implementation-plan.md)
- Open an issue in the relevant service repository

---

**Built with 🧠 Centralized Intelligence • 🔗 MCP Communication • 🎬 AI-Powered Creativity**