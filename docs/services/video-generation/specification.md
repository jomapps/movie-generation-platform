# Video Generation Agent Specification

**Last Updated**: 2025-09-29  
**Status**: Draft  
**Service Type**: Production Utility (image-to-video synthesis)

## Purpose
- Convert generated key frames into short animated segments (7–10s) using configured video synthesis provider.
- Produce smooth motion while preserving composition and style from source images.

## MVP Scope
- Support stitching 1–3 segments per request, each 2–4 seconds, for total runtime <= 12 seconds.
- Use a single provider preset (e.g., FAL.ai video or Runway Gen-3) with minimal parameter customization.
- No advanced editing, camera cuts, or audio muxing.

## Inputs
- `generated_frames` (array): Ordered list from Image Generation agent.
- `storyboard_frames` (array): For motion guidance cues.
- `video_settings` (optional): Frame rate, motion strength overrides.

## Outputs
- `video_segments` (array[object])
  - `segment_id` (string, e.g., `SEGMENT_1`)
  - `associated_frames` (array[string])
  - `video_url` (string) or `video_base64` (string)
  - `duration_seconds` (float)
  - `provider_metadata` (object)

## Core Responsibilities
1. Group storyboard frames into segments respecting scene boundaries.
2. Invoke provider API to synthesize motion clips matched to description prompts.
3. Ensure total runtime matches MVP target; adjust segment lengths accordingly.

## Workflow
1. Chunk frames by scene (default 2 frames per segment).
2. For each chunk, build prompt using storyboard description + motion hints (pan, zoom, action).
3. Call video generation provider, monitor job status until completion.
4. Return ordered `video_segments` payload ready for assembly.

## Interfaces & Contracts
### MCP Tool: `synthesize_video_segments`
- **Request Schema**
  ```json
  {
    "generated_frames": [
      {
        "frame_id": "SCENE_1_SHOT_1",
        "image_url": "https://..."
      }
    ],
    "storyboard_frames": [
      {
        "frame_id": "SCENE_1_SHOT_1",
        "description": "string",
        "camera_notes": "push-in"
      }
    ],
    "video_settings": {
      "provider": "runway_gen3",
      "fps": 24,
      "duration_per_segment": 3.0,
      "motion_strength": 0.6
    }
  }
  ```
- **Response Schema**
  ```json
  {
    "video_segments": [
      {
        "segment_id": "SEGMENT_1",
        "associated_frames": ["SCENE_1_SHOT_1", "SCENE_1_SHOT_2"],
        "video_url": "https://...",
        "duration_seconds": 3.2,
        "provider_metadata": {
          "model": "runway-gen3",
          "job_id": "abc123"
        }
      }
    ],
    "failed_segments": [
      {
        "segment_id": "SEGMENT_2",
        "error": "provider_timeout"
      }
    ]
  }
  ```

## Dependencies
- **Upstream**: Image Generation, Storyboard Artist.
- **Downstream**: Video Editor agent.
- **External**: Video synthesis provider API, temporary storage for rendered clips.

## Non-Functional Requirements
- Average synthesis latency <= 90s per segment (async job handling acceptable).
- Enforce consistent resolution (1280x720) and fps (24) in MVP.
- Ensure deterministic chunking to keep runtime within target.

## Operational Considerations
- Provide feature flag to switch provider between Runway and FAL.
- Use asynchronous polling loop with exponential backoff; surface progress to orchestrator.
- Optionally downscale or transcode outputs to MP4 H.264 baseline profile.

## Risks & Open Questions
- Provider cost/latency variability; need budget alarms.
- Motion artifacts when only two frames available; may require prompt augmentation.
- Handling failed segments quickly to avoid blocking pipeline.

## Testing Strategy
- **Unit**: Frame grouping logic, schema validation.
- **Integration**: Provider API mock tests, polling loop reliability.
- **End-to-End**: Weekly dry run using sample storyboard to ensure compatibility with Video Editor.

## Metrics
- `video_generation.segment_success_rate`
- `video_generation.avg_latency_ms`
- `video_generation.runtime_seconds_total`
