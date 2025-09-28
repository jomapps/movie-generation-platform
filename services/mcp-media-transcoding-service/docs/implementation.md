# mcp-media-transcoding-service

## Service overview and purpose
Specialized service for automatic media format conversion and optimization (video/audio/image) to standardize deliverables and enable fast previews/downloads.

## Technical requirements and dependencies
- Language: Python 3.11+
- FastAPI control endpoints + Celery workers
- FFmpeg toolchain
- Storage: PayloadCMS Media
- Broker: Redis

## API endpoints and interfaces
- HTTP:
  - POST `/transcode` { inputMediaId, targets: [{ format, codec, bitrate, resolution }] } → { jobId }
  - GET `/jobs/{jobId}` → status/result
  - GET `/health` → { ok: true }
- Celery tasks: `transcode.run`

## Database schema (if applicable)
Record in CMS or internal table:
- transcodeJobs: { jobId, inputMediaId, targets[], status, outputs: mediaIds[], createdAt }

## Integration points with PayloadCMS
- Read media by ID; download via signed URL
- Upload transcoded outputs; attach derivative links to original
- Emit progress to UI via WebSocket

## Step-by-step implementation guide
1. Define target presets (preview, mobile, archive)
2. Implement Celery task building FFmpeg commands
3. Stream progress; upload outputs to CMS
4. Maintain derivative relationships in metadata

## Testing strategy
- Unit: preset → FFmpeg arg mapping
- Integration: transcode small sample; validate codecs/bitrates

## Deployment considerations
- CPU-intensive; separate worker pool
- Ensure legal codec availability

