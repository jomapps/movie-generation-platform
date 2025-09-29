# Storyboard Artist Agent Specification

**Last Updated**: 2025-09-29  
**Status**: Draft  
**Service Type**: Visual MCP Tool (storyboard drafting)

## Purpose
- Translate scene breakdowns and character profiles into rough storyboard frames with camera guidance.
- Provide enough visual specificity for prompt-based image generation.

## MVP Scope
- Output 6–12 storyboard frames per request.
- Each frame includes composition notes, key action, and camera treatment; no sketches or rendered imagery in MVP.
- Maintain sequential order matching `scene_list`.

## Inputs
- `scene_list` (array): Ordered scenes from Episode Breakdown.
- `character_profiles` (array): Character Creator output.
- `visual_constraints` (optional): Style or aspect ratio requirements.

## Outputs
- `storyboard_frames` (array[object])
  - `frame_id` (string, `SCENE_{n}_SHOT_{m}`)
  - `scene_number` (int)
  - `shot_order` (int within scene)
  - `description` (string, <=60 words)
  - `camera_notes` (string)
  - `characters_present` (array[string])
  - `lighting_mood` (string, optional)
  - `prompt_seed` (string, optional guidance for image model)

## Core Responsibilities
1. Ensure visual flow captures major emotional beats and matches runtime constraints.
2. Provide actionable prompts for the Image Generation agent without conflicting instructions.
3. Highlight continuity requirements (e.g., props, costumes) when critical to narrative.

## Workflow
1. Ingest scenes and character profiles.
2. Determine shots per scene (1–2 in MVP) based on action density.
3. Generate textual storyboard descriptions through template-driven LLM prompts.
4. Validate ordering and payload structure; return to orchestrator.

## Interfaces & Contracts
### MCP Tool: `draft_storyboard_frames`
- **Request Schema**
  ```json
  {
    "scene_list": [
      {
        "scene_number": 1,
        "goal": "string",
        "location": "string",
        "primary_characters": ["string"],
        "visual_hook": "string"
      }
    ],
    "character_profiles": [
      {
        "name": "string",
        "visual_signature": "string"
      }
    ],
    "visual_constraints": {
      "aspect_ratio": "16:9",
      "style_reference": "cel_shaded"
    }
  }
  ```
- **Response Schema**
  ```json
  {
    "storyboard_frames": [
      {
        "frame_id": "SCENE_1_SHOT_1",
        "scene_number": 1,
        "shot_order": 1,
        "description": "string",
        "camera_notes": "string",
        "characters_present": ["string"],
        "lighting_mood": "string",
        "prompt_seed": "string"
      }
    ],
    "continuity_notes": ["string"]
  }
  ```

## Dependencies
- **Upstream**: Episode Breakdown, Character Creator.
- **Downstream**: Image Generation agent.
- **External**: Visual MCP runtime, prompt template repository.

## Non-Functional Requirements
- Latency target < 8s for 10 frames.
- Guarantee consistent naming convention for frames to support asset tracking.
- Avoid contradictory instructions (camera vs. description) by using validation checks.

## Operational Considerations
- Allow style presets per production (anime, live-action, etc.) configurable via context.
- Provide per-frame `prompt_seed` to stabilize downstream diffusion outputs.
- Record usage metrics for future prioritization of automation vs. human oversight.

## Risks & Open Questions
- High variance in LLM output quality; may require prompt tuning loop.
- Need guidelines for pacing when converting 5 scenes into 8+ frames.
- Future need for shot continuity matrix across frames.

## Testing Strategy
- **Unit**: Frame ID formatting, character coverage, schema checks.
- **Integration**: Validate compatibility with Image Generation prompt expectations.
- **Creative QA**: Weekly manual review of sample frames to calibrate prompts.

## Metrics
- `storyboard_artist.frame_count`
- `storyboard_artist.latency_ms`
- `storyboard_artist.continuity_notes`
