"""
FFmpeg Service for Video Assembly
"""
import subprocess
import logging
import json
import shlex
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple

from ..config import get_config
from ..models import AssemblySettings, TimelineEvent

logger = logging.getLogger(__name__)

class FFmpegError(Exception):
    """Base exception for FFmpeg errors"""
    pass

class FFmpegService:
    """Service for FFmpeg video processing operations"""
    
    def __init__(self):
        self.config = get_config()

    async def get_video_info(self, video_path: Path) -> Dict[str, Any]:
        """Get video metadata using ffprobe"""
        try:
            cmd = [
                self.config.ffprobe_path,
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                "-show_streams",
                str(video_path)
            ]
            
            logger.info(f"Running ffprobe: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return json.loads(result.stdout)
        except subprocess.CalledProcessError as e:
            logger.error(f"FFprobe failed: {e.stderr}")
            raise FFmpegError(f"FFprobe failed: {e.stderr}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse ffprobe output: {e}")
            raise FFmpegError(f"Failed to parse ffprobe output: {e}")

    async def assemble_videos(
        self, 
        input_paths: List[Path], 
        output_path: Path, 
        settings: AssemblySettings,
        timeline: List[TimelineEvent]
    ) -> float:
        """Assemble videos with transitions using FFmpeg"""
        try:
            cmd = self._build_ffmpeg_command(input_paths, output_path, settings, timeline)
            
            logger.info(f"Running FFmpeg: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Get duration of output video
            info = await self.get_video_info(output_path)
            duration = float(info["format"]["duration"])
            
            logger.info(f"Video assembly completed. Duration: {duration}s")
            return duration
            
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg failed: {e.stderr}")
            raise FFmpegError(f"FFmpeg assembly failed: {e.stderr}")

    def _build_ffmpeg_command(
        self, 
        input_paths: List[Path], 
        output_path: Path, 
        settings: AssemblySettings,
        timeline: List[TimelineEvent]
    ) -> List[str]:
        """Build FFmpeg command for video assembly"""
        
        cmd = [self.config.ffmpeg_path, "-y"]  # -y to overwrite output
        
        # Add input files
        for path in input_paths:
            cmd.extend(["-i", str(path)])
        
        # Build filter complex based on transition type
        if len(input_paths) == 1:
            # Single video - just apply fade out if requested
            filter_complex = self._build_single_video_filter(settings)
        elif settings.transition == "hard_cut":
            filter_complex = self._build_hard_cut_filter(input_paths, settings, timeline)
        elif settings.transition == "crossfade_0p5":
            filter_complex = self._build_crossfade_filter(input_paths, settings, timeline)
        else:
            raise FFmpegError(f"Unsupported transition: {settings.transition}")
        
        if filter_complex:
            cmd.extend(["-filter_complex", filter_complex])
        
        # Output settings
        cmd.extend([
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "23",
            "-f", "mp4"
        ])
        
        # Add resolution if specified
        if settings.output_resolution:
            cmd.extend(["-s", settings.output_resolution])
        
        # Add framerate if specified  
        if settings.frame_rate:
            cmd.extend(["-r", str(settings.frame_rate)])
        
        cmd.append(str(output_path))
        
        return cmd

    def _build_single_video_filter(self, settings: AssemblySettings) -> Optional[str]:
        """Build filter for single video with optional fade out"""
        if settings.fade_out_seconds and settings.fade_out_seconds > 0:
            return f"[0:v]fade=t=out:st={settings.fade_out_seconds}:d=1[v]"
        return None

    def _build_hard_cut_filter(
        self, 
        input_paths: List[Path], 
        settings: AssemblySettings, 
        timeline: List[TimelineEvent]
    ) -> str:
        """Build filter for hard cut concatenation"""
        
        filters = []
        
        # Concatenate videos
        concat_inputs = "".join(f"[{i}:v]" for i in range(len(input_paths)))
        filters.append(f"{concat_inputs}concat=n={len(input_paths)}:v=1:a=0[concat]")
        
        # Apply fade out if requested
        if settings.fade_out_seconds and settings.fade_out_seconds > 0:
            total_duration = sum(event.end_time - event.start_time for event in timeline)
            fade_start = total_duration - settings.fade_out_seconds
            filters.append(f"[concat]fade=t=out:st={fade_start:.2f}:d={settings.fade_out_seconds}[v]")
        else:
            filters.append("[concat]copy[v]")
        
        return ";".join(filters)

    def _build_crossfade_filter(
        self, 
        input_paths: List[Path], 
        settings: AssemblySettings, 
        timeline: List[TimelineEvent]
    ) -> str:
        """Build filter for crossfade transitions"""
        
        filters = []
        current_output = "[0:v]"
        
        # Apply crossfades between segments
        for i in range(1, len(input_paths)):
            fade_duration = 0.5  # Fixed 0.5s crossfade
            prev_event = timeline[i-1]
            curr_event = timeline[i]
            
            # Calculate offset for crossfade
            offset = prev_event.end_time - fade_duration
            
            xfade_filter = f"{current_output}[{i}:v]xfade=transition=fade:duration={fade_duration}:offset={offset:.2f}"
            
            if i < len(input_paths) - 1:
                xfade_filter += f"[xfade{i}]"
                current_output = f"[xfade{i}]"
            else:
                xfade_filter += "[xfaded]"
                current_output = "[xfaded]"
            
            filters.append(xfade_filter)
        
        # Apply fade out if requested
        if settings.fade_out_seconds and settings.fade_out_seconds > 0:
            total_duration = sum(event.end_time - event.start_time for event in timeline)
            fade_start = total_duration - settings.fade_out_seconds
            filters.append(f"{current_output}fade=t=out:st={fade_start:.2f}:d={settings.fade_out_seconds}[v]")
        else:
            filters.append(f"{current_output}copy[v]")
        
        return ";".join(filters)

    async def validate_video_compatibility(self, video_paths: List[Path]) -> Tuple[bool, List[str]]:
        """Check if videos have compatible formats for concatenation"""
        issues = []
        
        if not video_paths:
            return False, ["No video files provided"]
        
        # Get info for all videos
        video_infos = []
        for path in video_paths:
            try:
                info = await self.get_video_info(path)
                video_infos.append(info)
            except FFmpegError as e:
                issues.append(f"Cannot read {path.name}: {e}")
                continue
        
        if len(video_infos) != len(video_paths):
            return False, issues
        
        # Check compatibility
        first_video = video_infos[0]
        first_stream = first_video["streams"][0]  # Assume first stream is video
        
        reference_width = first_stream.get("width")
        reference_height = first_stream.get("height")
        reference_fps = eval(first_stream.get("r_frame_rate", "0/1"))  # Convert fraction to float
        
        for i, info in enumerate(video_infos[1:], 1):
            stream = info["streams"][0]
            width = stream.get("width")
            height = stream.get("height")
            fps = eval(stream.get("r_frame_rate", "0/1"))
            
            if width != reference_width or height != reference_height:
                issues.append(f"Video {i+1} resolution mismatch: {width}x{height} vs {reference_width}x{reference_height}")
            
            if abs(fps - reference_fps) > 0.1:
                issues.append(f"Video {i+1} framerate mismatch: {fps:.2f} vs {reference_fps:.2f}")
        
        return len(issues) == 0, issues