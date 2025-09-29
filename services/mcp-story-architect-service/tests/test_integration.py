"""
Integration Tests for Story Architect Service

Comprehensive integration tests covering the full story arc generation workflow
with mocked external dependencies.
"""

import pytest
import asyncio
import json
from unittest.mock import AsyncMock, Mock, patch
from typing import Dict, Any

from src.mcp.draft_story_arc import DraftStoryArcTool, StoryArcGenerationError, LLMError
from src.models.story_models import (
    ConceptBrief,
    CreativeGuidelines,
    StoryArc,
    ContinuityFlag,
    ContinuityFlagCode,
    ContinuitySeverity
)
from src.services.payload_service import PayloadCMSError


# Test fixtures
@pytest.fixture
def sample_concept_brief():
    """Sample concept brief for testing"""
    return {
        "title": "The Digital Detox",
        "logline": "A social media influencer must survive 30 days without technology in a remote cabin.",
        "core_conflict": "Modern dependency vs. authentic living",
        "tone_keywords": ["comedic", "heartwarming", "relatable"],
        "genre_tags": ["comedy", "drama"],
        "audience_promise": "Laughs and life lessons about digital addiction",
        "success_criteria": ["Viral potential", "Educational value"]
    }


@pytest.fixture
def sample_creative_guidelines():
    """Sample creative guidelines for testing"""
    return {
        "must_include": ["Technology withdrawal symptoms", "Rural setting"],
        "must_avoid": ["Excessive profanity", "Violence"],
        "target_runtime_seconds": 60,
        "trace_headers": {
            "x-trace-id": "test-trace-123",
            "x-request-id": "test-request-456", 
            "x-correlation-id": "test-correlation-789"
        }
    }


@pytest.fixture
def sample_llm_response():
    """Sample LLM response for story arc generation"""
    return {
        "beginning": "Maya, a top influencer with 2M followers, reluctantly arrives at a remote cabin for her 'Digital Detox Challenge' series. She immediately panics when she realizes there's no cell signal, Wi-Fi, or even electricity. Her withdrawal symptoms begin almost instantly - phantom vibrations from her phone, compulsive hand gestures as if scrolling, and talking to her ring light like it's a person.",
        
        "middle": "Day 15: Maya has learned to chop wood, failed spectacularly at fishing, and discovered she actually enjoys reading physical books. When a friendly neighbor invites her to a community barn dance, she initially refuses but eventually joins in. For the first time in years, she experiences genuine human connection without documenting it. However, she struggles with the urge to share these moments.",
        
        "end": "Day 30: Maya chooses to stay an extra week, having found peace and authentic relationships. When she finally returns online, she creates content about genuine connection rather than manufactured moments. Her follower count initially drops, but her engagement and personal satisfaction soar. She keeps the cabin as a monthly retreat.",
        
        "summary": "A digital detox journey transforms a social media influencer from seeking validation online to finding authentic connections in the real world.",
        
        "continuity_flags": [
            {
                "code": "CHARACTER_ARC_INCOMPLETE",
                "message": "Maya's transformation could be more gradual",
                "section": "middle",
                "severity": "WARNING"
            }
        ]
    }


@pytest.fixture
def mock_payload_service():
    """Mock PayloadCMS service"""
    mock_service = AsyncMock()
    
    # Mock prompt template response
    mock_template = Mock()
    mock_template.id = "test-prompt-template-123"
    mock_template.template_text = """
    Create a three-part story arc based on this concept:
    
    Title: {{ concept_brief.title }}
    Logline: {{ concept_brief.logline }}
    Core Conflict: {{ concept_brief.core_conflict }}
    Genre: {{ concept_brief.genre_tags | join(', ') }}
    Tone: {{ concept_brief.tone_keywords | join(', ') }}
    
    {% if character_roster %}
    Available Characters:
    {% for character in character_roster %}
    - {{ character.name }}: {{ character.description or character.role or 'Available character' }}
    {% endfor %}
    {% endif %}
    
    Target Runtime: {{ target_runtime }} seconds
    Word Limits: Soft {{ word_limit_soft }}, Hard {{ word_limit_hard }}
    
    {{ deterministic_seed }}
    
    Return a JSON object with "beginning", "middle", "end", "summary", and optional "continuity_flags" fields.
    """
    mock_service.get_prompt_template.return_value = mock_template
    
    # Mock character roster (empty for basic tests)
    mock_service.get_character_roster.return_value = []
    
    # Mock seed generation
    mock_seed = Mock()
    mock_seed.seed_value = "test-seed-12345"
    mock_service.get_or_create_seed.return_value = mock_seed
    
    # Mock story arc storage
    mock_service.create_story_arc_record.return_value = Mock(id="test-record-123")
    mock_service.create_continuity_flags.return_value = None
    
    return mock_service


@pytest.fixture
def mock_character_validation_service():
    """Mock character validation service"""
    mock_service = AsyncMock()
    
    # Return empty validation results by default
    mock_service.validate_story_arc.return_value = ([], [], [])
    mock_service.validate_character_consistency.return_value = []
    
    return mock_service


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response"""
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = json.dumps({
        "beginning": "Maya, a top influencer with 2M followers, reluctantly arrives at a remote cabin for her 'Digital Detox Challenge' series. She immediately panics when she realizes there's no cell signal, Wi-Fi, or even electricity. Her withdrawal symptoms begin almost instantly - phantom vibrations from her phone, compulsive hand gestures as if scrolling, and talking to her ring light like it's a person.",
        "middle": "Day 15: Maya has learned to chop wood, failed spectacularly at fishing, and discovered she actually enjoys reading physical books. When a friendly neighbor invites her to a community barn dance, she initially refuses but eventually joins in. For the first time in years, she experiences genuine human connection without documenting it. However, she struggles with the urge to share these moments.",
        "end": "Day 30: Maya chooses to stay an extra week, having found peace and authentic relationships. When she finally returns online, she creates content about genuine connection rather than manufactured moments. Her follower count initially drops, but her engagement and personal satisfaction soar. She keeps the cabin as a monthly retreat.",
        "summary": "A digital detox journey transforms a social media influencer from seeking validation online to finding authentic connections in the real world."
    })
    mock_response.usage.total_tokens = 450
    return mock_response


class TestDraftStoryArcIntegration:
    """Integration tests for draft story arc functionality"""
    
    @pytest.mark.asyncio
    async def test_successful_story_arc_generation(
        self, 
        sample_concept_brief, 
        sample_creative_guidelines,
        mock_payload_service,
        mock_character_validation_service,
        mock_openai_response
    ):
        """Test successful end-to-end story arc generation"""
        
        # Setup tool with mocked services
        tool = DraftStoryArcTool()
        tool.payload_service = mock_payload_service
        tool.character_validation_service = mock_character_validation_service
        
        # Mock OpenAI client
        with patch.object(tool, 'openai_client') as mock_client:
            mock_client.chat.completions.create.return_value = mock_openai_response
            
            # Execute story arc generation
            input_data = {
                "concept_brief": sample_concept_brief,
                "creative_guidelines": sample_creative_guidelines,
                "project_id": "test-project-123"
            }
            
            result = await tool.execute(input_data)
            
            # Verify successful response structure
            assert "story_arc" in result
            assert "request_id" in result
            assert "generated_at" in result
            assert "model_used" in result
            assert "processing_time_ms" in result
            
            # Verify story arc content
            story_arc = result["story_arc"]
            assert story_arc["beginning"]
            assert story_arc["middle"] 
            assert story_arc["end"]
            assert story_arc["summary"]
            
            # Verify service calls
            mock_payload_service.get_prompt_template.assert_called_once()
            mock_payload_service.get_character_roster.assert_called_once_with("test-project-123")
            mock_payload_service.create_story_arc_record.assert_called_once()
            mock_client.chat.completions.create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_story_arc_generation_without_project_id(
        self,
        sample_concept_brief,
        mock_payload_service, 
        mock_character_validation_service,
        mock_openai_response
    ):
        """Test story arc generation without project ID"""
        
        tool = DraftStoryArcTool()
        tool.payload_service = mock_payload_service
        tool.character_validation_service = mock_character_validation_service
        
        with patch.object(tool, 'openai_client') as mock_client:
            mock_client.chat.completions.create.return_value = mock_openai_response
            
            input_data = {
                "concept_brief": sample_concept_brief
            }
            
            result = await tool.execute(input_data)
            
            # Should still succeed
            assert "story_arc" in result
            assert result["story_arc"]["beginning"]
            
            # Character roster shouldn't be called without project_id
            mock_payload_service.get_character_roster.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_input_validation_error(
        self,
        mock_payload_service,
        mock_character_validation_service
    ):
        """Test input validation error handling"""
        
        tool = DraftStoryArcTool()
        tool.payload_service = mock_payload_service
        tool.character_validation_service = mock_character_validation_service
        
        # Invalid input - missing required fields
        input_data = {
            "concept_brief": {
                "title": "Incomplete Brief"
                # Missing required fields: logline, core_conflict, tone_keywords, genre_tags
            }
        }
        
        result = await tool.execute(input_data)
        
        # Should return error response
        assert "error" in result
        assert result["error"]["type"] == "StoryArcGenerationError"
        assert "Input validation failed" in result["error"]["message"]
        assert "request_id" in result["error"]
    
    @pytest.mark.asyncio
    async def test_payload_service_error_handling(
        self,
        sample_concept_brief,
        mock_character_validation_service,
        mock_openai_response
    ):
        """Test PayloadCMS service error handling"""
        
        tool = DraftStoryArcTool()
        tool.character_validation_service = mock_character_validation_service
        
        # Mock payload service to raise error
        mock_payload_service = AsyncMock()
        mock_payload_service.get_prompt_template.side_effect = PayloadCMSError("Connection failed")
        tool.payload_service = mock_payload_service
        
        input_data = {
            "concept_brief": sample_concept_brief
        }
        
        result = await tool.execute(input_data)
        
        # Should return error response
        assert "error" in result
        assert result["error"]["type"] == "StoryArcGenerationError"
        assert "No suitable prompt template found" in result["error"]["message"]
    
    @pytest.mark.asyncio
    async def test_llm_timeout_error(
        self,
        sample_concept_brief,
        mock_payload_service,
        mock_character_validation_service
    ):
        """Test LLM timeout error handling"""
        
        tool = DraftStoryArcTool()
        tool.payload_service = mock_payload_service
        tool.character_validation_service = mock_character_validation_service
        
        # Mock OpenAI client to raise timeout
        with patch.object(tool, 'openai_client') as mock_client:
            from openai import APITimeoutError
            mock_client.chat.completions.create.side_effect = APITimeoutError("Request timed out")
            
            input_data = {
                "concept_brief": sample_concept_brief
            }
            
            result = await tool.execute(input_data)
            
            # Should return error response
            assert "error" in result
            assert result["error"]["type"] == "LLMTimeoutError"
            assert "timeout" in result["error"]["message"].lower()
    
    @pytest.mark.asyncio
    async def test_invalid_llm_response(
        self,
        sample_concept_brief,
        mock_payload_service,
        mock_character_validation_service
    ):
        """Test invalid LLM response handling"""
        
        tool = DraftStoryArcTool()
        tool.payload_service = mock_payload_service
        tool.character_validation_service = mock_character_validation_service
        
        # Mock OpenAI client to return invalid JSON
        with patch.object(tool, 'openai_client') as mock_client:
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "Invalid JSON response"
            mock_response.usage.total_tokens = 100
            mock_client.chat.completions.create.return_value = mock_response
            
            input_data = {
                "concept_brief": sample_concept_brief
            }
            
            result = await tool.execute(input_data)
            
            # Should return error response
            assert "error" in result
            assert result["error"]["type"] == "LLMValidationError"
            assert "Invalid JSON response" in result["error"]["message"]
    
    @pytest.mark.asyncio
    async def test_word_limit_validation(
        self,
        sample_concept_brief,
        mock_payload_service,
        mock_character_validation_service
    ):
        """Test word limit validation and flagging"""
        
        tool = DraftStoryArcTool()
        tool.payload_service = mock_payload_service
        tool.character_validation_service = mock_character_validation_service
        
        # Mock OpenAI response with very long content
        long_content = " ".join(["word"] * 200)  # 200 words per section
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "beginning": long_content,
            "middle": long_content,
            "end": long_content,
            "summary": "Test summary"
        })
        mock_response.usage.total_tokens = 800
        
        with patch.object(tool, 'openai_client') as mock_client:
            mock_client.chat.completions.create.return_value = mock_response
            
            input_data = {
                "concept_brief": sample_concept_brief
            }
            
            result = await tool.execute(input_data)
            
            # Should succeed but include word limit flags
            assert "story_arc" in result
            
            # Verify continuity flags were stored
            mock_payload_service.create_continuity_flags.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_trace_context_propagation(
        self,
        sample_concept_brief,
        sample_creative_guidelines,
        mock_payload_service,
        mock_character_validation_service,
        mock_openai_response
    ):
        """Test trace context propagation through the system"""
        
        tool = DraftStoryArcTool()
        tool.payload_service = mock_payload_service
        tool.character_validation_service = mock_character_validation_service
        
        with patch.object(tool, 'openai_client') as mock_client:
            mock_client.chat.completions.create.return_value = mock_openai_response
            
            input_data = {
                "concept_brief": sample_concept_brief,
                "creative_guidelines": sample_creative_guidelines
            }
            
            result = await tool.execute(input_data)
            
            # Verify trace headers were included in LLM call
            call_args = mock_client.chat.completions.create.call_args
            assert "extra_headers" in call_args.kwargs
            
            extra_headers = call_args.kwargs["extra_headers"]
            assert "x-trace-id" in extra_headers
            assert extra_headers["x-trace-id"] == "test-trace-123"
    
    @pytest.mark.asyncio
    async def test_character_validation_integration(
        self,
        sample_concept_brief,
        mock_payload_service,
        mock_openai_response
    ):
        """Test character validation service integration"""
        
        tool = DraftStoryArcTool()
        tool.payload_service = mock_payload_service
        
        # Mock character validation service with flags
        mock_char_service = AsyncMock()
        char_flags = [
            ContinuityFlag(
                code=ContinuityFlagCode.CHARACTER_UNKNOWN,
                message="Unknown character 'Bob' referenced",
                section="beginning",
                severity=ContinuitySeverity.WARNING
            )
        ]
        mock_char_service.validate_story_arc.return_value = (char_flags, ["Maya"], ["Bob"])
        mock_char_service.validate_character_consistency.return_value = []
        tool.character_validation_service = mock_char_service
        
        # Mock character roster
        mock_payload_service.get_character_roster.return_value = [
            Mock(name="Maya", description="Social media influencer")
        ]
        
        with patch.object(tool, 'openai_client') as mock_client:
            mock_client.chat.completions.create.return_value = mock_openai_response
            
            input_data = {
                "concept_brief": sample_concept_brief,
                "project_id": "test-project-123"
            }
            
            result = await tool.execute(input_data)
            
            # Should succeed and include character validation flags
            assert "story_arc" in result
            
            # Verify character validation was called
            mock_char_service.validate_story_arc.assert_called_once()
            mock_char_service.validate_character_consistency.assert_called_once()
            
            # Verify continuity flags were stored
            mock_payload_service.create_continuity_flags.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_schema_retrieval(self):
        """Test MCP schema retrieval"""
        tool = DraftStoryArcTool()
        schema = tool.get_schema()
        
        # Verify schema structure
        assert schema["name"] == "draft_story_arc"
        assert "description" in schema
        assert "input_schema" in schema
        
        # Verify input schema has required fields
        input_schema = schema["input_schema"]
        assert input_schema["type"] == "object"
        assert "concept_brief" in input_schema["properties"]
        assert "concept_brief" in input_schema["required"]
        
        # Verify concept brief schema
        concept_brief_schema = input_schema["properties"]["concept_brief"]
        required_fields = ["title", "logline", "core_conflict", "tone_keywords", "genre_tags"]
        for field in required_fields:
            assert field in concept_brief_schema["properties"]
            assert field in concept_brief_schema["required"]