# Distribution Agent Implementation

**Last Updated**: 2025-09-29
**Status**: Draft Implementation Plan

## Overview
- Implements the Distribution MCP tool that finalizes delivery of QC-approved MP4 assets to PayloadCMS (backed by Cloudflare R2) and exposes a public download link to downstream consumers.
- Maintains lightweight metadata records (title, runtime, checksum, tags) inside PayloadCMS collections, ensuring a single authoritative store for distribution data.
- Emits JSON audit events for observability while enforcing strict QC validation and checksum integrity.

## System Responsibilities
1. Validate inputs (`final_edit`, `qc_report`, optional `distribution_settings`) and enforce `qc_report.status === "pass"` prior to any side effects.
2. Transfer the MP4 asset into the PayloadCMS media collection, leveraging its deterministic storage path and public URL generation.
3. Persist or update distribution metadata within a dedicated PayloadCMS collection (extend schema as required by MVP).
4. Produce a `distribution_record` response that includes storage location, public URL, expiry, metadata payload, and an `audit_log_id` for traceability.
5. Emit a JSON audit log event capturing publish details and halt processing immediately on failures (no automated retries).

## Data Contracts
### Request Payload
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
      "concept_id": "string",
      "tags": ["string"]
    }
  }
}
```

### Response Payload
```json
{
  "distribution_record": {
    "storage_location": "payloadcms://media/mvp/clip.mp4",
    "public_url": "https://cdn.example/r2/mvp/clip.mp4",
    "expires_at": "2025-10-02T12:00:00Z",
    "metadata": {
      "title": "string",
      "duration_seconds": 9.7,
      "checksum": "sha256:...",
      "tags": ["string"]
    },
    "audit_log_id": "dist_abc123"
  }
}
```

### Internal Data Shapes
- `ValidatedFinalEdit`: `{ video_url, duration_seconds, checksum }`
- `DistributionConfig`: `{ storage_prefix, url_expiry_hours, metadata{} }`
- `PayloadMediaUploadResult`: `{ asset_id, storage_path, public_url, expiry_timestamp }`
- `DistributionMetadataRecord`: `{ id, project_id, title, duration_seconds, checksum, tags[], storage_path, public_url, audit_log_id, published_at }`

## Processing Pipeline
1. **Input Validation**
   - Ensure `video_url`, `duration_seconds`, `checksum`, and QC status are present.
   - Reject requests where `qc_report.status !== "pass"` with a blocking error.
2. **Asset Retrieval**
   - Stream the MP4 from `final_edit.video_url`; verify checksum prior to upload.
3. **Media Collection Upload**
   - Upload via PayloadCMS media collection API with deterministic path: `<project_id>/<storage_prefix>/<audit_log_id>.mp4`.
   - Allow PayloadCMS/Cloudflare R2 to manage timestamps and signed URL creation; prefer public URL where available.
4. **Metadata Persistence**
   - Upsert a record in a PayloadCMS collection (e.g., `distributionRecords`) containing metadata, storage location, and audit ID.
   - Overwrite existing entries when `audit_log_id` already exists (idempotent behavior).
5. **Audit Event Emission**
   - Publish a JSON audit payload (`{ "id": audit_log_id, "status": "published", ... }`) to the logging sink or message bus defined by ops.
6. **Response Assembly**
   - Return `distribution_record` with resolved URLs, expiry timestamp (from PayloadCMS settings), and aggregated metadata.

## PayloadCMS & Cloudflare R2 Integration
- Treat PayloadCMS as the only storage abstraction; never create bespoke buckets or schemas.
- Use existing media collection for binary assets. If additional fields are required (e.g., `project_id`, `audit_log_id`, `checksum`), extend the PayloadCMS collection schema accordingly.
- Rely on PayloadCMS-provided public URLs or signed URLs. If signed URLs are disabled, return the public URL guaranteed by the media collection.
- Base URL resolution (per Domain-configs): `PAYLOADCMS_URL` → `PAYLOAD_PUBLIC_SERVER_URL` → `AUTO_MOVIE_URL` → `http://localhost:3010`. `PAYLOADCMS_API_KEY` is used for authenticated CMS calls.

- For direct R2 access (fallback only), use the same deterministic path scheme and immediately register the asset in PayloadCMS to maintain catalog consistency.

## Metadata Management
- Define a PayloadCMS collection (`distributionRecords`) with required fields: `project_id`, `audit_log_id`, `title`, `duration_seconds`, `checksum`, `tags`, `storage_path`, `public_url`, `expires_at`, `published_at`.
- Persist additional optional metadata from `distribution_settings.metadata` without introducing external databases.
- Enforce upsert semantics keyed by `audit_log_id`; overwriting is acceptable and recommended for re-publishes.

## Audit Logging & Observability
- Emit JSON events to the observability pipeline with fields: `audit_log_id`, `project_id`, `storage_path`, `public_url`, `duration_seconds`, `checksum`, `published_at`, `status`.
- Track metrics:
  - `distribution.publish_success_rate`
  - `distribution.latency_ms`
  - `distribution.asset_size_bytes`
- Log failures with sufficient context; no automatic retries. Surface the error to the orchestrator for manual intervention.

## Error Handling & Safeguards
- Abort immediately if QC validation fails or checksum mismatch occurs.
- On upload failure, stop processing, mark the audit event as `failed`, and notify the orchestrator—do not attempt automatic retries.
- Validate generated URLs (non-empty, HTTPS) before returning the response.
- Ensure access tokens or credentials for PayloadCMS are securely sourced from service configuration (never hardcoded).

## Security & Access Control
- Assume PayloadCMS handles signed URL generation; when signed URLs are unavailable, return the canonical public URL provided by the media collection.
- Restrict distribution to QC-passed assets; maintain audit logs for each publish attempt.
- Store only `public_url` and metadata in logs—avoid embedding credentials or temporary tokens.

## Testing Strategy
- **Unit Tests**: QC enforcement, checksum validation, deterministic path derivation, response schema validation.
- **Integration Tests**: Mock PayloadCMS media upload, metadata upsert, and audit log emission pathways.
- **Operational Tests**: Manual dry-run publish per release to verify URL accessibility and metadata correctness within PayloadCMS UI.

## Future Enhancements
- Introduce optional retry/backoff policies once observability confirms failure patterns.
- Add long-term archival hooks (e.g., cold storage tier) beyond MVP scope.
- Support variant bundles (e.g., captions, trailers) by expanding PayloadCMS schemas and response payloads.
- Integrate automated cleanup workflows for staging assets beyond the seven-day retention policy.
