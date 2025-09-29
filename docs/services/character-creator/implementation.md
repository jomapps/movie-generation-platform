# Character Creator Agent Implementation

**Last Updated**: 2025-09-29  
**Status**: Draft Implementation Plan

## Overview
- Implements the Character MCP tool responsible for generating lightweight character profiles that inform downstream visual and dialogue pipelines.
- Targets 2–4 principal characters per episode, focusing on role clarity, motivation, and succinct visual anchors rather than full biographies.
- Ensures alignment with Episode Breakdown outputs while preparing structured data for Storyboard Artist and Image Generation services.

## System Context & Responsibilities
1. Ingest `scene_list` (from Episode Breakdown) and `concept_brief` inputs, normalizing scene metadata.
2. Query the canonical character registry hosted in Auto-Menu PayloadCMS to consolidate previously defined characters.
3. Deduplicate characters discovered in scenes, enforcing naming uniqueness by appending alphabetical descriptors (`Eugene A`, `Eugene B`, ...).
4. Generate concise motivations and visual signatures through standardized LLM prompt templates (seeded set, e.g., `master_reference`).
5. Produce `character_profiles` payload and capture unresolved or ambiguous references for manual reconciliation.
6. Halt processing when guidance is insufficient (`"lacking_guidance"`) so the orchestrator can reroute for clarification.

## Data Contracts
### Request Payload
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

### Response Payload
```json
{
  "character_profiles": [
    {
      "name": "string",
      "role": "protagonist",
      "motivation": "<=50 words",
      "visual_signature": "<=40 words",
      "relationships": ["string"],
      "continuity_notes": ["string"]
    }
  ],
  "unresolved_references": ["string"]
}
```

### Internal Shapes
- `NormalizedScene`: `{ scene_number, primary_characters[], secondary_characters[], goal, notes }`
- `RegistryCharacter`: `{ id, name, project_id, attributes }`
- `WorkingProfile`: `{ name, role, motivation, visual_signature, relationships[], continuity_notes[], source_scenes[] }`

## Processing Pipeline
1. **Normalize Input**: Validate schema, coerce missing arrays to empty lists, and map scene characters into preliminary sets.
2. **Registry Sync**: Query Auto-Menu PayloadCMS collection (required fields: `name`, `project_id`) to seed known characters for deduplication.
3. **Character Extraction**: Aggregate characters across scenes, attaching originating scenes and goals.
4. **Deduplicate & Resolve Names**:
   - Match against registry entries (case-insensitive).
   - For new duplicates, append alphabetical suffixes (`Base Name`, `Base Name A`, `Base Name B`, ...).
   - Record any unresolved entities in `unresolved_references`.
5. **Profile Generation**:
   - Derive role from scene prominence (default ordering protagonist → antagonist → support).
   - Populate motivation and visual signature via LLM prompt templates (see **Prompt Templates**).
   - Only create `relationships` when data is available; otherwise set to `[]`.
   - Populate `continuity_notes`; if guidance is missing, assign `"lacking_guidance"` and abort further processing.
6. **Assemble Response**: Validate output schema, enforce word limits, and include unresolved references for UI follow-up.

## Character Registry Integration
- Use Auto-Menu PayloadCMS as the single source of truth for characters.
- Required fields: `name` (string), `project_id` (UUID/string). Additional attributes are optional and can be expanded iteratively.
- Workflow:
  1. Query registry at job start filtered by `project_id`.
  2. For new characters, create minimal entries (`name`, `project_id`) and persist asynchronously after validation.
  3. Update registry records as motivations/visual signatures evolve to keep downstream services synchronized.

## Prompt Templates
- Maintain a seed set of reusable prompts stored alongside service code (e.g., `/services/character-creator/prompts/master_reference.prompt`).
- **`master_reference` Template (example skeleton):**
  ```text
  You are generating a concise character anchor for storyboard and image teams.
  Context: {genre_tags}, tone {tone_keywords}, conflict {core_conflict}.
  Character: {name}, scenes {scene_numbers}, role {role}.
  Provide motivation (<=50 words) and visual signature (<=40 words) using neutral, bias-free descriptors.
  ```
- Additional templates can diverge by genre but should share the same output contract to simplify parsing.

## Relationships & Continuity Logic
- Create relationship descriptors only when explicit references exist; otherwise omit the field to prevent speculation.
- When upstream data lacks guidance, insert the literal string `"lacking_guidance"` into `continuity_notes`, halt processing, and surface the blocking issue to the orchestrator.
- Unresolved or ambiguous characters (`unknown soldier`, `mysterious figure`) should be logged in `unresolved_references` for manual follow-up while preventing downstream propagation.

## Error Handling & Safeguards
- **Validation Errors**: Reject requests missing mandatory fields with descriptive error messages for the orchestrator.
- **Lacking Guidance**: Immediately stop profile generation when `"lacking_guidance"` is encountered and return a blocking status.
- **Override Support**: Reserve hooks for future `context.overrides` payloads; design DTOs now but stub implementation until transport is finalized.
- **Logging**: Log registry queries, dedup decisions, prompt invocations, and unresolved outcomes for QA triage.

## Metrics & Observability
- `character_creator.profile_count`: Number of profiles generated per invocation.
- `character_creator.unresolved_reference_rate`: Ratio of unresolved references to total characters.
- `character_creator.latency_ms`: End-to-end latency (target < 5000 ms for <=4 characters).
- Emit structured logs for deduplication outcomes and prompt latency to support performance reviews.

## Testing Strategy
- **Unit Tests**: Validate deduplication naming, schema enforcement, role assignment defaults, and `lacking_guidance` halt behavior.
- **Integration Tests**: Mock registry interactions, confirm contract adherence with Storyboard Artist/Image Generation expectations, and verify unresolved reference propagation.
- **User Acceptance**: Weekly creative review of generated profiles to calibrate prompt templates and adjust tone.

## Future Enhancements
- Implement deterministic color palette generation once downstream services consume the new field.
- Finalize `context.overrides` schema and transport for orchestrator-driven adjustments.
- Expand prompt library with genre-specific archetype variations while maintaining shared contracts.
- Introduce batching or streaming to scale beyond four characters per invocation.
