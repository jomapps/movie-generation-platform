# MCP Story Bible Service - Technical Specification

**Last Updated**: January 28, 2025  
**Service Status**: ✅ **IMPLEMENTED** - Ready for development  
**Repository**: [jomapps/mcp-story-bible-service](https://github.com/jomapps/mcp-story-bible-service)

## 🎯 **Service Purpose**

The MCP Story Bible Service is a specialized Model Context Protocol (MCP) server that creates, manages, and maintains comprehensive story bibles for movie projects. It serves as the **authoritative source** for narrative structure, character development, plot consistency, and story documentation within the AI Movie Generation Platform.

## 🏗️ **System Architecture**

### **Service Integration Pattern**
```
┌─────────────────┐    MCP WebSocket    ┌────────────────────┐
│   LangGraph     │◄──────────────────►│  Story Bible       │
│   Orchestrator  │                    │  Service           │
└─────────────────┘                    └────────────────────┘
                                                │
                                                │ MCP Client
                                                ▼
┌─────────────────┐    MCP WebSocket    ┌────────────────────┐
│   Auto-Movie    │◄──────────────────►│  MCP Brain         │
│   Frontend      │                    │  Service           │
└─────────────────┘                    └────────────────────┘
                                                │
                                                │ Neo4j/Jina v4
                                                ▼
                                       ┌────────────────────┐
                                       │  Knowledge Graph   │
                                       │  & Embeddings      │
                                       └────────────────────┘
```

### **Core Integration Points**

#### **1. Brain Service Integration** 🧠
- **Knowledge Graph**: Character relationships and story elements stored in Neo4j
- **Semantic Search**: Find similar story patterns using Jina v4 embeddings
- **Cross-Reference**: Link story elements to existing knowledge base
- **Consistency Validation**: AI-powered plot hole and continuity checking

#### **2. LangGraph Orchestrator Integration** 🤖
- **Workflow Coordination**: Receive story creation requests from orchestrator
- **Agent Collaboration**: Coordinate with Character, Visual, and Audio MCP services
- **Progress Tracking**: Report story bible creation milestones
- **Decision Storage**: Log story development decisions for future reference

#### **3. Frontend Integration** 🎨
- **Real-time Updates**: WebSocket connection for live story bible editing
- **Collaborative Editing**: Multi-user story bible development
- **Visual Story Mapping**: Interactive story structure visualization
- **Export Capabilities**: Generate story bible documents in various formats

## 📊 **Service Configuration**

### **Port & Domain Assignment**
- **Local**: `localhost:8015`
- **Dev**: `story-bible.ngrok.pro`
- **Prod**: `story-bible.ft.tc`
- **Metrics**: `localhost:9015` (Prometheus metrics)

### **Database Configuration**
- **Primary Database**: PostgreSQL (story bible storage)
- **Connection Pool**: 10-50 connections
- **Migrations**: Alembic for schema management
- **Backup Strategy**: Daily automated backups

### **External Dependencies**
- **MCP Brain Service**: `https://brain.ft.tc` (production)
- **OpenAI API**: GPT-4 for story generation assistance
- **PostgreSQL**: Dedicated story bible database instance

## 🛠️ **MCP Tools Specification**

### **Core Story Bible Management**

#### **`create_story_bible(project_id: str, title: str, genre: str, premise: str) -> str`**
```python
# Creates a new story bible for a project
# Returns: story_bible_id
{
    "project_id": "proj_123",
    "title": "The Last Algorithm",
    "genre": "Sci-Fi Thriller",
    "premise": "An AI discovers it's living in a simulation..."
}
```

#### **`get_story_bible(story_bible_id: str) -> StoryBible`**
```python
# Retrieves complete story bible with all elements
# Returns: Full story bible object with characters, scenes, plot threads
```

#### **`update_story_bible(story_bible_id: str, updates: dict) -> bool`**
```python
# Updates story bible metadata and core information
# Returns: Success status
```

### **Character Management**

#### **`add_character(story_bible_id: str, character_data: dict) -> str`**
```python
# Adds a new character to the story bible
{
    "name": "Dr. Sarah Chen",
    "role": "protagonist",
    "background": "Brilliant AI researcher...",
    "motivation": "Discover the truth about reality",
    "arc_description": "From skeptic to believer to hero"
}
# Returns: character_id
```

#### **`generate_character_arc(character_id: str, story_context: str) -> CharacterArc`**
```python
# AI-assisted character development and arc creation
# Uses Brain Service for consistency checking
# Returns: Detailed character arc with development milestones
```

#### **`find_similar_characters(description: str, project_id: str) -> List[Character]`**
```python
# Semantic search for similar characters using Brain Service
# Prevents character duplication and ensures uniqueness
```

### **Plot & Structure Management**

#### **`create_story_outline(story_bible_id: str, outline_data: dict) -> str`**
```python
# Creates the main story structure
{
    "act_structure": "three_act",
    "genre_conventions": ["hero_journey", "mystery_elements"],
    "plot_points": [
        {"type": "inciting_incident", "description": "...", "act": 1},
        {"type": "plot_point_1", "description": "...", "act": 1},
        {"type": "midpoint", "description": "...", "act": 2}
    ]
}
```

#### **`track_plot_thread(story_bible_id: str, thread_data: dict) -> str`**
```python
# Manages multiple plot threads and their resolution
{
    "thread_name": "The Mystery of the Algorithm",
    "thread_type": "main_plot",
    "introduction_scene": "scene_001",
    "resolution_scene": "scene_045",
    "key_scenes": ["scene_012", "scene_023", "scene_039"]
}
```

#### **`validate_story_consistency(story_bible_id: str) -> ConsistencyReport`**
```python
# AI-powered plot hole detection and continuity checking
# Returns: Detailed report with identified issues and suggestions
{
    "consistency_score": 0.87,
    "issues": [
        {
            "type": "character_contradiction",
            "severity": "medium",
            "description": "Character X knows information they shouldn't have in Scene 12"
        }
    ],
    "suggestions": [...]
}
```

### **Scene Management**

#### **`add_scene(story_bible_id: str, scene_data: dict) -> str`**
```python
# Adds scene information to story bible
{
    "sequence_number": 15,
    "location": "Chen's AI Lab",
    "time_of_day": "night",
    "characters_present": ["Dr. Sarah Chen", "AI Unit 7"],
    "scene_purpose": "revelation",
    "description": "Sarah discovers the truth about her reality...",
    "emotional_beats": ["curiosity", "shock", "determination"]
}
```

#### **`suggest_scene_transitions(story_bible_id: str, scene_id: str) -> List[Suggestion]`**
```python
# AI-powered scene flow optimization
# Suggests improvements for pacing and narrative flow
```

### **Collaboration & Export**

#### **`generate_story_bible_export(story_bible_id: str, format: str) -> bytes`**
```python
# Exports story bible in various formats
# Supported formats: "pdf", "docx", "markdown", "json"
```

#### **`track_story_bible_changes(story_bible_id: str, user_id: str, changes: dict) -> bool`**
```python
# Version control and change tracking for collaborative editing
```

## 📈 **Performance Specifications**

### **Response Time Requirements**
- **Story Bible Creation**: <500ms (including Brain Service integration)
- **Character Addition**: <200ms
- **Consistency Validation**: <2 seconds for full story bible
- **Scene Management**: <100ms per operation
- **Export Generation**: <5 seconds for PDF, <2 seconds for JSON

### **Throughput Targets**
- **Concurrent Story Bibles**: 100+ active story bibles per instance
- **Concurrent Users**: 50+ simultaneous editors
- **API Requests**: 1000+ requests/minute
- **WebSocket Connections**: 100+ concurrent connections

### **Scalability Design**
- **Horizontal Scaling**: Multiple service instances with load balancing
- **Database Scaling**: Read replicas for query optimization
- **Caching Strategy**: Redis caching for frequently accessed story bibles
- **CDN Integration**: Static export files served via CDN

## 🔒 **Security & Data Management**

### **Authentication & Authorization**
- **Project-Based Access**: Users can only access their project's story bibles
- **Role-Based Permissions**: Read/Write/Admin roles for collaborative editing
- **API Key Authentication**: Secure service-to-service communication
- **JWT Tokens**: Session management for WebSocket connections

### **Data Protection**
- **Encryption at Rest**: Database encryption for sensitive story data
- **Encryption in Transit**: TLS for all API communications
- **Backup Strategy**: Daily automated backups with 30-day retention
- **GDPR Compliance**: User data deletion and privacy controls

### **Project Isolation**
- **Multi-Tenant Architecture**: Complete data separation between projects
- **Database Partitioning**: Project-based data partitioning for performance
- **Cross-Project Prevention**: Strict validation to prevent data leakage

## 🧪 **Testing Strategy**

### **Unit Testing**
- **MCP Tool Testing**: Individual tool functionality validation
- **Database Operations**: CRUD operations and consistency checks
- **AI Integration**: Brain Service communication testing
- **Business Logic**: Story consistency validation algorithms

### **Integration Testing**
- **Brain Service Integration**: Full MCP communication workflow
- **Database Integration**: PostgreSQL connection and transaction testing
- **Orchestrator Integration**: LangGraph workflow coordination
- **Frontend Integration**: WebSocket real-time updates

### **Performance Testing**
- **Load Testing**: 1000+ concurrent requests simulation
- **Stress Testing**: Service behavior under extreme load
- **WebSocket Testing**: Multiple concurrent connection handling
- **Database Performance**: Query optimization and indexing validation

## 📊 **Monitoring & Metrics**

### **Health Monitoring**
- **Service Health**: Uptime, response times, error rates
- **Database Health**: Connection pool status, query performance
- **Brain Service Connectivity**: MCP connection status and latency
- **Story Bible Operations**: Creation/update success rates

### **Business Metrics**
- **Story Bible Statistics**: Number of active story bibles per project
- **User Engagement**: Collaborative editing sessions and duration
- **Content Metrics**: Average story bible completion rates
- **Consistency Scores**: Plot validation success rates

### **Performance Metrics**
- **Response Times**: P50, P95, P99 response time percentiles
- **Throughput**: Requests per second, concurrent users
- **Resource Utilization**: CPU, memory, database connections
- **Export Performance**: Generation times by format and size

## 🚀 **Development Roadmap**

### **Phase 1: Core Implementation** (Weeks 1-2)
- ✅ **Basic service structure** - FastAPI, PostgreSQL, Docker
- ✅ **MCP protocol integration** - WebSocket server and tool definitions
- ✅ **Database models** - Story bible, character, scene data structures
- ⏳ **Brain Service client** - MCP communication for AI integration
- ⏳ **Basic CRUD operations** - Story bible creation and management

### **Phase 2: Advanced Features** (Weeks 3-4)
- **AI-powered features** - Story consistency validation, character arc generation
- **Export functionality** - PDF, DOCX, Markdown export capabilities
- **Real-time collaboration** - WebSocket-based collaborative editing
- **Scene management** - Advanced scene organization and transition suggestions

### **Phase 3: Production Deployment** (Week 5)
- **Production configuration** - Environment-specific settings
- **Monitoring setup** - Prometheus metrics, health checks
- **Performance optimization** - Caching, query optimization
- **Security hardening** - Authentication, authorization, data encryption

### **Phase 4: Integration Testing** (Week 6)
- **Orchestrator integration** - Full workflow coordination testing
- **Frontend integration** - Real-time UI updates and collaborative features
- **End-to-end testing** - Complete story bible creation workflow
- **Performance validation** - Load testing and optimization

## 📚 **Related Documentation**

- **[MCP Brain Service](../JINA_V4_INTEGRATION.md)** - AI and knowledge graph integration
- **[LangGraph Orchestrator](../PRODUCTION_ENDPOINTS.md)** - Workflow coordination service
- **[Domain Configuration](../Domain-configs.md)** - Port assignments and deployment
- **[Production Endpoints](../PRODUCTION_ENDPOINTS.md)** - Live service information

---

**This MCP Story Bible Service represents a critical component of the AI Movie Generation Platform, providing the narrative foundation that coordinates all other creative services. Its integration with the Brain Service ensures consistency and quality while its collaboration features enable seamless team-based story development.**