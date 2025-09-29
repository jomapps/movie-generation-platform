# MCP Story Bible Service - Complete Implementation Specification

**Version**: 1.0  
**Last Updated**: January 28, 2025  
**Status**: Ready for Implementation  
**Priority**: High - Core Platform Service

---

## 🚨 **CRITICAL ARCHITECTURE DECISION**

**✅ CONFIRMED**: The MCP Story Bible Service will use **PayloadCMS** (via Auto-Movie App) as the **single source of truth** for all data storage. This eliminates the need for a separate PostgreSQL database and ensures data consistency across the platform.

### **Data Flow Architecture**:
```
MCP Story Bible Service → PayloadCMS API → MongoDB (Auto-Movie App)
                      ↓
              All story bible data stored
              in PayloadCMS collections
```

---

## 📋 **Table of Contents**

1. [Service Overview](#service-overview)
2. [PayloadCMS Integration](#payloadcms-integration)
3. [MCP Tools Specification](#mcp-tools-specification)
4. [API Specifications](#api-specifications)
5. [Authentication Architecture](#authentication-architecture)
6. [Data Models](#data-models)
7. [Implementation Roadmap](#implementation-roadmap)
8. [File Structure](#file-structure)
9. [Testing Strategy](#testing-strategy)
10. [Deployment Configuration](#deployment-configuration)

---

## 🎯 **Service Overview**

### **Core Purpose**
The MCP Story Bible Service manages comprehensive story bibles for movie projects through:
- **Story Structure Management**: Outlines, plots, themes, character arcs
- **Character Development**: Backgrounds, motivations, relationships
- **Scene Organization**: Sequences, locations, dialogue notes
- **Plot Consistency**: AI-powered validation and continuity checking
- **Export Capabilities**: Multiple format generation (PDF, DOCX, JSON)

### **Integration Points**
- **PayloadCMS**: Primary data storage via REST API
- **MCP Brain Service**: AI features (Jina v4 embeddings, Neo4j knowledge graph)
- **LangGraph Orchestrator**: Workflow coordination and agent collaboration
- **Auto-Movie Frontend**: Real-time collaborative editing interface

### **Service Configuration**
- **Local Development**: `localhost:8015`
- **Development**: `story-bible.ngrok.pro`
- **Production**: `story-bible.ft.tc`
- **Metrics**: `localhost:9015` (Prometheus)

## 🏗️ **System Architecture**

### **Service Integration Pattern**
```
┌─────────────────┐    MCP WebSocket    ┌────────────────────┐
│   LangGraph     │◄──────────────────►│  Story Bible       │
│   Orchestrator  │                    │  Service           │
└─────────────────┘                    └────────────────────┘
                                                │
                                                │ REST API
                                                ▼
┌─────────────────┐    WebSocket/HTTP   ┌────────────────────┐
│   Auto-Movie    │◄──────────────────►│    PayloadCMS      │
│   Frontend      │                    │   (Auto-Movie)     │
└─────────────────┘                    └────────────────────┘
                                                │
                                                │ MongoDB
                                                ▼
                                       ┌────────────────────┐
                                       │   Story Bible      │
                                       │   Collections      │
                                       └────────────────────┘
                                                ▲
                                                │ REST API
┌─────────────────┐    MCP WebSocket    ┌────────────────────┐
│  Story Bible    │◄──────────────────►│  MCP Brain         │
│   Service       │                    │  Service           │
└─────────────────┘                    └────────────────────┘
                                                │
                                                │ Neo4j/Jina v4
                                                ▼
                                       ┌────────────────────┐
                                       │  Knowledge Graph   │
                                       │  & Embeddings      │
                                       └────────────────────┘
```

### **Data Flow Architecture**
```
1. Frontend Request → Story Bible Service (MCP Tools)
2. Story Bible Service → PayloadCMS API (CRUD Operations)
3. PayloadCMS → MongoDB (Data Persistence)
4. Story Bible Service → Brain Service (AI Analysis)
5. Brain Service → Neo4j/Jina v4 (Knowledge & Embeddings)
6. Results → Frontend (Real-time Updates)
```

### **Key Integration Points**
- **PayloadCMS REST API**: All story bible data storage and retrieval
- **MCP Brain Service**: AI-powered analysis and semantic search
- **WebSocket Connections**: Real-time collaboration and updates
- **Bearer Token Authentication**: Unified auth across all services

---

## 💾 **PayloadCMS Integration**

### **🔄 Data Storage Strategy**

**DECISION**: Instead of separate PostgreSQL, all story bible data will be stored in PayloadCMS collections accessible via the Auto-Movie App's API.

#### **PayloadCMS Collection Requirements**

**1. Story Bibles Collection** - `story-bibles`
```typescript
interface StoryBible {
  id: string;
  project_id: string;        // Links to existing project
  title: string;
  genre: string;
  premise: string;
  logline?: string;
  treatment?: string;
  themes: string[];          // Array of theme strings
  status: 'draft' | 'in_progress' | 'completed';
  created_at: Date;
  updated_at: Date;
  created_by: string;        // User ID
  
  // Relationships
  characters: Character[];   // Has many characters
  scenes: Scene[];          // Has many scenes  
  plot_threads: PlotThread[]; // Has many plot threads
}
```

**2. Characters Collection** - `story-bible-characters`
```typescript
interface Character {
  id: string;
  story_bible: string;       // Relationship to story bible
  name: string;
  role: 'protagonist' | 'antagonist' | 'supporting' | 'minor';
  background: string;
  motivation: string;
  arc_description: string;
  physical_description?: string;
  personality_traits: string[];
  dialogue_style?: string;
  created_at: Date;
  updated_at: Date;
  
  // Relationships
  relationships: CharacterRelationship[]; // Has many relationships
  scenes: Scene[];          // Many to many with scenes
}
```

**3. Character Relationships Collection** - `character-relationships`
```typescript
interface CharacterRelationship {
  id: string;
  character_from: string;    // Character ID
  character_to: string;      // Character ID
  relationship_type: string; // 'family', 'friend', 'enemy', 'romantic', etc.
  description: string;
  strength: number;          // 1-10 relationship strength
  story_bible: string;       // Parent story bible
}
```

**4. Scenes Collection** - `story-bible-scenes`
```typescript
interface Scene {
  id: string;
  story_bible: string;       // Relationship to story bible
  sequence_number: number;
  title: string;
  location: string;
  time_of_day: 'dawn' | 'morning' | 'afternoon' | 'evening' | 'night';
  scene_purpose: 'setup' | 'conflict' | 'resolution' | 'character_development' | 'plot_advancement';
  description: string;
  dialogue_notes?: string;
  emotional_beats: string[];
  estimated_duration?: number; // In seconds
  created_at: Date;
  updated_at: Date;
  
  // Relationships
  characters_present: Character[]; // Many to many
  plot_threads: PlotThread[];      // Many to many
}
```

**5. Plot Threads Collection** - `plot-threads`
```typescript
interface PlotThread {
  id: string;
  story_bible: string;       // Relationship to story bible
  thread_name: string;
  thread_type: 'main_plot' | 'subplot' | 'character_arc' | 'theme';
  description: string;
  introduction_scene?: string; // Scene ID where introduced
  resolution_scene?: string;   // Scene ID where resolved
  status: 'active' | 'resolved' | 'abandoned';
  created_at: Date;
  updated_at: Date;
  
  // Relationships
  key_scenes: Scene[];       // Many to many
}
```

### **PayloadCMS API Integration**

#### **Service Layer for PayloadCMS Communication**
```python
# src/services/payload_service.py
import httpx
from typing import List, Dict, Optional
from ..config import settings

class PayloadCMSService:
    def __init__(self):
        self.base_url = settings.PAYLOADCMS_API_URL  # Auto-Movie App API
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
    
    async def get_story_bible(self, story_bible_id: str) -> Dict:
        """Get story bible with all relationships"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/story-bibles/{story_bible_id}",
                params={"populate": "characters,scenes,plot_threads"},
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            response.raise_for_status()
            return response.json()
    
    async def create_character(self, data: Dict) -> Dict:
        """Create character in story bible"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/story-bible-characters",
                json=data,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
            )
            response.raise_for_status()
            return response.json()
    
    # Additional CRUD methods for all collections...
```

### **Configuration Updates Required**
```bash
# .env updates needed
PAYLOADCMS_API_URL=http://localhost:3010  # Auto-Movie App URL
PAYLOADCMS_API_KEY=your-payload-api-key-here

# Production
PAYLOADCMS_API_URL=https://auto-movie.ft.tc
```

---

## 🛠️ **MCP Tools Specification**

### **Core Story Bible Management Tools**

#### **1. `create_story_bible`**
```python
async def create_story_bible(
    project_id: str,
    title: str, 
    genre: str,
    premise: str,
    logline: Optional[str] = None
) -> str:
    """
    Creates a new story bible in PayloadCMS
    
    Args:
        project_id: Project identifier
        title: Story title
        genre: Story genre (action, drama, comedy, etc.)
        premise: Core story premise
        logline: Optional one-line story summary
        
    Returns:
        str: Story bible ID
        
    Implementation:
        1. Validate project access
        2. Create story bible record in PayloadCMS
        3. Initialize with default structure
        4. Store initial data in Brain Service for AI features
        5. Return story bible ID
    """
```

#### **2. `get_story_bible`**
```python
async def get_story_bible(story_bible_id: str) -> Dict:
    """
    Retrieves complete story bible with all relationships
    
    Returns:
        Dict: Complete story bible data including:
        - Basic info (title, genre, premise)
        - All characters with relationships
        - All scenes with sequence
        - All plot threads with status
        - Consistency validation results
    """
```

#### **3. `add_character`**
```python
async def add_character(
    story_bible_id: str,
    character_data: Dict
) -> str:
    """
    Adds character to story bible
    
    Args:
        story_bible_id: Parent story bible
        character_data: Character information including:
            - name: Character name
            - role: protagonist/antagonist/supporting/minor
            - background: Character history
            - motivation: What drives the character
            - arc_description: Character development arc
            - physical_description: Appearance details
            - personality_traits: Array of traits
            
    Returns:
        str: Character ID
        
    Implementation:
        1. Validate story bible exists and user has access
        2. Check for character name conflicts
        3. Create character in PayloadCMS
        4. Generate embedding for semantic search via Brain Service
        5. Create initial relationships if specified
    """
```

#### **4. `create_story_outline`**
```python
async def create_story_outline(
    story_bible_id: str,
    outline_data: Dict
) -> str:
    """
    Creates structured story outline
    
    Args:
        outline_data: Outline structure including:
            - act_structure: "three_act", "five_act", "hero_journey"
            - genre_conventions: Array of genre elements
            - plot_points: Array of key story beats
            - estimated_runtime: Target length in minutes
            - target_audience: Intended audience
            
    Implementation:
        1. Validate outline structure
        2. Create plot threads for major story beats
        3. Generate scene templates based on structure
        4. Use Brain Service for genre convention validation
        5. Store outline metadata in story bible
    """
```

#### **5. `add_scene`**
```python
async def add_scene(
    story_bible_id: str,
    scene_data: Dict
) -> str:
    """
    Adds scene to story bible
    
    Args:
        scene_data: Scene information including:
            - sequence_number: Order in story
            - title: Scene title/description
            - location: Where scene takes place
            - time_of_day: When scene occurs
            - characters_present: Array of character IDs
            - scene_purpose: Story function of scene
            - description: Detailed scene description
            - dialogue_notes: Key dialogue points
            - emotional_beats: Emotional journey
            - estimated_duration: Length in seconds
            
    Implementation:
        1. Validate scene data and story bible access
        2. Check sequence number conflicts
        3. Create scene in PayloadCMS
        4. Link to specified characters
        5. Update related plot threads
        6. Generate scene embedding for similarity search
    """
```

### **AI-Powered Analysis Tools**

#### **6. `validate_story_consistency`**
```python
async def validate_story_consistency(story_bible_id: str) -> Dict:
    """
    AI-powered story consistency validation
    
    Returns:
        Dict: Consistency report including:
            - consistency_score: 0.0-1.0 overall score
            - plot_holes: Array of identified issues
            - character_inconsistencies: Character behavior conflicts
            - timeline_issues: Chronological problems
            - thematic_conflicts: Theme contradictions
            - suggestions: AI-generated improvement suggestions
            
    Implementation:
        1. Retrieve complete story bible from PayloadCMS
        2. Send story data to Brain Service for AI analysis
        3. Use LLM to identify plot holes and inconsistencies
        4. Check character behavior patterns
        5. Validate timeline and causality
        6. Generate actionable improvement suggestions
    """
```

#### **7. `generate_character_arc`**
```python
async def generate_character_arc(
    character_id: str,
    story_context: Optional[str] = None
) -> Dict:
    """
    AI-assisted character development arc generation
    
    Returns:
        Dict: Character arc including:
            - development_stages: Key character growth points
            - emotional_journey: Character's emotional progression
            - relationship_evolution: How relationships change
            - skill_progression: Character abilities development
            - internal_conflict: Character's inner struggle
            - resolution: How character grows/changes
            
    Implementation:
        1. Get character data from PayloadCMS
        2. Analyze story context and genre conventions
        3. Use Brain Service LLM for arc generation
        4. Validate arc against story structure
        5. Suggest specific scenes for arc development
    """
```

#### **8. `suggest_scene_transitions`**
```python
async def suggest_scene_transitions(
    story_bible_id: str,
    scene_id: str
) -> List[Dict]:
    """
    AI-powered scene flow optimization
    
    Returns:
        List[Dict]: Transition suggestions including:
            - transition_type: "cut", "fade", "montage", etc.
            - pacing_notes: Rhythm and timing suggestions
            - emotional_bridge: How emotions connect
            - visual_continuity: Visual flow considerations
            - dialogue_hooks: Connecting dialogue elements
            
    Implementation:
        1. Get scene and surrounding context
        2. Analyze genre and pacing requirements
        3. Use Brain Service for transition analysis
        4. Generate multiple transition options
        5. Rank by effectiveness and genre appropriateness
    """
```

### **Export and Collaboration Tools**

#### **9. `generate_story_bible_export`**
```python
async def generate_story_bible_export(
    story_bible_id: str,
    format: str,  # "pdf", "docx", "markdown", "json"
    sections: Optional[List[str]] = None
) -> bytes:
    """
    Exports story bible in specified format
    
    Args:
        format: Export format
        sections: Optional specific sections to include
        
    Returns:
        bytes: Generated document
        
    Implementation:
        1. Retrieve complete story bible from PayloadCMS
        2. Apply formatting templates based on format
        3. Generate document with proper styling
        4. Include charts, character maps if requested
        5. Return formatted document
    """
```

#### **10. `track_story_bible_changes`**
```python
async def track_story_bible_changes(
    story_bible_id: str,
    user_id: str,
    changes: Dict
) -> bool:
    """
    Version control and change tracking
    
    Implementation:
        1. Store change metadata in PayloadCMS
        2. Track user attribution
        3. Enable rollback functionality
        4. Notify collaborators of changes
    """
```

---

## 🔐 **Authentication Architecture**

### **🚨 CRITICAL DECISION: Platform Authentication Standard**

**RECOMMENDATION**: Standardize on **`Authorization: Bearer <token>`** across all services to match Auto-Movie App pattern.

#### **Authentication Flow**
```
1. User authenticates with Auto-Movie App (PayloadCMS)
2. Receives JWT token
3. MCP Story Bible Service validates token via PayloadCMS API
4. All subsequent requests use Bearer token
```

#### **Implementation**
```python
# src/middleware/auth.py
from fastapi import HTTPException, Header, Depends
from typing import Optional
import httpx
from ..config import settings

async def verify_bearer_token(authorization: Optional[str] = Header(None)) -> Dict:
    """
    Verify JWT Bearer token with PayloadCMS
    
    Args:
        authorization: "Bearer <token>" header value
        
    Returns:
        Dict: User information from PayloadCMS
        
    Raises:
        HTTPException: 401 if token invalid
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Bearer token required in Authorization header"
        )
    
    token = authorization.replace("Bearer ", "")
    
    # Validate token with PayloadCMS
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.PAYLOADCMS_API_URL}/api/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired token"
            )
            
        return response.json()
```

### **Project Access Control**
```python
async def verify_project_access(project_id: str, user: Dict) -> bool:
    """
    Verify user has access to project via PayloadCMS
    """
    # Check project membership in PayloadCMS
    # Implementation depends on PayloadCMS project structure
```

---

## 📊 **Data Models**

### **Pydantic Models for API Validation**

```python
# src/models/story_bible.py
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime

class StoryBibleCreate(BaseModel):
    project_id: str = Field(..., description="Project identifier")
    title: str = Field(..., min_length=1, max_length=200)
    genre: str = Field(..., description="Story genre")
    premise: str = Field(..., min_length=10, description="Core story premise")
    logline: Optional[str] = Field(None, max_length=300, description="One-line summary")

class StoryBible(BaseModel):
    id: str
    project_id: str
    title: str
    genre: str
    premise: str
    logline: Optional[str]
    treatment: Optional[str]
    themes: List[str]
    status: Literal['draft', 'in_progress', 'completed']
    created_at: datetime
    updated_at: datetime
    created_by: str
    
    # Populated relationships
    characters: Optional[List['Character']]
    scenes: Optional[List['Scene']]
    plot_threads: Optional[List['PlotThread']]

class CharacterCreate(BaseModel):
    story_bible_id: str
    name: str = Field(..., min_length=1, max_length=100)
    role: Literal['protagonist', 'antagonist', 'supporting', 'minor']
    background: str = Field(..., min_length=10)
    motivation: str = Field(..., min_length=5)
    arc_description: str = Field(..., min_length=10)
    physical_description: Optional[str] = None
    personality_traits: List[str] = Field(default_factory=list)
    dialogue_style: Optional[str] = None

class Character(BaseModel):
    id: str
    story_bible_id: str
    name: str
    role: str
    background: str
    motivation: str
    arc_description: str
    physical_description: Optional[str]
    personality_traits: List[str]
    dialogue_style: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    # Relationships
    relationships: Optional[List['CharacterRelationship']]

class SceneCreate(BaseModel):
    story_bible_id: str
    sequence_number: int = Field(..., ge=1)
    title: str = Field(..., min_length=1, max_length=200)
    location: str = Field(..., min_length=1)
    time_of_day: Literal['dawn', 'morning', 'afternoon', 'evening', 'night']
    scene_purpose: Literal['setup', 'conflict', 'resolution', 'character_development', 'plot_advancement']
    description: str = Field(..., min_length=10)
    dialogue_notes: Optional[str] = None
    emotional_beats: List[str] = Field(default_factory=list)
    estimated_duration: Optional[int] = Field(None, ge=1, description="Duration in seconds")
    characters_present: List[str] = Field(default_factory=list, description="Character IDs")

class Scene(BaseModel):
    id: str
    story_bible_id: str
    sequence_number: int
    title: str
    location: str
    time_of_day: str
    scene_purpose: str
    description: str
    dialogue_notes: Optional[str]
    emotional_beats: List[str]
    estimated_duration: Optional[int]
    created_at: datetime
    updated_at: datetime
    
    # Relationships
    characters_present: Optional[List[Character]]
    plot_threads: Optional[List['PlotThread']]

# Additional models for PlotThread, CharacterRelationship, etc.
```

---

## 🗂️ **File Structure**

```
services/mcp-story-bible-service/
├── README.md
├── IMPLEMENTATION_SPECIFICATION.md  # This document
├── requirements.txt
├── .env.example
├── docker-compose.yml
├── Dockerfile
├── .gitignore
├── pyproject.toml
├── pytest.ini
│
├── src/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app entry point
│   ├── config.py                  # Settings and configuration
│   │
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── auth.py               # Bearer token authentication
│   │   ├── cors.py               # CORS configuration
│   │   └── project_isolation.py  # Project access control
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── health.py             # Health check endpoints
│   │   ├── api.py                # REST API routes
│   │   └── mcp.py                # MCP WebSocket server
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── payload_service.py     # PayloadCMS API client
│   │   ├── brain_client.py       # MCP Brain Service client
│   │   ├── story_bible_service.py # Core business logic
│   │   └── export_service.py     # Document export functionality
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── story_bible.py        # Story bible Pydantic models
│   │   ├── character.py          # Character models
│   │   ├── scene.py              # Scene models
│   │   └── responses.py          # API response models
│   │
│   ├── mcp/
│   │   ├── __init__.py
│   │   ├── server.py             # MCP WebSocket server
│   │   ├── tools.py              # MCP tool implementations
│   │   └── protocol.py           # MCP protocol handlers
│   │
│   └── utils/
│       ├── __init__.py
│       ├── validation.py         # Input validation utilities
│       ├── formatting.py         # Data formatting helpers
│       └── exceptions.py         # Custom exception classes
│
├── tests/
│   ├── conftest.py               # Test configuration
│   ├── unit/
│   │   ├── test_services/
│   │   ├── test_models/
│   │   └── test_utils/
│   ├── integration/
│   │   ├── test_payloadcms/
│   │   ├── test_brain_service/
│   │   └── test_mcp_tools/
│   └── mcp/
│       ├── test_protocol/
│       └── test_websocket/
│
├── scripts/
│   ├── test_mcp_tools.py         # MCP tools testing
│   ├── setup_collections.py     # PayloadCMS collection setup
│   └── validate_integration.py  # Integration validation
│
└── docs/
    ├── api_reference.md
    ├── mcp_tools.md
    └── deployment.md
```

---

## 🚀 **Implementation Roadmap**

### **Phase 1: Foundation (Week 1)**
**Goal**: Core infrastructure and PayloadCMS integration

#### **Day 1-2: Project Setup**
- [ ] Initialize project structure
- [ ] Configure development environment
- [ ] Set up PayloadCMS collections (coordinate with Auto-Movie team)
- [ ] Implement basic FastAPI application structure

#### **Day 3-4: PayloadCMS Integration**
- [ ] Implement `PayloadCMSService` class
- [ ] Create CRUD operations for all collections
- [ ] Set up authentication middleware with Bearer tokens
- [ ] Implement project access control

#### **Day 5-7: Core Services**
- [ ] Implement `StoryBibleService` with basic CRUD
- [ ] Set up health check endpoints
- [ ] Implement basic REST API routes
- [ ] Add comprehensive error handling

### **Phase 2: MCP Implementation (Week 2)**
**Goal**: MCP protocol integration and tool implementation

#### **Day 1-3: MCP Server Setup**
- [ ] Implement MCP WebSocket server
- [ ] Set up MCP protocol handling
- [ ] Create tool registration system
- [ ] Implement request/response routing

#### **Day 4-7: MCP Tools Implementation**
- [ ] Implement all core MCP tools (create_story_bible, add_character, etc.)
- [ ] Add Brain Service client for AI features
- [ ] Implement story consistency validation
- [ ] Add character arc generation

### **Phase 3: AI Integration (Week 3)**
**Goal**: Brain Service integration and AI-powered features

#### **Day 1-3: Brain Service Client**
- [ ] Implement MCP client for Brain Service
- [ ] Set up WebSocket connection management
- [ ] Add embedding generation for semantic search
- [ ] Implement knowledge graph storage

#### **Day 4-7: AI Features**
- [ ] Complete story consistency validation
- [ ] Implement scene transition suggestions
- [ ] Add character similarity search
- [ ] Implement plot hole detection

### **Phase 4: Testing & Documentation (Week 4)**
**Goal**: Comprehensive testing and documentation

#### **Day 1-3: Testing**
- [ ] Unit tests for all services and models
- [ ] Integration tests with PayloadCMS
- [ ] MCP protocol testing
- [ ] Performance testing

#### **Day 4-7: Documentation & Polish**
- [ ] Complete API documentation
- [ ] MCP tools reference
- [ ] Deployment guide
- [ ] Code cleanup and optimization

### **Phase 5: Production Deployment (Week 5)**
**Goal**: Production deployment and monitoring

#### **Day 1-3: Production Setup**
- [ ] Production Docker configuration
- [ ] Environment configuration
- [ ] Monitoring setup (Prometheus metrics)
- [ ] Logging configuration

#### **Day 4-7: Deployment & Validation**
- [ ] Deploy to production
- [ ] Integration testing with live services
- [ ] Performance validation
- [ ] User acceptance testing

---

## 🧪 **Testing Strategy**

### **Unit Testing**
```python
# tests/unit/test_services/test_story_bible_service.py
import pytest
from unittest.mock import AsyncMock, Mock
from src.services.story_bible_service import StoryBibleService
from src.services.payload_service import PayloadCMSService

@pytest.fixture
def payload_service_mock():
    return AsyncMock(spec=PayloadCMSService)

@pytest.fixture  
def story_service(payload_service_mock):
    return StoryBibleService(payload_service_mock)

@pytest.mark.asyncio
async def test_create_story_bible_success(story_service, payload_service_mock):
    # Test successful story bible creation
    payload_service_mock.create_story_bible.return_value = {"id": "test-id"}
    
    result = await story_service.create_story_bible(
        project_id="proj-123",
        title="Test Story",
        genre="Drama",
        premise="A compelling story about..."
    )
    
    assert result == "test-id"
    payload_service_mock.create_story_bible.assert_called_once()
```

### **Integration Testing**
```python
# tests/integration/test_payloadcms/test_story_bible_crud.py
import pytest
import httpx
from src.services.payload_service import PayloadCMSService

@pytest.mark.integration
@pytest.mark.asyncio
async def test_payloadcms_story_bible_crud():
    # Test full CRUD cycle with real PayloadCMS instance
    service = PayloadCMSService()
    
    # Create
    story_bible_data = {
        "project_id": "test-proj",
        "title": "Integration Test Story",
        "genre": "Test",
        "premise": "Test premise"
    }
    
    created = await service.create_story_bible(story_bible_data)
    assert "id" in created
    
    # Read
    retrieved = await service.get_story_bible(created["id"])
    assert retrieved["title"] == story_bible_data["title"]
    
    # Update
    update_data = {"title": "Updated Title"}
    updated = await service.update_story_bible(created["id"], update_data)
    assert updated["title"] == "Updated Title"
    
    # Delete
    deleted = await service.delete_story_bible(created["id"])
    assert deleted is True
```

### **MCP Protocol Testing**
```python
# tests/mcp/test_websocket/test_connection.py
import pytest
from fastapi.testclient import TestClient
from src.main import app

def test_mcp_websocket_connection():
    with TestClient(app) as client:
        with client.websocket_connect("/mcp") as websocket:
            # Test MCP protocol handshake
            websocket.send_json({
                "jsonrpc": "2.0",
                "method": "initialize",
                "id": 1,
                "params": {"protocolVersion": "1.0.0"}
            })
            
            response = websocket.receive_json()
            assert response["jsonrpc"] == "2.0"
            assert "result" in response
```

---

## 🔧 **Configuration Specifications**

### **Environment Variables**
```bash
# Service Configuration
PORT=8015
HOST=0.0.0.0
ENVIRONMENT=development

# PayloadCMS Integration (CRITICAL)
PAYLOADCMS_API_URL=http://localhost:3010  # Auto-Movie App
PAYLOADCMS_API_KEY=your-payload-api-key-here

# MCP Brain Service Integration
BRAIN_SERVICE_URL=http://localhost:8002
BRAIN_SERVICE_WS_URL=ws://localhost:8002/mcp

# Authentication
JWT_SECRET_KEY=your-jwt-secret-here
JWT_ALGORITHM=HS256

# AI Configuration
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-4

# Monitoring
ENABLE_METRICS=true
METRICS_PORT=9015
LOG_LEVEL=INFO

# Production Overrides
# PAYLOADCMS_API_URL=https://auto-movie.ft.tc
# BRAIN_SERVICE_URL=https://brain.ft.tc
# BRAIN_SERVICE_WS_URL=wss://brain.ft.tc/mcp
```

### **Docker Configuration**
```yaml
# docker-compose.yml
version: '3.8'

services:
  story-bible-service:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8015:8015"
      - "9015:9015"  # Metrics
    environment:
      - PORT=8015
      - HOST=0.0.0.0
      - ENVIRONMENT=development
      - PAYLOADCMS_API_URL=http://host.docker.internal:3010
      - BRAIN_SERVICE_URL=http://host.docker.internal:8002
      - BRAIN_SERVICE_WS_URL=ws://host.docker.internal:8002/mcp
    volumes:
      - ./logs:/app/logs
    networks:
      - movie-platform-network

networks:
  movie-platform-network:
    external: true  # Connect to main platform network
```

---

## 📋 **Implementation Checklist**

### **🔴 CRITICAL ITEMS (Must Complete First)**

- [ ] **PayloadCMS Collections**: Create all required collections in Auto-Movie App
- [ ] **Authentication Standard**: Implement Bearer token validation
- [ ] **PayloadCMS API Integration**: Complete CRUD operations
- [ ] **Project Access Control**: Ensure proper security isolation
- [ ] **MCP Protocol Implementation**: WebSocket server and tool registration

### **🟡 HIGH PRIORITY**

- [ ] **Core MCP Tools**: Implement all 10 primary tools
- [ ] **Brain Service Integration**: AI features and embeddings
- [ ] **Error Handling**: Comprehensive error management
- [ ] **Data Validation**: Input validation and sanitization
- [ ] **Testing Framework**: Unit and integration tests

### **🟢 MEDIUM PRIORITY**

- [ ] **Export Functionality**: PDF, DOCX, Markdown generation
- [ ] **Real-time Features**: WebSocket updates for collaboration
- [ ] **Monitoring**: Prometheus metrics and health checks
- [ ] **Documentation**: API reference and user guides
- [ ] **Performance Optimization**: Caching and query optimization

---

## ⚡ **Success Criteria**

### **Functional Requirements**
- [ ] ✅ All MCP tools functional and tested
- [ ] ✅ PayloadCMS integration working for all collections
- [ ] ✅ Authentication and authorization implemented
- [ ] ✅ Brain Service AI features operational
- [ ] ✅ Export functionality for all formats
- [ ] ✅ Real-time collaboration features

### **Performance Requirements**
- [ ] ✅ Story bible creation: <500ms response time
- [ ] ✅ Character operations: <200ms response time
- [ ] ✅ AI consistency validation: <2 seconds
- [ ] ✅ Export generation: <5 seconds (PDF), <2 seconds (JSON)
- [ ] ✅ Concurrent users: 50+ simultaneous editors
- [ ] ✅ WebSocket connections: 100+ concurrent connections

### **Quality Requirements**
- [ ] ✅ Test coverage: >90%
- [ ] ✅ No critical security vulnerabilities
- [ ] ✅ Full API documentation
- [ ] ✅ Error handling for all failure scenarios
- [ ] ✅ Monitoring and alerting configured

---

## 🎯 **Next Steps**

1. **IMMEDIATE**: Create PayloadCMS collections in Auto-Movie App
2. **PRIORITY 1**: Implement PayloadCMS service integration
3. **PRIORITY 2**: Set up MCP WebSocket server
4. **PRIORITY 3**: Implement core MCP tools
5. **PRIORITY 4**: Add Brain Service integration for AI features

---

**This specification provides a complete blueprint for implementing the MCP Story Bible Service. All architectural decisions have been made, including the critical integration with PayloadCMS as the single source of truth for data storage. The service is ready for development.**

---

## 📄 **Related Documents**

- **[IMPLEMENTATION_TODO.md](./IMPLEMENTATION_TODO.md)** - Detailed implementation checklist with task breakdown
- **[README.md](../../../services/mcp-story-bible-service/README.md)** - Service overview and quick start guide
- **[MCP_STORY_BIBLE_SERVICE.md](../MCP_STORY_BIBLE_SERVICE.md)** - High-level service specification
