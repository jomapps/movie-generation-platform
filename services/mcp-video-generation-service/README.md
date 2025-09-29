# MCP Video Generation Service

## Overview
`mcp-video-generation-service` implements the MCP tool `synthesize_video_segments`, which groups storyboard frames into 2–4s motion segments and drives FAL.ai video synthesis presets. The service returns ordered segment metadata that the Video Editor agent concatenates into the final master clip.

## Core Workflow
- Validate the `generated_frames` and `storyboard_frames` payloads with Pydantic schemas.
- Group frames by incremental scene numbers (default two frames per segment, max total runtime ≤12s).
- Build motion prompts directly from storyboard descriptions, camera notes, and prompt seeds.
- Invoke the configured FAL.ai model (`fal-ai/veo3/fast/image-to-video` by default) and collect provider metadata.
- Stop further processing on the first provider failure and surface the failed segment back to the orchestrator.

## Requirements
- Python 3.11+
- Access to FAL.ai video synthesis APIs
- PayloadCMS instance for persisting rendered assets (upload handled by orchestrator or future extensions)

### Environment variables
| Variable | Purpose |
| --- | --- |
| `FAL_API_KEY` | API token for authenticating against FAL.ai. |
| `FAL_IMAGE_TO_VIDEO` | Model identifier for image-to-video jobs (default `fal-ai/veo3/fast/image-to-video`). |
| `FAL_TEXT_TO_VIDEO` | Alternate preset for text-to-video jobs when orchestration requests it. |
| `FAL_TEXT_TO_IMAGE_MODEL` / `FAL_IMAGE_TO_IMAGE_MODEL` | Prompt references shared with upstream image services (kept for parity). |
| `ELEVENLABS_API_KEY` | Reserved for voiceover workflows; stored alongside other media credentials. |

## Installation
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
pip install mcp  # install Model Context Protocol package if not present
```

## Running the service
```bash
.venv\Scripts\activate
python -m src.mcp_server
```
The binary exposes MCP over stdio; register it with your orchestration layer (e.g., Claude Flow, LangGraph) to enable the `synthesize_video_segments` tool.

## MCP Tool: `synthesize_video_segments`
**Input**
```json
{
  "generated_frames": [
    {
      "frame_id": "SCENE_1_SHOT_1",
      "image_url": "https://payloadcms/media/projects/demo/storyboard/frame1.png",
      "scene_number": 1,
      "shot_order": 1
    },
    {
      "frame_id": "SCENE_1_SHOT_2",
      "image_url": "https://...",
      "scene_number": 1,
      "shot_order": 2
    }
  ],
  "storyboard_frames": [
    {
      "frame_id": "SCENE_1_SHOT_1",
      "description": "Hero bursts through neon doorway",
      "camera_notes": "push-in",
      "prompt_seed": "neon-noir",
      "duration_seconds": 3.0
    }
  ],
  "video_settings": {
    "duration_per_segment": 3.0,
    "motion_strength": 0.6,
    "provider_override": "fal-ai"
  }
}
```

**Output**
```json
{
  "video_segments": [
    {
      "segment_id": "SEGMENT_1",
      "associated_frames": ["SCENE_1_SHOT_1", "SCENE_1_SHOT_2"],
      "video_url": "https://payloadcms/media/projects/demo/segments/segment_1.mp4",
      "duration_seconds": 3.0,
      "provider_metadata": {
        "provider": "fal-ai",
        "model": "fal-ai/veo3/fast/image-to-video",
        "job_id": "job-123",
        "webhook_id": null
      }
    }
  ],
  "failed_segments": []
}
```

When a provider error occurs, the service halts immediately and returns a single entry inside `failed_segments` so the orchestrator can trigger remediation or reruns.

## Operational Notes
- Expect synchronous execution for short jobs; integrate webhook listeners if you enable long-running FAL workflows.
- All video assets, prompts, and audit logs should ultimately live in PayloadCMS collections as described in the service specification.
- No automatic retries or alternative prompt strategies are performed—any failure is surfaced upstream for manual handling.
