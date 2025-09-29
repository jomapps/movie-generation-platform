# Image Generation Agent Specification

**Last Updated**: 2025-09-29  
**Status**: Draft  
**Service Type**: Visual MCP Tool (key frame synthesis)

## Purpose
- Produce rendered key frames for each storyboard entry using configured diffusion provider (FAL.ai integration for MVP).
- Deliver consistent aspect ratio, style, and character continuity across frames.

## MVP Scope
- Generate 6–12 images per request based on storyboard frames.
- Use preconfigured model/preset; no fine-tuning or ControlNet flows at v0.
- Return direct image URLs or base64 payloads to orchestrator for downstream use.

## Inputs
- `storyboard_frames` (array): Output from Storyboard Artist.
- `character_profiles` (array): For visual signature references.
- `render_settings` (optional): Override aspect ratio, resolution, provider presets.

## Outputs
- `generated_frames` (array[object])
  - `frame_id` (string) — mirrors storyboard frame ID.
  - `image_url` (string) or `image_base64` (string)
  - `negative_prompts` (array[string], optional)
  - `provider_metadata` (object) — steps, seed, model name.
  - `quality_score` (float, optional future use)

## Core Responsibilities
1. Convert textual frame descriptions into stable prompts per frame.
2. Ensure prompts include character visual signatures and maintain continuity.
3. Handle provider retries and surface failure details when image generation fails.

## Workflow
1. For each frame, assemble positive/negative prompt strings from storyboard + character metadata.
2. Call configured FAL.ai endpoint (or other provider) with shared settings (seed, guidance, etc.).
3. Collect image references; upload to object storage if provider returns base64.
4. Return structured results maintaining input order.

## Interfaces & Contracts
### MCP Tool: `render_storyboard_frames`
- **Request Schema**
  ```json
  {
    "storyboard_frames": [
      {
        "frame_id": "SCENE_1_SHOT_1",
        "description": "string",
        "camera_notes": "string",
        "lighting_mood": "string",
        "prompt_seed": "string"
      }
    ],
    "character_profiles": [
      {
        "name": "string",
        "visual_signature": "string"
      }
    ],
    "render_settings": {
      "provider": "fal_ai",
      "model": "flux-pro",
      "aspect_ratio": "16:9",
      "guidance_scale": 4.5,
      "steps": 24,
      "seed": 123456
    }
  }
  ```
- **Response Schema**
  ```json
  {
    "generated_frames": [
      {
        "frame_id": "SCENE_1_SHOT_1",
        "image_url": "https://...",
        "provider_metadata": {
          "seed": 123456,
          "model": "flux-pro",
          "inference_time_ms": 2300
        }
      }
    ],
    "failed_frames": [
      {
        "frame_id": "SCENE_2_SHOT_1",
        "error": "provider_timeout"
      }
    ]
  }
  ```

## Dependencies
- **Upstream**: Storyboard Artist, Character Creator.
- **Downstream**: Video Generation agent.
- **External**: FAL.ai or equivalent diffusion API, object storage (S3-compatible) for hosting.

## Non-Functional Requirements
- Average render latency <= 15s per batch; sequential fallback allowed.
- Support max resolution 1280x720 for MVP.
- Implement exponential backoff retries (max 2) for provider failures.

## Operational Considerations
- Use standardized prompt template stored in config; allow hot reload without redeploy.
- Mask sensitive tokens (provider API keys) and rotate monthly.
- Provide optional downscaling or compression for preview assets.

## Risks & Open Questions
- Provider drift may change visual style; need prompt library versioning.
- Handling complex camera moves (motion blur) may require ControlNet later.
- Cost management—need to monitor inference credits closely.

## Testing Strategy
- **Unit**: Prompt assembly, schema validation, failure handling.
- **Integration**: Provider API call tests using sandbox credentials.
- **Visual QA**: Weekly sample review to ensure character continuity.

## Metrics
- `image_generation.success_rate`
- `image_generation.avg_latency_ms`
- `image_generation.retry_count`
