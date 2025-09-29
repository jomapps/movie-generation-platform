from __future__ import annotations

import asyncio
import json
from typing import Any, Dict, List

from pydantic import ValidationError

try:
    import mcp
    from mcp import types
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
except Exception:  # pragma: no cover - allow tests without MCP installed
    mcp = None
    types = None
    Server = None
    stdio_server = None

from video_generation.schemas import (
    RequestPayload,
    ResponsePayload,
    VideoSegment,
    FailedSegment,
    ProviderMetadata,
)
from video_generation.grouping import group_frames_into_segments, to_segment_specs
from providers.fal_ai import FalAIVideoClient


SERVICE_NAME = "mcp-video-generation-service"
TOOL_NAME = "synthesize_video_segments"


async def _handle_synthesize(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Core handler for synthesize_video_segments tool."""
    # Validate input
    payload = RequestPayload(**arguments)

    # Group frames into segments
    duration = payload.video_settings.duration_per_segment if payload.video_settings else 3.0
    motion_strength = payload.video_settings.motion_strength if payload.video_settings else None

    chunks = group_frames_into_segments(
        payload.generated_frames,
        default_chunk_size=2,
        duration_per_segment=duration,
        max_total_runtime=12.0,
    )

    segment_specs = to_segment_specs(chunks)

    client = FalAIVideoClient()

    video_segments: List[Dict[str, Any]] = []
    failed_segments: List[Dict[str, Any]] = []

    for spec in segment_specs:
        sid = spec["segment_id"]
        frame_ids = spec["frame_ids"]
        primary = next((f for f in payload.generated_frames if f.frame_id == frame_ids[0]), None)
        secondary = (
            next((f for f in payload.generated_frames if f.frame_id == frame_ids[1]), None)
            if len(frame_ids) > 1
            else None
        )

        # Build prompt from storyboard metadata (verbatim usage per clarifications)
        # Find the storyboard entry for the primary frame
        sb = next((s for s in payload.storyboard_frames if s.frame_id == frame_ids[0]), None)
        desc = (sb.description if sb else "").strip()
        cam = (sb.camera_notes if sb and sb.camera_notes else "").strip()
        seed = (sb.prompt_seed if sb and sb.prompt_seed else "").strip()
        prompt = " ".join(x for x in [desc, cam, seed] if x)

        try:
            synth = await client.synthesize(
                primary_image_url=str(primary.image_url) if primary else "",
                secondary_image_url=str(secondary.image_url) if secondary else None,
                prompt=prompt,
                duration_seconds=duration,
                motion_strength=motion_strength,
            )

            video_segments.append(
                {
                    "segment_id": sid,
                    "associated_frames": frame_ids,
                    "video_url": synth["video_url"],
                    "duration_seconds": duration,
                    "provider_metadata": synth["provider_metadata"],
                }
            )
        except Exception as e:  # noqa: BLE001
            failed_segments.append(
                {
                    "segment_id": sid,
                    "error": "provider_error",
                    "message": str(e),
                }
            )
            break  # Stop further processing on first failure as per clarifications

    return {"video_segments": video_segments, "failed_segments": failed_segments}


# Optional: standalone MCP server runner (not used by unit tests)
async def main() -> None:  # pragma: no cover
    if Server is None:
        raise RuntimeError("MCP package not available in this environment")

    server = Server(SERVICE_NAME)

    @server.list_tools()
    async def handle_list_tools() -> List[types.Tool]:  # type: ignore[name-defined]
        return [
            types.Tool(  # type: ignore[attr-defined]
                name=TOOL_NAME,
                description="Convert storyboard-driven frames to motion video segments (FAL.ai)",
                inputSchema={
                    "type": "object",
                    "properties": {},  # Schema is validated via Pydantic in call
                },
            )
        ]

    @server.call_tool()
    async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:  # type: ignore[name-defined]
        if name != TOOL_NAME:
            return [types.TextContent(type="text", text=json.dumps({"success": False, "error": "unknown_tool"}))]  # type: ignore[attr-defined]
        try:
            result = await _handle_synthesize(arguments)
            return [types.TextContent(type="text", text=json.dumps(result))]  # type: ignore[attr-defined]
        except ValidationError as ve:
            return [types.TextContent(type="text", text=json.dumps({"success": False, "error": "validation_error", "details": json.loads(ve.json())}))]  # type: ignore[attr-defined]
        except Exception as e:  # noqa: BLE001
            return [types.TextContent(type="text", text=json.dumps({"success": False, "error": str(e)}))]  # type: ignore[attr-defined]

    async with stdio_server() as (read_stream, write_stream):  # type: ignore[misc]
        await server.run(read_stream, write_stream)  # type: ignore[misc]


if __name__ == "__main__":  # pragma: no cover
    asyncio.run(main())

