# Troubleshooting Guide - Integration Issues

## Overview

This guide covers common integration issues when connecting services to the MCP Brain Service and provides step-by-step solutions.

## Connection Issues

### WebSocket Connection Failures

#### Symptom
```
WebSocket connection failed: Error during WebSocket handshake: Unexpected response code: 403
```

#### Possible Causes
1. **Service not running**: Brain service is not started
2. **Port conflicts**: Port 8002 is already in use
3. **Network policies**: Firewall blocking connections
4. **Wrong URL**: Incorrect WebSocket endpoint

#### Solutions

**1. Verify Brain Service Status**
```bash
# Check if service is running
curl http://localhost:8002/health

# Expected response:
# {"status": "healthy", "timestamp": "2024-01-27T10:30:00Z"}

# If service is down:
cd services/mcp-brain-service
docker-compose up -d

# Or start manually:
python -m uvicorn src.main:app --host 0.0.0.0 --port 8002
```

**2. Check Port Availability**
```bash
# Check what's using port 8002
netstat -tulpn | grep 8002
# or
lsof -i :8002

# If port is occupied, either:
# - Stop the conflicting service
# - Change brain service port in environment variables
```

**3. Verify WebSocket Endpoint**
```bash
# Test WebSocket connection manually
wscat -c ws://localhost:8002/mcp

# Correct endpoints:
# Development: ws://localhost:8002/mcp
# Production: wss://brain.ft.tc/mcp
```

---

### MCP Protocol Handshake Issues

#### Symptom
```
MCP initialization failed: Protocol version mismatch
```

#### Possible Causes
1. **Version mismatch**: Client and server using different MCP versions
2. **Invalid handshake**: Missing or incorrect initialization message
3. **Capability negotiation**: Unsupported capabilities requested

#### Solutions

**1. Verify MCP Version Compatibility**
```python
# Check client MCP version
import mcp
print(f"MCP Client Version: {mcp.__version__}")

# Ensure using compatible versions:
# mcp-server >= 0.4.0
# mcp-client >= 0.4.0
```

**2. Correct Handshake Implementation**
```python
# Python client example
async def initialize_mcp(websocket):
    # Send initialization request
    init_request = {
        "jsonrpc": "2.0",
        "id": "init",
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "clientInfo": {
                "name": "your-service-name",
                "version": "1.0.0"
            }
        }
    }

    await websocket.send(json.dumps(init_request))
    response = await websocket.recv()

    # Handle initialization response
    init_response = json.loads(response)
    if "error" in init_response:
        raise Exception(f"MCP initialization failed: {init_response['error']}")

    # Send initialized notification
    initialized_notification = {
        "jsonrpc": "2.0",
        "method": "notifications/initialized",
        "params": {}
    }

    await websocket.send(json.dumps(initialized_notification))
```

**3. TypeScript/JavaScript Client**
```typescript
async function initializeMcp(websocket: WebSocket): Promise<void> {
    return new Promise((resolve, reject) => {
        websocket.onmessage = (event) => {
            const response = JSON.parse(event.data);
            if (response.id === 'init') {
                if (response.error) {
                    reject(new Error(`MCP init failed: ${response.error.message}`));
                } else {
                    // Send initialized notification
                    websocket.send(JSON.stringify({
                        jsonrpc: '2.0',
                        method: 'notifications/initialized',
                        params: {}
                    }));
                    resolve();
                }
            }
        };

        // Send initialization request
        websocket.send(JSON.stringify({
            jsonrpc: '2.0',
            id: 'init',
            method: 'initialize',
            params: {
                protocolVersion: '2024-11-05',
                capabilities: { tools: {} },
                clientInfo: {
                    name: 'auto-movie-frontend',
                    version: '1.0.0'
                }
            }
        }));
    });
}
```

## Tool Execution Issues

### Tool Not Found Errors

#### Symptom
```json
{
  "error": {
    "code": "TOOL_NOT_FOUND",
    "message": "Tool 'embed_text' not found"
  }
}
```

#### Solutions

**1. Verify Available Tools**
```python
async def list_available_tools(websocket):
    request = {
        "jsonrpc": "2.0",
        "id": "list_tools",
        "method": "tools/list",
        "params": {}
    }

    await websocket.send(json.dumps(request))
    response = await websocket.recv()
    tools_response = json.loads(response)

    print("Available tools:")
    for tool in tools_response["result"]["tools"]:
        print(f"- {tool['name']}: {tool['description']}")
```

**2. Check Tool Name Spelling**
```python
# Correct tool names (case-sensitive):
correct_tools = [
    "embed_text",                 # NOT "embedText" or "embed-text"
    "search_by_embedding",        # NOT "searchByEmbedding"
    "store_document",             # NOT "storeDocument"
    "create_relationship",        # NOT "createRelationship"
    "query_graph",                # NOT "queryGraph"
    "batch_embed_texts",          # NOT "batchEmbedTexts"
    "bulk_store_documents",       # NOT "bulkStoreDocuments"
    "health_check"                # NOT "healthCheck"
]
```

---

### Parameter Validation Errors

#### Symptom
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Missing required parameter: project_id"
  }
}
```

#### Solutions

**1. Required Parameters Check**
```python
# All tools require project_id except health_check
required_params = {
    "embed_text": ["text", "project_id"],
    "search_by_embedding": ["embedding", "project_id"],
    "store_document": ["content", "metadata", "project_id"],
    "create_relationship": ["from_id", "to_id", "relationship_type"],
    "query_graph": ["cypher_query", "project_id"],
    "batch_embed_texts": ["texts", "project_id"],
    "bulk_store_documents": ["documents", "project_id"]
}

# Example correct call:
request = {
    "jsonrpc": "2.0",
    "id": "1",
    "method": "tools/call",
    "params": {
        "name": "embed_text",
        "arguments": {
            "text": "Sample text",      # Required
            "project_id": "proj-123"   # Required
        }
    }
}
```

**2. Parameter Type Validation**
```python
# Common type errors and fixes:

# ❌ Wrong: embedding as string
"arguments": {
    "embedding": "0.1,0.2,0.3",  # String
    "project_id": "proj-123"
}

# ✅ Correct: embedding as array
"arguments": {
    "embedding": [0.1, 0.2, 0.3],  # Array of numbers
    "project_id": "proj-123"
}

# ❌ Wrong: metadata as string
"arguments": {
    "content": "Document content",
    "metadata": "title=Sample Doc",  # String
    "project_id": "proj-123"
}

# ✅ Correct: metadata as object
"arguments": {
    "content": "Document content",
    "metadata": {"title": "Sample Doc"},  # Object
    "project_id": "proj-123"
}
```

## Service Integration Issues

### LangGraph Orchestrator Integration

#### Common Issues

**1. Neo4j Dependencies Still Present**

```bash
# Check for Neo4j references
cd services/langgraph-orchestrator
grep -r "neo4j" . --exclude-dir=.git
grep -r "NEO4J" . --exclude-dir=.git

# Remove Neo4j dependencies:
# 1. Remove from requirements.txt
# 2. Remove from environment files
# 3. Update import statements to use brain client
```

**2. Brain Client Not Initialized**

```python
# ❌ Wrong: Direct database access
from neo4j import GraphDatabase

class WorkflowService:
    def __init__(self):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

# ✅ Correct: Brain service client
from .clients.brain_client import BrainServiceClient

class WorkflowService:
    def __init__(self):
        self.brain_client = BrainServiceClient("ws://localhost:8002/mcp")
        await self.brain_client.connect()
```

**3. Environment Variables**

```bash
# Update .env file
# Remove:
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# Add:
BRAIN_SERVICE_BASE_URL=http://localhost:8002
BRAIN_SERVICE_WS_URL=ws://localhost:8002/mcp
```

---

### Auto-Movie Frontend Integration

#### Missing TypeScript Client

**Problem**: No MCP client for TypeScript/Next.js

**Solution**: Implement WebSocket MCP client

```typescript
// File: apps/auto-movie/src/lib/brain-client.ts

interface MCPRequest {
  jsonrpc: string;
  id: string;
  method: string;
  params: {
    name: string;
    arguments: Record<string, any>;
  };
}

interface MCPResponse {
  jsonrpc: string;
  id: string;
  result?: {
    content: Array<{ type: string; text: string }>;
  };
  error?: {
    code: string;
    message: string;
    data?: any;
  };
}

export class BrainServiceClient {
  private ws: WebSocket | null = null;
  private requestId = 0;
  private pendingRequests = new Map<string, {
    resolve: (value: any) => void;
    reject: (error: Error) => void;
  }>();

  constructor(private wsUrl: string) {}

  async connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      this.ws = new WebSocket(this.wsUrl);

      this.ws.onopen = async () => {
        try {
          await this.initializeMcp();
          resolve();
        } catch (error) {
          reject(error);
        }
      };

      this.ws.onmessage = (event) => {
        const response: MCPResponse = JSON.parse(event.data);
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

      this.ws.onerror = (error) => reject(error);
    });
  }

  async embedText(text: string, projectId: string): Promise<string> {
    const result = await this.callTool('embed_text', {
      text,
      project_id: projectId
    });

    return result.content[0].text;
  }

  async searchSimilar(query: string, projectId: string, limit = 10): Promise<any> {
    return this.callTool('find_similar_characters', {
      description: query,
      project_id: projectId,
      limit
    });
  }

  private async callTool(toolName: string, arguments: any): Promise<any> {
    const requestId = (++this.requestId).toString();

    const request: MCPRequest = {
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

      // Timeout after 30 seconds
      setTimeout(() => {
        const pending = this.pendingRequests.get(requestId);
        if (pending) {
          this.pendingRequests.delete(requestId);
          pending.reject(new Error('Request timeout'));
        }
      }, 30000);
    });
  }

  private async initializeMcp(): Promise<void> {
    // Implementation similar to Python version
    // Send initialize request and handle response
  }
}
```

**Usage in React Component**:
```typescript
// File: apps/auto-movie/src/components/CharacterSearch.tsx

import { useState, useEffect } from 'react';
import { BrainServiceClient } from '@/lib/brain-client';

export function CharacterSearch() {
  const [client, setClient] = useState<BrainServiceClient | null>(null);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const initClient = async () => {
      const brainClient = new BrainServiceClient(
        process.env.NEXT_PUBLIC_BRAIN_SERVICE_URL + '/mcp'
      );
      await brainClient.connect();
      setClient(brainClient);
    };

    initClient().catch(console.error);
  }, []);

  const handleSearch = async (query: string) => {
    if (!client) return;

    setLoading(true);
    try {
      const searchResults = await client.searchSimilar(query, 'movie-project');
      setResults(searchResults);
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      {/* Search UI implementation */}
    </div>
  );
}
```

---

### Celery Task Service Integration

#### Missing Brain Client

**Problem**: Celery service needs brain service integration

**Solution**: Add brain client to task service

```python
# File: services/celery-redis/app/clients/brain_client.py

import asyncio
import websockets
import json
from typing import Dict, Any, Optional

class BrainServiceClient:
    def __init__(self, ws_url: str):
        self.ws_url = ws_url
        self.websocket: Optional[websockets.WebSocketServerProtocol] = None
        self.request_id = 0

    async def connect(self):
        """Connect to brain service and initialize MCP"""
        self.websocket = await websockets.connect(self.ws_url)
        await self._initialize_mcp()

    async def store_task_result(self, task_id: str, result_data: Dict[str, Any], project_id: str) -> str:
        """Store task execution result in brain service"""
        return await self._call_tool("store_document", {
            "content": f"Task {task_id} completed with result: {result_data}",
            "metadata": {
                "task_id": task_id,
                "task_type": "celery_task",
                "status": "completed",
                "result": result_data
            },
            "project_id": project_id
        })

    async def search_similar_tasks(self, task_description: str, project_id: str) -> Dict[str, Any]:
        """Find similar task patterns"""
        return await self._call_tool("search_similar_workflows", {
            "query": task_description,
            "project_id": project_id,
            "limit": 5
        })

    async def _call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call MCP tool and return result"""
        # Implementation similar to other clients
        pass

    async def _initialize_mcp(self):
        """Initialize MCP protocol"""
        # Implementation similar to other clients
        pass
```

**Integration with Celery Tasks**:
```python
# File: services/celery-redis/app/tasks/movie_tasks.py

from celery import Celery
from .clients.brain_client import BrainServiceClient
import asyncio
import os

app = Celery('movie_tasks')

@app.task
def generate_character(character_brief: dict, project_id: str):
    """Generate character and store result in brain service"""

    # Your character generation logic here
    character_result = {
        "name": "Generated Character",
        "description": "Character description",
        "traits": ["trait1", "trait2"]
    }

    # Store result in brain service
    async def store_result():
        client = BrainServiceClient(os.getenv('BRAIN_SERVICE_WS_URL'))
        await client.connect()

        await client.store_task_result(
            task_id=generate_character.request.id,
            result_data=character_result,
            project_id=project_id
        )

    # Run async operation in sync context
    asyncio.run(store_result())

    return character_result
```

## External Service Issues

### Jina API Problems

#### API Key Issues

**Symptom**: `401 Unauthorized` or `403 Forbidden`

**Solutions**:
```bash
# Check API key configuration
echo $JINA_API_KEY

# Verify key format (should be jina_xxx format)
# Get new key from: https://jina.ai/

# Update environment
export JINA_API_KEY=jina_your_actual_key_here

# Or in .env file:
echo "JINA_API_KEY=jina_your_actual_key_here" >> .env
```

#### Rate Limiting

**Symptom**: `429 Too Many Requests`

**Solutions**:
```python
# Implement retry with exponential backoff
import time
import random

async def embed_with_retry(text: str, max_retries: int = 3):
    for attempt in range(max_retries):
        try:
            return await jina_service.embed(text)
        except RateLimitError as e:
            if attempt == max_retries - 1:
                raise e

            # Exponential backoff with jitter
            delay = (2 ** attempt) + random.uniform(0, 1)
            await asyncio.sleep(delay)
```

#### API Endpoint Issues

**Check API Status**:
```bash
# Test Jina API directly
curl -X POST "https://api.jina.ai/v1/embeddings" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer jina_your_key" \
  -d '{
    "model": "jina-embeddings-v2-base-en",
    "input": ["test text"]
  }'
```

---

### Neo4j Connection Issues

#### Connection Refused

**Symptom**: `ServiceUnavailable: Failed to establish connection`

**Solutions**:
```bash
# Check if Neo4j is running
docker ps | grep neo4j

# Start Neo4j if not running
docker run -d \
  --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:5.13

# Test connection
cypher-shell -a bolt://localhost:7687 -u neo4j -p password
```

#### Authentication Issues

**Solutions**:
```bash
# Reset Neo4j password
docker exec -it neo4j cypher-shell
# Run: CALL dbms.security.changeUserPassword('neo4j', 'newpassword');

# Update environment variables
NEO4J_USER=neo4j
NEO4J_PASSWORD=newpassword
NEO4J_URI=bolt://localhost:7687
```

## Environment Configuration Issues

### Missing Environment Variables

**Check Required Variables**:
```bash
# Brain service requirements
echo "Checking brain service environment..."
echo "JINA_API_KEY: ${JINA_API_KEY:-MISSING}"
echo "NEO4J_URI: ${NEO4J_URI:-MISSING}"
echo "NEO4J_USER: ${NEO4J_USER:-MISSING}"
echo "NEO4J_PASSWORD: ${NEO4J_PASSWORD:-MISSING}"

# Client service requirements
echo "BRAIN_SERVICE_BASE_URL: ${BRAIN_SERVICE_BASE_URL:-MISSING}"
echo "BRAIN_SERVICE_WS_URL: ${BRAIN_SERVICE_WS_URL:-MISSING}"
```

**Template Files**:

`.env.template` for brain service:
```bash
# Jina API Configuration
JINA_API_KEY=jina_your_api_key_here
JINA_API_URL=https://api.jina.ai/v1/embeddings

# Neo4j Database Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password_here

# MCP Server Configuration
MCP_SERVER_PORT=8002
LOG_LEVEL=INFO
```

`.env.template` for client services:
```bash
# Brain Service Connection
BRAIN_SERVICE_BASE_URL=http://localhost:8002
BRAIN_SERVICE_WS_URL=ws://localhost:8002/mcp

# Project Configuration
DEFAULT_PROJECT_ID=your_project_id_here
```

## Performance Issues

### Slow Response Times

#### Diagnosis Commands
```bash
# Check brain service health with timing
time curl http://localhost:8002/health

# Monitor WebSocket connections
netstat -an | grep :8002

# Check service logs
docker logs mcp-brain-service

# Monitor resource usage
docker stats mcp-brain-service
```

#### Solutions

**1. Optimize Batch Sizes**
```python
# Instead of processing one by one:
for text in texts:
    await client.embed_text(text, project_id)

# Use batch processing:
await client.batch_embed_texts(texts, project_id)
```

**2. Connection Pooling**
```python
# Maintain persistent connections
class BrainServicePool:
    def __init__(self, pool_size: int = 5):
        self.pool = asyncio.Queue(maxsize=pool_size)
        self.pool_size = pool_size

    async def initialize(self):
        for _ in range(self.pool_size):
            client = BrainServiceClient("ws://localhost:8002/mcp")
            await client.connect()
            await self.pool.put(client)

    async def get_client(self) -> BrainServiceClient:
        return await self.pool.get()

    async def return_client(self, client: BrainServiceClient):
        await self.pool.put(client)
```

**3. Enable Compression**
```python
# Enable WebSocket compression
websocket = await websockets.connect(
    uri,
    compression='deflate',
    max_size=10 * 1024 * 1024  # 10MB max message size
)
```

## Debugging Tools

### WebSocket Testing

**wscat** (Command line WebSocket client):
```bash
# Install wscat
npm install -g wscat

# Connect to brain service
wscat -c ws://localhost:8002/mcp

# Send MCP initialization
> {"jsonrpc":"2.0","id":"1","method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{"tools":{}},"clientInfo":{"name":"debug-client","version":"1.0.0"}}}

# Send tool call
> {"jsonrpc":"2.0","id":"2","method":"tools/call","params":{"name":"health_check","arguments":{}}}
```

### Log Analysis

**Brain Service Logs**:
```bash
# Follow logs in real-time
docker logs -f mcp-brain-service

# Search for specific errors
docker logs mcp-brain-service 2>&1 | grep -i error

# Filter by tool name
docker logs mcp-brain-service 2>&1 | grep "embed_text"
```

**Structured Log Analysis**:
```bash
# Extract JSON logs and format them
docker logs mcp-brain-service 2>&1 | \
  grep '{"timestamp"' | \
  jq -r '"\(.timestamp) [\(.level)] \(.message)"'
```

### Health Check Script

```bash
#!/bin/bash
# File: scripts/health-check.sh

echo "=== Movie Platform Health Check ==="

# Check brain service
echo "1. Checking brain service..."
if curl -s http://localhost:8002/health > /dev/null; then
    echo "✅ Brain service: healthy"
else
    echo "❌ Brain service: unhealthy"
fi

# Check Neo4j
echo "2. Checking Neo4j..."
if nc -z localhost 7687; then
    echo "✅ Neo4j: accessible"
else
    echo "❌ Neo4j: not accessible"
fi

# Check WebSocket
echo "3. Checking WebSocket..."
if timeout 5 wscat -c ws://localhost:8002/mcp -x '{"jsonrpc":"2.0","id":"health","method":"ping"}' > /dev/null 2>&1; then
    echo "✅ WebSocket: responding"
else
    echo "❌ WebSocket: not responding"
fi

# Check orchestrator
echo "4. Checking orchestrator..."
if curl -s http://localhost:8003/health > /dev/null; then
    echo "✅ Orchestrator: healthy"
else
    echo "❌ Orchestrator: unhealthy"
fi

# Check frontend
echo "5. Checking frontend..."
if curl -s http://localhost:3010 > /dev/null; then
    echo "✅ Frontend: accessible"
else
    echo "❌ Frontend: not accessible"
fi

echo "=== Health Check Complete ==="
```

## Getting Help

### Support Channels

1. **Check Documentation**: Review [architecture docs](../architecture/brain-service.md)
2. **Review API Reference**: Check [API documentation](../api/brain-service-api.md)
3. **Implementation Status**: See [implementation plan](../fixing-docs/jina-fix-implementation-plan.md)
4. **Common Issues**: Most issues are covered in this troubleshooting guide

### Creating Support Tickets

**Include This Information**:
1. **Service Version**: Docker image tags or commit hashes
2. **Environment**: Development/staging/production
3. **Error Messages**: Complete error text and stack traces
4. **Steps to Reproduce**: Exact sequence of actions
5. **Configuration**: Relevant environment variables (redacted)
6. **Logs**: Recent log entries around the time of the issue

**Example Support Request**:
```
Subject: WebSocket connection failing to brain service

Environment: Development
Brain Service Version: mcp-brain-service:latest
Client: langgraph-orchestrator

Error Message:
WebSocket connection failed: Error during WebSocket handshake: Unexpected response code: 500

Steps to Reproduce:
1. Start brain service with docker-compose up
2. Start orchestrator service
3. Orchestrator attempts to connect to ws://localhost:8002/mcp
4. Connection fails immediately

Logs:
[Brain Service] 2024-01-27 10:30:15 ERROR: WebSocket connection error: AttributeError: 'NoneType' object has no attribute 'connect'
[Orchestrator] 2024-01-27 10:30:15 ERROR: Failed to connect to brain service

Configuration:
BRAIN_SERVICE_WS_URL=ws://localhost:8002/mcp
JINA_API_KEY=jina_*** (redacted)
NEO4J_URI=bolt://localhost:7687
```

This comprehensive troubleshooting guide should help resolve most integration issues with the MCP Brain Service.