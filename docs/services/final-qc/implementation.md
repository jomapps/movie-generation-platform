# Final QC Agent Implementation

**Last Updated**: 2025-09-29  
**Status**: Draft Implementation Plan

## Overview
- Implements the Post-Production MCP tool that validates MP4 deliverables prior to distribution, catching catastrophic visual or structural defects and providing remediation guidance.
- Leverages FFmpeg/FFprobe (assumed available in runtime) for deterministic analysis of sub-15-second clips.
- Persists thresholds, reports, preview assets, and alert/ticket artifacts exclusively within PayloadCMS (Auto-Movie instance), ensuring centralized governance.

## System Responsibilities
1. Accept `final_edit` payload plus optional `qc_settings`, validate schema, and prepare runtime configuration (thresholds, sampling strategy).
2. Download clip via provided URL (trusting signed/public URL) and orchestrate FFprobe/FFmpeg analyses for metadata integrity, freeze/black-frame detection, and duration verification.
3. Generate optional preview frames (first, middle, last) when requested; upload resulting PNGs to PayloadCMS media collection and record descriptive metadata.
4. Compile structured `qc_report` including status, issue list, recommended actions, and preview URLs; store full report and issue records in PayloadCMS collections.
5. Emit blocking failures when issues exceed thresholds, instructing orchestrator to halt pipeline, while also creating alert/ticket entries in PayloadCMS.

## Data Contracts
### Request Payload
```json
{
  "final_edit": {
    "video_url": "https://...",
    "duration_seconds": 9.7,
    "checksum": "sha256:..."  // optional, unused for validation but retained for metadata
  },
  "qc_settings": {
    "generate_previews": true,
    "frame_sample_count": 3,
    "threshold_profile_id": "default",
    "notes": "string"
  }
}
```

### Response Payload
```json
{
  "qc_report": {
    "status": "fail",
    "issues": [
      {
        "code": "BLACK_FRAME_DETECTED",
        "severity": "high",
        "description": "Frame 120 has luma variance below threshold",
        "detected_at": 4.2
      }
    ],
    "recommended_actions": [
      "Re-render segment covering frames 100-140 with adjusted exposure"
    ],
    "preview_images": ["https://payloadcms/media/previews/final_123_first.png"],
    "report_url": "https://payloadcms/media/qc-reports/final_123_report.pdf"
  }
}
```

### Internal Collections & Shapes (PayloadCMS)
- `qcThresholdProfiles`: `{ id, name, brightness_min, freeze_variance_min, duration_tolerance_ms, updated_at }`
- `qcReports`: `{ id, project_id, final_edit_id, status, issues[], recommended_actions[], preview_media_ids[], report_media_id, created_at }`
- `qcIssues`: `{ id, report_id, code, severity, description, detected_at, remediation }`
- `qcAlerts`: `{ id, report_id, status, assigned_to, created_at, notes }`
- `media` (existing): stores preview PNGs and PDF reports with descriptive metadata.

## Processing Pipeline
1. **Configuration Resolution**
   - Load threshold profile ID from request or default to `qcThresholdProfiles.default`.
   - If profile missing, create default entry with baseline values (e.g., `brightness_min=0.05`, `freeze_variance_min=0.02`, `duration_tolerance_ms=500`).
2. **Asset Acquisition**
   - Download MP4 via HTTP(S) streaming; store in temp location.
   - Record asset metadata (size, fetch duration) for logging.
3. **Metadata Verification**
   - Invoke FFprobe to extract duration, codec, resolution; compare against `final_edit` expectations and `duration_tolerance_ms`.
4. **Visual Integrity Checks**
   - Sample frames (start/middle/end or `frame_sample_count`) using FFmpeg.
   - Compute luma variance per frame; flag `BLACK_FRAME_DETECTED` when below `brightness_min`.
   - Compare histogram similarity between consecutive samples to detect freezes (`FREEZE_FRAME_DETECTED`).
5. **Preview Generation (Optional)**
   - Capture PNGs at designated timestamps when `generate_previews` true.
   - Upload previews to PayloadCMS media collection with descriptive text (scene, timestamp) and capture returned URLs.
6. **Report Compilation**
   - Aggregate issues with codes, severities, and descriptive context.
   - Derive `status`: `fail` when any high-severity issue exists or when threshold breach occurs; otherwise `pass`.
   - Produce remediation instructions (e.g., “Adjust exposure in segment 2 and re-render”); include request `notes` if provided.
   - Render PDF summary (using template engine) and upload to media collection; store resulting URL in report record.
7. **Persistence & Alerts**
   - Upsert `qcReports` entry with full payload; create child `qcIssues` entries for analytics.
   - If `status == fail`, create `qcAlerts` record to track manual follow-up and mark pipeline blocking.
8. **Response Delivery**
   - Return structured `qc_report` with URLs and recommended actions; include pipeline blocking flag in orchestrator envelope (outside scope of response schema but handled by orchestrator contract).

## Threshold & Settings Management
- Manage QC threshold profiles entirely within PayloadCMS (`qcThresholdProfiles`).
- Allow overrides per request by referencing profile ID or providing inline values to be stored as ad-hoc profile entries.
- Ensure all thresholds are versioned (timestamped) for auditability; maintain deterministic behavior by logging profile ID used.

## Issue Catalog & Recommended Actions
- Maintain canonical issue catalog in configuration module:
  - `BLACK_FRAME_DETECTED` → Remediation: “Check lighting/exposure; re-render with adjusted settings.”
  - `FREEZE_FRAME_DETECTED` → Remediation: “Inspect source timeline for duplicated frames; re-export segment.”
  - `DURATION_MISMATCH` → Remediation: “Confirm edit timeline matches brief; re-export final clip.”
  - Additional codes can be appended as coverage expands.
- Recommended actions should be actionable sentences, optionally referencing internal documentation stored in PayloadCMS (link IDs).

## Alerting & Ticketing
- Store alerts in `qcAlerts` collection with fields: `{ report_id, severity, status, assigned_to, created_at, updated_at, notes }`.
- Future integration with external systems can read from this collection; MVP requires only storage and retrieval.
- Surface alert IDs back to orchestrator for UI display.

## Error Handling & Safeguards
- Abort and return `fail` when FFprobe/FFmpeg commands return non-zero status; log command output for debugging.
- Enforce runtime limit of 15 seconds per clip; if exceeded, raise `RUNTIME_EXCEEDED` issue.
- Validate uploaded previews/report URLs before including in response.
- On storage failures, mark QC as failed due to `REPORT_PERSISTENCE_ERROR` and alert ops.

## Metrics & Observability
- Emit structured logs containing:
  - `final_qc.runtime_ms`
  - `final_qc.issue_count`
  - `final_qc.pass_rate`
  - Threshold profile ID and FFmpeg command runtimes.
- Record metrics per report in PayloadCMS collections for dashboarding.

## Testing Strategy
- **Unit Tests**: Threshold comparisons, issue aggregation, remediation selection.
- **Integration Tests**: FFprobe parsing, FFmpeg frame sampling, media uploads to PayloadCMS.
- **Regression Tests**: Library of known-fail clips to ensure detection of black frames, freezes, duration mismatches.
- **Performance Tests**: Verify runtime stays under 15 seconds for max clip length.

## Future Enhancements
- Add audio waveform checks (silence, clipping) once audio tracks are available.
- Extend issue catalog with jitter, dropped-frame detection, and color space validation.
- Integrate automated ticket dispatch (e.g., email/slack) from `qcAlerts` collection to ops tooling.
- Support configurable retry policies when storage upload transient failures occur.
