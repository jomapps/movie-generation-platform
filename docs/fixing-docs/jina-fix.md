# Jina Architecture Fix Plan

## Problem Statement

The current architecture violates the intended design where the MCP Brain Service should be the **single gateway** to Neo4j and embedding services. Currently:

- `langgraph-orchestrator` has direct Neo4j connections
- `mcp-brain-service` also connects directly to Neo4j  
- Multiple services are handling embeddings independently
- No centralized knowledge graph management

## Target Architecture

```
┌─────────────────────┐    MCP WebSocket    ┌─────────────────────┐
│ langgraph-          │ ──────────────────► │ mcp-brain-service   │
│ orchestrator        │                     │                     │
└─────────────────────┘                     │ ┌─────────────────┐ │
                                            │ │ Jina Embeddings │ │
┌─────────────────────┐    MCP WebSocket    │ └─────────────────┘ │
│ auto-movie          │ ──────────────────► │                     │
│ (Next.js)           │                     │ ┌─────────────────┐ │
└─────────────────────┘                     │ │ Neo4j Database  │ │
                                            │ └─────────────────┘ │
┌─────────────────────┐    MCP WebSocket    └─────────────────────┘
│ task-service        │ ──────────────────►
└─────────────────────┘
```

## Phase 1: MCP Brain Service Enhancements

### Repository: `services/mcp-brain-service`

#### 1.1 Expand MCP Tools
**Current tools:**
- `create_character`
- `find_similar_characters`

**Add new tools:**
```python
# Text embedding tools
- embed_text(text: str, project_id: str) -> EmbeddingResult
- search_by_embedding(embedding: List[float], project_id: str) -> SearchResults
- store_document(content: str, metadata: dict, project_id: str) -> DocumentId

# Knowledge graph operations  
- create_relationship(from_id: str, to_id: str, relationship_type: str) -> bool
- query_graph(cypher_query: str, project_id: str) -> QueryResults
- get_node_neighbors(node_id: str, project_id: str) -> NeighborResults

# Batch operations
- batch_embed_texts(texts: List[str], project_id: str) -> List[EmbeddingResult]
- bulk_store_documents(documents: List[Document], project_id: str) -> List[DocumentId]
```

#### 1.2 Enhanced Data Models
**File:** `src/models/knowledge.py`
```python
class Document(BaseModel):
    content: str
    metadata: Dict[str, Any]
    document_type: str  # "character", "scene", "dialogue", "workflow"
    project_id: str

class EmbeddingResult(BaseModel):
    embedding: List[float]
    document_id: str
    similarity_score: Optional[float] = None

class GraphNode(BaseModel):
    id: str
    labels: List[str]
    properties: Dict[str, Any]
    
class GraphRelationship(BaseModel):
    from_node: str
    to_node: str
    type: str
    properties: Dict[str, Any]
```

#### 1.3 Service Layer Expansion
**File:** `src/services/knowledge_service.py`
```python
class KnowledgeService:
    def __init__(self, jina_service, neo4j_service):
        self.jina = jina_service
        self.neo4j = neo4j_service
    
    async def store_workflow_data(self, workflow_data: dict, project_id: str):
        """Store LangGraph workflow execution data"""
        
    async def search_similar_workflows(self, query: str, project_id: str):
        """Find similar workflow patterns"""
        
    async def store_agent_memory(self, agent_id: str, memory_data: dict, project_id: str):
        """Store agent conversation/decision memory"""
```

#### 1.4 Production Jina Integration
**Current:** Mock embeddings
**Target:** Real Jina v3 API with proper error handling

**File:** `src/lib/embeddings.py`
```python
class JinaEmbeddingService:
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Batch embedding with retry logic"""
        
    async def embed_image(self, image_data: bytes) -> List[float]:
        """Image embedding support"""
```

## Phase 2: LangGraph Orchestrator Refactoring

### Repository: `services/langgraph-orchestrator`

#### 2.1 Remove Direct Neo4j Dependencies
**Files to modify:**
- `coolify-env-variables.txt` - Remove Neo4j vars
- `.coolify-with-neo4j.yml` - Remove neo4j service
- `requirements.txt` - Remove neo4j driver

#### 2.2 Add MCP Brain Client
**New file:** `src/clients/brain_client.py`
```python
class BrainServiceClient:
    def __init__(self, brain_service_url: str):
        self.ws_url = brain_service_url.replace('https://', 'wss://').replace('http://', 'ws://')
    
    async def store_workflow_execution(self, workflow_data: dict, project_id: str):
        """Store workflow execution in knowledge graph"""
        
    async def search_similar_patterns(self, query: str, project_id: str):
        """Find similar workflow patterns for optimization"""
        
    async def store_agent_decision(self, agent_id: str, decision_data: dict, project_id: str):
        """Store agent decision-making context"""
```

#### 2.3 Update Environment Variables
**File:** `coolify-env-variables.txt`
```bash
# Remove these:
# NEO4J_URI=https://neo4j.ft.tc
# NEO4J_USER=neo4j  
# NEO4J_PASSWORD=***

# Keep/Add these:
BRAIN_SERVICE_BASE_URL=https://brain.ft.tc
BRAIN_SERVICE_WS_URL=wss://brain.ft.tc
```

#### 2.4 Workflow Integration Points
**File:** `src/workflows/base_workflow.py`
```python
class BaseWorkflow:
    def __init__(self):
        self.brain_client = BrainServiceClient(settings.BRAIN_SERVICE_BASE_URL)
    
    async def log_execution_step(self, step_data: dict):
        """Log workflow step to knowledge graph"""
        await self.brain_client.store_workflow_execution(step_data, self.project_id)
```

## Phase 3: Auto-Movie Integration

### Repository: `auto-movie`

#### 3.1 MCP Brain Client Integration
**New file:** `src/lib/brain-client.ts`
```typescript
export class BrainServiceClient {
  private wsUrl: string;
  
  constructor(baseUrl: string) {
    this.wsUrl = baseUrl.replace('https://', 'wss://').replace('http://', 'ws://');
  }
  
  async createCharacter(character: CharacterData, projectId: string): Promise<string> {
    // MCP WebSocket call to brain service
  }
  
  async findSimilarCharacters(query: string, projectId: string): Promise<Character[]> {
    // Semantic search via brain service
  }
  
  async storeSceneData(scene: SceneData, projectId: string): Promise<void> {
    // Store scene information for future reference
  }
}
```

#### 3.2 Environment Configuration
**File:** `.env.example`
```bash
# Add brain service connection
NEXT_PUBLIC_BRAIN_SERVICE_URL=https://brain.ft.tc
```

## Phase 4: Task Service Integration

### Repository: `services/task-service`

#### 4.1 Remove Direct Neo4j (if exists)
- Audit current Neo4j usage
- Replace with MCP Brain Service calls

#### 4.2 Add Brain Service Client
**File:** `src/clients/brain_client.py`
```python
class TaskBrainClient:
    async def store_task_execution(self, task_data: dict, project_id: str):
        """Store task execution patterns"""
        
    async def find_similar_tasks(self, task_description: str, project_id: str):
        """Find similar completed tasks for optimization"""
```

## Implementation Timeline

### Week 1: Brain Service Enhancement
- [ ] Implement expanded MCP tools
- [ ] Add real Jina v3 integration
- [ ] Create knowledge service layer
- [ ] Add batch processing capabilities

### Week 2: LangGraph Refactoring  
- [ ] Remove direct Neo4j dependencies
- [ ] Implement MCP Brain client
- [ ] Update workflow logging to use brain service
- [ ] Test workflow execution with new architecture

### Week 3: Frontend Integration
- [ ] Add brain service client to auto-movie
- [ ] Update character creation flow
- [ ] Implement semantic search UI
- [ ] Test end-to-end character workflows

### Week 4: Task Service & Testing
- [ ] Audit and update task service
- [ ] Comprehensive integration testing
- [ ] Performance optimization
- [ ] Production deployment

## Success Criteria

### Technical Validation
- [ ] Only `mcp-brain-service` connects to Neo4j
- [ ] All services communicate via MCP WebSocket protocol
- [ ] Real Jina embeddings working in production
- [ ] Sub-10ms semantic search response times
- [ ] Proper project isolation across all operations

### Functional Validation
- [ ] Character creation works end-to-end
- [ ] Semantic search returns relevant results
- [ ] Workflow patterns are stored and retrievable
- [ ] Agent decisions are logged to knowledge graph
- [ ] Cross-service data consistency maintained

## Risk Mitigation

### Data Migration
- Export existing Neo4j data before refactoring
- Implement data migration scripts
- Maintain backward compatibility during transition

### Service Dependencies
- Implement graceful degradation if brain service is unavailable
- Add circuit breaker patterns for external service calls
- Comprehensive error handling and retry logic

### Performance Concerns
- Implement connection pooling for WebSocket connections
- Add caching layer for frequently accessed embeddings
- Monitor and optimize batch processing performance

## Monitoring & Observability

### Metrics to Track
- MCP WebSocket connection health
- Embedding generation latency
- Neo4j query performance
- Cross-service communication success rates
- Knowledge graph growth and query patterns

### Alerting
- Brain service availability
- Jina API quota and errors
- Neo4j connection issues
- Abnormal embedding generation times