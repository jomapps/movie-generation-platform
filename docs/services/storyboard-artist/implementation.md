# Storyboard Artist Agent Implementation

**Last Updated**: 2025-09-29  
**Status**: Draft Implementation Plan

## Overview
- Implements the Visual MCP tool responsible for converting `scene_list` and `character_profiles` into 6–12 sequential storyboard frames with actionable camera guidance and timing metadata.
- Balances narrative coverage with 7-second shot segments, ensuring each frame supports downstream Image Generation and Video Generation workflows.
- Centralizes prompt templates, vocabulary libraries, and generated outputs within PayloadCMS for automatic versioning and reuse.

## System Responsibilities
1. Ingest ordered scenes, character profiles, and optional visual constraints; validate schemas and normalize data (trim strings, dedupe characters).
2. Determine shot counts per scene using heuristic scoring (goal complexity, action density, scene runtime budget) while respecting overall frame targets.
3. Generate frame descriptions, camera notes, lighting moods, prompt seeds, and per-frame duration estimates through LLM prompts seeded for deterministic output.
4. Reconcile scene instructions with character profiles, prioritizing scene directives when conflicts arise; surface discrepancies via `continuity_notes` with machine-readable codes.
5. Persist generated frames, timing metadata, vocabulary entries, and continuity notes to PayloadCMS collections.
6. Return structured `storyboard_frames` array to orchestrator or block with descriptive error when confident output cannot be produced.

## Data Contracts
### Request Payload
```json
{
  "scene_list": [
    {
      "scene_number": 1,
      "goal": "string",
      "location": "string",
      "primary_characters": ["string"],
      "visual_hook": "string",
      "beat_notes": ["string"],
      "suggested_runtime_seconds": 6.5
    }
  ],
  "character_profiles": [
    {
      "name": "string",
      "visual_signature": "string",
      "relationships": ["string"],
      "continuity_notes": ["string"]
    }
  ],
  "visual_constraints": {
    "aspect_ratio": "16:9",
    "style_reference": "cel_shaded",
    "seed_hint": "noir-rain"
  }
}
```

### Response Payload
```json
{
  "storyboard_frames": [
    {
      "frame_id": "SCENE_1_SHOT_1",
      "scene_number": 1,
      "shot_order": 1,
      "description": "<=60 words",
      "camera_notes": "string",
      "characters_present": ["string"],
      "lighting_mood": "string",
      "prompt_seed": "string",
      "duration_seconds": 3.2
    }
  ],
  "continuity_notes": [
    {
      "code": "WARDROBE_CONFLICT",
      "message": "Scene 2 shot 1 uses red jacket per scene brief despite profile reference to blue."
    }
  ]
}
```

### Internal PayloadCMS Collections
- `storyboardPromptTemplates`: `{ id, name, version, template_text, max_runtime_seconds, updated_at }`
- `storyboardVocabularies`: `{ id, type (camera|lighting|prompt_seed), values[], allow_custom: true }`
- `storyboardFrames`: `{ id, project_id, scene_number, shot_order, description, camera_notes, lighting_mood, prompt_seed, duration_seconds, frame_id, generated_at }`
- `storyboardContinuity`: `{ id, frame_id, code, message, severity, created_at }`
- `storyboardRuntimeHeuristics`: `{ id, weights: { goal_complexity, action_density, hook_intensity }, updated_at }`

## Shot Planning Heuristics
- Base target: 1–2 shots per scene; expand to 3 when `beat_notes` > 2 or `visual_hook` denotes dynamic action.
- Enforce per-shot duration cap of 7 seconds; compute total scene runtime using `suggested_runtime_seconds` fallback to 6 seconds when absent.
- Heuristic weights stored in `storyboardRuntimeHeuristics`; adjust without code changes via PayloadCMS.
- Ensure overall frame count stays within 6–12; if heuristic allocation exceeds bounds, rebalance by trimming lowest-priority beats.

## Prompt Template & Vocabulary Management
- Fetch latest storyboard template by version tag; template includes instructions for camera notes, lighting, prompt seeds, and timing metadata.
- Vocabulary lists (camera move verbs, lighting moods) retrieved from `storyboardVocabularies`; allow LLM to add novel entries while recording them back to collection for future reuse.
- Deterministic seeds composed from scene number + shot order + optional `visual_constraints.seed_hint` to stabilize downstream diffusion prompts.

## Character & Scene Reconciliation
- Merge character data per scene by matching `primary_characters` and optional supporting cast.
- When discrepancies exist (wardrobe, props), favor scene instructions; log continuity note with code `SCENE_OVERRIDES_PROFILE` and include descriptive message.
- Ensure each frame references at least one character when `primary_characters` non-empty; allow empty character lists for establishing shots and tag with `ESTABLISHING_SHOT` code if no characters present.

## Timing Metadata Generation
- Derive `duration_seconds` per frame by dividing scene runtime across allocated shots proportional to heuristic weight (e.g., action beats receive larger share).
- Enforce 0.5s minimum to avoid zero-duration segments.
- Include cumulative runtime tracking to assist Video Generation pacing; store totals in frame records for analytics.

## Error Handling & Fallbacks
- If LLM cannot produce confident description (e.g., missing mandatory scene info), abort generation and return MCP error with `continuity_notes` containing `INSUFFICIENT_CONTEXT`.
- Validate schema post-generation; any failure triggers single retry with clarified instructions, else escalate error.
- Reject outputs exceeding 60-word description limit unless trimming maintains meaning; log soft violations for monitoring.

## Persistence Workflow
1. After validation, upsert frames into `storyboardFrames` collection (idempotent by `frame_id`).
2. Store continuity notes in `storyboardContinuity` with severity (`low`, `medium`, `high`).
3. Record template version, seed, latency metrics alongside frame records for audit.

## Observability & Metrics
- Emit metrics:
  - `storyboard_artist.frame_count`
  - `storyboard_artist.latency_ms`
  - `storyboard_artist.continuity_note_count`
  - `storyboard_artist.average_shot_duration`
- Log trace IDs from orchestrator headers; include scene/shot context for downstream debugging.

## Testing Strategy
- **Unit Tests**: Frame ID formatting, heuristic shot allocation, duration distribution, continuity note coding.
- **Integration Tests**: LLM prompt execution, PayloadCMS vocabulary updates, schema validation against Image Generation expectations.
- **Creative QA**: Weekly sample review to assess narrative coverage and consistency with character/scene briefs.

## Future Enhancements
- Introduce style-specific prompt variants curated per production.
- Add storyboard-to-shot continuity matrix for animatics planning.
- Support automatic thumbnail generation once image synthesis integration is available.
- Expand timing metadata to include easing suggestions or transition cues for Video Generation.
