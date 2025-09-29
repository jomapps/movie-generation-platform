"""
Configuration for Video Editor MCP Service
"""
from pydantic import BaseSettings, Field, AnyUrl
from typing import Optional

class VideoEditorConfig(BaseSettings):
    # General
    env: str = Field(default="development", env="VIDEO_EDITOR_ENV")
    log_level: str = Field(default="INFO", env="VIDEO_EDITOR_LOG_LEVEL")
    temp_dir: str = Field(default="/tmp/video-editor", env="VIDEO_EDITOR_TEMP_DIR")

    # FFmpeg
    ffmpeg_path: str = Field(default="ffmpeg", env="FFMPEG_PATH")
    ffprobe_path: str = Field(default="ffprobe", env="FFPROBE_PATH")

    # PayloadCMS
    payload_url: AnyUrl = Field(default="http://localhost:3000", env="PAYLOAD_CMS_URL")
    payload_api_key: Optional[str] = Field(default=None, env="PAYLOAD_CMS_API_KEY")
    payload_timeout_seconds: int = Field(default=60, env="PAYLOAD_CMS_TIMEOUT")

    # Limits
    max_segments: int = 3
    max_total_duration_seconds: float = 15.0

    class Config:
        env_file = ".env"
        case_sensitive = False

_config: Optional[VideoEditorConfig] = None

def get_config() -> VideoEditorConfig:
    global _config
    if _config is None:
        _config = VideoEditorConfig()
    return _config
