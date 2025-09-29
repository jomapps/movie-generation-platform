# Story Architect Agent Implementation

**Last Updated**: 2025-09-29  
**Status**: Draft Implementation Plan

## Overview
- Implements the Story MCP tool that transforms a Series Creator concept brief into a structured three-part story arc (setup, escalation, resolution) plus emotional beats.
- Ensures continuity with existing character rosters, propagates orchestrator trace metadata, and emits machine-readable continuity flags for downstream automation.
- Stores prompts, generated arcs, and continuity data within PayloadCMS to maintain versioning and cross-service alignment.

## System Responsibilities
1. Accept `concept_brief` and optional `creative_guidelines`, performing schema validation and normalization (trim whitespace, ensure arrays).
2. Retrieve genre/tone-specific prompt templates and deterministic seed values from PayloadCMS configuration collections.
3. Invoke configured LLM provider with prompt instructions, enforcing JSON output schema and carrying forward orchestrator trace headers.
4. Validate returned arc content against constraints (English-only, pacing, no new characters) and map continuity notes to machine-readable codes.
5. Persist story arc artifacts, validation metadata, and continuity flags to PayloadCMS collections for auditing and reuse.
6. Return `story_arc` payload to orchestrator; block when critical validation fails (e.g., new character introduction) with descriptive continuity flags.

## Data Contracts
### Request Payload
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

### Response Payload
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

### PayloadCMS Collections
- `storyArchitectPrompts`: `{ id, genre_tag, tone_tag, template_text, version, updated_at }`
- `storyArchitectSeeds`: `{ id, project_id, service_name, seed_value, last_used_at }`
- `characters`: canonical roster shared across services.
- `storyArcs`: `{ id, project_id, concept_brief_id, story_arc, continuity_flags[], seed, model_used, trace_ids, created_at }`
- `storyContinuityFlags`: `{ id, arc_id, code, message, severity, created_at }`

## Processing Pipeline
1. **Input Validation**
   - Confirm `concept_brief.core_conflict` present; reject otherwise.
   - Normalize tone/genre arrays (max length 3) and ensure English locale.
2. **Configuration Resolution**
   - Select prompt template matching primary `genre_tag`; fallback to default template if none.
   - Retrieve deterministic seed from `storyArchitectSeeds`; create entry if missing using hash of concept brief ID.
   - Fetch character roster from PayloadCMS `characters` collection for continuity checks.
3. **Prompt Assembly**
   - Build prompt referencing concept brief fields, creative guidelines, word-count guidance (soft limit ~80 words per section), and requirement to avoid introducing new characters.
   - Include instructions to produce machine-readable continuity flag suggestions with codes when assumptions are made.
   - Attach trace headers to LLM request for observability.
4. **LLM Invocation**
   - Call configured provider with JSON schema enforcement and deterministic seed.
   - On schema validation failure, retry once with error context.
5. **Post-Processing & Validation**
   - Parse JSON; ensure arc sections are non-empty and mention only characters present in roster.
   - Generate `continuity_flags` entries for issues (unknown characters, tone mismatches, runtime padding) with codes from catalog.
   - Accept sections exceeding 80 words if necessary; log length metrics for monitoring.
6. **Persistence**
   - Store arc, continuity flags, prompt version, seed, and trace metadata in `storyArcs` and `storyContinuityFlags` collections.
7. **Response Assembly**
   - Return normalized `story_arc` with continuity flags (code + message) and seed used.
   - If high-severity flag (e.g., `CHARACTER_NOT_FOUND`) present, instruct orchestrator to halt via response metadata (outside schema) while still returning arc for review.

## Continuity Flagging
- Maintain catalog of machine-readable codes, e.g.:
  - `CHARACTER_NOT_FOUND`
  - `LOCATION_UNSPECIFIED`
  - `CONFLICT_DRIFT`
  - `RUNTIME_FEASIBILITY_RISK`
- Use LLM to propose descriptive messages; map to codes via deterministic lookup.
- Persist flags in PayloadCMS for UI surfacing and downstream automation.

## Trace Propagation & Logging
- Accept trace headers from orchestrator and pass through to LLM provider via custom headers/metadata.
- Log request/response metadata (excluding raw concept brief) with trace IDs for correlation.
- Emit structured logs capturing template version, seed, latency, retry count.

## Error Handling
- Fatal errors (missing core conflict, template retrieval failure, character roster unavailable) result in MCP error response with `continuity_flags` describing blocker.
- Non-fatal issues captured as flags; arc still returned.
- Ensure LLM command failures include trace ID in error payload for debugging.

## Metrics & Observability
- Emit metrics: `story_architect.latency_ms`, `story_architect.arc_rejects`, `story_architect.continuity_flag_rate`, `story_architect.template_version` tag.
- Track distribution of word counts per arc section; monitor rate of schema retries.

## Testing Strategy
- **Unit Tests**: Character roster validation, continuity flag mapping, seed retrieval.
- **Integration Tests**: Prompt selection by genre, LLM call success path with schema enforcement, PayloadCMS persistence.
- **Regression Tests**: Golden concept briefs ensuring the arcs remain consistent and no new characters introduced.

## Future Enhancements
- Introduce adaptive prompt selection heuristics considering tone combinations.
- Support multilingual arcs once concept briefs support locales.
- Add automated suggestions when runtime feasibility flags trigger (e.g., recommending two-scene structure).
- Integrate with Brain/Story Bible services for franchise continuity once available.
