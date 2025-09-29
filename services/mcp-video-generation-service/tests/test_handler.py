import sys, pathlib, asyncio
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from mcp_server import _handle_synthesize


def test_handle_synthesize_happy_path():
    args = {
        "generated_frames": [
            {
                "frame_id": "SCENE_1_SHOT_1",
                "image_url": "https://example.com/a.png",
                "scene_number": 1,
                "shot_order": 1,
            },
            {
                "frame_id": "SCENE_1_SHOT_2",
                "image_url": "https://example.com/b.png",
                "scene_number": 1,
                "shot_order": 2,
            },
        ],
        "storyboard_frames": [
            {
                "frame_id": "SCENE_1_SHOT_1",
                "description": "noir alley",
                "camera_notes": "push-in",
                "prompt_seed": "rain"
            }
        ],
        "video_settings": {"duration_per_segment": 3.0, "motion_strength": 0.6},
    }

    result = asyncio.run(_handle_synthesize(args))
    assert "video_segments" in result
    assert len(result["video_segments"]) >= 1
    seg = result["video_segments"][0]
    assert seg["segment_id"].startswith("SEGMENT_")
    assert seg["video_url"].startswith("http")

