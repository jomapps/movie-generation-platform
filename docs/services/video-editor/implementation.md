# Video Editor Agent Implementation

**Last Updated**: 2025-09-29  
**Status**: Draft Implementation Plan

## Overview
- Implements the Post-Production MCP tool that assembles up to three generated video segments (≤15s total) into a single MP4 master aligned with storyboard pacing.
- Performs lightweight transitions (hard cuts, optional 0.5s crossfades, 1s fade-to-black outro) using local FFmpeg binaries.
- Manages asset lifecycle via PayloadCMS collections for segment metadata, assembly runs, and final deliverables, ensuring consistent naming for downstream Distribution and Final QC agents.

## System Responsibilities
1. Accept `video_segments`, optional `storyboard_frames`, and `assembly_settings`; validate schemas and sequencing against storyboard references when provided.
2. Download segment assets to controlled temp storage, mapping each to deterministic filenames derived from PayloadCMS metadata (project/episode/scene identifiers).
3. Construct FFmpeg concat scripts applying requested transitions, enforcing shared resolution/fps assumptions without re-encoding or frame-rate normalization (per MVP constraints).
4. Execute FFmpeg locally, capturing logs and exit codes; abort on failure without retries and propagate error to orchestrator.
5. Upload assembled MP4 to PayloadCMS media collection, create/update assembly records, and return `final_edit` metadata (URL, duration, edit timeline, checksum).

## Data Contracts
### Request Payload
```json
{
  "video_segments": [
    {
      "segment_id": "SEGMENT_1",
      "video_url": "https://...",
      "duration_seconds": 3.2,
      "scene_number": 1,
      "shot_order": 1
    }
  ],
  "storyboard_frames": [
    {
      "frame_id": "SCENE_1_SHOT_1",
      "duration_seconds": 3.2,
      "transition_out": "hard_cut"
    }
  ],
  "assembly_settings": {
    "transition": "crossfade_0p5",
    "fade_out_seconds": 1.0,
    "output_resolution": "1280x720",
    "frame_rate": 24
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
  "final_edit": {
    "video_url": "https://payloadcms/media/projects/{project_id}/{episode_id}/final.mp4",
    "duration_seconds": 9.8,
    "edit_timeline": [
      {
        "segment_id": "SEGMENT_1",
        "start_time": 0.0,
        "end_time": 3.2,
        "transition_out": "hard_cut"
      }
    ],
    "checksum": "sha256:..."
  }
}
```

### PayloadCMS Collections
- `videoSegments`: `{ id, project_id, episode_id, scene_number, shot_order, source_url, duration_seconds, created_at }`
- `videoAssemblies`: `{ id, project_id, episode_id, assembly_status, segment_ids[], timeline[], transitions, duration_seconds, checksum, media_id, created_at }`
- `media`: existing PayloadCMS collection storing uploaded MP4 masters with descriptive metadata.

## Processing Pipeline
1. **Validation & Ordering**
   - Ensure `video_segments` length ≤3 and total duration ≤15s (soft check based on provided metadata).
   - Confirm segment order matches storyboard when frames supplied; otherwise rely on input sequence.
   - Verify presence of required URLs; fail fast on missing assets.
2. **Asset Preparation**
   - Download each segment to temp directory (`/tmp/{project_id}/{segment_id}.mp4`).
   - Record file paths and bytes for cleanup tracking.
   - Optional: cross-reference `videoSegments` collection to confirm metadata alignment; log discrepancies.
3. **FFmpeg Script Generation**
   - Build filtergraph applying:
     - Hard cuts by default.
     - 0.5s crossfade if `assembly_settings.transition == "crossfade_0p5"`.
     - 1s fade-to-black outro when `fade_out_seconds` provided.
   - Enforce output codec `libx264` and container MP4; omit audio track operations per MVP.
   - Emit `edit_timeline` entries capturing start/end times and transitions.
4. **Execution & Error Handling**
   - Run FFmpeg; capture stderr for diagnostics.
   - On non-zero exit, abort assembly, persist failure entry in `videoAssemblies` with status `failed`, and propagate error without retry.
5. **Upload & Persistence**
   - Upload final MP4 to PayloadCMS media collection under path `projects/{project_id}/episodes/{episode_id}/{timestamp}_final.mp4`.
   - Compute SHA-256 checksum locally and store in `videoAssemblies` alongside timeline metadata and media ID.
   - Remove temp files post-upload.
6. **Response Assembly**
   - Return `final_edit` with media URL, duration from FFprobe output, timeline events, and checksum.

## Naming & Storage Conventions
- File naming: `{project_id}_{episode_id}_{scene_numbers_joined}_draft.mp4` for deterministic references; actual storage path managed by PayloadCMS media collection.
- Maintain metadata linking media entry to `videoAssemblies` record via `media_id` field for Distribution/Final QC lookup.

## Transition Logic
- Hard cut (default): segments concatenated back-to-back without overlap.
- Crossfade 0.5s: overlay next segment 0.5s before previous ends, using FFmpeg `xfade=transition=fade:duration=0.5` filter.
- Fade-to-black outro: apply `fade=t=out:st={duration-1}:d=1` when `fade_out_seconds >= 1`.
- Unsupported transitions result in validation error.

## Storyboard Alignment
- When `storyboard_frames` provided, map each segment to corresponding frame ID (matching `segment_id` to `frame_id` by suffix) to validate durations ±0.5s tolerance.
- Record mismatches in `videoAssemblies` with warning flag `STORYBOARD_DRIFT`; still proceed unless difference exceeds 1s.

## Error Reporting
- Propagate FFmpeg errors and upstream FAL.ai failures directly; no retries or resumable assembly in MVP.
- Include `error_message` and `failed_step` fields in `videoAssemblies` record for postmortem.
- If segment download fails, mark status `failed_download` and halt.

## Observability & Metrics
- Capture simple metrics per assembly (duration, number of segments) when storing `videoAssemblies`; no external telemetry pipeline required per clarifications.
- Log FFmpeg command strings (sans URLs) and exit codes for debugging.

## Testing Strategy
- **Unit Tests**: FFmpeg command construction, timeline generation, transition validation, checksum calculation.
- **Integration Tests**: Assemble sample segments verifying crossfade/outro behavior and PayloadCMS upload flow.
- **Regression Tests**: End-to-end assembly followed by Distribution and Final QC consumption to ensure compatibility.

## Future Enhancements
- Support frame-rate normalization/re-encoding when mismatches occur.
- Add optional silent audio track injection based on distribution requirements.
- Implement retry/backoff strategies or resumable workflows for intermittent FFmpeg failures.
- Introduce richer telemetry (latency, duration drift) once observability stack defined.
