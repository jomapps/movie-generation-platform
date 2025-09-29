from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, HttpUrl


class GeneratedFrame(BaseModel):
    frame_id: str
    image_url: HttpUrl
    scene_number: int
    shot_order: int


class StoryboardFrame(BaseModel):
    frame_id: str
    description: str
    camera_notes: Optional[str] = None
    prompt_seed: Optional[str] = None
    duration_seconds: Optional[float] = None


class VideoSettings(BaseModel):
    duration_per_segment: float = 3.0
    motion_strength: Optional[float] = 0.6
    provider_override: Optional[str] = None


class ProjectContext(BaseModel):
    project_id: Optional[str] = None
    episode_id: Optional[str] = None


class ProviderMetadata(BaseModel):
    provider: str
    model: Optional[str] = None
    job_id: Optional[str] = None
    webhook_id: Optional[str] = None


class VideoSegment(BaseModel):
    segment_id: str
    associated_frames: List[str]
    video_url: HttpUrl
    duration_seconds: float
    provider_metadata: ProviderMetadata


class FailedSegment(BaseModel):
    segment_id: str
    error: str
    message: Optional[str] = None


class RequestPayload(BaseModel):
    generated_frames: List[GeneratedFrame]
    storyboard_frames: List[StoryboardFrame]
    video_settings: Optional[VideoSettings] = None
    project_context: Optional[ProjectContext] = None


class ResponsePayload(BaseModel):
    video_segments: List[VideoSegment]
    failed_segments: List[FailedSegment] = []

