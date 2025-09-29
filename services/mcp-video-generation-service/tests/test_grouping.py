import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))



from video_generation.grouping import group_frames_into_segments, to_segment_specs
from video_generation.schemas import GeneratedFrame


def _gf(id_: str, scene: int, shot: int) -> GeneratedFrame:
    return GeneratedFrame(
        frame_id=id_, image_url="https://example.com/img.png", scene_number=scene, shot_order=shot
    )


def test_groups_by_scene_and_chunk_size():
    frames = [
        _gf("SCENE_1_SHOT_1", 1, 1),
        _gf("SCENE_1_SHOT_2", 1, 2),
        _gf("SCENE_2_SHOT_1", 2, 1),
        _gf("SCENE_2_SHOT_2", 2, 2),
        _gf("SCENE_3_SHOT_1", 3, 1),
    ]

    chunks = group_frames_into_segments(frames, default_chunk_size=2, duration_per_segment=3.0, max_total_runtime=12.0)
    specs = to_segment_specs(chunks)

    # Max segments by runtime: floor(12/3)=4, MVP cap=3
    assert len(specs) == 3

    # Each segment references up to 2 frames
    assert all(1 <= len(c["frame_ids"]) <= 2 for c in specs)

    # First segment uses first two shots of scene 1
    assert specs[0]["frame_ids"] == ["SCENE_1_SHOT_1", "SCENE_1_SHOT_2"]


def test_handles_single_frame_scene():
    frames = [
        _gf("SCENE_1_SHOT_1", 1, 1),
        _gf("SCENE_2_SHOT_1", 2, 1),
    ]
    chunks = group_frames_into_segments(frames, default_chunk_size=2)
    specs = to_segment_specs(chunks)
    assert specs[0]["frame_ids"] == ["SCENE_1_SHOT_1"]

