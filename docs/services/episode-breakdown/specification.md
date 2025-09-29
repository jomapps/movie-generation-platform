# Episode Breakdown Agent Specification

**Last Updated**: 2025-09-29  
**Status**: Draft  
**Service Type**: Story MCP Tool (scene planning)

## Purpose
- Expand the story arc into a concise list of scenes with key beats that downstream visual agents can execute.
- Provide actionable structure including scene goals, locations, and visual hooks.

## MVP Scope
- Limit output to 3–5 scenes total for the short clip.
- Capture only essential metadata: location, participating characters, beat summary.
- No branching logic, alternate takes, or multi-episode continuity in MVP.

## Inputs
- `story_arc` (object): Output of Story Architect agent.
- `concept_brief` (object): Pass-through data for maintaining thematic consistency.

## Outputs
- `scene_list` (array[object]) where each scene contains:
  - `scene_number` (int)
  - `goal` (string, <=40 words)
  - `location` (string)
  - `primary_characters` (array[string], <=4)
  - `visual_hook` (string) — camera or imagery idea
  - `beat_notes` (array[string], optional, <=3)

## Core Responsibilities
1. Translate arc phases into sequential scenes that preserve emotional pacing.
2. Provide enough visual direction for storyboard creation without over-specifying.
3. Maintain continuity with concept brief details (genre, tone, conflict).

## Workflow
1. Receive `story_arc` and `concept_brief` from orchestrator.
2. Expand each arc section into one or more scenes, ensuring total <=5.
3. Validate that characters referenced exist in prior payloads; flag extras.
4. Return structured `scene_list` JSON to orchestrator.

## Interfaces & Contracts
### MCP Tool: `generate_episode_breakdown`
- **Request Schema**
  ```json
  {
    "story_arc": {
      "setup": "string",
      "escalation": "string",
      "resolution": "string",
      "emotional_beats": ["string"]
    },
    "concept_brief": {
      "title": "string",
      "core_conflict": "string",
      "genre_tags": ["string"]
    }
  }
  ```
- **Response Schema**
  ```json
  {
    "scene_list": [
      {
        "scene_number": 1,
        "goal": "string",
        "location": "string",
        "primary_characters": ["string"],
        "visual_hook": "string",
        "beat_notes": ["string"]
      }
    ],
    "continuity_flags": ["string"]
  }
  ```

## Dependencies
- **Upstream**: Story Architect; optionally Series Creator for validation.
- **Downstream**: Character Creator (character profiles) and Storyboard Artist.

## Non-Functional Requirements
- Latency target < 7s
- Strict schema validation; ensure `scene_number` increments sequentially starting from 1.
- Provide deterministic outputs for same inputs (use seed-based sampling).

## Operational Considerations
- Reuse canonical character list once Character Creator completes; for MVP rely on names from concept/arc.
- Provide heuristics to prevent location drift (limit to 1–2 locations by default).
- Emit structured logs to support later analytics on scene counts and pacing.

## Risks & Open Questions
- Risk of introducing new characters before Character Creator has defined them.
- Need guardrails around unrealistic locations given budget/time (future integration with production constraints).
- Potential overlap with Character Creator responsibilities; alignment required.

## Testing Strategy
- **Unit**: Scene count/ordering validation, character reference checks.
- **Integration**: Ensure compatibility with Storyboard Artist schema expectations.
- **Scenario**: Regression suite using representative concept briefs.

## Metrics
- `episode_breakdown.scene_count`
- `episode_breakdown.validation_warnings`
- `episode_breakdown.latency_ms`
