# Troubleshooting Documentation

This directory contains comprehensive troubleshooting guides for the movie generation platform.

## Available Guides

### Integration Issues
- **[Integration Issues Guide](integration-issues.md)** - Complete troubleshooting guide for service integration
  - WebSocket connection failures
  - MCP protocol handshake issues
  - Tool execution errors
  - Service-specific integration problems
  - External service issues (Jina API, Neo4j)
  - Environment configuration problems
  - Performance optimization
  - Debugging tools and utilities

## Quick Reference

### Most Common Issues

1. **Brain Service Not Responding**
   ```bash
   # Check service health
   curl http://localhost:8002/health

   # Expected: {"status": "healthy"}
   ```

2. **WebSocket Connection Failed**
   ```bash
   # Test WebSocket connectivity
   wscat -c ws://localhost:8002/mcp

   # Or check if port is open
   netstat -tulpn | grep 8002
   ```

3. **MCP Tool Not Found**
   ```python
   # List available tools
   await client.list_tools()

   # Check tool name spelling (case-sensitive)
   "embed_text"  # ✅ Correct
   "embedText"   # ❌ Wrong
   ```

4. **Missing Environment Variables**
   ```bash
   # Check required variables
   echo "JINA_API_KEY: ${JINA_API_KEY:-MISSING}"
   echo "NEO4J_URI: ${NEO4J_URI:-MISSING}"
   echo "BRAIN_SERVICE_BASE_URL: ${BRAIN_SERVICE_BASE_URL:-MISSING}"
   ```

### Emergency Diagnostics

**Run this script for immediate system status:**

```bash
#!/bin/bash
# Quick health check

echo "=== Emergency Diagnostics ==="

# Brain service
if curl -s http://localhost:8002/health > /dev/null; then
    echo "✅ Brain service: healthy"
else
    echo "❌ Brain service: DOWN"
fi

# Neo4j
if nc -z localhost 7687; then
    echo "✅ Neo4j: accessible"
else
    echo "❌ Neo4j: DOWN"
fi

# WebSocket
if timeout 5 wscat -c ws://localhost:8002/mcp > /dev/null 2>&1; then
    echo "✅ WebSocket: responding"
else
    echo "❌ WebSocket: NOT responding"
fi

echo "=== Check logs for details ==="
docker logs mcp-brain-service --tail 10
```

## Error Categories

### Connection Errors
- **WebSocket failures**: Port conflicts, service down, network issues
- **Database connection**: Neo4j authentication, connectivity
- **API endpoints**: Jina API key, rate limiting, service availability

### Protocol Errors
- **MCP handshake**: Version mismatch, capability negotiation
- **Tool execution**: Invalid parameters, missing tools, validation failures
- **Message format**: JSON-RPC formatting, request structure

### Integration Errors
- **Service setup**: Missing clients, incorrect configuration
- **Environment**: Missing variables, wrong URLs, authentication
- **Dependencies**: Service startup order, health checks

### Performance Issues
- **Slow responses**: Network latency, resource constraints, inefficient queries
- **Timeouts**: Connection timeouts, request timeouts, health check failures
- **Resource usage**: Memory leaks, CPU usage, connection pools

## Debugging Workflow

### 1. Initial Assessment
```bash
# Check overall system health
./scripts/health-check.sh

# Review recent logs
docker-compose logs --tail 50

# Check resource usage
docker stats
```

### 2. Service-Specific Debugging
```bash
# Brain service logs
docker logs mcp-brain-service -f

# Orchestrator logs
docker logs langgraph-orchestrator -f

# Database logs
docker logs neo4j -f
```

### 3. Network Connectivity
```bash
# Test internal networking
docker network ls
docker network inspect movie-platform_default

# Check port availability
netstat -tulpn | grep -E "8002|8003|3010|8001|7687|7474"
```

### 4. Protocol Testing
```bash
# Manual WebSocket testing
wscat -c ws://localhost:8002/mcp

# Send test MCP message
> {"jsonrpc":"2.0","id":"1","method":"tools/list","params":{}}
```

## Prevention Strategies

### Monitoring Setup
1. **Health Checks**: Implement regular health monitoring
2. **Log Aggregation**: Centralize logs for easier debugging
3. **Metrics Collection**: Track key performance indicators
4. **Alert Configuration**: Set up alerts for critical failures

### Configuration Management
1. **Environment Templates**: Use .env.template files
2. **Validation Scripts**: Check configuration before startup
3. **Documentation**: Keep environment docs updated
4. **Version Control**: Track configuration changes

### Testing Practices
1. **Integration Tests**: Test service-to-service communication
2. **Health Checks**: Verify all dependencies before deployment
3. **Load Testing**: Ensure performance under load
4. **Chaos Engineering**: Test failure scenarios

## Getting Support

### Self-Service Resources
1. **Integration Issues Guide**: Detailed troubleshooting steps
2. **API Documentation**: Complete API reference and examples
3. **Architecture Documentation**: Service design and communication patterns
4. **Implementation Plan**: Current status and known issues

### Creating Support Requests

**Include This Information:**
- **Environment**: Development/staging/production
- **Service Versions**: Docker tags or commit hashes
- **Error Messages**: Complete error text and stack traces
- **Reproduction Steps**: Exact sequence to trigger the issue
- **System State**: Output from health checks and diagnostics
- **Configuration**: Relevant environment variables (redacted)
- **Logs**: Recent log entries around the time of issue

**Example Support Request Template:**
```
Subject: [SERVICE] Brief description of issue

Environment: [Development/Staging/Production]
Affected Services: [brain-service, orchestrator, etc.]
Severity: [High/Medium/Low]

Issue Description:
[Clear description of what's happening vs expected behavior]

Error Messages:
[Complete error text, stack traces]

Steps to Reproduce:
1. [Step 1]
2. [Step 2]
3. [Error occurs]

System State:
- Brain Service Health: [✅/❌]
- Neo4j Status: [✅/❌]
- WebSocket Connectivity: [✅/❌]

Logs:
[Relevant log entries with timestamps]

Configuration:
[Environment variables, docker-compose settings - redacted as needed]

Attempted Solutions:
[What you've tried already]
```

## Escalation Path

### Level 1: Self-Service
- Check troubleshooting guides
- Run diagnostic scripts
- Review configuration
- Check logs

### Level 2: Team Support
- Create detailed support request
- Include all diagnostic information
- Propose potential solutions
- Schedule debugging session if needed

### Level 3: Architecture Review
- Complex integration issues
- Performance problems
- Service design questions
- Major configuration changes

---

**Last Updated:** 2025-01-28
**Coverage:** All platform services and integrations
**Status:** Complete troubleshooting documentation