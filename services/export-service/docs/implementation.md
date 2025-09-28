# export-service

## Service overview and purpose
Centralized export orchestration for the platform. Produces downloadable deliverables: project PDF briefs, ZIP bundles (scripts, media references), and coordinates video export via video/transcoding services.

## Technical requirements and dependencies
- Language: Python 3.11+
- Framework: FastAPI + Celery workers for long exports
- Libraries: WeasyPrint/ReportLab for PDF; Python `zipfile`/`tarfile` for archives
- Integrations: mcp-video-processing-service and mcp-media-transcoding-service for video deliverables
- Storage: Upload exports to PayloadCMS Media with derivative links

## API endpoints and interfaces
- HTTP:
  - POST `/exports/project-pdf` { projectId, options? } → { jobId }
  - POST `/exports/project-zip` { projectId, includeMedia?, options? } → { jobId }
  - POST `/exports/video` { projectId, timeline, preset } → { jobId } (delegates to video/transcode services)
  - GET `/jobs/{jobId}` → status/result (mediaId)
  - GET `/health` → { ok: true }
- MCP tools:
  - `export.project_pdf`
  - `export.project_zip`

## Database schema (if applicable)
- exportJobs: { jobId, type, projectId, params, status, resultMediaId?, createdAt }

## Integration points with PayloadCMS
- Read Projects, Media, and generated script/story artifacts
- Upload finished exports to Media; attach derivative relationships and metadata
- Emit progress events for UI (WebSocket)

## Step-by-step implementation guide
1. Implement job submission routes and Celery tasks
2. Build PDF generator using project data from CMS
3. Build ZIP bundler; fetch assets via signed URLs
4. For video exports, orchestrate calls to video/transcoding services
5. Upload outputs to CMS; return result mediaId

## Testing strategy
- Unit: PDF renderer (template with deterministic sample data)
- Integration: ZIP export with small assets; validate contents and checksums
- Orchestration: stubbed calls to video/transcoding services

## Deployment considerations
- Worker autoscaling; temp disk space for build artifacts
- Size/time limits for exports; chunked downloads from CMS
- No automatic retries; surface best possible error messages

