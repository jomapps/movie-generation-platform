# Video Editor Agent Specification

**Last Updated**: 2025-09-29  
**Status**: Draft  
**Service Type**: Post-Production Utility (assembly)

## Purpose
- Assemble generated video segments into a single MP4 clip, enforcing pacing and transitions defined in the storyboard.
- Perform minimal post-processing (hard cuts, fade in/out) suitable for MVP output.

## MVP Scope
- Support up to three input segments totaling <= 15 seconds.
- Apply basic transitions: hard cut, optional 0.5s crossfade between segments, 1s fade-to-black outro.
- No complex color grading, audio mixing, or titles in MVP.

## Inputs
- `video_segments` (array): Ordered segments from Video Generation agent.
- `storyboard_frames` (array): For reference to ensure correct sequencing.
- `assembly_settings` (optional): Transition style, output resolution override.

## Outputs
- `final_edit` (object)
  - `video_url` (string) or `video_base64` (string)
  - `duration_seconds` (float)
  - `edit_timeline` (array) — metadata for each segment placement
  - `checksum` (string) — integrity verification

## Core Responsibilities
1. Concatenate segments in storyboard order while preserving resolution/fps.
2. Apply simple transitions and ensure final runtime < target.
3. Export MP4 (H.264, AAC silent audio track if provider requires audio channel).

## Workflow
1. Validate inputs (matching fps/resolution, presence of URLs).
2. Download segments to temp storage.
3. Use FFmpeg (or cloud service) to concatenate with specified transitions.
4. Upload final MP4 to storage and return metadata.

## Interfaces & Contracts
### MCP Tool: `assemble_video`
- **Request Schema**
  ```json
  {
    "video_segments": [
      {
        "segment_id": "SEGMENT_1",
        "video_url": "https://...",
        "duration_seconds": 3.1
      }
    ],
    "assembly_settings": {
      "transition": "hard_cut",
      "fade_out_seconds": 1.0,
      "output_resolution": "1280x720",
      "frame_rate": 24
    }
  }
  ```
- **Response Schema**
  ```json
  {
    "final_edit": {
      "video_url": "https://...",
      "duration_seconds": 9.7,
      "edit_timeline": [
        {
          "segment_id": "SEGMENT_1",
          "start_time": 0.0,
          "end_time": 3.1,
          "transition_out": "hard_cut"
        }
      ],
      "checksum": "sha256:..."
    }
  }
  ```

## Dependencies
- **Upstream**: Video Generation agent.
- **Downstream**: Final QC agent.
- **External**: Object storage for assets, FFmpeg runtime.

## Non-Functional Requirements
- Assembly latency < 30s for three segments.
- Ensure deterministic output naming (e.g., `${project_id}_draft.mp4`).
- Validate that silent audio track is present if required by distribution channels.

## Operational Considerations
- Temp storage cleanup after upload to prevent disk bloat.
- Provide optional burn-in of slate frame in future (deferred).
- Log per-segment duration deltas vs. source metadata for auditing.

## Risks & Open Questions
- Mismatched frame rates from provider may require re-encoding (quality trade-off).
- Potential need for audio placeholder even without background music.
- Handling corrupted segment downloads gracefully.

## Testing Strategy
- **Unit**: Timeline assembly, transition mapping, schema validation.
- **Integration**: FFmpeg pipeline tests with sample assets.
- **End-to-End**: Regression clip assembly to ensure compatibility with Distribution agent.

## Metrics
- `video_editor.assembly_latency_ms`
- `video_editor.segment_mismatch_rate`
- `video_editor.output_duration`
