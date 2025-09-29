"""
MCP Story Architect Service Main Entry Point

Entry point for the Story Architect service that transforms Series Creator concept briefs
into structured three-part story arcs for short-form video content.
"""

import asyncio
import sys
import signal
import json
from typing import Dict, Any, List
import structlog
from mcp import McpServer
from mcp.types import Tool, JsonRPCError, ErrorCode

from .config import get_config, StoryArchitectConfig
from .mcp.draft_story_arc import draft_story_arc_tool
from .services.payload_service import PayloadCMSService


logger = structlog.get_logger(__name__)


class StoryArchitectMCPServer:
    """MCP Server for Story Architect service"""
    
    def __init__(self):
        self.config = get_config()
        
        # Initialize server
        self.server = McpServer()
        
        # Initialize services
        self.payload_service = PayloadCMSService()
        
        # Track server state
        self._is_running = False
        self._shutdown_event = asyncio.Event()
        
    def setup_handlers(self):
        """Setup MCP tool handlers"""
        
        # Register the draft_story_arc tool
        @self.server.tool()
        async def draft_story_arc(**kwargs) -> Dict[str, Any]:
            """Transform a concept brief into a structured story arc"""
            try:
                return await draft_story_arc_tool.execute(kwargs)
            except Exception as e:
                logger.error("draft_story_arc tool failed", error=str(e), error_type=type(e).__name__)
                raise JsonRPCError(
                    code=ErrorCode.INTERNAL_ERROR,
                    message=f"Story arc generation failed: {str(e)}"
                )
        
        # Register health check tool
        @self.server.tool()
        async def health_check() -> Dict[str, Any]:
            """Check service health status"""
            try:
                health_status = await self._check_health()
                return {"status": "healthy", "details": health_status}
            except Exception as e:
                logger.error("Health check failed", error=str(e))
                return {"status": "unhealthy", "error": str(e)}
        
        # Register configuration info tool
        @self.server.tool()
        async def get_service_info() -> Dict[str, Any]:
            """Get service configuration and capabilities"""
            return {
                "service_name": "Story Architect",
                "version": "1.0.0",
                "description": "Transforms concept briefs into structured story arcs",
                "capabilities": {
                    "llm_providers": list(self.config.llm_providers.keys()),
                    "default_provider": self.config.default_llm_provider,
                    "word_limits": {
                        "soft": self.config.word_limit_soft,
                        "hard": self.config.word_limit_hard
                    },
                    "character_validation": self.config.strict_character_validation,
                    "deterministic_seeds": self.config.deterministic_seed_enabled,
                    "persistence": self.config.persist_story_arcs
                },
                "payload_cms": {
                    "url": self.config.payload_cms_url,
                    "collections": ["storyArchitectPrompts", "storyArchitectSeeds", "storyArcs", "storyContinuityFlags"]
                }
            }
    
    async def _check_health(self) -> Dict[str, Any]:
        """Perform comprehensive health check"""
        health_details = {}
        
        # Check PayloadCMS connectivity
        try:
            await self.payload_service.health_check()
            health_details["payload_cms"] = {"status": "healthy"}
        except Exception as e:
            health_details["payload_cms"] = {"status": "unhealthy", "error": str(e)}
        
        # Check LLM configuration
        try:
            effective_config = self.config.effective_llm_config
            health_details["llm"] = {
                "status": "configured",
                "provider": effective_config["provider"],
                "model": effective_config["model"]
            }
        except Exception as e:
            health_details["llm"] = {"status": "misconfigured", "error": str(e)}
        
        # Check configuration validity
        try:
            # Test configuration access
            _ = self.config.word_limit_soft
            _ = self.config.word_limit_hard
            health_details["configuration"] = {"status": "valid"}
        except Exception as e:
            health_details["configuration"] = {"status": "invalid", "error": str(e)}
        
        return health_details
    
    def get_available_tools(self) -> List[Tool]:
        """Get list of available MCP tools"""
        tools = []
        
        # Add draft_story_arc tool
        tools.append(Tool(
            name="draft_story_arc",
            description="Transform a concept brief into a structured three-part story arc for short-form video content",
            inputSchema=draft_story_arc_tool.get_schema()["input_schema"]
        ))
        
        # Add health check tool
        tools.append(Tool(
            name="health_check", 
            description="Check service health status",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        ))
        
        # Add service info tool
        tools.append(Tool(
            name="get_service_info",
            description="Get service configuration and capabilities",
            inputSchema={
                "type": "object", 
                "properties": {},
                "additionalProperties": False
            }
        ))
        
        return tools
    
    async def start(self):
        """Start the MCP server"""
        try:
            logger.info(
                "Starting Story Architect MCP Service",
                word_limits={"soft": self.config.word_limit_soft, "hard": self.config.word_limit_hard},
                llm_provider=self.config.default_llm_provider,
                payload_url=self.config.payload_cms_url
            )
            
            # Setup signal handlers for graceful shutdown
            if sys.platform != "win32":
                loop = asyncio.get_event_loop()
                for sig in (signal.SIGTERM, signal.SIGINT):
                    loop.add_signal_handler(sig, self._signal_handler)
            
            # Setup tool handlers
            self.setup_handlers()
            
            # Initialize PayloadCMS collections if needed
            if self.config.auto_setup_payload_collections:
                try:
                    await self.payload_service.setup_collections()
                    logger.info("PayloadCMS collections initialized")
                except Exception as e:
                    logger.warning("Failed to setup PayloadCMS collections", error=str(e))
            
            self._is_running = True
            
            # Start server
            await self.server.start()
            
            # Wait for shutdown
            await self._shutdown_event.wait()
            
        except Exception as e:
            logger.error("Failed to start Story Architect service", error=str(e))
            raise
        finally:
            await self.cleanup()
    
    def _signal_handler(self):
        """Handle shutdown signals"""
        logger.info("Received shutdown signal")
        self.shutdown()
    
    def shutdown(self):
        """Initiate graceful shutdown"""
        if self._is_running:
            logger.info("Initiating graceful shutdown")
            self._is_running = False
            self._shutdown_event.set()
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            logger.info("Cleaning up resources")
            
            # Cleanup PayloadCMS service
            if hasattr(self.payload_service, 'cleanup'):
                await self.payload_service.cleanup()
            
            # Cleanup LLM clients
            if hasattr(draft_story_arc_tool, '_openai_client') and draft_story_arc_tool._openai_client:
                await draft_story_arc_tool._openai_client.close()
            
            logger.info("Cleanup completed")
            
        except Exception as e:
            logger.error("Error during cleanup", error=str(e))


async def main():
    """Main entry point"""
    try:
        # Configure structured logging
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
        
        logger.info("Initializing Story Architect MCP Service")
        
        # Create and start server
        server = StoryArchitectMCPServer()
        await server.start()
        
    except KeyboardInterrupt:
        logger.info("Service interrupted by user")
    except Exception as e:
        logger.error("Service failed", error=str(e), exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())