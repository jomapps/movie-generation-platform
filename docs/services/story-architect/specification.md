# Story Architect Agent Specification

**Last Updated**: 2025-09-29  
**Status**: Draft  
**Service Type**: Story MCP Tool (high-level arc design)

## Purpose
- Transform the concept brief into a cohesive story arc for a short-form episode.
- Define beginning, middle, end beats and emotional cadence to guide subsequent breakdown work.

## MVP Scope
- Produce a single three-part arc (setup, confrontation, resolution) sized for a 10–30s video.
- Limit to one arc per concept brief; manual re-runs handle iterations.
- No branching storylines or multi-episode planning in MVP.

## Inputs
- `concept_brief` (object): Output from Series Creator agent.
- `creative_guidelines` (optional): Tone/genre overrides supplied by producers.

## Outputs
- `story_arc` (object): Minimal structure for Episode Breakdown agent.
  - `setup` (string, <=80 words)
  - `escalation` (string, <=80 words)
  - `resolution` (string, <=80 words)
  - `emotional_beats` (array[string], 3 items)
  - `continuity_flags` (array[string], optional warnings)

## Core Responsibilities
1. Preserve the core conflict defined in the concept brief.
2. Ensure pacing supports a short-form clip (clear hook, midpoint, payoff) without extra subplots.
3. Provide continuity flags when assumptions are made (e.g., off-screen events).

## Workflow
1. Receive `concept_brief` payload from orchestrator.
2. Apply reusable prompt template to produce arc sections via LLM.
3. Validate length constraints and ensure conflict references align with concept brief.
4. Emit structured `story_arc` JSON.

## Interfaces & Contracts
### MCP Tool: `draft_story_arc`
- **Request Schema**
  ```json
  {
    "concept_brief": {
      "title": "string",
      "logline": "string",
      "core_conflict": "string",
      "tone_keywords": ["string"],
      "genre_tags": ["string"]
    },
    "creative_guidelines": {
      "must_include": ["string"],
      "must_avoid": ["string"],
      "target_runtime_seconds": 30
    }
  }
  ```
- **Response Schema**
  ```json
  {
    "story_arc": {
      "setup": "string",
      "escalation": "string",
      "resolution": "string",
      "emotional_beats": ["string"],
      "continuity_flags": ["string"]
    }
  }
  ```

## Dependencies
- **Upstream**: Series Creator agent.
- **Downstream**: Episode Breakdown agent.
- **External**: Same LLM provider as Series Creator (shared prompt harness).

## Non-Functional Requirements
- Latency target < 6s.
- Enforce deterministic JSON schema using shared validation library.
- Trace IDs propagated from orchestrator for observability.

## Operational Considerations
- Maintain prompt variants per genre in config; choose variant based on `genre_tags`.
- Capture key assumptions in `continuity_flags` for transparency.
- Provide structured logs for future fine-tuning dataset creation.

## Risks & Open Questions
- Very short runtimes may compress arcs too much; consider templated guardrails.
- Future extension to multi-episode arcs will require persistence layer.
- Need fallback if LLM introduces new characters not defined yet.

## Testing Strategy
- **Unit**: Schema validation, tone keyword propagation.
- **Integration**: LLM response parsing, orchestrator message handling.
- **Regression**: Golden set of concept briefs to detect drift in arc quality.

## Metrics
- `story_architect.latency_ms`
- `story_architect.arc_rejects`
- `story_architect.continuity_flag_rate`
