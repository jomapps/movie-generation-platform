# MCP Brain Service API Reference

## Overview

The MCP Brain Service provides a comprehensive WebSocket API following the Model Context Protocol (MCP) standard. All communication happens over WebSocket connections with JSON-RPC 2.0 message format.

## Connection Details

- **WebSocket URL**: `ws://localhost:8002/mcp`
- **Protocol**: MCP (Model Context Protocol)
- **Message Format**: JSON-RPC 2.0
- **Port**: 8002 (default)

## Authentication

Currently, the service operates without authentication for development. In production deployments, implement:
- **API Keys**: Service-to-service authentication
- **mTLS**: Mutual TLS for secure communication
- **Network Policies**: Restrict access to authorized services

## MCP Tools Reference

### Embedding Tools

#### `embed_text`

Generate embedding for a single text string.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": "1",
  "method": "tools/call",
  "params": {
    "name": "embed_text",
    "arguments": {
      "text": "This is a sample text to embed",
      "project_id": "project-123"
    }
  }
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": "1",
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

**Parameters:**
- `text` (string, required): Text content to embed
- `project_id` (string, required): Project isolation identifier

**Returns:** Document ID for the embedded text

---

#### `batch_embed_texts`

Process multiple texts efficiently in parallel.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": "2",
  "method": "tools/call",
  "params": {
    "name": "batch_embed_texts",
    "arguments": {
      "texts": [
        "First text to embed",
        "Second text to embed",
        "Third text to embed"
      ],
      "project_id": "project-123"
    }
  }
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": "2",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Batch embedded 3 texts"
      }
    ]
  }
}
```

**Parameters:**
- `texts` (array[string], required): Array of text strings
- `project_id` (string, required): Project isolation identifier

**Returns:** Count of successfully embedded texts

### Search Tools

#### `search_by_embedding`

Find similar content using embedding vectors.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": "3",
  "method": "tools/call",
  "params": {
    "name": "search_by_embedding",
    "arguments": {
      "embedding": [0.1, 0.2, 0.3, ...],
      "project_id": "project-123",
      "limit": 5
    }
  }
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": "3",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Found 5 results in 45ms"
      }
    ]
  }
}
```

**Parameters:**
- `embedding` (array[number], required): Vector embedding for similarity search
- `project_id` (string, required): Project isolation identifier
- `limit` (integer, optional): Maximum results to return (default: 10)

**Returns:** Search results with similarity scores

---

#### `batch_similarity_search`

Perform multiple similarity searches concurrently.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": "4",
  "method": "tools/call",
  "params": {
    "name": "batch_similarity_search",
    "arguments": {
      "queries": [
        "Find characters like Gandalf",
        "Search for epic battle scenes",
        "Look for romantic storylines"
      ],
      "project_id": "project-123",
      "limit_per_query": 10
    }
  }
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": "4",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Batch search: 3/3 queries in 0.12s"
      }
    ]
  }
}
```

**Parameters:**
- `queries` (array[string], required): Array of query strings
- `project_id` (string, required): Project isolation identifier
- `limit_per_query` (integer, optional): Results per query (default: 10)

**Returns:** Batch search results with performance metrics

### Document Storage Tools

#### `store_document`

Store document with automatic embedding generation.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": "5",
  "method": "tools/call",
  "params": {
    "name": "store_document",
    "arguments": {
      "content": "This is the document content to store and embed",
      "metadata": {
        "title": "Sample Document",
        "author": "John Doe",
        "category": "story"
      },
      "project_id": "project-123"
    }
  }
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": "5",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Document stored with ID: doc-789"
      }
    ]
  }
}
```

**Parameters:**
- `content` (string, required): Document content
- `metadata` (object, required): Document metadata
- `project_id` (string, required): Project isolation identifier

**Returns:** Document ID for future reference

---

#### `bulk_store_documents`

Store multiple documents with embeddings efficiently.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": "6",
  "method": "tools/call",
  "params": {
    "name": "bulk_store_documents",
    "arguments": {
      "documents": [
        {
          "content": "First document content",
          "metadata": {"title": "Doc 1"},
          "document_type": "story"
        },
        {
          "content": "Second document content",
          "metadata": {"title": "Doc 2"},
          "document_type": "character"
        }
      ],
      "project_id": "project-123"
    }
  }
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": "6",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Bulk stored 2 documents"
      }
    ]
  }
}
```

**Parameters:**
- `documents` (array[object], required): Array of document objects
  - `content` (string): Document content
  - `metadata` (object): Document metadata
  - `document_type` (string): Type classification
- `project_id` (string, required): Project isolation identifier

**Returns:** Array of document IDs

### Knowledge Graph Tools

#### `create_relationship`

Create relationships between nodes in the knowledge graph.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": "7",
  "method": "tools/call",
  "params": {
    "name": "create_relationship",
    "arguments": {
      "from_id": "char-gandalf",
      "to_id": "char-frodo",
      "relationship_type": "MENTORS",
      "properties": {
        "strength": "strong",
        "duration": "entire_journey"
      }
    }
  }
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": "7",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Relationship created: true"
      }
    ]
  }
}
```

**Parameters:**
- `from_id` (string, required): Source node ID
- `to_id` (string, required): Target node ID
- `relationship_type` (string, required): Type of relationship
- `properties` (object, optional): Relationship properties

**Returns:** Boolean success status

---

#### `query_graph`

Execute Cypher queries on the knowledge graph.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": "8",
  "method": "tools/call",
  "params": {
    "name": "query_graph",
    "arguments": {
      "cypher_query": "MATCH (c:Character)-[r:MENTORS]->(s:Character) WHERE c.project_id = $project_id RETURN c.name, s.name, r.strength",
      "project_id": "project-123",
      "parameters": {
        "project_id": "project-123"
      }
    }
  }
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": "8",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Query executed: 5 records in 25ms"
      }
    ]
  }
}
```

**Parameters:**
- `cypher_query` (string, required): Cypher query string
- `project_id` (string, required): Project isolation identifier
- `parameters` (object, optional): Query parameters

**Returns:** Query results with execution metrics

---

#### `get_node_neighbors`

Get neighbors and relationships of a specific node.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": "9",
  "method": "tools/call",
  "params": {
    "name": "get_node_neighbors",
    "arguments": {
      "node_id": "char-gandalf",
      "project_id": "project-123"
    }
  }
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": "9",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Found 8 neighbors and 12 relationships"
      }
    ]
  }
}
```

**Parameters:**
- `node_id` (string, required): Node identifier
- `project_id` (string, required): Project isolation identifier

**Returns:** Neighboring nodes and relationships

### Workflow Integration Tools

#### `store_workflow_data`

Store LangGraph workflow execution data.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": "10",
  "method": "tools/call",
  "params": {
    "name": "store_workflow_data",
    "arguments": {
      "workflow_id": "wf-story-generation-001",
      "agent_id": "agent-story-writer",
      "step_name": "character_development",
      "input_data": {
        "character_brief": "Create a wizard character",
        "style": "fantasy"
      },
      "output_data": {
        "character": {
          "name": "Gandalf",
          "description": "Wise wizard with grey robes"
        }
      },
      "execution_time_ms": 1500,
      "project_id": "project-123"
    }
  }
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": "10",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Workflow data stored with ID: wf-data-456"
      }
    ]
  }
}
```

**Parameters:**
- `workflow_id` (string, required): Workflow identifier
- `agent_id` (string, required): Agent identifier
- `step_name` (string, required): Workflow step name
- `input_data` (object, required): Step input data
- `output_data` (object, required): Step output data
- `execution_time_ms` (number, required): Execution time in milliseconds
- `project_id` (string, required): Project isolation identifier

**Returns:** Workflow data ID

---

#### `search_similar_workflows`

Find similar workflow patterns using semantic search.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": "11",
  "method": "tools/call",
  "params": {
    "name": "search_similar_workflows",
    "arguments": {
      "query": "character development for fantasy stories",
      "project_id": "project-123",
      "limit": 5
    }
  }
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": "11",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Found 3 similar workflows"
      }
    ]
  }
}
```

**Parameters:**
- `query` (string, required): Workflow query description
- `project_id` (string, required): Project isolation identifier
- `limit` (integer, optional): Maximum results (default: 5)

**Returns:** Similar workflows with metadata

---

#### `store_agent_memory`

Store agent conversation and decision memory.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": "12",
  "method": "tools/call",
  "params": {
    "name": "store_agent_memory",
    "arguments": {
      "agent_id": "agent-story-writer",
      "memory_type": "decision",
      "content": "Decided to make the wizard character older and wiser based on the fantasy genre requirements",
      "metadata": {
        "context": "character_development",
        "confidence": 0.9,
        "reasoning": "Fantasy stories typically benefit from wise mentor figures"
      },
      "project_id": "project-123"
    }
  }
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": "12",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Agent memory stored with ID: mem-789"
      }
    ]
  }
}
```

**Parameters:**
- `agent_id` (string, required): Agent identifier
- `memory_type` (string, required): Type of memory (conversation, decision, context)
- `content` (string, required): Memory content
- `metadata` (object, required): Memory metadata
- `project_id` (string, required): Project isolation identifier

**Returns:** Memory ID

### Batch Processing Tools

#### `process_document_batch`

Process large batches of documents efficiently with concurrent execution.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": "13",
  "method": "tools/call",
  "params": {
    "name": "process_document_batch",
    "arguments": {
      "documents": [
        {
          "content": "Document 1 content",
          "metadata": {"type": "story"},
          "document_type": "narrative"
        },
        {
          "content": "Document 2 content",
          "metadata": {"type": "character"},
          "document_type": "character_profile"
        }
      ],
      "project_id": "project-123"
    }
  }
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": "13",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Batch processed: 2/2 documents in 0.85s"
      }
    ]
  }
}
```

**Parameters:**
- `documents` (array[object], required): Array of document objects
- `project_id` (string, required): Project isolation identifier

**Returns:** Batch processing metrics

### System Tools

#### `health_check`

Check service health and connectivity to external dependencies.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": "14",
  "method": "tools/call",
  "params": {
    "name": "health_check",
    "arguments": {}
  }
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": "14",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Health Check - Jina: healthy, Neo4j: healthy"
      }
    ]
  }
}
```

**Parameters:** None

**Returns:** Health status for all dependencies

### Character Tools (Legacy)

#### `create_character`

Create a new character with embedding (legacy compatibility).

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": "15",
  "method": "tools/call",
  "params": {
    "name": "create_character",
    "arguments": {
      "name": "Gandalf the Grey",
      "description": "A wise and powerful wizard who serves as a guide and protector",
      "traits": ["wise", "powerful", "protective", "mysterious"],
      "project_id": "project-123"
    }
  }
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": "15",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Character created with ID: char-456"
      }
    ]
  }
}
```

**Parameters:**
- `name` (string, required): Character name
- `description` (string, required): Character description
- `traits` (array[string], optional): Character traits
- `project_id` (string, required): Project isolation identifier

**Returns:** Character ID

---

#### `find_similar_characters`

Find characters similar to a description (legacy compatibility).

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": "16",
  "method": "tools/call",
  "params": {
    "name": "find_similar_characters",
    "arguments": {
      "description": "A powerful magic user who helps heroes on their journey",
      "project_id": "project-123",
      "limit": 5
    }
  }
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": "16",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Found 3 similar characters in 45ms"
      }
    ]
  }
}
```

**Parameters:**
- `description` (string, required): Character description to match
- `project_id` (string, required): Project isolation identifier
- `limit` (integer, optional): Maximum results (default: 5)

**Returns:** Similar characters with similarity scores

## Error Handling

### Error Response Format

All errors follow the JSON-RPC 2.0 error format:

```json
{
  "jsonrpc": "2.0",
  "id": "request-id",
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "data": {
      "details": "Additional error context",
      "retry_after": 5000,
      "service": "jina"
    }
  }
}
```

### Common Error Codes

| Code | Description | Retry Strategy |
|------|-------------|----------------|
| `VALIDATION_ERROR` | Invalid input parameters | Fix parameters, don't retry |
| `SERVICE_UNAVAILABLE` | Jina API or Neo4j down | Exponential backoff retry |
| `RATE_LIMIT_EXCEEDED` | API rate limit hit | Wait for retry_after seconds |
| `EMBEDDING_FAILED` | Embedding generation failed | Retry with exponential backoff |
| `GRAPH_QUERY_FAILED` | Neo4j query error | Check query syntax |
| `PROJECT_NOT_FOUND` | Invalid project_id | Verify project exists |
| `INTERNAL_ERROR` | Unexpected server error | Contact support |

### Error Examples

**Validation Error:**
```json
{
  "jsonrpc": "2.0",
  "id": "1",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Missing required parameter: project_id",
    "data": {
      "parameter": "project_id",
      "provided_params": ["text"]
    }
  }
}
```

**Service Unavailable:**
```json
{
  "jsonrpc": "2.0",
  "id": "2",
  "error": {
    "code": "SERVICE_UNAVAILABLE",
    "message": "Jina embedding service is currently unavailable",
    "data": {
      "service": "jina",
      "retry_after": 30000,
      "status": "connection_timeout"
    }
  }
}
```

**Rate Limit:**
```json
{
  "jsonrpc": "2.0",
  "id": "3",
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "API rate limit exceeded for Jina service",
    "data": {
      "service": "jina",
      "retry_after": 60000,
      "limit": "1000_requests_per_hour",
      "reset_time": "2024-01-27T15:00:00Z"
    }
  }
}
```

## Performance Guidelines

### Request Optimization

1. **Batch Operations**: Use batch tools for multiple operations
   - `batch_embed_texts` instead of multiple `embed_text` calls
   - `bulk_store_documents` for document storage
   - `batch_similarity_search` for multiple queries

2. **Connection Reuse**: Maintain persistent WebSocket connections
   - Avoid reconnecting for each request
   - Implement connection pooling for high-volume scenarios

3. **Project Isolation**: Use consistent `project_id` values
   - Enables efficient caching and indexing
   - Improves query performance

### Response Times

| Operation | Expected Time | Factors |
|-----------|---------------|---------|
| `embed_text` | < 100ms | Text length, API latency |
| `search_by_embedding` | < 50ms | Collection size, similarity threshold |
| `store_document` | < 150ms | Text length, embedding time |
| `query_graph` | < 200ms | Query complexity, graph size |
| `batch_embed_texts` (10 items) | < 500ms | Batch size, concurrency |

### Best Practices

1. **Error Handling**: Implement exponential backoff for retries
2. **Timeout Management**: Set appropriate timeouts (default: 30s)
3. **Connection Management**: Handle WebSocket disconnections gracefully
4. **Monitoring**: Track request latency and error rates
5. **Caching**: Cache embeddings when possible to reduce API calls

## Usage Examples

### Complete Workflow Example

```python
import asyncio
import websockets
import json

async def complete_workflow_example():
    # Connect to brain service
    uri = "ws://localhost:8002/mcp"
    async with websockets.connect(uri) as websocket:

        # 1. Store a character document
        character_request = {
            "jsonrpc": "2.0",
            "id": "1",
            "method": "tools/call",
            "params": {
                "name": "store_document",
                "arguments": {
                    "content": "Gandalf is a wise wizard who guides Frodo on his journey",
                    "metadata": {
                        "name": "Gandalf",
                        "type": "character",
                        "role": "mentor"
                    },
                    "project_id": "lotr-project"
                }
            }
        }

        await websocket.send(json.dumps(character_request))
        response = await websocket.recv()
        character_result = json.loads(response)
        print(f"Character stored: {character_result}")

        # 2. Search for similar characters
        search_request = {
            "jsonrpc": "2.0",
            "id": "2",
            "method": "tools/call",
            "params": {
                "name": "find_similar_characters",
                "arguments": {
                    "description": "A wise mentor figure who helps heroes",
                    "project_id": "lotr-project",
                    "limit": 3
                }
            }
        }

        await websocket.send(json.dumps(search_request))
        response = await websocket.recv()
        search_result = json.loads(response)
        print(f"Similar characters: {search_result}")

        # 3. Store workflow data
        workflow_request = {
            "jsonrpc": "2.0",
            "id": "3",
            "method": "tools/call",
            "params": {
                "name": "store_workflow_data",
                "arguments": {
                    "workflow_id": "character-creation-001",
                    "agent_id": "character-agent",
                    "step_name": "character_definition",
                    "input_data": {"brief": "Create a wizard mentor"},
                    "output_data": {"character": "Gandalf created"},
                    "execution_time_ms": 1200,
                    "project_id": "lotr-project"
                }
            }
        }

        await websocket.send(json.dumps(workflow_request))
        response = await websocket.recv()
        workflow_result = json.loads(response)
        print(f"Workflow data stored: {workflow_result}")

# Run the example
asyncio.run(complete_workflow_example())
```

This comprehensive API reference provides all the information needed to integrate with the MCP Brain Service effectively.