"""
MCP Story Architect Service

A comprehensive service that transforms Series Creator concept briefs
into structured three-part story arcs for short-form video content.

Features:
- Concept brief to story arc transformation
- Character roster validation
- Continuity flagging and validation
- Deterministic seed management
- Comprehensive observability
"""

from .config import get_config, StoryArchitectConfig
from .main import StoryArchitectMCPServer, main

__version__ = "1.0.0"
__author__ = "Movie Generation Platform Team"
__description__ = "Story Architect MCP Service - Transform concept briefs into structured story arcs"

__all__ = [
    "get_config",
    "StoryArchitectConfig",
    "StoryArchitectMCPServer", 
    "main"
]