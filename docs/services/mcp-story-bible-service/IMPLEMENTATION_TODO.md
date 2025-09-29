# MCP Story Bible Service - Implementation Checklist

**Status**: Service structure created, implementation needed  
**Priority**: High - Critical for story bible functionality

## 🚨 **CRITICAL ARCHITECTURE UPDATE**

**✅ CONFIRMED**: This service now uses **PayloadCMS** (Auto-Movie App) as the single source of truth for data storage. **No separate database required.**

## 🎯 **Implementation Phases**

### **Phase 1: Core Infrastructure** (Week 1)

#### **PayloadCMS Integration Layer**
- [ ] **`src/services/payload_service.py`** - PayloadCMS API client with full CRUD operations
- [ ] **`src/models/story_bible.py`** - Pydantic models for API validation (not SQLAlchemy)
- [ ] **`src/models/character.py`** - Character and relationship Pydantic models
- [ ] **`src/models/scene.py`** - Scene and plot thread Pydantic models
- [ ] **PayloadCMS Collections Setup** - Coordinate with Auto-Movie team to create:
  - [ ] `story-bibles` collection
  - [ ] `story-bible-characters` collection
  - [ ] `character-relationships` collection
  - [ ] `story-bible-scenes` collection
  - [ ] `plot-threads` collection

#### **API Routes** 
- [ ] **`src/routes/health.py`** - Health check endpoints
- [ ] **`src/routes/api.py`** - REST API for story bibles
- [ ] **`src/routes/mcp.py`** - MCP WebSocket server
- [ ] **`src/middleware/auth.py`** - Authentication middleware
- [ ] **`src/middleware/cors.py`** - CORS configuration

#### **Core Services**
- [ ] **`src/services/story_bible_service.py`** - Business logic with PayloadCMS integration
- [ ] **`src/services/brain_client.py`** - Brain service MCP client
- [ ] **`src/config.py`** - Update with PayloadCMS configuration
- [ ] **`src/middleware/auth.py`** - Bearer token authentication (consistent with Auto-Movie)

### **Phase 2: MCP Implementation** (Week 2)

#### **MCP Protocol Integration**
- [ ] **WebSocket Server Setup** - MCP protocol WebSocket handling
- [ ] **Tool Registration** - Register all MCP tools with server
- [ ] **Request Router** - Route MCP requests to appropriate handlers
- [ ] **Response Formatter** - Format responses according to MCP spec
- [ ] **Error Handling** - MCP-compliant error responses

#### **MCP Tools Implementation**
```python
# All these need full implementation:
- [ ] create_story_bible()
- [ ] get_story_bible()  
- [ ] update_story_bible()
- [ ] add_character()
- [ ] generate_character_arc()
- [ ] create_story_outline()
- [ ] add_scene()
- [ ] track_plot_thread()
- [ ] validate_story_consistency()
- [ ] suggest_scene_transitions()
- [ ] generate_story_bible_export()
```

#### **Brain Service Integration**
- [ ] **MCP Client Connection** - WebSocket connection to Brain Service
- [ ] **Authentication** - Handle Brain Service authentication
- [ ] **Tool Calling** - Call Brain Service MCP tools
- [ ] **Response Processing** - Handle Brain Service responses
- [ ] **Error Recovery** - Fallback when Brain Service unavailable

### **Phase 3: Authentication & Security** (Week 3)

#### **Authentication Standardization**
**✅ DECISION MADE**: Use `Authorization: Bearer <token>` to match Auto-Movie App and PayloadCMS

```python
# STANDARDIZED: Use Bearer token authentication
headers = {"Authorization": "Bearer jwt-token-here"}

# Validate with PayloadCMS API
response = await client.get(
    f"{settings.PAYLOADCMS_API_URL}/api/users/me",
    headers={"Authorization": f"Bearer {token}"}
)
```

- [ ] **Implement Bearer Token Auth** - Validate tokens with PayloadCMS
- [ ] **Auth Middleware** - Consistent with Auto-Movie App pattern
- [ ] **Update Documentation** - Remove X-API-Key references
- [ ] **Client Integration** - Use Bearer tokens for all API calls

#### **Security Implementation**
- [ ] **Project Isolation** - Ensure story bibles are project-scoped via PayloadCMS
- [ ] **Input Validation** - Validate all API inputs with Pydantic models
- [ ] **PayloadCMS Security** - Rely on PayloadCMS built-in security features
- [ ] **Rate Limiting** - Prevent API abuse
- [ ] **CORS Configuration** - Secure cross-origin requests

### **Phase 4: Testing** (Week 4)

#### **Test Infrastructure**
- [ ] **`tests/conftest.py`** - Test configuration and fixtures
- [ ] **`tests/unit/`** - Unit tests for all services
- [ ] **`tests/integration/`** - Integration tests with Brain Service
- [ ] **`tests/mcp/`** - MCP protocol tests
- [ ] **`scripts/test_mcp_tools.py`** - MCP tools testing script

#### **Test Coverage**
- [ ] **PayloadCMS Integration** - CRUD operations testing via API
- [ ] **MCP Tools** - All tool functions tested
- [ ] **Brain Service Integration** - Mock and real integration tests
- [ ] **Bearer Token Auth** - Auth middleware testing
- [ ] **Error Handling** - Error scenario testing

### **Phase 5: Production Deployment** (Week 5)

#### **Production Configuration**
- [ ] **Environment Variables** - PayloadCMS API URL and credentials
- [ ] **Docker Production** - Production Docker setup (no database needed)
- [ ] **PayloadCMS Collections** - Ensure collections exist in production
- [ ] **Monitoring** - Prometheus metrics implementation
- [ ] **Logging** - Structured logging setup

#### **Deployment Scripts**
- [ ] **CI/CD Pipeline** - GitHub Actions workflow
- [ ] **Health Checks** - Production health monitoring
- [ ] **Backup Strategy** - Database backup configuration
- [ ] **Scaling Configuration** - Load balancing setup

## 🔧 **Critical Missing Files**

### **Immediate Implementation Needed:**

1. **`src/services/payload_service.py`** - PayloadCMS API Client
```python
import httpx
from typing import Dict, List, Optional
from ..config import settings

class PayloadCMSService:
    def __init__(self):
        self.base_url = settings.PAYLOADCMS_API_URL
        self.api_key = settings.PAYLOADCMS_API_KEY
        
    async def create_story_bible(self, data: Dict) -> Dict:
        """Create new story bible in PayloadCMS"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/story-bibles",
                json=data,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
            )
            response.raise_for_status()
            return response.json()
```

2. **`src/models/story_bible.py`** - Pydantic Models
```python
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime

class StoryBibleCreate(BaseModel):
    project_id: str = Field(..., description="Project identifier")
    title: str = Field(..., min_length=1, max_length=200)
    genre: str = Field(..., description="Story genre")
    premise: str = Field(..., min_length=10, description="Core story premise")
    logline: Optional[str] = Field(None, max_length=300)

class StoryBible(BaseModel):
    id: str
    project_id: str
    title: str
    genre: str
    premise: str
    status: Literal['draft', 'in_progress', 'completed']
    created_at: datetime
    updated_at: datetime
```

3. **`src/services/story_bible_service.py`** - Business Logic
```python
from typing import List, Optional, Dict
from ..services.payload_service import PayloadCMSService
from ..services.brain_client import BrainServiceClient

class StoryBibleService:
    def __init__(self, payload_service: PayloadCMSService, brain_client: BrainServiceClient):
        self.payload_service = payload_service
        self.brain_client = brain_client
    
    async def create_story_bible(self, project_id: str, title: str, genre: str, premise: str) -> str:
        """Create story bible via PayloadCMS"""
        data = {
            "project_id": project_id,
            "title": title,
            "genre": genre,
            "premise": premise,
            "status": "draft"
        }
        result = await self.payload_service.create_story_bible(data)
        return result["id"]
```

3. **`src/routes/mcp.py`**
```python
from fastapi import WebSocket, WebSocketDisconnect
from ..services.story_bible_service import StoryBibleService

class MCPWebSocketHandler:
    def __init__(self, story_service: StoryBibleService):
        self.story_service = story_service
        
    async def handle_connection(self, websocket: WebSocket):
        # MCP protocol implementation needed
        pass
```

## ✅ **CRITICAL DECISIONS RESOLVED**

1. **✅ Authentication Standard**: Bearer token authentication (matches Auto-Movie App)
2. **✅ Data Storage**: PayloadCMS collections (no separate database needed)
3. **⏳ MCP Protocol Version**: Latest MCP specification to implement
4. **⏳ Brain Service Integration**: WebSocket MCP client connection strategy
5. **⏳ Error Handling**: Service failure and recovery strategies

## 🚨 **CRITICAL DEPENDENCIES**

**PREREQUISITE**: PayloadCMS collections must be created in Auto-Movie App first:
- [ ] `story-bibles` collection
- [ ] `story-bible-characters` collection  
- [ ] `character-relationships` collection
- [ ] `story-bible-scenes` collection
- [ ] `plot-threads` collection

## 📋 **Updated Summary**

**Major Architecture Change**: Now uses PayloadCMS instead of separate database

- **~70% structure complete** (Docker, configs, architecture decisions)
- **~30% core implementation needed** (MCP tools, PayloadCMS integration)
- **✅ Authentication issue resolved** - Bearer tokens standard
- **Estimated 3-4 weeks** for full production implementation (reduced due to no database setup)

**Next Steps**: 
1. Create PayloadCMS collections
2. Implement PayloadCMS service layer
3. Build MCP tools on top of PayloadCMS
