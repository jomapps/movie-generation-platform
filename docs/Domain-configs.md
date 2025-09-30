# AI Movie Platform - Domain & Port Configuration

**Last Updated:** January 30, 2025  
**Status:** Production services marked with ✅ | Planned services marked with 📋

## 📌 Service Communication Protocols

### HTTP/WebSocket Services
These services have public URLs and listen on ports:
- ✅ **Auto-Movie App** - HTTP/WebSocket (port 3010)
- ✅ **Celery Task Service** - HTTP REST API (port 8001)
- ✅ **MCP Brain Service** - HTTP + WebSocket (port 8002)
- ✅ **LangGraph Orchestrator** - HTTP REST API (port 8003)

### stdio-based MCP Services (No Public URL)
These services use MCP stdio protocol (standard input/output) and do NOT have public URLs or listening ports:
- ✅ **MCP Story Service** - stdio only (no port, spawned by orchestrator)
- 📋 Other MCP services may follow this pattern

**Note:** stdio-based services are accessed by spawning the process and communicating via stdin/stdout, not via HTTP requests.

## Core Application Services

### 1. **Auto-Movie App** (Main Dashboard & PayloadCMS) ✅ LIVE
- **Protocol**: HTTP/WebSocket
- **Local**: `localhost:3010`
- **Dev**: `auto-movie.ngrok.pro` 
- **Prod**: `auto-movie.ft.tc`
- **Status**: ✅ Running (PM2: auto-movie)
- **Purpose**: Main user interface, PayloadCMS admin, prompt management, chat interface

### 2. **Celery Task Service** (GPU Processing) ✅ LIVE
- **Protocol**: HTTP REST API
- **Local**: `localhost:8001`
- **Dev**: `tasks.ngrok.pro`
- **Prod**: `tasks.ft.tc`
- **Status**: ✅ Running (PM2: celery-api, celery-worker)
- **Purpose**: Video/image generation, audio processing, heavy AI tasks

### 3. **MCP Brain Service** (Knowledge Graph) ✅ LIVE
- **Protocol**: HTTP + WebSocket
- **Local**: `localhost:8002`
- **Dev**: `brain.ngrok.pro`
- **Prod**: `brain.ft.tc`
- **Status**: ✅ Running (PM2: brain-api)
- **Purpose**: Jina v4 embeddings + Neo4j knowledge graph, MCP WebSocket endpoint

## Database & Infrastructure Services

### 4. **Neo4j Database Interface**
- **Local**: `localhost:7474` (HTTP), `localhost:7687` (Bolt)
- **Dev**: `neo4j.ngrok.pro`
- **Prod**: `neo4j.ft.tc` (admin interface only, internal bolt connection)
- **Purpose**: Graph database web interface for debugging

### 5. **Redis Insight** (Optional - Redis Management)
- **Local**: `localhost:8101`
- **Dev**: `redis.ngrok.pro`
- **Prod**: `redis.ft.tc`
- **Purpose**: Redis cache and queue monitoring

### 6. **MongoDB Express** (Optional - Database Admin)
- **Local**: `localhost:8102`
- **Dev**: `mongo.ngrok.pro`
- **Prod**: `mongo.ft.tc`
- **Purpose**: MongoDB administration interface

## Agent & Orchestration Services

### 7. **LangGraph Agent Orchestrator** ✅ LIVE
- **Protocol**: HTTP REST API
- **Local**: `localhost:8003`
- **Dev**: `agents.ngrok.pro`
- **Prod**: `agents.ft.tc`
- **Status**: ✅ Running (PM2: agents-api)
- **Purpose**: Agent workflow coordination, spawns stdio MCP services

### 8. **Domain-Specific MCP Servers** (Future Phases)

#### MCP Story Bible Service 📋 PLANNED
- **Protocol**: TBD (likely HTTP)
- **Local**: `localhost:8015`
- **Dev**: `story-bible.ngrok.pro`
- **Prod**: `story-bible.ft.tc`
- **Status**: 📋 Not deployed yet
- **Purpose**: Story bible management, world building, consistency tracking
- **Repo**: https://github.com/jomapps/mcp-story-bible-service.git

#### Story MCP Server ✅ LIVE
- **Protocol**: ⚠️ stdio-based MCP (NO public URL/port)
- **Local**: Spawned via `python -m src.mcp.server` (no port)
- **Dev**: N/A (stdio only)
- **Prod**: N/A (stdio only)
- **Status**: ✅ Running (PM2: mcp-story-service)
- **Purpose**: Story structure analysis, plot thread tracking, consistency validation
- **Access**: Via MCP stdio protocol (spawned by orchestrator)
- **Note**: This service does NOT listen on port 8010. Port reserved for future HTTP wrapper if needed.
- **Repo**: https://github.com/jomapps/mcp-story-service.git

#### Character MCP Server 📋 PLANNED
- **Protocol**: TBD (likely stdio-based)
- **Local**: `localhost:8011` (if HTTP) or stdio (if MCP)
- **Dev**: `character.ngrok.pro` (if HTTP)
- **Prod**: `character.ft.tc` (if HTTP)
- **Status**: 📋 Not deployed yet
- **Purpose**: Character creation, tracking, and consistency

#### Visual MCP Server 📋 PLANNED
- **Protocol**: TBD (likely HTTP for image generation)
- **Local**: `localhost:8012`
- **Dev**: `visual.ngrok.pro`
- **Prod**: `visual.ft.tc`
- **Status**: 📋 Not deployed yet
- **Purpose**: Storyboarding, image generation (FAL.ai integration)
- **Repo**: https://github.com/jomapps/mcp-visual-design-service.git

#### Audio MCP Server 📋 PLANNED
- **Protocol**: TBD (likely HTTP)
- **Local**: `localhost:8013`
- **Dev**: `audio.ngrok-free.dev`
- **Prod**: `audio.ft.tc` ⚠️ (fix domain - currently conflicts with story-architect.ft.tc)
- **Status**: 📋 Not deployed yet
- **Purpose**: Audio processing, TTS, music generation
- **Repo**: https://github.com/jomapps/mcp-audio-service.git

#### Asset MCP Server 📋 PLANNED
- **Protocol**: TBD (likely HTTP)
- **Local**: `localhost:8014`
- **Dev**: `asset.ngrok.pro`
- **Prod**: `asset.ft.tc`
- **Status**: 📋 Not deployed yet
- **Purpose**: 3D asset management and processing
- **Repo**: https://github.com/jomapps/mcp-3d-asset-service.git

## Monitoring & Analytics Services

### 9. **Prometheus Metrics**
- **Local**: `localhost:9090`
- **Dev**: `metrics.ngrok.pro`
- **Prod**: `metrics.ft.tc`
- **Purpose**: Performance monitoring and metrics collection

### 10. **Grafana Dashboard**
- **Local**: `localhost:3001`
- **Dev**: `dash-board.ngrok.pro`
- **Prod**: `dash-board.ft.tc`
- **Purpose**: Visual monitoring dashboards

### 11. **System Health API**
- **Local**: `localhost:8100`
- **Dev**: `health.ngrok.pro`
- **Prod**: `health.ft.tc`
- **Purpose**: Service health checks and status monitoring

## Media & CDN Services

### 12. **Media CDN** (Cloudflare R2 Custom Domain)
- **Dev**: `media-dev.ft.tc`
- **Prod**: `media.ft.tc`
- **Purpose**: Optimized media delivery for generated assets

### 13. **File Upload Proxy** (Optional)
- **Local**: `localhost:8200`
- **Dev**: `uploads.ngrok.pro`
- **Prod**: `uploads.ft.tc`
- **Purpose**: Direct file upload handling, bypassing main app

## Development & Testing Services

### 14. **API Documentation** (OpenAPI/Swagger)
- **Local**: `localhost:8300`
- **Dev**: `app-docs.ngrok.pro`
- **Prod**: `app-docs.ft.tc`
- **Purpose**: Interactive API documentation

### 15. **Test Environment**
- **Local**: `localhost:3011`
- **Dev**: `app-test.ngrok.pro`
- **Prod**: `app-test.ft.tc` (staging environment)
- **Purpose**: Isolated testing environment

## Port Allocation Summary

### **✅ Currently Running Services**
```bash
3010 - Auto-Movie App (Main)                    ✅ LIVE
8001 - Celery Task Service                      ✅ LIVE
8002 - MCP Brain Service                        ✅ LIVE
8003 - LangGraph Orchestrator                   ✅ LIVE
7474 - Neo4j HTTP Interface                     ✅ Available
7687 - Neo4j Bolt Protocol                      ✅ Available
6379 - Redis Server (db 0: brain, db 1: story) ✅ Available
27017 - MongoDB Server                          ✅ Available
N/A  - MCP Story Service (stdio, no port)      ✅ LIVE
```

### **📋 Reserved Ports (Not Yet Deployed)**
```bash
8010 - Story MCP (reserved, currently stdio)    📋 Reserved
8011 - Character MCP Server                     📋 Planned
8012 - Visual MCP Server                        📋 Planned
8013 - Audio MCP Server                         📋 Planned
8014 - Asset MCP Server                         📋 Planned
8015 - MCP Story Bible Service                  📋 Planned
9090 - Prometheus Metrics                       📋 Not installed
3001 - Grafana Dashboard                        📋 Not installed
8100 - Health Check API                         📋 Planned
8101 - Redis Insight                            📋 Optional
8102 - MongoDB Express                          📋 Optional
```

### **⚠️ Important Notes**
- **Port 8010**: Reserved but unused. Story Service uses stdio protocol (no port).
- **stdio Services**: Access via process spawn, not HTTP. No port needed.
- **Redis DB Allocation**: db 0 (Brain Service), db 1 (Story Service sessions)

### **Development Services**
```bash
8200 - Upload Proxy
8300 - API Documentation  
3011 - Test Environment
```

## Ngrok Configuration Commands

### Core Services Setup
```bash
# Auto-Movie App
ngrok http 3010 --domain=auto-movie.ngrok.pro

# Task Service
ngrok http 8001 --domain=tasks.ngrok.pro

# Brain Service  
ngrok http 8002 --domain=brain.ngrok.pro

# Neo4j Interface
ngrok http 7474 --domain=neo4j.ngrok.pro
```

### Extended Services
```bash
# Agent Orchestrator
ngrok http 8003 --domain=agents.ngrok.pro

# Domain MCP Servers
ngrok http 8015 --domain=story-bible.ngrok.pro
ngrok http 8010 --domain=story.ngrok.pro
ngrok http 8011 --domain=character.ngrok.pro
ngrok http 8012 --domain=visual.ngrok.pro
ngrok http 8013 --domain=audio.ngrok-free.dev
ngrok http 8014 --domain=asset.ngrok.pro

# Monitoring
ngrok http 9090 --domain=metrics.ngrok.pro
ngrok http 3001 --domain=dashboard.ngrok.pro
```

## Docker Compose Port Mapping

```yaml
# docker-compose.yml
version: '3.8'

services:
  auto-movie:
    ports:
      - "3010:3000"
    
  celery-api:
    ports:
      - "8001:8001"
      
  mcp-brain:
    ports:
      - "8002:8002"
      
  neo4j:
    ports:
      - "7474:7474"
      - "7687:7687"
      
  redis:
    ports:
      - "6379:6379"
      
  mongodb:
    ports:
      - "27017:27017"
```

## Environment Configuration

### **Auto-Movie App (.env)**
```bash
PORT=3000
PAYLOAD_PUBLIC_SERVER_URL=http://localhost:3010

# Development
NEXT_PUBLIC_TASK_SERVICE_URL=http://localhost:8001
NEXT_PUBLIC_BRAIN_SERVICE_URL=http://localhost:8002

# Production URLs  
NEXT_PUBLIC_TASK_SERVICE_URL=https://tasks.ft.tc
NEXT_PUBLIC_BRAIN_SERVICE_URL=https://brain.ft.tc
```

### **Service Discovery Configuration**
```typescript
// src/config/services.ts
const serviceUrls = {
  development: {
    autoMovie: 'http://localhost:3010',
    taskService: 'http://localhost:8001', 
    brainService: 'http://localhost:8002',
    neo4j: 'http://localhost:7474',
  },
  staging: {
    autoMovie: 'https://auto-movie.ngrok.pro',
    taskService: 'https://tasks.ngrok.pro',
    brainService: 'https://brain.ngrok.pro', 
    neo4j: 'https://neo4j.ngrok.pro',
  },
  production: {
    autoMovie: 'https://auto-movie.ft.tc',
    taskService: 'https://tasks.ft.tc',
    brainService: 'https://brain.ft.tc',
    neo4j: 'https://neo4j.ft.tc',
  }
}
```

## 🎯 Current Platform Status (January 30, 2025)

### Services Running in Production

| Service | Type | Port | Protocol | PM2 Name | Status |
|---------|------|------|----------|----------|--------|
| Auto-Movie App | Frontend | 3010 | HTTP/WebSocket | auto-movie | ✅ Online |
| Celery API | Task Queue | 8001 | HTTP REST | celery-api | ✅ Online |
| Celery Worker | Background | - | Internal | celery-worker | ✅ Online |
| Brain Service | Knowledge | 8002 | HTTP + WS | brain-api | ✅ Online |
| Orchestrator | Coordination | 8003 | HTTP REST | agents-api | ✅ Online |
| Story Service | Story Analysis | N/A | stdio MCP | mcp-story-service | ✅ Online |

**Total:** 6 services running (5 HTTP services + 1 stdio service)

### Services Ready to Deploy (Priority Order)

1. **Character Service** (port 8011) - Needs PayloadCMS API key
2. **Visual Service** (port 8012) - Needs FAL + OpenRouter API keys
3. **Story Bible Service** (port 8015) - Needs PayloadCMS API key

### Deployment Progress

- **Core Platform:** ✅ 100% Complete (all HTTP services live)
- **MCP Services:** 🔄 20% Complete (1 of 5 domain services deployed)
- **MVP Pipeline:** 🔄 30% Complete (story pipeline unblocked)

---

This gives you a complete, scalable domain architecture that grows with your platform development phases!

## 📚 Related Documentation

- **Fast-Pace Development:** `/docs/fast-pace-development.md` - MVP deployment plan
- **Story Service Guide:** `/services/mcp-story-service/DEPLOY.md` - Deployment details
- **Platform Secrets:** `/docs/platform-secrets-and-startup.md` - All service configurations