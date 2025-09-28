# MCP Brain Service Architecture

## Overview

The MCP Brain Service is the centralized AI/ML hub of the movie generation platform. It provides embeddings, semantic search, knowledge graph management, and workflow data storage through a standardized MCP (Model Context Protocol) WebSocket interface.

## Architecture Components

### Core Services

```
┌─────────────────────────────────────────────────────────────┐
│                    MCP Brain Service                        │
│                      (Port: 8002)                          │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐  │
│  │  MCP Server     │  │ Knowledge       │  │ Batch        │  │
│  │  (WebSocket)    │  │ Service         │  │ Service      │  │
│  └─────────────────┘  └─────────────────┘  └──────────────┘  │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐                   │
│  │ Jina v4         │  │ Neo4j           │                   │
│  │ Embedding       │  │ Graph Database  │                   │
│  │ Service         │  │ Client          │                   │
│  └─────────────────┘  └─────────────────┘                   │
└─────────────────────────────────────────────────────────────┘
```

### External Dependencies

- **Jina v4 API**: Production embedding generation service
- **Neo4j Database**: Knowledge graph storage and queries
- **MCP Protocol**: WebSocket communication standard

## MCP Tools Interface

The brain service exposes 20+ MCP tools organized into functional categories:

### 1. Core Embedding Tools

#### `embed_text`
Generates embeddings for a single text string.

**Parameters:**
- `text` (string): Text to embed
- `project_id` (string): Project isolation identifier

**Returns:** EmbeddingResult with document ID and metadata

#### `batch_embed_texts`
Efficiently processes multiple texts in parallel.

**Parameters:**
- `texts` (array): List of text strings
- `project_id` (string): Project isolation identifier

**Returns:** Array of EmbeddingResult objects

### 2. Semantic Search Tools

#### `search_by_embedding`
Finds similar content using embedding vectors.

**Parameters:**
- `embedding` (array): Vector embedding for similarity search
- `project_id` (string): Project isolation identifier
- `limit` (integer): Maximum results to return (default: 10)

**Returns:** SearchResults with similarity scores and metadata

#### `batch_similarity_search`
Performs multiple similarity searches concurrently.

**Parameters:**
- `queries` (array): List of query strings
- `project_id` (string): Project isolation identifier
- `limit_per_query` (integer): Results per query (default: 10)

**Returns:** Batch search results with performance metrics

### 3. Document Storage Tools

#### `store_document`
Stores document with automatic embedding generation.

**Parameters:**
- `content` (string): Document content
- `metadata` (object): Document metadata
- `project_id` (string): Project isolation identifier

**Returns:** Document ID for future reference

#### `bulk_store_documents`
Efficiently stores multiple documents with embeddings.

**Parameters:**
- `documents` (array): Array of document objects
- `project_id` (string): Project isolation identifier

**Returns:** Array of document IDs

### 4. Knowledge Graph Tools

#### `create_relationship`
Creates relationships between nodes in the knowledge graph.

**Parameters:**
- `from_id` (string): Source node ID
- `to_id` (string): Target node ID
- `relationship_type` (string): Type of relationship
- `properties` (object): Relationship properties (optional)

**Returns:** Boolean success status

#### `query_graph`
Executes Cypher queries on the knowledge graph.

**Parameters:**
- `cypher_query` (string): Cypher query string
- `project_id` (string): Project isolation identifier
- `parameters` (object): Query parameters (optional)

**Returns:** QueryResults with records and execution metrics

#### `get_node_neighbors`
Retrieves neighboring nodes and their relationships.

**Parameters:**
- `node_id` (string): Node identifier
- `project_id` (string): Project isolation identifier

**Returns:** NeighborResults with nodes and relationships

### 5. Workflow Integration Tools

#### `store_workflow_data`
Stores LangGraph workflow execution data.

**Parameters:**
- `workflow_id` (string): Workflow identifier
- `agent_id` (string): Agent identifier
- `step_name` (string): Workflow step name
- `input_data` (object): Step input data
- `output_data` (object): Step output data
- `execution_time_ms` (number): Execution time in milliseconds
- `project_id` (string): Project isolation identifier

**Returns:** Workflow data ID

#### `search_similar_workflows`
Finds similar workflow patterns using semantic search.

**Parameters:**
- `query` (string): Workflow query description
- `project_id` (string): Project isolation identifier
- `limit` (integer): Maximum results (default: 5)

**Returns:** SearchResults with similar workflows

#### `store_agent_memory`
Stores agent conversation and decision memory.

**Parameters:**
- `agent_id` (string): Agent identifier
- `memory_type` (string): Type of memory (conversation, decision, context)
- `content` (string): Memory content
- `metadata` (object): Memory metadata
- `project_id` (string): Project isolation identifier

**Returns:** Memory ID

### 6. Batch Processing Tools

#### `process_document_batch`
Processes large batches of documents with concurrent execution.

**Parameters:**
- `documents` (array): Array of document objects
- `project_id` (string): Project isolation identifier

**Returns:** Batch processing metrics and results

### 7. System Tools

#### `health_check`
Checks service health and connectivity to external dependencies.

**Parameters:** None

**Returns:** Health status for Jina API and Neo4j database

## Data Models

### Core Models

```python
@dataclass
class Document:
    content: str
    metadata: Dict[str, Any]
    document_type: str
    project_id: str
    id: Optional[str] = None
    created_at: Optional[datetime] = None

@dataclass
class EmbeddingResult:
    document_id: str
    embedding: List[float]
    model_used: str
    processing_time_ms: float

@dataclass
class SearchResults:
    results: List[SearchResult]
    total_count: int
    query_time_ms: float
    model_used: str

@dataclass
class SearchResult:
    document_id: str
    similarity_score: float
    content: str
    metadata: Dict[str, Any]
```

### Graph Models

```python
@dataclass
class GraphNode:
    id: str
    labels: List[str]
    properties: Dict[str, Any]
    project_id: str

@dataclass
class GraphRelationship:
    id: str
    type: str
    start_node_id: str
    end_node_id: str
    properties: Dict[str, Any]

@dataclass
class QueryResults:
    records: List[Dict[str, Any]]
    summary: Dict[str, Any]
    query_time_ms: float
```

### Workflow Models

```python
@dataclass
class WorkflowData:
    workflow_id: str
    agent_id: str
    step_name: str
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    execution_time_ms: float
    project_id: str
    timestamp: datetime

@dataclass
class AgentMemory:
    agent_id: str
    memory_type: str  # conversation, decision, context
    content: str
    metadata: Dict[str, Any]
    project_id: str
    timestamp: datetime
```

## MCP WebSocket Communication

### Connection Flow

1. **Client Connection**: Service connects to `ws://brain-service:8002/mcp`
2. **MCP Handshake**: Protocol initialization and capability negotiation
3. **Tool Discovery**: Client receives list of available tools
4. **Tool Execution**: Request/response cycles for MCP tool calls
5. **Connection Management**: Automatic reconnection and error handling

### Message Format

**Tool Request:**
```json
{
  "jsonrpc": "2.0",
  "id": "request-id",
  "method": "tools/call",
  "params": {
    "name": "embed_text",
    "arguments": {
      "text": "Sample text to embed",
      "project_id": "project-123"
    }
  }
}
```

**Tool Response:**
```json
{
  "jsonrpc": "2.0",
  "id": "request-id",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Text embedded with document ID: doc-456"
      }
    ]
  }
}
```

## Performance Characteristics

### Embedding Performance
- **Single Text**: < 100ms average response time
- **Batch Processing**: 80% reduction in API calls vs individual requests
- **Concurrent Requests**: Supports 100+ concurrent WebSocket connections

### Search Performance
- **Similarity Search**: < 50ms for 10K+ document collections
- **Graph Queries**: < 200ms for complex multi-hop queries
- **Batch Operations**: Linear scaling with configurable concurrency limits

### Resource Usage
- **Memory**: ~2GB baseline + ~10MB per 1K documents
- **CPU**: 2-4 cores recommended for production workloads
- **Storage**: Variable based on document volume and graph complexity

## Project Isolation

All operations are isolated by `project_id` to enable:
- **Multi-tenancy**: Multiple projects in single service instance
- **Data Separation**: Logical isolation without physical separation
- **Access Control**: Project-based permission boundaries
- **Resource Quotas**: Per-project resource limits (future)

## Error Handling

### Error Categories

1. **Validation Errors**: Invalid input parameters
2. **Service Errors**: Jina API or Neo4j connectivity issues
3. **Processing Errors**: Embedding generation or search failures
4. **Resource Errors**: Rate limits or capacity constraints

### Error Response Format

```json
{
  "jsonrpc": "2.0",
  "id": "request-id",
  "error": {
    "code": "EMBEDDING_FAILED",
    "message": "Failed to generate embedding",
    "data": {
      "service": "jina",
      "retry_after": 5000,
      "error_details": "Rate limit exceeded"
    }
  }
}
```

## Monitoring and Observability

### Health Endpoints
- `GET /health` - Service health status
- `GET /metrics` - Prometheus-compatible metrics
- `GET /ready` - Readiness probe for orchestration

### Key Metrics
- **Request Latency**: P50, P95, P99 response times
- **Throughput**: Requests per second by tool type
- **Error Rates**: Error percentage by category
- **Resource Usage**: CPU, memory, and connection counts
- **External Dependencies**: Jina API and Neo4j health

### Logging
- **Structured Logging**: JSON format with correlation IDs
- **Tool Execution**: Request/response logging for debugging
- **Error Tracking**: Detailed error context and stack traces
- **Audit Trail**: Project-level operation logging

## Security Considerations

### Authentication
- **Service-to-Service**: Mutual TLS for production deployments
- **API Keys**: Jina API key management and rotation
- **Database**: Neo4j authentication and connection encryption

### Data Protection
- **Encryption**: TLS for all external communications
- **Isolation**: Project-based data boundaries
- **Sanitization**: Input validation and output sanitization
- **Audit**: Operation logging for compliance

## Deployment Architecture

### Container Deployment

```yaml
# docker-compose.yml
services:
  brain-service:
    image: mcp-brain-service:latest
    ports:
      - "8002:8002"
    environment:
      - JINA_API_KEY=${JINA_API_KEY}
      - NEO4J_URI=${NEO4J_URI}
      - NEO4J_USER=${NEO4J_USER}
      - NEO4J_PASSWORD=${NEO4J_PASSWORD}
    depends_on:
      - neo4j
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8002/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  neo4j:
    image: neo4j:5.13
    ports:
      - "7474:7474"
      - "7687:7687"
    environment:
      - NEO4J_AUTH=${NEO4J_USER}/${NEO4J_PASSWORD}
    volumes:
      - neo4j_data:/data
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: brain-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: brain-service
  template:
    metadata:
      labels:
        app: brain-service
    spec:
      containers:
      - name: brain-service
        image: mcp-brain-service:latest
        ports:
        - containerPort: 8002
        env:
        - name: JINA_API_KEY
          valueFrom:
            secretKeyRef:
              name: brain-service-secrets
              key: jina-api-key
        - name: NEO4J_URI
          value: "bolt://neo4j:7687"
        livenessProbe:
          httpGet:
            path: /health
            port: 8002
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8002
          initialDelaySeconds: 5
          periodSeconds: 5
```

## Integration Examples

### Python Client (LangGraph Orchestrator)

```python
import asyncio
import websockets
import json
from typing import Dict, Any

class BrainServiceClient:
    def __init__(self, ws_url: str):
        self.ws_url = ws_url
        self.websocket = None
        self.request_id = 0

    async def connect(self):
        self.websocket = await websockets.connect(self.ws_url)
        # Perform MCP handshake
        await self._initialize_mcp()

    async def embed_text(self, text: str, project_id: str) -> Dict[str, Any]:
        return await self._call_tool("embed_text", {
            "text": text,
            "project_id": project_id
        })

    async def search_similar(self, query: str, project_id: str, limit: int = 10) -> Dict[str, Any]:
        # First get embedding for query
        embedding_result = await self.embed_text(query, project_id)

        # Then search by embedding
        return await self._call_tool("search_by_embedding", {
            "embedding": embedding_result["embedding"],
            "project_id": project_id,
            "limit": limit
        })

    async def store_workflow_step(self, workflow_data: Dict[str, Any]) -> str:
        result = await self._call_tool("store_workflow_data", workflow_data)
        return result["workflow_id"]

    async def _call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        self.request_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": str(self.request_id),
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }

        await self.websocket.send(json.dumps(request))
        response = await self.websocket.recv()
        return json.loads(response)
```

### TypeScript Client (Auto-Movie Frontend)

```typescript
class BrainServiceClient {
  private ws: WebSocket | null = null;
  private requestId = 0;
  private pendingRequests = new Map<string, {resolve: Function, reject: Function}>();

  constructor(private wsUrl: string) {}

  async connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      this.ws = new WebSocket(this.wsUrl);

      this.ws.onopen = () => {
        this.initializeMcp().then(resolve).catch(reject);
      };

      this.ws.onmessage = (event) => {
        const response = JSON.parse(event.data);
        const pending = this.pendingRequests.get(response.id);
        if (pending) {
          this.pendingRequests.delete(response.id);
          if (response.error) {
            pending.reject(new Error(response.error.message));
          } else {
            pending.resolve(response.result);
          }
        }
      };

      this.ws.onerror = reject;
    });
  }

  async embedText(text: string, projectId: string): Promise<any> {
    return this.callTool('embed_text', { text, project_id: projectId });
  }

  async searchSimilar(query: string, projectId: string, limit = 10): Promise<any> {
    return this.callTool('search_by_embedding', {
      query,
      project_id: projectId,
      limit
    });
  }

  private async callTool(toolName: string, arguments: any): Promise<any> {
    const requestId = (++this.requestId).toString();

    const request = {
      jsonrpc: '2.0',
      id: requestId,
      method: 'tools/call',
      params: {
        name: toolName,
        arguments
      }
    };

    return new Promise((resolve, reject) => {
      this.pendingRequests.set(requestId, { resolve, reject });
      this.ws?.send(JSON.stringify(request));
    });
  }
}
```

## Future Enhancements

### Planned Features
1. **Model Versioning**: Support for multiple embedding models
2. **Caching Layer**: Redis-based caching for frequently accessed embeddings
3. **Rate Limiting**: Per-project rate limiting and quotas
4. **Analytics**: Enhanced usage analytics and insights
5. **Federation**: Multi-instance federation for scaling

### Optimization Opportunities
1. **Vector Database**: Migration to specialized vector database (Pinecone, Weaviate)
2. **Model Fine-tuning**: Domain-specific embedding model training
3. **Compression**: Embedding compression techniques for storage efficiency
4. **Streaming**: Streaming responses for large batch operations

---

This architecture provides a robust, scalable foundation for centralized AI/ML operations in the movie generation platform, ensuring consistency, performance, and maintainability across all services.