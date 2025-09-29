"""
Integration Tests for Video Editor Service
"""
import pytest
import asyncio
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

from src.models import (
    VideoSegment, AssembleVideoRequest, AssemblySettings, ProjectContext
)
from src.mcp.assemble_video import AssembleVideoTool
from src.services.ffmpeg_service import FFmpegService
from src.services.payload_service import PayloadService


@pytest.fixture
def sample_video_segments():
    """Sample video segments for testing"""
    return [
        VideoSegment(
            segment_id="SEGMENT_1",
            video_url="https://example.com/video1.mp4",
            duration_seconds=3.0,
            scene_number=1,
            shot_order=1
        ),
        VideoSegment(
            segment_id="SEGMENT_2", 
            video_url="https://example.com/video2.mp4",
            duration_seconds=4.0,
            scene_number=1,
            shot_order=2
        )
    ]


@pytest.fixture
def sample_assembly_settings():
    """Sample assembly settings"""
    return AssemblySettings(
        transition="hard_cut",
        fade_out_seconds=1.0,
        output_resolution="1280x720",
        frame_rate=24
    )


@pytest.fixture
def sample_project_context():
    """Sample project context"""
    return ProjectContext(
        project_id="test-project-123",
        episode_id="episode-456"
    )


@pytest.fixture
def mock_payload_service():
    """Mock PayloadCMS service"""
    mock = AsyncMock(spec=PayloadService)
    
    # Mock upload response
    mock.upload_media_file.return_value = {
        "id": "media-123",
        "url": "https://payloadcms.com/media/test-video.mp4"
    }
    
    # Mock assembly creation
    mock.create_video_assembly.return_value = "assembly-456"
    
    return mock


@pytest.fixture
def mock_ffmpeg_service():
    """Mock FFmpeg service"""
    mock = AsyncMock(spec=FFmpegService)
    
    # Mock successful assembly
    mock.assemble_videos.return_value = 7.0  # duration
    
    # Mock video info
    mock.get_video_info.return_value = {
        "format": {"duration": "7.0"},
        "streams": [{"width": 1280, "height": 720, "r_frame_rate": "24/1"}]
    }
    
    return mock


class TestAssembleVideoTool:
    """Integration tests for AssembleVideoTool"""

    @pytest.mark.asyncio
    async def test_successful_video_assembly(
        self,
        sample_video_segments,
        sample_assembly_settings, 
        sample_project_context,
        mock_payload_service,
        mock_ffmpeg_service
    ):
        """Test successful video assembly workflow"""
        
        # Create tool with mocked services
        tool = AssembleVideoTool()
        tool.payload = mock_payload_service
        tool.ffmpeg = mock_ffmpeg_service
        
        # Mock file downloads
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = Mock()
            mock_response.content = b"fake video content"
            mock_response.raise_for_status = Mock()
            
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            # Mock file operations
            with patch("pathlib.Path.write_bytes"), \
                 patch("pathlib.Path.mkdir"), \
                 patch("builtins.open", create=True), \
                 patch("pathlib.Path.glob", return_value=[]), \
                 patch("pathlib.Path.rmdir"):
                
                # Execute assembly
                request_data = {
                    "video_segments": [s.dict() for s in sample_video_segments],
                    "assembly_settings": sample_assembly_settings.dict(),
                    "project_context": sample_project_context.dict()
                }
                
                result = await tool.execute(request_data)
                
                # Verify response structure
                assert "final_edit" in result
                final_edit = result["final_edit"]
                
                assert final_edit["video_url"] == "https://payloadcms.com/media/test-video.mp4"
                assert final_edit["duration_seconds"] == 7.0
                assert len(final_edit["edit_timeline"]) == 2
                assert final_edit["checksum"].startswith("sha256:")
                
                # Verify timeline events
                timeline = final_edit["edit_timeline"]
                assert timeline[0]["segment_id"] == "SEGMENT_1"
                assert timeline[0]["start_time"] == 0.0
                assert timeline[0]["end_time"] == 3.0
                
                assert timeline[1]["segment_id"] == "SEGMENT_2"  
                assert timeline[1]["start_time"] == 3.0
                assert timeline[1]["end_time"] == 7.0
                
                # Verify service calls
                mock_ffmpeg_service.assemble_videos.assert_called_once()
                mock_payload_service.upload_media_file.assert_called_once()
                mock_payload_service.create_video_assembly.assert_called_once()

    @pytest.mark.asyncio
    async def test_single_segment_assembly(
        self,
        sample_assembly_settings,
        sample_project_context,
        mock_payload_service,
        mock_ffmpeg_service
    ):
        """Test assembly with single video segment"""
        
        single_segment = [
            VideoSegment(
                segment_id="ONLY_SEGMENT",
                video_url="https://example.com/solo.mp4",
                duration_seconds=5.0
            )
        ]
        
        tool = AssembleVideoTool()
        tool.payload = mock_payload_service
        tool.ffmpeg = mock_ffmpeg_service
        
        # Mock successful processing
        mock_ffmpeg_service.assemble_videos.return_value = 5.0
        
        with patch("httpx.AsyncClient") as mock_client, \
             patch("pathlib.Path.write_bytes"), \
             patch("pathlib.Path.mkdir"), \
             patch("builtins.open", create=True), \
             patch("pathlib.Path.glob", return_value=[]), \
             patch("pathlib.Path.rmdir"):
            
            mock_response = Mock()
            mock_response.content = b"video content"
            mock_response.raise_for_status = Mock()
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            request_data = {
                "video_segments": [s.dict() for s in single_segment],
                "assembly_settings": sample_assembly_settings.dict(),
                "project_context": sample_project_context.dict()
            }
            
            result = await tool.execute(request_data)
            
            # Should succeed with single segment
            assert "final_edit" in result
            assert result["final_edit"]["duration_seconds"] == 5.0
            assert len(result["final_edit"]["edit_timeline"]) == 1

    @pytest.mark.asyncio
    async def test_crossfade_transition(
        self,
        sample_video_segments,
        sample_project_context,
        mock_payload_service,
        mock_ffmpeg_service
    ):
        """Test crossfade transition assembly"""
        
        crossfade_settings = AssemblySettings(
            transition="crossfade_0p5",
            fade_out_seconds=1.0
        )
        
        tool = AssembleVideoTool()
        tool.payload = mock_payload_service
        tool.ffmpeg = mock_ffmpeg_service
        
        with patch("httpx.AsyncClient") as mock_client, \
             patch("pathlib.Path.write_bytes"), \
             patch("pathlib.Path.mkdir"), \
             patch("builtins.open", create=True), \
             patch("pathlib.Path.glob", return_value=[]), \
             patch("pathlib.Path.rmdir"):
            
            mock_response = Mock()
            mock_response.content = b"video content"
            mock_response.raise_for_status = Mock()
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            request_data = {
                "video_segments": [s.dict() for s in sample_video_segments],
                "assembly_settings": crossfade_settings.dict(),
                "project_context": sample_project_context.dict()
            }
            
            result = await tool.execute(request_data)
            
            # Should succeed with crossfade
            assert "final_edit" in result
            timeline = result["final_edit"]["edit_timeline"]
            assert all(event["transition_out"] == "crossfade_0p5" for event in timeline)

    @pytest.mark.asyncio 
    async def test_input_validation_errors(self):
        """Test input validation error handling"""
        
        tool = AssembleVideoTool()
        
        # Test empty segments
        result = await tool.execute({
            "video_segments": []
        })
        assert "error" in result
        assert result["error"]["type"] == "ValidationError"
        
        # Test too many segments
        many_segments = [
            {"segment_id": f"SEG_{i}", "video_url": "https://example.com/video.mp4", "duration_seconds": 3.0}
            for i in range(5)  # More than max of 3
        ]
        result = await tool.execute({
            "video_segments": many_segments
        })
        assert "error" in result
        assert result["error"]["type"] == "ValidationError"
        
        # Test total duration too long
        long_segments = [
            {"segment_id": "SEG_1", "video_url": "https://example.com/video.mp4", "duration_seconds": 10.0},
            {"segment_id": "SEG_2", "video_url": "https://example.com/video.mp4", "duration_seconds": 8.0}
        ]
        result = await tool.execute({
            "video_segments": long_segments
        })
        assert "error" in result
        assert result["error"]["type"] == "ValidationError"

    @pytest.mark.asyncio
    async def test_download_failure_handling(
        self,
        sample_video_segments,
        mock_payload_service,
        mock_ffmpeg_service
    ):
        """Test handling of segment download failures"""
        
        tool = AssembleVideoTool()
        tool.payload = mock_payload_service
        tool.ffmpeg = mock_ffmpeg_service
        
        # Mock failed download
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get.side_effect = Exception("Download failed")
            
            request_data = {
                "video_segments": [s.dict() for s in sample_video_segments]
            }
            
            result = await tool.execute(request_data)
            
            # Should return error
            assert "error" in result
            assert "Download failed" in result["error"]["message"]

    @pytest.mark.asyncio
    async def test_ffmpeg_failure_handling(
        self,
        sample_video_segments,
        mock_payload_service
    ):
        """Test handling of FFmpeg processing failures"""
        
        tool = AssembleVideoTool()
        tool.payload = mock_payload_service
        
        # Mock FFmpeg failure
        mock_ffmpeg = AsyncMock(spec=FFmpegService)
        mock_ffmpeg.assemble_videos.side_effect = Exception("FFmpeg failed")
        tool.ffmpeg = mock_ffmpeg
        
        with patch("httpx.AsyncClient") as mock_client, \
             patch("pathlib.Path.write_bytes"), \
             patch("pathlib.Path.mkdir"):
            
            mock_response = Mock()
            mock_response.content = b"video content"
            mock_response.raise_for_status = Mock()
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            request_data = {
                "video_segments": [s.dict() for s in sample_video_segments]
            }
            
            result = await tool.execute(request_data)
            
            # Should return error
            assert "error" in result
            assert "FFmpeg failed" in result["error"]["message"]

    @pytest.mark.asyncio
    async def test_deterministic_naming(
        self,
        sample_video_segments,
        sample_project_context,
        mock_payload_service,
        mock_ffmpeg_service
    ):
        """Test deterministic output file naming"""
        
        tool = AssembleVideoTool()
        tool.payload = mock_payload_service
        tool.ffmpeg = mock_ffmpeg_service
        
        # Create request with scene numbers
        segments_with_scenes = [
            VideoSegment(
                segment_id="SEGMENT_1",
                video_url="https://example.com/video1.mp4",
                duration_seconds=3.0,
                scene_number=1
            ),
            VideoSegment(
                segment_id="SEGMENT_2",
                video_url="https://example.com/video2.mp4", 
                duration_seconds=3.0,
                scene_number=2
            )
        ]
        
        with patch("httpx.AsyncClient") as mock_client, \
             patch("pathlib.Path.write_bytes"), \
             patch("pathlib.Path.mkdir"), \
             patch("builtins.open", create=True), \
             patch("pathlib.Path.glob", return_value=[]), \
             patch("pathlib.Path.rmdir"):
            
            mock_response = Mock()
            mock_response.content = b"video content"
            mock_response.raise_for_status = Mock()
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            request_data = {
                "video_segments": [s.dict() for s in segments_with_scenes],
                "project_context": sample_project_context.dict()
            }
            
            result = await tool.execute(request_data)
            
            # Verify upload was called with correct filename
            upload_call_args = mock_payload_service.upload_media_file.call_args
            filename = upload_call_args[1]["filename"]  # keyword arg
            
            # Should include project, episode, and scene numbers
            assert "test-project-123" in filename
            assert "episode-456" in filename
            assert "1-2" in filename  # scene numbers joined
            assert filename.endswith("_draft.mp4")

    def test_schema_retrieval(self):
        """Test MCP tool schema"""
        tool = AssembleVideoTool()
        schema = tool.get_schema()
        
        assert schema["name"] == "assemble_video"
        assert "description" in schema
        assert "input_schema" in schema
        
        input_schema = schema["input_schema"]
        assert "video_segments" in input_schema["properties"]
        assert "video_segments" in input_schema["required"]