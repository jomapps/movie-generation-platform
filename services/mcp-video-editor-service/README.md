# Video Editor MCP Service

The Video Editor service is a post-production MCP tool that assembles up to three generated video segments (≤15s total) into a single MP4 master aligned with storyboard pacing.

## Features

- **Video Assembly**: Concatenate up to 3 video segments into a single MP4
- **Basic Transitions**: Hard cuts and 0.5s crossfades between segments  
- **Fade Effects**: Optional 1s fade-to-black outro
- **PayloadCMS Integration**: Store assembly metadata and upload final videos
- **Deterministic Naming**: Consistent file naming based on project/episode/scene IDs
- **Error Handling**: Comprehensive error reporting with no retries (fail fast)

## Requirements

- Python 3.8+
- FFmpeg and FFprobe binaries
- PayloadCMS instance
- Disk space for temporary video processing

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your PayloadCMS settings and FFmpeg paths

# Run service
python -m src.main
```

## Configuration

Key environment variables:

- `PAYLOAD_CMS_URL`: PayloadCMS endpoint
- `PAYLOAD_CMS_API_KEY`: API key for PayloadCMS
- `FFMPEG_PATH`: Path to ffmpeg binary (default: "ffmpeg")
- `FFPROBE_PATH`: Path to ffprobe binary (default: "ffprobe")
- `VIDEO_EDITOR_TEMP_DIR`: Temporary directory for processing

## API

### `assemble_video`

Assembles video segments into a final MP4.

**Input:**
```json
{
  "video_segments": [
    {
      "segment_id": "SEGMENT_1",
      "video_url": "https://...",
      "duration_seconds": 3.2
    }
  ],
  "assembly_settings": {
    "transition": "hard_cut",
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

**Output:**
```json
{
  "final_edit": {
    "video_url": "https://...",
    "duration_seconds": 9.8,
    "edit_timeline": [...],
    "checksum": "sha256:..."
  }
}
```

## Limitations

- Maximum 3 video segments per assembly
- Total duration must be ≤15 seconds
- No frame rate normalization (segments must have matching fps/resolution)
- No audio processing
- No retries on FFmpeg failures
- Basic transitions only (hard cut, crossfade)

## Error Handling

The service fails fast on any error:
- Invalid input validation → ValidationError
- Segment download failures → HTTPError  
- FFmpeg processing errors → FFmpegError
- PayloadCMS upload issues → PayloadError

No retries are attempted. Errors are logged and returned to the orchestrator.

## Temporary Storage

The service downloads segments to temporary directories and cleans up after processing. Cleanup is best-effort and may leave files on disk if the process crashes.