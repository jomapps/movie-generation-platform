# Video Generation Agent Implementation

**Last Updated**: 2025-09-29  
**Status**: Draft Implementation Plan

## Overview
- Implements the Production MCP tool that converts storyboard-driven frames into short motion segments using the configured FAL.ai video synthesis presets.
- Groups frames by incremental scene numbers to maintain pacing alignment with storyboard and episode breakdown outputs.
- Persists provider configurations, prompt templates, job audit trails, and rendered asset metadata in PayloadCMS for centralized governance and versioning.

## System Responsibilities
1. Accept `generated_frames`, `storyboard_frames`, and optional `video_settings`; validate schemas, sort inputs by scene/shot order, and normalize strings.
2. Group frames into segments (default 2 frames per segment) respecting scene boundaries and total runtime (≤12s) while allowing 1–3 segments per request.
3. Construct motion prompts leveraging storyboard descriptions, camera notes, and prompt seeds without altering provided terminology.
4. Invoke FAL.ai synchronous APIs by default while registering webhook callbacks for long-running jobs; track job lifecycle until completion or failure.
5. Store rendered segment metadata, provider responses, and webhook events in PayloadCMS collections; upload final clips to the media collection when provider supplies downloadable URLs.
6. Return ordered `video_segments` payload; halt processing and report failures immediately without retries.

## Data Contracts
### Request Payload
```json
{
  "generated_frames": [
    {
      "frame_id": "SCENE_1_SHOT_1",
      "image_url": "https://...",
      "scene_number": 1,
      "shot_order": 1
    }
  ],
  "storyboard_frames": [
    {
      "frame_id": "SCENE_1_SHOT_1",
      "description": "string",
      "camera_notes": "push-in",
      "prompt_seed": "noir-rain",
      "duration_seconds": 3.0
    }
  ],
  "video_settings": {
    "duration_per_segment": 3.0,
    "motion_strength": 0.6,
    "provider_override": "fal-ai"
  },
  "project_context": {
    "project_id": "uuid",
    "episode_id": "uuid"
  }
}
```

### Response Payload
```json
{
  "video_segments": [
    {
      "segment_id": "SEGMENT_1",
      "associated_frames": ["SCENE_1_SHOT_1", "SCENE_1_SHOT_2"],
      "video_url": "https://payloadcms/media/projects/{project_id}/{episode_id}/segments/segment_1.mp4",
      "duration_seconds": 3.1,
      "provider_metadata": {
        "provider": "fal-ai",
        "model": "fal-ai/veo3/fast/image-to-video",
        "job_id": "job-123",
        "webhook_id": "hook-456"
      }
    }
  ],
  "failed_segments": [
    {
      "segment_id": "SEGMENT_2",
      "error": "provider_error",
      "message": "FAL job returned failure status"
    }
  ]
}
```

### PayloadCMS Collections
- `videoGenPromptTemplates`: `{ id, name, version, template_text, model, updated_at }`
- `videoGenProviderConfigs`: `{ id, provider: "fal-ai", model_presets, webhook_url, credentials_ref }`
- `videoGenJobs`: `{ id, project_id, episode_id, segment_id, job_id, status, webhook_events[], created_at, completed_at }`
- `videoSegments`: `{ id, project_id, episode_id, segment_id, associated_frames[], video_url, duration_seconds, provider_metadata, created_at }`
- `media`: shared PayloadCMS media storage for persisted MP4 outputs.

## Frame Grouping Strategy
- Sort frames by `scene_number` then `shot_order`; use incremental scene breaks to define segment boundaries.
- Default chunk size: two frames per segment, ensuring each segment spans 2–4 seconds; adjust to single frame when only one shot exists for a scene.
- Respect storyboard-provided `duration_seconds`; scale segment duration to maintain total runtime ≤12 seconds.
- Document grouping decisions in `videoGenJobs` for traceability.

## Prompt & Parameter Assembly
- Retrieve latest motion prompt template from `videoGenPromptTemplates`; populate with storyboard description, camera notes, lighting cues, and prompt seeds verbatim.
- Include frame URLs (primary image + optional secondary keyframe) in provider payload as required by FAL presets.
- Use environment-configured credentials (`FAL_TEXT_TO_VIDEO`, `FAL_IMAGE_TO_VIDEO`) referenced via `videoGenProviderConfigs`.
- Enforce provider defaults: resolution 1280x720, fps 24; rely on provider guarantees—no post-processing.

## Job Orchestration
- Submit synchronous FAL job and, if response indicates asynchronous processing, register webhook callback using configured endpoint stored in PayloadCMS.
- Poll job status every 10 seconds with capped duration (90s) while webhook listener remains active; webhook completion supersedes polling.
- Capture all job state transitions in `videoGenJobs.webhook_events` for auditing.
- If provider reports runtime exceeding targets, leave job active and return pending status to orchestrator with `failed_segments` entry referencing `provider_pending` (or rely on webhook to complete asynchronously).

## Failure Handling
- Treat provider errors, rejected prompts, or download failures as terminal; record entry in `failed_segments` and in `videoGenJobs` with status `failed`.
- Do not retry automatically; orchestration layer may re-invoke with adjusted inputs if desired.
- Ensure partial successes are returned so Video Editor can proceed with available segments or trigger remediation.

## Storage & Delivery
- When provider returns downloadable URL, optionally re-upload segment to PayloadCMS media collection for consistent access control.
- Store final asset URL and metadata in `videoSegments`; link to `videoGenJobs` via foreign key for lineage.
- Maintain naming convention `segment_{sceneNumber}_{shotIndex}.mp4` within project/episode directories.

## Observability & Metrics
- Record synthesis latency, segment duration, and success/failure counts within PayloadCMS collections; expose aggregate metrics via analytics pipeline when available.
- Log trace IDs from orchestrator context to tie jobs to upstream story arcs and episodes.

## Testing Strategy
- **Unit Tests**: Frame grouping, prompt assembly, schema validation, handling of failed segments.
- **Integration Tests**: Provider API mocks for job submission, webhook processing, and metadata storage.
- **End-to-End Tests**: Periodic dry runs with sample storyboard to ensure compatibility with Video Editor assembly expectations.

## Future Enhancements
- Support multiple providers by extending `videoGenProviderConfigs` and prompt templates.
- Implement adaptive chunking leveraging storyboard timing metadata to better match emotional beats.
- Add optional post-processing (color stabilization, resolution normalization) once requirements emerge.
- Introduce retry logic with alternate prompt variants when providers allow cost-effective re-generation.
