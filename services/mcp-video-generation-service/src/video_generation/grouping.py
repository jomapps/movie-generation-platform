from __future__ import annotations

from typing import List, Dict, Any

from .schemas import GeneratedFrame


def group_frames_into_segments(
    generated_frames: List[GeneratedFrame],
    default_chunk_size: int = 2,
    duration_per_segment: float = 3.0,
    max_total_runtime: float = 12.0,
) -> List[List[GeneratedFrame]]:
    """Group frames into segments by scene, default 2 frames per segment.

    - Sort by (scene_number, shot_order)
    - Break segments on scene change
    - Emit segments of up to default_chunk_size within a scene
    - Cap segments by runtime and by 3 segments in MVP
    """
    if not generated_frames:
        return []

    sorted_frames = sorted(
        generated_frames, key=lambda f: (f.scene_number, f.shot_order)
    )

    chunks: List[List[GeneratedFrame]] = []
    current: List[GeneratedFrame] = []
    current_scene = None

    for fr in sorted_frames:
        if current_scene is None:
            current_scene = fr.scene_number
        if fr.scene_number != current_scene:
            if current:
                chunks.append(current)
                current = []
            current_scene = fr.scene_number
        current.append(fr)
        if len(current) >= max(1, default_chunk_size):
            chunks.append(current)
            current = []

    if current:
        chunks.append(current)

    # Cap segments by runtime and MVP max of 3
    if duration_per_segment <= 0:
        duration_per_segment = 3.0
    max_by_runtime = int(max_total_runtime // duration_per_segment)
    max_segments = max(1, min(3, max_by_runtime))

    # Ensure each segment has at least 1 and at most 2 frames
    capped = [seg[:2] for seg in chunks[:max_segments]]
    return capped


def to_segment_specs(chunks: List[List[GeneratedFrame]]) -> List[Dict[str, Any]]:
    """Convert grouped frames to simple segment specs (id + frame_ids)."""
    specs: List[Dict[str, Any]] = []
    for i, seg in enumerate(chunks, start=1):
        specs.append(
            {
                "segment_id": f"SEGMENT_{i}",
                "frame_ids": [f.frame_id for f in seg],
            }
        )
    return specs

