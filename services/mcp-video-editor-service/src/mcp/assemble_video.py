"""
MCP tool: assemble_video
"""
import asyncio
import logging
import hashlib
import base64
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

import httpx
from pydantic import ValidationError

from ..config import get_config
from ..models import (
    AssembleVideoRequest, AssembleVideoResponse, FinalEdit,
    TimelineEvent, AssemblySettings
)
from ..services.payload_service import PayloadService, PayloadError
from ..services.ffmpeg_service import FFmpegService, FFmpegError

logger = logging.getLogger(__name__)

class AssembleVideoTool:
    """MCP Tool for assembling video segments into a final MP4"""

    def __init__(self):
        self.config = get_config()
        self.payload = PayloadService()
        self.ffmpeg = FFmpegService()

    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": "assemble_video",
            "description": "Assemble up to three video segments into a single MP4 with basic transitions",
            "input_schema": {
                "type": "object",
                "properties": {
                    "video_segments": {"type": "array"},
                    "storyboard_frames": {"type": "array"},
                    "assembly_settings": {"type": "object"},
                    "project_context": {"type": "object"}
                },
                "required": ["video_segments"]
            }
        }

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        request_id = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
        temp_root = Path(self.config.temp_dir) / request_id
        temp_root.mkdir(parents=True, exist_ok=True)

        try:
            # 1) Validate input
            req = AssembleVideoRequest(**input_data)
            settings = req.assembly_settings or AssemblySettings()

            # 2) Prepare timeline (sequential based on provided durations)
            timeline: List[TimelineEvent] = []
            cursor = 0.0
            for seg in req.video_segments:
                start = cursor
                end = start + seg.duration_seconds
                transition_out = settings.transition
                timeline.append(TimelineEvent(
                    segment_id=seg.segment_id,
                    start_time=round(start, 3),
                    end_time=round(end, 3),
                    transition_out=transition_out
                ))
                cursor = end

            # 3) Download segments
            downloaded_paths = await self._download_segments(req.video_segments, temp_root)

            # 4) Assemble with FFmpeg
            output_filename = self._deterministic_output_name(req)
            output_path = temp_root / output_filename

            duration = await self.ffmpeg.assemble_videos(
                input_paths=downloaded_paths,
                output_path=output_path,
                settings=settings,
                timeline=timeline
            )

            # 5) Compute checksum
            checksum = self._sha256_file(output_path)

            # 6) Upload to PayloadCMS media
            project_id = req.project_context.project_id if req.project_context else "unknown"
            episode_id = req.project_context.episode_id if req.project_context else None

            media = await self.payload.upload_media_file(
                file_path=output_path,
                filename=output_filename,
                project_id=project_id,
                episode_id=episode_id
            )
            video_url = media.get("url") or media.get("data", {}).get("url")

            # 7) Persist assembly record
            assembly_data = {
                "project_id": project_id,
                "episode_id": episode_id,
                "assembly_status": "completed",
                "segment_ids": [s.segment_id for s in req.video_segments],
                "timeline": [e.dict() for e in timeline],
                "transitions": settings.dict(),
                "duration_seconds": duration,
                "checksum": checksum,
                "media_url": video_url,
            }
            await self.payload.create_video_assembly(assembly_data)

            # 8) Return response
            final = FinalEdit(
                video_url=video_url,
                duration_seconds=duration,
                edit_timeline=timeline,
                checksum=f"sha256:{checksum}"
            )
            resp = AssembleVideoResponse(final_edit=final)
            return resp.dict(exclude_none=True)

        except ValidationError as e:
            return {"error": {"type": "ValidationError", "message": str(e)}}
        except (FFmpegError, PayloadError, httpx.HTTPError) as e:
            return {"error": {"type": type(e).__name__, "message": str(e)}}
        except Exception as e:
            logger.exception("Unexpected error in assemble_video")
            return {"error": {"type": type(e).__name__, "message": str(e)}}
        finally:
            # Best effort cleanup
            try:
                for p in temp_root.glob("**/*"):
                    p.unlink(missing_ok=True)
                temp_root.rmdir()
            except Exception:
                pass

    async def _download_segments(self, segments, temp_root: Path) -> List[Path]:
        paths: List[Path] = []
        async with httpx.AsyncClient(timeout=60) as client:
            for seg in segments:
                filename = f"{seg.segment_id}.mp4"
                path = temp_root / filename
                r = await client.get(str(seg.video_url))
                r.raise_for_status()
                path.write_bytes(r.content)
                paths.append(path)
        return paths

    def _sha256_file(self, path: Path) -> str:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()

    def _deterministic_output_name(self, req: AssembleVideoRequest) -> str:
        pc = req.project_context
        if pc:
            scene_parts = [str(s.scene_number) for s in req.video_segments if s.scene_number is not None]
            scenes = "_" + "-".join(scene_parts) if scene_parts else ""
            return f"{pc.project_id}_{pc.episode_id or 'ep'}{scenes}_draft.mp4"
        return "final_draft.mp4"


assemble_video_tool = AssembleVideoTool()
