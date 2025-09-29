"""
Video Editor Models
"""
from pydantic import BaseModel, HttpUrl, Field, validator
from typing import List, Optional, Literal

class VideoSegment(BaseModel):
    segment_id: str
    video_url: HttpUrl
    duration_seconds: float = Field(gt=0, le=15)
    scene_number: Optional[int] = None
    shot_order: Optional[int] = None

class StoryboardFrame(BaseModel):
    frame_id: str
    duration_seconds: float
    transition_out: Optional[Literal["hard_cut", "crossfade_0p5"]] = "hard_cut"

class AssemblySettings(BaseModel):
    transition: Literal["hard_cut", "crossfade_0p5"] = "hard_cut"
    fade_out_seconds: Optional[float] = 1.0
    output_resolution: Optional[str] = "1280x720"
    frame_rate: Optional[int] = 24

class ProjectContext(BaseModel):
    project_id: str
    episode_id: Optional[str] = None

class AssembleVideoRequest(BaseModel):
    video_segments: List[VideoSegment]
    storyboard_frames: Optional[List[StoryboardFrame]] = None
    assembly_settings: Optional[AssemblySettings] = None
    project_context: Optional[ProjectContext] = None

    @validator("video_segments")
    def limit_segments(cls, v: List[VideoSegment]):
        if len(v) == 0:
            raise ValueError("At least one segment required")
        if len(v) > 3:
            raise ValueError("Max 3 segments allowed in MVP")
        total = sum(s.duration_seconds for s in v)
        if total > 15.0:
            raise ValueError("Total duration must be <= 15 seconds for MVP")
        return v

class TimelineEvent(BaseModel):
    segment_id: str
    start_time: float
    end_time: float
    transition_out: Literal["hard_cut", "crossfade_0p5"]

class FinalEdit(BaseModel):
    video_url: Optional[str] = None
    video_base64: Optional[str] = None
    duration_seconds: float
    edit_timeline: List[TimelineEvent]
    checksum: str

class AssembleVideoResponse(BaseModel):
    final_edit: FinalEdit
