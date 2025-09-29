# Story Architect Service Documentation

## Overview

The Story Architect service is a comprehensive MCP (Model Context Protocol) service that transforms Series Creator concept briefs into structured three-part story arcs for short-form video content. This service acts as a bridge between conceptual ideas and structured narratives, ensuring consistency, character validation, and content quality through automated workflows.

## Architecture

### Service Components

```
┌─────────────────────────────────────────────────────────────────────┐
│                          Story Architect Service                    │
├─────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐     │
│  │   MCP Handler   │  │  Draft Story    │  │   Validation    │     │
│  │                 │  │   Arc Tool      │  │    Services     │     │
│  │ • Tool routing  │  │ • Orchestration │  │ • Character     │     │
│  │ • Error mgmt    │  │ • LLM integration│ │ • Word count    │     │
│  │ • Health checks │  │ • Response mgmt │  │ • Continuity    │     │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘     │
├─────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐     │
│  │ PayloadCMS      │  │ Character       │  │ Template        │     │
│  │ Service         │  │ Validation      │  │ Management      │     │
│  │ • CRUD ops      │  │ Service         │  │ • Jinja2        │     │
│  │ • Collections   │  │ • Roster check  │  │ • Fallback      │     │
│  │ • Seed mgmt     │  │ • Consistency   │  │ • Variables     │     │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘     │
├─────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │                    Configuration & Models                       │ │
│  │ • Pydantic models  • Environment config  • LLM settings        │ │
│  └─────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Input Reception**: MCP tool receives concept brief and optional creative guidelines
2. **Resource Gathering**: Retrieve prompt templates, character rosters, and deterministic seeds
3. **Prompt Assembly**: Render templates with concept data and context
4. **LLM Generation**: Generate structured story arc using OpenAI API
5. **Validation**: Validate word counts, character consistency, and content quality
6. **Flag Generation**: Create continuity flags for identified issues
7. **Persistence**: Store story arc and flags in PayloadCMS
8. **Response Assembly**: Return structured response with story arc and metadata

## Features

### Core Functionality

- **Concept Brief Transformation**: Convert high-level concepts into detailed three-part narratives
- **Character Roster Validation**: Ensure story consistency with established character databases
- **Continuity Flagging**: Automated detection and reporting of narrative inconsistencies
- **Deterministic Generation**: Reproducible results using seed-based generation
- **Word Limit Enforcement**: Configurable soft and hard limits with violation flagging
- **Template Management**: Genre and tone-specific prompt templates with Jinja2 support

### Advanced Features

- **Trace Propagation**: Full observability through distributed trace headers
- **Multi-Provider LLM Support**: Configurable LLM providers with fallback support
- **Graceful Error Handling**: Comprehensive error recovery and user-friendly messaging
- **Health Monitoring**: Real-time service health checks and dependency validation
- **Structured Logging**: JSON-formatted logs with correlation IDs and context

## Configuration

### Environment Variables

```bash
# Service Configuration
STORY_ARCHITECT_PORT=8003
STORY_ARCHITECT_LOG_LEVEL=INFO
STORY_ARCHITECT_ENV=development

# PayloadCMS Configuration
PAYLOAD_CMS_URL=http://localhost:3000
PAYLOAD_CMS_API_KEY=your_api_key_here
PAYLOAD_CMS_TIMEOUT=30
AUTO_SETUP_PAYLOAD_COLLECTIONS=true

# LLM Configuration
DEFAULT_LLM_PROVIDER=openai
OPENAI_API_KEY=your_openai_key
OPENAI_MODEL=gpt-4
OPENAI_MAX_TOKENS=1500
OPENAI_TEMPERATURE=0.7
OPENAI_TIMEOUT=60

# Content Limits
WORD_LIMIT_SOFT=400
WORD_LIMIT_HARD=500
MIN_WORDS_PER_SECTION=30
SECTION_BALANCE_THRESHOLD=0.3

# Feature Flags
DETERMINISTIC_SEED_ENABLED=true
STRICT_CHARACTER_VALIDATION=true
PERSIST_STORY_ARCS=true
DEFAULT_TARGET_RUNTIME=90
```

### Configuration Validation

The service validates all configuration at startup:
- Required environment variables presence
- Numeric value ranges
- URL format validation
- LLM provider availability
- PayloadCMS connectivity

## API Reference

### MCP Tools

#### `draft_story_arc`

Transform a concept brief into a structured story arc.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "concept_brief": {
      "type": "object",
      "properties": {
        "title": {"type": "string"},
        "logline": {"type": "string"},
        "core_conflict": {"type": "string"},
        "tone_keywords": {"type": "array", "items": {"type": "string"}},
        "genre_tags": {"type": "array", "items": {"type": "string"}},
        "audience_promise": {"type": "string"},
        "success_criteria": {"type": "array", "items": {"type": "string"}}
      },
      "required": ["title", "logline", "core_conflict", "tone_keywords", "genre_tags"]
    },
    "creative_guidelines": {
      "type": "object",
      "properties": {
        "must_include": {"type": "array", "items": {"type": "string"}},
        "must_avoid": {"type": "array", "items": {"type": "string"}},
        "target_runtime_seconds": {"type": "integer", "minimum": 5, "maximum": 300},
        "trace_headers": {
          "type": "object",
          "properties": {
            "x-trace-id": {"type": "string"},
            "x-request-id": {"type": "string"},
            "x-correlation-id": {"type": "string"}
          }
        }
      }
    },
    "project_id": {"type": "string"}
  },
  "required": ["concept_brief"]
}
```

**Response Schema:**
```json
{
  "story_arc": {
    "beginning": "string",
    "middle": "string", 
    "end": "string",
    "summary": "string"
  },
  "request_id": "string",
  "generated_at": "datetime",
  "model_used": "string",
  "processing_time_ms": "number"
}
```

#### `health_check`

Check service health and dependency status.

**Response Schema:**
```json
{
  "status": "healthy|unhealthy",
  "details": {
    "payload_cms": {"status": "healthy|unhealthy", "error": "string"},
    "llm": {"status": "configured|misconfigured", "provider": "string", "model": "string"},
    "configuration": {"status": "valid|invalid", "error": "string"}
  }
}
```

#### `get_service_info`

Retrieve service configuration and capabilities.

**Response Schema:**
```json
{
  "service_name": "Story Architect",
  "version": "1.0.0", 
  "description": "string",
  "capabilities": {
    "llm_providers": ["string"],
    "default_provider": "string",
    "word_limits": {"soft": "number", "hard": "number"},
    "character_validation": "boolean",
    "deterministic_seeds": "boolean",
    "persistence": "boolean"
  },
  "payload_cms": {
    "url": "string",
    "collections": ["string"]
  }
}
```

## Data Models

### Core Models

#### ConceptBrief
```python
class ConceptBrief(BaseModel):
    title: str
    logline: str
    core_conflict: str
    tone_keywords: List[str]
    genre_tags: List[str]
    audience_promise: Optional[str] = None
    success_criteria: Optional[List[str]] = None
```

#### StoryArc
```python
class StoryArc(BaseModel):
    beginning: str = Field(..., min_length=10, max_length=2000)
    middle: str = Field(..., min_length=10, max_length=2000)
    end: str = Field(..., min_length=10, max_length=2000)
    summary: Optional[str] = Field(None, max_length=500)
```

#### ContinuityFlag
```python
class ContinuityFlag(BaseModel):
    code: ContinuityFlagCode
    message: str
    section: str
    severity: ContinuitySeverity
    details: Optional[Dict[str, Any]] = None
    suggestions: Optional[List[str]] = None
```

### PayloadCMS Collections

#### storyArchitectPrompts
- Template management for different genres and tones
- Jinja2 template strings with variable substitution
- Metadata for template selection and versioning

#### storyArchitectSeeds
- Deterministic seed storage for reproducible generation
- Project-based organization
- Concept hash-based retrieval

#### storyArcs
- Complete story arc records with metadata
- Generation context and trace information
- Associated concept briefs and guidelines

#### storyContinuityFlags
- Validation flags linked to story arcs
- Machine-readable error codes
- Human-readable descriptions and suggestions

## Error Handling

### Error Categories

1. **Validation Errors**: Input schema violations, missing required fields
2. **Service Errors**: PayloadCMS connectivity, timeout issues
3. **LLM Errors**: API failures, timeout, quota exceeded, invalid responses
4. **Generation Errors**: Prompt rendering failures, content validation failures
5. **System Errors**: Configuration issues, dependency failures

### Error Response Format

```json
{
  "error": {
    "type": "ErrorClassName",
    "message": "Human-readable error description",
    "request_id": "uuid",
    "trace_id": "trace-identifier",
    "processing_time_ms": "number",
    "details": "object" // Optional additional context
  }
}
```

### Recovery Strategies

- **LLM Timeouts**: Automatic retry with exponential backoff
- **PayloadCMS Failures**: Graceful degradation with warning logs
- **Invalid LLM Responses**: Content validation with structured error reporting
- **Template Rendering**: Fallback to basic string replacement
- **Missing Dependencies**: Clear error messages with resolution steps

## Performance Considerations

### Optimization Strategies

1. **Caching**: Template caching, seed caching, character roster caching
2. **Connection Pooling**: Reuse HTTP connections to external services
3. **Async Processing**: Non-blocking I/O for concurrent request handling
4. **Resource Management**: Lazy initialization of LLM clients
5. **Content Optimization**: Efficient word counting, minimal processing overhead

### Performance Targets

- **Response Time**: < 10 seconds for typical story arc generation
- **Throughput**: 10+ concurrent requests per instance
- **Memory Usage**: < 512MB per instance
- **Error Rate**: < 1% under normal load conditions

### Monitoring Metrics

- Request processing time distribution
- LLM API response times
- PayloadCMS operation latencies
- Error rates by category
- Memory and CPU utilization
- Active request count

## Security Considerations

### Data Privacy

- **Concept Brief Hashing**: User ideas hashed before logging
- **Trace Data Scrubbing**: Sensitive information removed from traces
- **Log Sanitization**: Configurable log level filtering
- **API Key Security**: Environment variable storage only

### Access Control

- **PayloadCMS Authentication**: API key-based access control
- **LLM Provider Security**: Secure credential management
- **Service Isolation**: Container-based deployment isolation
- **Network Security**: Internal service communication only

### Compliance

- **Data Retention**: Configurable story arc persistence
- **Audit Logging**: Complete request/response audit trails  
- **Error Reporting**: Structured error logging without sensitive data
- **Dependency Scanning**: Regular security vulnerability assessment

## Deployment

### Requirements

- Python 3.9+
- PayloadCMS instance
- OpenAI API access
- Container runtime (Docker/Podman)
- Load balancer (for production)

### Environment Setup

1. **Development**:
   ```bash
   # Install dependencies
   pip install -r requirements.txt
   
   # Configure environment
   cp .env.example .env
   # Edit .env with your settings
   
   # Run service
   python -m src.main
   ```

2. **Production**:
   ```bash
   # Build container
   docker build -t story-architect-service .
   
   # Run with environment file
   docker run --env-file .env -p 8003:8003 story-architect-service
   ```

### Health Checks

The service provides multiple health check endpoints:
- `/health` - Basic service health
- `/health/detailed` - Comprehensive dependency check
- `/health/ready` - Kubernetes readiness probe
- `/metrics` - Prometheus metrics (if enabled)

### Scaling Considerations

- **Horizontal Scaling**: Multiple service instances behind load balancer
- **Resource Allocation**: 1 CPU core, 512MB RAM per instance
- **Database Scaling**: PayloadCMS instance scaling
- **Rate Limiting**: LLM API quota management
- **Caching Strategy**: Redis for shared caching (optional)

## Integration Patterns

### Series Creator Integration

```python
# Concept brief from Series Creator
concept_brief = {
    "title": "The Digital Detox",
    "logline": "A social media influencer must survive 30 days without technology.",
    "core_conflict": "Modern dependency vs. authentic living",
    "tone_keywords": ["comedic", "heartwarming"],
    "genre_tags": ["comedy", "drama"]
}

# Call Story Architect
story_arc = await story_architect_client.draft_story_arc(
    concept_brief=concept_brief,
    project_id="project-123"
)
```

### Character Service Integration

```python
# Character validation flow
character_roster = await payload_service.get_character_roster(project_id)
validation_flags = await character_validation_service.validate_story_arc(
    story_arc, character_roster, project_id
)
```

### Orchestrator Integration

```python
# Trace propagation
trace_headers = {
    "x-trace-id": "trace-123",
    "x-request-id": "req-456", 
    "x-correlation-id": "corr-789"
}

story_arc = await story_architect_client.draft_story_arc(
    concept_brief=concept_brief,
    creative_guidelines={"trace_headers": trace_headers}
)
```

## Testing Strategy

### Test Categories

1. **Unit Tests**: Individual component validation
2. **Integration Tests**: End-to-end workflow testing
3. **Performance Tests**: Load and stress testing
4. **Contract Tests**: API schema validation
5. **Security Tests**: Vulnerability scanning

### Test Coverage

- **Models**: Pydantic validation, edge cases
- **Services**: PayloadCMS integration, character validation
- **Tools**: MCP tool functionality, error handling
- **Configuration**: Environment variable validation
- **Error Scenarios**: Comprehensive error condition coverage

### Test Execution

```bash
# Unit tests
pytest tests/unit/ -v

# Integration tests  
pytest tests/integration/ -v

# All tests with coverage
pytest --cov=src tests/ --cov-report=html
```

## Troubleshooting

### Common Issues

1. **PayloadCMS Connection Failures**
   - Check URL and API key configuration
   - Verify network connectivity
   - Review PayloadCMS service logs

2. **LLM API Errors**
   - Validate API key and quota
   - Check model availability
   - Review timeout settings

3. **Template Rendering Failures**
   - Verify Jinja2 syntax in templates
   - Check variable availability
   - Review template selection logic

4. **Character Validation Issues**
   - Ensure character roster is populated
   - Check character name matching logic
   - Review validation service logs

### Diagnostic Commands

```bash
# Service health check
curl -X POST http://localhost:8003/health_check

# Service information
curl -X POST http://localhost:8003/get_service_info

# Test story arc generation
curl -X POST http://localhost:8003/draft_story_arc \
  -H "Content-Type: application/json" \
  -d '{"concept_brief": {...}}'
```

### Log Analysis

The service produces structured JSON logs with the following fields:
- `timestamp`: ISO 8601 timestamp
- `level`: Log level (DEBUG, INFO, WARN, ERROR)
- `logger`: Component name
- `message`: Human-readable message
- `request_id`: Request correlation ID
- `trace_id`: Distributed trace ID
- `context`: Additional context data

## Future Enhancements

### Planned Features

1. **Multi-Language Support**: i18n for story generation
2. **Advanced Character AI**: Dynamic character creation
3. **Visual Story Boards**: Integration with image generation
4. **Collaborative Editing**: Multi-user story refinement
5. **A/B Testing**: Multiple story arc variants
6. **Analytics Dashboard**: Story performance tracking

### Roadmap

- **Q1**: Enhanced character validation and roster management
- **Q2**: Multi-provider LLM support and optimization
- **Q3**: Visual story board generation integration
- **Q4**: Advanced analytics and performance dashboard

---

*This documentation is maintained by the Movie Generation Platform team. For questions or contributions, please refer to the project repository.*