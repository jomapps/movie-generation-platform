# API Documentation

This directory contains comprehensive API documentation for all services in the movie generation platform.

## Available Documentation

### MCP Brain Service API
- **[Brain Service API Reference](brain-service-api.md)** - Complete API documentation for the MCP Brain Service
  - 20+ MCP tools for embeddings, search, and knowledge graph operations
  - Request/response examples for every tool
  - Parameter validation and error handling
  - Performance guidelines and best practices

## API Overview

### Core Services

#### MCP Brain Service (Port: 8002)
**Primary AI/ML API providing:**
- Text embedding generation via Jina v4
- Semantic similarity search
- Knowledge graph operations
- Document storage and retrieval
- Workflow and agent memory storage
- Batch processing capabilities

**Communication Protocol:** MCP (Model Context Protocol) over WebSocket
**Endpoint:** `ws://localhost:8002/mcp`

#### LangGraph Orchestrator (Port: 8003)
**Workflow orchestration API:**
- Agent coordination
- Workflow execution
- Task management
- **Integration:** Connects to Brain Service via MCP WebSocket

#### Auto-Movie Frontend (Port: 3010)
**User interface API:**
- Movie generation workflows
- Character management
- Story development
- **Integration:** Needs Brain Service MCP client (pending)

#### Celery Task Service (Port: 8001)
**Background task processing:**
- Asynchronous task execution
- Task queue management
- Result storage
- **Integration:** Needs Brain Service MCP client (pending)

## API Usage Patterns

### 1. Direct MCP Tool Calls

For services that need immediate AI/ML operations:

```json
{
  "jsonrpc": "2.0",
  "id": "1",
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

### 2. Batch Operations

For high-volume processing:

```json
{
  "jsonrpc": "2.0",
  "id": "2",
  "method": "tools/call",
  "params": {
    "name": "batch_embed_texts",
    "arguments": {
      "texts": ["Text 1", "Text 2", "Text 3"],
      "project_id": "project-123"
    }
  }
}
```

### 3. Knowledge Graph Queries

For relationship and graph operations:

```json
{
  "jsonrpc": "2.0",
  "id": "3",
  "method": "tools/call",
  "params": {
    "name": "query_graph",
    "arguments": {
      "cypher_query": "MATCH (n:Character) WHERE n.project_id = $project_id RETURN n",
      "project_id": "project-123"
    }
  }
}
```

## Integration Clients

### Python Client (LangGraph Orchestrator)
```python
from clients.brain_client import BrainServiceClient

client = BrainServiceClient("ws://localhost:8002/mcp")
await client.connect()

# Embed text
result = await client.embed_text("Sample text", "project-123")

# Search similar content
results = await client.search_similar("query text", "project-123")
```

### TypeScript Client (Auto-Movie Frontend)
```typescript
import { BrainServiceClient } from '@/lib/brain-client';

const client = new BrainServiceClient('ws://localhost:8002/mcp');
await client.connect();

// Embed text
const result = await client.embedText('Sample text', 'project-123');

// Search similar content
const results = await client.searchSimilar('query text', 'project-123');
```

## Error Handling

All APIs follow consistent error response patterns:

```json
{
  "jsonrpc": "2.0",
  "id": "request-id",
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "data": {
      "details": "Additional context",
      "retry_after": 5000
    }
  }
}
```

## Performance Guidelines

### Response Time Expectations
- **Text Embedding**: < 100ms per text
- **Similarity Search**: < 50ms for 10K+ documents
- **Graph Queries**: < 200ms for complex queries
- **Batch Operations**: 80% reduction vs individual calls

### Best Practices
1. **Use Batch Operations** for multiple items
2. **Maintain WebSocket Connections** to avoid reconnection overhead
3. **Implement Retry Logic** with exponential backoff
4. **Set Appropriate Timeouts** (default: 30 seconds)
5. **Monitor Request Latency** and error rates

## Authentication & Security

### Development
- **No Authentication**: Services communicate without authentication
- **Network Isolation**: Services run in isolated Docker networks

### Production
- **API Keys**: Service-to-service authentication
- **mTLS**: Mutual TLS for secure communication
- **Network Policies**: Restrict access to authorized services
- **Rate Limiting**: Per-service rate limits and quotas

## Monitoring & Observability

### Health Checks
- `GET /health` - Service health status
- `GET /metrics` - Prometheus-compatible metrics
- `GET /ready` - Readiness probe

### Key Metrics
- Request latency (P50, P95, P99)
- Throughput (requests per second)
- Error rates by category
- Resource usage (CPU, memory)
- External dependency health

## Versioning Strategy

### API Versioning
- **MCP Protocol**: Uses semantic versioning (currently 2024-11-05)
- **Tool Schemas**: Backward compatible additions only
- **Breaking Changes**: New major version with migration path

### Compatibility
- **Clients**: Must support MCP protocol version 2024-11-05 or later
- **Tools**: New tools added without breaking existing functionality
- **Parameters**: Optional parameters added, required parameters never removed

## Development Workflow

### Adding New API Endpoints

1. **Define Tool Schema** in brain service MCP server
2. **Implement Tool Handler** with validation and business logic
3. **Add Client Methods** in Python and TypeScript clients
4. **Update Documentation** with examples and specifications
5. **Add Integration Tests** for the new functionality

### API Documentation Updates

1. **Tool Changes**: Update brain-service-api.md
2. **New Services**: Create new API documentation files
3. **Integration Examples**: Add client code examples
4. **Error Handling**: Document new error codes and responses

## Support

For API-related issues:
1. **Check API Documentation**: Review specific service documentation
2. **Review Troubleshooting Guide**: [Integration Issues](../troubleshooting/integration-issues.md)
3. **Test with Health Checks**: Verify service connectivity
4. **Check Implementation Status**: [Implementation Plan](../fixing-docs/jina-fix-implementation-plan.md)

---

**Last Updated:** 2025-01-28
**API Version:** MCP Protocol 2024-11-05
**Documentation Status:** Complete and Production-Ready