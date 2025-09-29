# Character Creator Agent Specification

**Last Updated**: 2025-09-29  
**Status**: Draft  
**Service Type**: Character MCP Tool (profile generation)

## Purpose
- Produce minimal character profiles to inform visual design and dialogue tone.
- Ensure each primary character has clear role, motivation, and visual anchors for consistency.

## MVP Scope
- Limit to 2–4 characters per episode breakdown.
- Output lightweight profiles focusing on role, appearance highlights, and motivation.
- No long-form biographies or relational graphs in MVP; defer to Story Bible integration later.

## Inputs
- `scene_list` (array): Output from Episode Breakdown.
- `concept_brief` (object): For tone, genre, and conflict context.

## Outputs
- `character_profiles` (array[object]) each with:
  - `name` (string)
  - `role` (enum: protagonist, antagonist, support)
  - `motivation` (string, <=50 words)
  - `visual_signature` (string, <=40 words)
  - `relationships` (array[string], optional, simple descriptors)
  - `continuity_notes` (array[string], optional)

## Core Responsibilities
1. Extract implied characters from scenes and consolidate duplicates.
2. Provide concise visual cues to support Storyboard Artist and Image Generation prompts.
3. Flag ambiguities (e.g., unnamed characters) for manual resolution.

## Workflow
1. Parse `scene_list` to identify characters; allow orchestrator to pass manual overrides.
2. Generate or refine character descriptions via LLM prompt templates.
3. Deduplicate names, apply naming conventions (e.g., keep consistent across scenes).
4. Return structured profile list to orchestrator.

## Interfaces & Contracts
### MCP Tool: `generate_character_profiles`
- **Request Schema**
  ```json
  {
    "scene_list": [
      {
        "scene_number": 1,
        "primary_characters": ["Rhea"],
        "goal": "..."
      }
    ],
    "concept_brief": {
      "genre_tags": ["string"],
      "tone_keywords": ["string"],
      "core_conflict": "string"
    }
  }
  ```
- **Response Schema**
  ```json
  {
    "character_profiles": [
      {
        "name": "string",
        "role": "protagonist",
        "motivation": "string",
        "visual_signature": "string",
        "relationships": ["string"],
        "continuity_notes": ["string"]
      }
    ],
    "unresolved_references": ["string"]
  }
  ```

## Dependencies
- **Upstream**: Episode Breakdown and Concept Brief.
- **Downstream**: Storyboard Artist and Image Generation agents.
- **External**: Character MCP service runtime; optional future integration with Story Bible service.

## Non-Functional Requirements
- Latency target < 5s for four characters.
- Enforce naming uniqueness; auto-append descriptors when duplicates detected.
- Provide deterministic color palette suggestions in future (deferred).

## Operational Considerations
- Maintain dictionary of genre-specific archetypes to improve prompt accuracy.
- Allow manual overrides via `context.overrides` payload (deferred, but design schema now).
- Log unresolved references for QA triage.

## Risks & Open Questions
- Potential mismatch between automatically inferred characters and creative intent; need UI confirmation loop.
- Visual signatures might bias later prompts; consider neutral phrasing.
- Scaling beyond four characters will require batching or streaming responses.

## Testing Strategy
- **Unit**: Deduplication, schema validation, role assignment defaults.
- **Integration**: Test interplay with Storyboard Artist expected fields.
- **User Acceptance**: Weekly review of generated profiles by creative team.

## Metrics
- `character_creator.profile_count`
- `character_creator.unresolved_reference_rate`
- `character_creator.latency_ms`
