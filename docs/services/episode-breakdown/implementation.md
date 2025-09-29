# Episode Breakdown Agent Implementation

**Last Updated**: 2025-09-29  
**Status**: Draft Implementation Plan

## Overview
- Implements the Story MCP tool responsible for translating the story arc into a constrained list of 3–5 sequential scenes with actionable beats for downstream creative agents.
- Balances emotional pacing and production pragmatics (1–2 locations, <=4 primary characters per scene) while preserving thematic alignment with the concept brief.
- Integrates with PayloadCMS collections to validate canonical characters, persist deterministic seeding data, and log continuity flags for orchestrator and UI consumption.

## System Responsibilities
1. Accept `story_arc` and `concept_brief` payloads, validating schema and normalizing text inputs.
2. Dynamically derive scene counts from arc pacing cues (no fixed heuristics) while keeping the total within 3–5 scenes; escalate to human intervention when additional scenes are required.
3. Resolve character references against the PayloadCMS character collection, extending the schema when additional fields are needed.
4. Generate scene records with goals, locations, visual hooks, and beat notes, including rationales for each `visual_hook`.
5. Log `continuity_flags` and deterministic seed metadata into PayloadCMS collections to ensure reproducibility across retries.
6. Return `scene_list` and continuity data to the orchestrator, halting when blocking validation issues occur.

## Data Contracts
### Request Payload
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
    "genre_tags": ["string"],
    "tone_keywords": ["string"]
  }
}
```

### Response Payload
```json
{
  "scene_list": [
    {
      "scene_number": 1,
      "goal": "<=40 words",
      "location": "string",
      "primary_characters": ["string"],
      "visual_hook": "string",
      "visual_hook_rationale": "string",
      "beat_notes": ["string"]
    }
  ],
  "continuity_flags": ["string"],
  "deterministic_seed": "string"
}
```

### Internal Data Shapes
- `ArcSection`: `{ name, text, priority, inferred_length }`
- `SceneDraft`: `{ scene_number, goal, location, primary_characters[], visual_hook, rationale, beats[], source_arc_sections[] }`
- `CharacterRecord`: `{ id, name, project_id, traits, status }` (PayloadCMS collection)
- `ContinuityFlag`: `{ id, scene_number, description, severity }`
- `DeterministicSeedRecord`: `{ seed_value, source_service, project_id, last_used_at }`

## Processing Pipeline
1. **Input Validation & Normalization**
   - Confirm mandatory fields are present; trim whitespace and coerce empty arrays.
   - Derive context bundle (`title`, `genre_tags`, tone markers) for prompt generation.
2. **Arc Analysis & Scene Planning**
   - Analyze arc sections and emotional beats to determine pacing; dynamically compute target scene count (3–5) with fallback to human escalation if more beats demand additional scenes.
   - Allocate beats to scenes, merging lower-priority beats when necessary but never exceeding five scenes without emitting a blocking warning.
3. **Character Validation**
   - Query PayloadCMS `characters` collection (ensure required fields exist, add as needed: `name`, `project_id`, `aliases`, `status`).
   - Validate each referenced character; flag unknown names via `continuity_flags` and prompt orchestrator for intervention.
4. **Scene Draft Generation**
   - Populate `goal`, `location`, and `primary_characters` for each scene, limiting characters to four.
   - Generate `visual_hook` and associated `visual_hook_rationale` using deterministic LLM prompts seeded with the stored seed value.
   - Produce up to three concise `beat_notes` when additional context is beneficial.
5. **Deterministic Seeding**
   - Retrieve or create a deterministic seed entry in PayloadCMS (`deterministicSeeds` collection) keyed by project/service.
   - Use the seed to initialize random/stateful components, ensuring reproducible outputs for identical inputs; persist updated timestamps post-run.
6. **Continuity Flag Logging**
   - Store continuity issues (e.g., missing characters, beat overflows) in PayloadCMS `continuityFlags` collection with references to scene numbers.
7. **Response Assembly**
   - Ensure `scene_number` increments sequentially from 1.
   - Enforce goal length and character count constraints.
   - Return structured payload with `scene_list`, aggregated `continuity_flags`, and `deterministic_seed` used for the run.

## PayloadCMS Integration
- Extend or create the following collections as required:
  - `characters`: canonical character registry (shared with Character Creator).
  - `deterministicSeeds`: `{ project_id, service_name, seed_value, last_used_at }`.
  - `continuityFlags`: `{ project_id, service_name, scene_number, description, severity }`.
- Use PayloadCMS API for both reads and writes; avoid external databases.
- Store rationales and continuity data to facilitate UI surfacing and downstream agent coordination.

## Visual Hook Generation
- Maintain prompt templates under `/services/episode-breakdown/prompts/` (e.g., `visual_hook_master.prompt`).
- Template must request both hook and rationale, emphasizing production feasibility and alignment with genre/tone.
- Outputs should be concise, bias-free, and reference scene goals to inform storyboarders.
- Ensure rationales are persisted alongside hooks within the scene record.

## Continuity & Escalation Policies
- Limit scenes to <=5; if beat coverage requires more, generate a high-severity continuity flag and halt further scene generation pending human review.
- Record unresolved characters or setting conflicts in `continuity_flags` and in PayloadCMS.
- Locations remain unconstrained (no whitelist), but maintain a heuristic to prefer 1–2 distinct locations; note deviations via medium-severity flags.

## Error Handling & Safeguards
- Reject requests missing required arc sections or concept brief fields.
- Abort processing when character validation fails and cannot be resolved via registry (return continuity flag and descriptive error).
- Ensure deterministic seed retrieval failures surface an actionable error rather than silently generating non-deterministic output.
- Provide clear status codes/messages to orchestrator for blocked runs (e.g., beat overflow, unknown character).

## Metrics & Observability
- Emit structured logs capturing:
  - `episode_breakdown.scene_count`
  - `episode_breakdown.validation_warnings`
  - `episode_breakdown.latency_ms`
  - Seed value used and whether cached or newly generated.
- Track counts of high-severity continuity flags to monitor script quality issues.

## Testing Strategy
- **Unit Tests**: Scene count enforcement, character registry validation, deterministic seed usage, visual hook rationale presence.
- **Integration Tests**: Interaction with PayloadCMS collections, ensuring continuity flags persist and can be retrieved by downstream agents.
- **Scenario Tests**: End-to-end runs with representative story arcs to confirm human intervention triggers when beat counts exceed five scenes.

## Future Enhancements
- Introduce heuristic-based location budgeting once production constraints are modeled.
- Support automated merging suggestions for beat overflows instead of manual intervention only.
- Expand deterministic seeding to coordinate with other services (shared seed bus) for synchronized retries.
- Provide richer rationale data structures (e.g., linking to concept brief excerpts) for downstream explainability.
