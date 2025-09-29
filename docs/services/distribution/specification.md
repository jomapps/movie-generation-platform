# Distribution Agent Specification

**Last Updated**: 2025-09-29  
**Status**: Draft  
**Service Type**: Post-Production Utility (delivery)

## Purpose
- Deliver the final MP4 artifact to downstream consumers (UI download, internal storage) after QC approval.
- Generate minimal metadata required for cataloging first-version outputs.

## MVP Scope
- Support publishing a single MP4 per request to configured storage bucket and returning a signed download URL.
- Maintain lightweight metadata record (title, runtime, checksum) stored in Story MCP or ops database.
- No social distribution, CDN fan-out, or analytics pipelines in MVP.

## Inputs
- `final_edit` (object): Output MP4 metadata and URL from Video Editor.
- `qc_report` (object): Final QC status (must be `pass`).
- `distribution_settings` (optional): Storage target, URL expiry, metadata tags.

## Outputs
- `distribution_record` (object)
  - `storage_location` (string)
  - `public_url` (string)
  - `expires_at` (timestamp)
  - `metadata` (object) — title, runtime, checksum, tags
  - `audit_log_id` (string)

## Core Responsibilities
1. Verify QC pass status before publishing.
2. Upload final MP4 to target storage (S3-compatible or local disk) with deterministic path naming.
3. Generate signed URL and store distribution metadata for retrieval by UI.

## Workflow
1. Validate `qc_report.status == "pass"`.
2. Copy MP4 from staging bucket to distribution bucket (or move within same storage).
3. Record metadata entry (JSON) in Story MCP datastore or ops DB.
4. Return distribution record to orchestrator and emit audit log event.

## Interfaces & Contracts
### MCP Tool: `publish_final_asset`
- **Request Schema**
  ```json
  {
    "final_edit": {
      "video_url": "https://...",
      "duration_seconds": 9.7,
      "checksum": "sha256:..."
    },
    "qc_report": {
      "status": "pass"
    },
    "distribution_settings": {
      "storage_prefix": "mvp/",
      "url_expiry_hours": 72,
      "metadata": {
        "title": "string",
        "concept_id": "string"
      }
    }
  }
  ```
- **Response Schema**
  ```json
  {
    "distribution_record": {
      "storage_location": "s3://bucket/mvp/clip.mp4",
      "public_url": "https://...",
      "expires_at": "2025-10-02T12:00:00Z",
      "metadata": {
        "title": "string",
        "duration_seconds": 9.7,
        "checksum": "sha256:..."
      },
      "audit_log_id": "dist_abc123"
    }
  }
  ```

## Dependencies
- **Upstream**: Video Editor, Final QC.
- **Downstream**: UI download endpoint, archival workflows.
- **External**: Object storage provider, optional metadata DB.

## Non-Functional Requirements
- Publish latency < 10s (dominated by file copy time).
- Ensure signed URL expiry configurable; default 72 hours.
- Enforce checksum validation post-upload.

## Operational Considerations
- Implement idempotency using `audit_log_id` to avoid duplicate uploads.
- Keep staging assets for 7 days before cleanup to allow re-download if needed.
- Provide ops alert when upload fails or QC status is invalid.

## Risks & Open Questions
- Need for long-term archival strategy beyond MVP (cold storage, CDN).
- Handling re-publish after edits—should versioning be introduced early?
- Permissions model for download URLs (public vs. authenticated access).

## Testing Strategy
- **Unit**: QC status enforcement, URL generation, metadata schema.
- **Integration**: Storage provider interactions (mock + staging bucket tests).
- **Operational**: Manual publish dry run per release to confirm access works.

## Metrics
- `distribution.publish_success_rate`
- `distribution.latency_ms`
- `distribution.replica_count`
