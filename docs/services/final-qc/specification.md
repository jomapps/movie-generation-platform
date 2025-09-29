# Final QC Agent Specification

**Last Updated**: 2025-09-29  
**Status**: Draft  
**Service Type**: Post-Production Utility (quality check)

## Purpose
- Perform lightweight automated verification of the assembled MP4 prior to distribution.
- Catch catastrophic issues (black frames, encoding errors, missing segments) and surface minimal fix suggestions.

## MVP Scope
- Run deterministic checks on a single MP4 clip under 15 seconds.
- Provide pass/fail status plus list of detected issues; no automatic fixes in MVP beyond trivial re-encode request.
- Optional screenshot extraction (first/last frame) for manual review.

## Inputs
- `final_edit` (object): Output from Video Editor agent.
- `qc_settings` (optional): Threshold overrides, screenshot options.

## Outputs
- `qc_report` (object)
  - `status` (enum: pass, fail)
  - `issues` (array[object]) with `code`, `severity`, `description`
  - `recommended_actions` (array[string])
  - `preview_images` (array[string], optional URLs)

## Core Responsibilities
1. Validate video integrity (decode check, duration, resolution consistency).
2. Detect obvious visual issues (all-black frames, frozen frames, dropped segments).
3. Provide concise remediation guidance to operations team.

## Workflow
1. Download MP4 asset from provided URL.
2. Run FFprobe analysis (duration, codec, key metadata).
3. Sample frames at start/middle/end for luma variance and freeze detection.
4. Optionally generate preview PNGs and upload to storage.
5. Compile structured report and return to orchestrator.

## Interfaces & Contracts
### MCP Tool: `run_final_qc`
- **Request Schema**
  ```json
  {
    "final_edit": {
      "video_url": "https://...",
      "duration_seconds": 9.7,
      "checksum": "sha256:..."
    },
    "qc_settings": {
      "generate_previews": true,
      "frame_sample_count": 3,
      "min_brightness_threshold": 0.05
    }
  }
  ```
- **Response Schema**
  ```json
  {
    "qc_report": {
      "status": "pass",
      "issues": [
        {
          "code": "BLACK_FRAME_DETECTED",
          "severity": "high",
          "description": "Frame 120 has luma variance below threshold"
        }
      ],
      "recommended_actions": ["Re-render segment 2"],
      "preview_images": ["https://..."]
    }
  }
  ```

## Dependencies
- **Upstream**: Video Editor agent.
- **Downstream**: Distribution agent.
- **External**: FFmpeg/FFprobe utilities, object storage for preview images.

## Non-Functional Requirements
- QC runtime <= 15s per clip.
- Ensure deterministic brightness thresholds for reproducibility.
- Provide structured logs for all detected issues.

## Operational Considerations
- Maintain lookup table of issue codes/severities for consistent reporting.
- Store QC artifacts (reports, previews) with retention policy (7 days).
- Allow skip flag for manual override when QC fails but release is approved.

## Risks & Open Questions
- Some visual defects (e.g., subtle flicker) may not be captured; manual review still needed.
- Need to ensure checksum verification to detect stale assets.
- Future expansion to audio checks when soundtrack is added.

## Testing Strategy
- **Unit**: Threshold calculations, schema validation.
- **Integration**: FFprobe command execution and parsing.
- **Regression**: Library of known-bad clips to ensure detection accuracy.

## Metrics
- `final_qc.pass_rate`
- `final_qc.runtime_ms`
- `final_qc.issue_count`
