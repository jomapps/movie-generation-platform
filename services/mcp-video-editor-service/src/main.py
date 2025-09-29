"""
Video Editor MCP Service Main
"""
import asyncio
import logging
from typing import Dict, Any

from mcp.server import McpServer
from mcp.types import Tool, JsonRPCError

from .config import get_config
from .mcp.assemble_video import assemble_video_tool
from .services.payload_service import PayloadService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VideoEditorMCPServer:
    """MCP Server for Video Editor"""
    
    def __init__(self):
        self.config = get_config()
        self.server = McpServer()
        self.payload = PayloadService()
        
    def setup_tools(self):
        """Register MCP tools"""
        
        @self.server.tool()
        async def assemble_video(**kwargs) -> Dict[str, Any]:
            """Assemble video segments into final MP4"""
            try:
                return await assemble_video_tool.execute(kwargs)
            except Exception as e:
                logger.exception("assemble_video failed")
                return {"error": {"type": type(e).__name__, "message": str(e)}}
                
        @self.server.tool()
        async def health_check() -> Dict[str, Any]:
            """Health check for video editor service"""
            try:
                # Basic connectivity test
                return {"status": "healthy", "service": "video-editor"}
            except Exception as e:
                return {"status": "unhealthy", "error": str(e)}

    async def start(self):
        """Start the MCP server"""
        logger.info("Starting Video Editor MCP Service")
        self.setup_tools()
        await self.server.start()

async def main():
    """Main entry point"""
    server = VideoEditorMCPServer()
    await server.start()

if __name__ == "__main__":
    asyncio.run(main())