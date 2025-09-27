# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Repository Overview

This is a **centralized brain service architecture** for an AI-powered movie generation platform. The key architectural principle is that **only the MCP Brain Service connects directly to external AI services (Jina) and databases (Neo4j)** - all other services communicate through standardized MCP (Model Context Protocol) WebSocket connections.

## Architecture Overview

The platform consists of a **monorepo with Git submodules** organizing multiple independent services that communicate through a central brain service:

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

### Key Services
- **MCP Brain Service** (Port 8002): Centralized AI/ML hub with 20+ MCP tools
- **LangGraph Orchestrator** (Port 8003): Workflow orchestration and agent coordination  
- **Auto-Movie Frontend** (Port 3010): Next.js React application
- **Celery Task Service** (Port 8001): Background task processing

## Development Commands

### Core Development Scripts

Since this is a **Windows PowerShell environment**, use these primary commands:

#### Submodule Management
```powershell
# Initialize all submodules (required for first setup)
git submodule update --init --recursive

# Add external repositories as submodules
pwsh scripts/add-submodules.ps1

# Update all submodules to latest
git submodule foreach --recursive git pull origin $(git rev-parse --abbrev-ref HEAD)
```

#### Service Development

**MCP Brain Service (Core - Start First):**
```powershell
cd services/mcp-brain-service
# Setup virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Run with development settings
python -m src.main
# Health check: http://localhost:8002/health
```

**LangGraph Orchestrator:**
```powershell
cd services/langgraph-orchestrator  
# Setup and run (requires brain service)
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run.py
```

**Auto-Movie Frontend:**
```powershell
cd apps/auto-movie
npm install
npm run dev
# Access: http://localhost:3010
```

#### Testing Commands

**Run Integration Tests:**
```powershell
# Quick health checks
python tests/run_integration_tests.py --suite fast

# Test brain service specifically  
python tests/run_integration_tests.py --suite brain_service

# Full test suite
python tests/run_integration_tests.py --suite all

# Generate comprehensive test report
python tests/run_integration_tests.py --generate-report
```

**Run Single Tests:**
```powershell
cd tests
python -m pytest integration/test_brain_service_integration.py -v
python -m pytest performance/test_mcp_websocket_performance.py -v
```

### Claude Flow Commands (Advanced Development)

This project uses **SPARC methodology** with Claude-Flow orchestration:

```powershell
# Core SPARC commands
npx claude-flow sparc modes                    # List available modes
npx claude-flow sparc run <mode> "<task>"      # Execute specific mode
npx claude-flow sparc tdd "<feature>"          # Run complete TDD workflow

# Batch processing
npx claude-flow sparc batch <modes> "<task>"   # Parallel execution
npx claude-flow sparc pipeline "<task>"        # Full pipeline processing
```

## Code Architecture & Patterns

### MCP Integration Pattern

**All services MUST use MCP WebSocket clients to communicate with the brain service.** Never connect directly to external services.

**Python MCP Client Pattern:**
```python
# services/[service]/src/clients/brain_client.py
class BrainServiceClient:
    def __init__(self, ws_url: str):
        self.ws_url = ws_url
        
    async def embed_text(self, text: str, project_id: str):
        return await self._call_tool("embed_text", {
            "text": text, "project_id": project_id
        })
```

**TypeScript MCP Client Pattern:**
```typescript  
// apps/auto-movie/src/lib/brain-client.ts
class BrainServiceClient {
    private ws: WebSocket;
    
    async embedText(text: string, projectId: string) {
        return this.callTool('embed_text', { text, project_id: projectId });
    }
}
```

### Project Isolation

All operations use `project_id` for multi-tenancy:
- Every MCP tool call requires `project_id`
- Data is logically isolated by project
- Use format: `"project-{identifier}"` 

### File Organization Rules

**Critical: Never save files to root directory** - use these subdirectories:
- `/services/` - Individual service codebases (as submodules)
- `/apps/` - Frontend applications (as submodules)  
- `/docs/` - Documentation and markdown files
- `/tests/` - All test files and test utilities
- `/scripts/` - Utility and setup scripts

### Data Models

The brain service uses comprehensive data models in `services/mcp-brain-service/src/models/knowledge.py`:
- `Document`, `EmbeddingResult`, `SearchResults`
- `GraphNode`, `GraphRelationship`, `QueryResults`  
- `WorkflowData`, `AgentMemory`

## Environment Configuration

### Required Environment Variables

**Core LLM Services (All Services):**
```bash
# OpenRouter (Primary LLM service)
OPENROUTER_API_KEY=sk-or-v1-your-openrouter-api-key
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_DEFAULT_MODEL=anthropic/claude-sonnet-4
OPENROUTER_BACKUP_MODEL=qwen/qwen3-vl-235b-a22b-thinking

# Fal.ai (Media generation)
FAL_KEY=your-fal-api-key
FAL_TEXT_TO_IMAGE_MODEL=fal-ai/nano-banana
FAL_IMAGE_TO_IMAGE_MODEL=fal-ai/nano-banana/edit

# ElevenLabs (Voice generation)
ELEVENLABS_API_KEY=sk_your-elevenlabs-api-key
```

**MCP Brain Service (Port 8002) - CRITICAL:**
```bash
JINA_API_KEY=jina_your-jina-api-key
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
MCP_SERVER_PORT=8002
```

**Service Communication:**
```bash
# LangGraph Orchestrator
BRAIN_SERVICE_BASE_URL=http://localhost:8002
BRAIN_SERVICE_WS_URL=ws://localhost:8002/mcp

# Auto-Movie Frontend  
NEXT_PUBLIC_BRAIN_SERVICE_URL=http://localhost:8002

# Celery Task Service
BRAIN_SERVICE_BASE_URL=http://localhost:8002
```

## Development Guidelines

### Service Startup Order

1. **Neo4j Database** (Port 7474) - Must be running first
2. **MCP Brain Service** (Port 8002) - Core service, start second
3. **Other services in any order** - All depend on brain service

### MCP Tools Available (20+)

The brain service provides these MCP tool categories:
- **Core Embedding**: `embed_text`, `batch_embed_texts`
- **Semantic Search**: `search_by_embedding`, `batch_similarity_search`
- **Document Storage**: `store_document`, `bulk_store_documents`
- **Knowledge Graph**: `create_relationship`, `query_graph`, `get_node_neighbors`
- **Workflow Integration**: `store_workflow_data`, `search_similar_workflows`
- **System**: `health_check`

### Debugging Common Issues

**LLM Service Issues:**
```powershell
# Test OpenRouter API connectivity
curl -H "Authorization: Bearer $env:OPENROUTER_API_KEY" https://openrouter.ai/api/v1/models

# Test Fal.ai service
curl -H "Authorization: Key $env:FAL_KEY" https://fal.run/fal-ai/models
```

**WebSocket Connection Issues:**
```powershell
# Check brain service health
curl http://localhost:8002/health

# Test WebSocket connection
curl --include --no-buffer --header "Connection: Upgrade" --header "Upgrade: websocket" http://localhost:8002/mcp
```

**Submodule Issues:**
```powershell
# Reset submodules
git submodule deinit --all
git submodule update --init --recursive

# Check submodule status
git submodule status
```

## Implementation Status

**Overall Progress: 65% Complete**

| Component | Status | Notes |
|-----------|--------|-------|
| MCP Brain Service | ✅ Complete | 100% - Production ready |
| LangGraph Orchestrator | 🔄 75% | Cleanup needed |
| Auto-Movie Frontend | ❌ 0% | Integration pending |
| Celery Task Service | ❌ 0% | Integration pending |
| Documentation | ✅ Complete | 100% |

### Current Focus Areas

1. **Complete LangGraph integration** - Remove Neo4j dependencies
2. **Implement TypeScript MCP client** - For auto-movie frontend
3. **Add Celery brain integration** - Background task storage
4. **Production deployment** - Docker orchestration

## Performance Characteristics

- **Embedding Generation**: <100ms average response time
- **Similarity Search**: <50ms for 10K+ documents  
- **WebSocket Connections**: Supports 100+ concurrent connections
- **Batch Processing**: 80% reduction in API calls vs individual requests

## Testing Strategy

The platform uses **comprehensive integration testing**:
- Service health and startup tests
- MCP WebSocket connectivity tests  
- Cross-service data flow validation
- Performance and load testing
- Knowledge graph consistency checks

Use `python tests/run_integration_tests.py --help` for all testing options.