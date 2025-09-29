# MCP Story Architect Service

## Overview

The Story Architect Service is an MCP (Model Context Protocol) tool that transforms Series Creator concept briefs into structured three-part story arcs for short-form video content. It provides the `draft_story_arc` tool that creates setup, escalation, and resolution sections with emotional beats and continuity validation.

## Features

- **Three-Part Story Arc Generation**: Creates setup, escalation, and resolution sections
- **Character Roster Validation**: Ensures story arcs don't introduce new characters
- **Continuity Flagging**: Machine-readable continuity flags with code mapping
- **Genre/Tone-Specific Prompts**: Template selection based on concept brief attributes
- **Deterministic Seed Management**: Consistent story generation for the same inputs
- **Trace Propagation**: Full observability with orchestrator trace headers
- **PayloadCMS Integration**: Persistent storage for arcs, prompts, and continuity data

## Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Run the service**:
   ```bash
   python src/main.py
   ```

## MCP Tool

### `draft_story_arc`

**Input Schema**:
```json
{
  "concept_brief": {
    "title": "string",
    "logline": "string", 
    "core_conflict": "string",
    "tone_keywords": ["string"],
    "genre_tags": ["string"],
    "audience_promise": "string",
    "success_criteria": ["string"]
  },
  "creative_guidelines": {
    "must_include": ["string"],
    "must_avoid": ["string"],
    "target_runtime_seconds": 30,
    "trace_headers": {
      "x-trace-id": "string",
      "x-request-id": "string"
    }
  }
}
```

**Output Schema**:
```json
{
  "story_arc": {
    "setup": "string",
    "escalation": "string", 
    "resolution": "string",
    "emotional_beats": ["string"],
    "continuity_flags": [
      {
        "code": "CHARACTER_NOT_FOUND",
        "message": "Arc referenced character 'Nova' not present in roster"
      }
    ],
    "seed": "string"
  }
}
```

## Architecture

- **MCP Tool Layer**: `draft_story_arc` tool implementation
- **Service Layer**: Character validation, continuity flagging, prompt management
- **PayloadCMS Integration**: Templates, seeds, arcs, continuity flags storage
- **LLM Integration**: OpenAI with deterministic seed support
- **Observability**: Metrics, logging, and trace propagation

## PayloadCMS Collections

- **storyArchitectPrompts**: Genre/tone-specific prompt templates
- **storyArchitectSeeds**: Deterministic seed management per project
- **characters**: Shared character roster for validation
- **storyArcs**: Generated story arcs with metadata
- **storyContinuityFlags**: Machine-readable continuity validation

## Continuity Flag Codes

- `CHARACTER_NOT_FOUND`: Referenced character not in roster
- `LOCATION_UNSPECIFIED`: Story lacks clear location context
- `CONFLICT_DRIFT`: Arc deviates from concept brief core conflict
- `RUNTIME_FEASIBILITY_RISK`: Story too complex for target runtime
- `TONE_MISMATCH`: Generated tone doesn't match concept brief
- `PACING_ISSUE`: Story structure inappropriate for short-form

## Development

Run tests:
```bash
pytest tests/
```

Code formatting:
```bash
black src/
ruff check src/
```

Type checking:
```bash
mypy src/
```

## Configuration

Key configuration options:

- **Word Limits**: Soft limit (~80 words) and hard limit (~120 words) per section
- **Character Validation**: Strict validation against PayloadCMS character roster
- **Continuity Flagging**: Enable/disable continuity validation
- **Deterministic Seeds**: Reproducible story generation
- **Trace Propagation**: Orchestrator trace header support

## Metrics

- `story_architect.latency_ms`: Request processing time
- `story_architect.arc_rejects`: Failed arc generation attempts
- `story_architect.continuity_flag_rate`: Rate of continuity issues detected
- `story_architect.template_version`: Active prompt template versions

## License

Private - Movie Generation Platform