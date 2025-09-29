"""
PayloadCMS Service for Video Editor
"""
import httpx
import json
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from pathlib import Path

from ..config import get_config

logger = logging.getLogger(__name__)

class PayloadError(Exception):
    """Base exception for PayloadCMS errors"""
    pass

class PayloadService:
    """Service for managing PayloadCMS collections for video editor"""
    
    def __init__(self):
        self.config = get_config()
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.config.payload_timeout_seconds),
            headers={
                "Authorization": f"Bearer {self.config.payload_api_key}" if self.config.payload_api_key else None,
                "Content-Type": "application/json"
            } if self.config.payload_api_key else {}
        )

    async def create_video_segment(self, segment_data: Dict[str, Any]) -> str:
        """Create video segment record"""
        try:
            response = await self.client.post(
                f"{self.config.payload_url}/api/video-segments",
                json=segment_data
            )
            response.raise_for_status()
            return response.json().get("id")
        except Exception as e:
            logger.error(f"Failed to create video segment: {e}")
            raise PayloadError(f"Create video segment failed: {e}")

    async def create_video_assembly(self, assembly_data: Dict[str, Any]) -> str:
        """Create video assembly record"""
        try:
            response = await self.client.post(
                f"{self.config.payload_url}/api/video-assemblies",
                json=assembly_data
            )
            response.raise_for_status()
            return response.json().get("id")
        except Exception as e:
            logger.error(f"Failed to create video assembly: {e}")
            raise PayloadError(f"Create video assembly failed: {e}")

    async def upload_media_file(self, file_path: Path, filename: str, project_id: str, episode_id: Optional[str] = None) -> Dict[str, Any]:
        """Upload media file and create media record"""
        try:
            with open(file_path, "rb") as f:
                files = {"file": (filename, f, "video/mp4")}
                
                # Create folder structure for organization
                folder_name = f"{project_id}"
                if episode_id:
                    folder_name += f"/{episode_id}"
                
                data = {
                    "alt": f"Final edit for {project_id}",
                    "filename": filename
                }
                
                response = await self.client.post(
                    f"{self.config.payload_url}/api/media",
                    files=files,
                    data=data
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Failed to upload media: {e}")
            raise PayloadError(f"Upload media failed: {e}")

    async def update_video_assembly_status(self, assembly_id: str, status: str, **updates) -> None:
        """Update video assembly status and metadata"""
        try:
            update_data = {"assembly_status": status, **updates}
            response = await self.client.patch(
                f"{self.config.payload_url}/api/video-assemblies/{assembly_id}",
                json=update_data
            )
            response.raise_for_status()
        except Exception as e:
            logger.error(f"Failed to update assembly status: {e}")
            raise PayloadError(f"Update assembly failed: {e}")

    async def get_video_segment(self, segment_id: str) -> Optional[Dict[str, Any]]:
        """Get video segment by ID"""
        try:
            response = await self.client.get(
                f"{self.config.payload_url}/api/video-segments/{segment_id}"
            )
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get video segment: {e}")
            raise PayloadError(f"Get video segment failed: {e}")

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()