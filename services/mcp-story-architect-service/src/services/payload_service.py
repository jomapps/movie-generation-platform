"""
PayloadCMS Integration Service

Handles all PayloadCMS operations for the Story Architect service including
collections for prompts, seeds, arcs, characters, and continuity flags.
"""

import asyncio
from datetime import datetime
from typing import Optional, List, Dict, Any
import httpx
import structlog
from pydantic import ValidationError

from ..config import get_config
from ..models.story_models import (
    StoryArchitectPrompt,
    StoryArchitectSeed,
    Character,
    StoryArcRecord,
    StoryContinuityFlag,
    PromptSelectionCriteria
)


logger = structlog.get_logger(__name__)


class PayloadCMSError(Exception):
    """Base exception for PayloadCMS operations"""
    pass


class PayloadCMSConnectionError(PayloadCMSError):
    """Connection or network error with PayloadCMS"""
    pass


class PayloadCMSValidationError(PayloadCMSError):
    """Validation error from PayloadCMS"""
    pass


class PayloadCMSService:
    """Service for PayloadCMS operations"""
    
    def __init__(self):
        self.config = get_config()
        self.base_url = self.config.payload_api_url.rstrip('/')
        self.timeout = self.config.payload_timeout_seconds
        self.headers = {
            "Authorization": f"Bearer {self.config.payload_api_secret}",
            "Content-Type": "application/json"
        }
    
    async def health_check(self) -> bool:
        """Check PayloadCMS service health"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/health")
                return response.status_code == 200
        except Exception as e:
            logger.warning("PayloadCMS health check failed", error=str(e))
            return False
    
    # Prompt Template Operations
    
    async def get_prompt_template(self, criteria: PromptSelectionCriteria) -> Optional[StoryArchitectPrompt]:
        """Get the best matching prompt template based on criteria"""
        try:
            # Build query parameters for template selection
            params = {
                "where[is_active][equals]": True,
                "sort": "-priority,-created_at",
                "limit": 10
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/storyArchitectPrompts",
                    headers=self.headers,
                    params=params
                )
                response.raise_for_status()
                
                data = response.json()
                docs = data.get("docs", [])
                
                if not docs:
                    logger.warning("No active prompt templates found")
                    return None
                
                # Select best matching template
                selected_template = self._select_best_template(docs, criteria)
                if selected_template:
                    return StoryArchitectPrompt(**selected_template)
                
                return None
                
        except httpx.HTTPError as e:
            logger.error("Failed to fetch prompt templates", error=str(e))
            raise PayloadCMSConnectionError(f"Failed to fetch prompt templates: {e}")
        except ValidationError as e:
            logger.error("Invalid prompt template data", error=str(e))
            raise PayloadCMSValidationError(f"Invalid prompt template: {e}")
    
    def _select_best_template(self, templates: List[Dict], criteria: PromptSelectionCriteria) -> Optional[Dict]:
        """Select the best matching template from available options"""
        
        # First, try to find exact matches
        for template in templates:
            genre_match = (
                not criteria.primary_genre or 
                template.get("genre_tag") == criteria.primary_genre
            )
            tone_match = (
                not criteria.primary_tone or
                template.get("tone_tag") == criteria.primary_tone
            )
            
            if genre_match and tone_match:
                logger.info(
                    "Selected exact matching template",
                    template_id=template.get("id"),
                    genre=template.get("genre_tag"),
                    tone=template.get("tone_tag")
                )
                return template
        
        # Try genre-only matches
        if criteria.primary_genre:
            for template in templates:
                if template.get("genre_tag") == criteria.primary_genre:
                    logger.info(
                        "Selected genre-matching template",
                        template_id=template.get("id"),
                        genre=template.get("genre_tag")
                    )
                    return template
        
        # Try tone-only matches
        if criteria.primary_tone:
            for template in templates:
                if template.get("tone_tag") == criteria.primary_tone:
                    logger.info(
                        "Selected tone-matching template",
                        template_id=template.get("id"),
                        tone=template.get("tone_tag")
                    )
                    return template
        
        # Fall back to default template (no genre/tone specified)
        if criteria.fallback_to_default:
            for template in templates:
                if not template.get("genre_tag") and not template.get("tone_tag"):
                    logger.info(
                        "Selected default template",
                        template_id=template.get("id")
                    )
                    return template
        
        # Fall back to highest priority template
        if templates and criteria.fallback_to_default:
            logger.info(
                "Selected highest priority template as fallback",
                template_id=templates[0].get("id")
            )
            return templates[0]
        
        return None
    
    async def create_prompt_template(self, template: StoryArchitectPrompt) -> StoryArchitectPrompt:
        """Create a new prompt template"""
        try:
            template_dict = template.dict(exclude={"id"})
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/storyArchitectPrompts",
                    headers=self.headers,
                    json=template_dict
                )
                response.raise_for_status()
                
                created_template = response.json()
                return StoryArchitectPrompt(**created_template)
                
        except httpx.HTTPError as e:
            logger.error("Failed to create prompt template", error=str(e))
            raise PayloadCMSConnectionError(f"Failed to create template: {e}")
        except ValidationError as e:
            logger.error("Invalid prompt template data", error=str(e))
            raise PayloadCMSValidationError(f"Invalid template data: {e}")
    
    # Seed Operations
    
    async def get_or_create_seed(self, project_id: str, concept_brief_hash: str) -> StoryArchitectSeed:
        """Get existing seed or create new one for deterministic generation"""
        try:
            # Try to find existing seed
            params = {
                "where[project_id][equals]": project_id,
                "where[concept_brief_hash][equals]": concept_brief_hash,
                "where[service_name][equals]": "story-architect",
                "limit": 1
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/storyArchitectSeeds",
                    headers=self.headers,
                    params=params
                )
                response.raise_for_status()
                
                data = response.json()
                docs = data.get("docs", [])
                
                if docs:
                    # Update usage count and last used timestamp
                    existing_seed = docs[0]
                    await self._update_seed_usage(existing_seed["id"])
                    return StoryArchitectSeed(**existing_seed)
                
                # Create new seed
                import hashlib
                seed_value = hashlib.sha256(f"{project_id}:{concept_brief_hash}:story-architect".encode()).hexdigest()[:16]
                
                new_seed = StoryArchitectSeed(
                    project_id=project_id,
                    service_name="story-architect",
                    seed_value=seed_value,
                    concept_brief_hash=concept_brief_hash,
                    usage_count=1
                )
                
                return await self._create_seed(new_seed)
                
        except httpx.HTTPError as e:
            logger.error("Failed to get/create seed", error=str(e))
            raise PayloadCMSConnectionError(f"Failed to get/create seed: {e}")
    
    async def _create_seed(self, seed: StoryArchitectSeed) -> StoryArchitectSeed:
        """Create new seed in PayloadCMS"""
        try:
            seed_dict = seed.dict(exclude={"id"})
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/storyArchitectSeeds",
                    headers=self.headers,
                    json=seed_dict
                )
                response.raise_for_status()
                
                created_seed = response.json()
                return StoryArchitectSeed(**created_seed)
                
        except httpx.HTTPError as e:
            raise PayloadCMSConnectionError(f"Failed to create seed: {e}")
    
    async def _update_seed_usage(self, seed_id: str) -> None:
        """Update seed usage count and timestamp"""
        try:
            update_data = {
                "usage_count": {"$inc": 1},
                "last_used_at": datetime.utcnow().isoformat()
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.patch(
                    f"{self.base_url}/storyArchitectSeeds/{seed_id}",
                    headers=self.headers,
                    json=update_data
                )
                response.raise_for_status()
                
        except httpx.HTTPError as e:
            logger.warning("Failed to update seed usage", seed_id=seed_id, error=str(e))
    
    # Character Operations
    
    async def get_character_roster(self, project_id: Optional[str] = None) -> List[Character]:
        """Get character roster for validation"""
        try:
            params = {
                "where[is_active][equals]": True,
                "limit": 100
            }
            
            if project_id:
                params["where[project_id][equals]"] = project_id
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/characters",
                    headers=self.headers,
                    params=params
                )
                response.raise_for_status()
                
                data = response.json()
                docs = data.get("docs", [])
                
                characters = []
                for doc in docs:
                    try:
                        characters.append(Character(**doc))
                    except ValidationError as e:
                        logger.warning("Invalid character data", character_id=doc.get("id"), error=str(e))
                
                logger.info(f"Retrieved {len(characters)} characters from roster")
                return characters
                
        except httpx.HTTPError as e:
            logger.error("Failed to fetch character roster", error=str(e))
            raise PayloadCMSConnectionError(f"Failed to fetch character roster: {e}")
    
    # Story Arc Operations
    
    async def store_story_arc(self, arc_record: StoryArcRecord) -> StoryArcRecord:
        """Store generated story arc"""
        try:
            # Convert to dict for JSON serialization
            record_dict = arc_record.dict(exclude={"id"})
            
            # Ensure datetime fields are properly serialized
            if "created_at" in record_dict:
                record_dict["created_at"] = record_dict["created_at"].isoformat()
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/storyArcs",
                    headers=self.headers,
                    json=record_dict
                )
                response.raise_for_status()
                
                stored_record = response.json()
                return StoryArcRecord(**stored_record)
                
        except httpx.HTTPError as e:
            logger.error("Failed to store story arc", request_id=arc_record.request_id, error=str(e))
            raise PayloadCMSConnectionError(f"Failed to store story arc: {e}")
        except ValidationError as e:
            logger.error("Invalid story arc data", error=str(e))
            raise PayloadCMSValidationError(f"Invalid story arc data: {e}")
    
    async def get_story_arc(self, request_id: str) -> Optional[StoryArcRecord]:
        """Get story arc by request ID"""
        try:
            params = {
                "where[request_id][equals]": request_id,
                "limit": 1
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/storyArcs",
                    headers=self.headers,
                    params=params
                )
                response.raise_for_status()
                
                data = response.json()
                docs = data.get("docs", [])
                
                if not docs:
                    return None
                
                record_data = docs[0]
                return StoryArcRecord(**record_data)
                
        except httpx.HTTPError as e:
            logger.error("Failed to fetch story arc", request_id=request_id, error=str(e))
            raise PayloadCMSConnectionError(f"Failed to fetch story arc: {e}")
        except ValidationError as e:
            logger.error("Invalid story arc data", error=str(e))
            raise PayloadCMSValidationError(f"Invalid story arc data: {e}")
    
    # Continuity Flag Operations
    
    async def store_continuity_flags(self, arc_id: str, flags: List[StoryContinuityFlag]) -> List[StoryContinuityFlag]:
        """Store continuity flags for a story arc"""
        stored_flags = []
        
        for flag in flags:
            try:
                flag_dict = flag.dict(exclude={"id"})
                flag_dict["arc_id"] = arc_id
                
                if "created_at" in flag_dict:
                    flag_dict["created_at"] = flag_dict["created_at"].isoformat()
                
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(
                        f"{self.base_url}/storyContinuityFlags",
                        headers=self.headers,
                        json=flag_dict
                    )
                    response.raise_for_status()
                    
                    stored_flag = response.json()
                    stored_flags.append(StoryContinuityFlag(**stored_flag))
                    
            except (httpx.HTTPError, ValidationError) as e:
                logger.warning(
                    "Failed to store continuity flag",
                    arc_id=arc_id,
                    flag_code=flag.code,
                    error=str(e)
                )
        
        logger.info(f"Stored {len(stored_flags)}/{len(flags)} continuity flags")
        return stored_flags
    
    async def get_continuity_flags(self, arc_id: str) -> List[StoryContinuityFlag]:
        """Get continuity flags for a story arc"""
        try:
            params = {
                "where[arc_id][equals]": arc_id,
                "sort": "-created_at",
                "limit": 50
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/storyContinuityFlags",
                    headers=self.headers,
                    params=params
                )
                response.raise_for_status()
                
                data = response.json()
                docs = data.get("docs", [])
                
                flags = []
                for doc in docs:
                    try:
                        flags.append(StoryContinuityFlag(**doc))
                    except ValidationError as e:
                        logger.warning("Invalid continuity flag data", flag_id=doc.get("id"), error=str(e))
                
                return flags
                
        except httpx.HTTPError as e:
            logger.error("Failed to fetch continuity flags", arc_id=arc_id, error=str(e))
            raise PayloadCMSConnectionError(f"Failed to fetch continuity flags: {e}")
    
    # Initialization and Setup
    
    async def setup_collections(self) -> None:
        """Initialize PayloadCMS collections with baseline data if needed"""
        try:
            logger.info("Setting up PayloadCMS collections for Story Architect")
            
            # Check if we need baseline prompt template
            criteria = PromptSelectionCriteria(fallback_to_default=True)
            template = await self.get_prompt_template(criteria)
            if not template:
                await self._create_default_prompt_template()
            
            logger.info("PayloadCMS collections setup complete")
            
        except Exception as e:
            logger.error("Failed to setup PayloadCMS collections", error=str(e))
            raise PayloadCMSError(f"Collections setup failed: {e}")
    
    async def _create_default_prompt_template(self) -> StoryArchitectPrompt:
        """Create default prompt template for story arc generation"""
        default_template = StoryArchitectPrompt(
            genre_tag=None,  # Default template applies to all genres
            tone_tag=None,   # Default template applies to all tones
            template_text="""
You are a professional story architect for short-form video content. Transform the given concept brief into a three-part story arc.

CONCEPT BRIEF:
Title: {{ concept_brief.title }}
Logline: {{ concept_brief.logline }}
Core Conflict: {{ concept_brief.core_conflict }}
Genre Tags: {{ concept_brief.genre_tags | join(', ') }}
Tone Keywords: {{ concept_brief.tone_keywords | join(', ') }}

{% if creative_guidelines %}
CREATIVE GUIDELINES:
{% if creative_guidelines.must_include %}Must Include: {{ creative_guidelines.must_include | join(', ') }}{% endif %}
{% if creative_guidelines.must_avoid %}Must Avoid: {{ creative_guidelines.must_avoid | join(', ') }}{% endif %}
Target Runtime: {{ creative_guidelines.target_runtime_seconds or 30 }} seconds
{% endif %}

CHARACTER ROSTER (DO NOT introduce new characters):
{% for character in character_roster %}
- {{ character.name }}: {{ character.description or character.role or 'Available character' }}
{% endfor %}

INSTRUCTIONS:
1. Create a three-part arc suitable for {{ creative_guidelines.target_runtime_seconds or 30 }}-second video
2. Each section should be approximately 80 words (can exceed if necessary)
3. Preserve the core conflict from the concept brief
4. Only reference characters from the roster above
5. Include 3 distinct emotional beats that progress through the arc
6. If you make assumptions or spot potential issues, note them in continuity_flags

Return ONLY a JSON object with this structure:
{
  "setup": "String describing the beginning/hook (~80 words)",
  "escalation": "String describing the confrontation/middle (~80 words)",
  "resolution": "String describing the conclusion/payoff (~80 words)",
  "emotional_beats": ["Emotional beat 1", "Emotional beat 2", "Emotional beat 3"],
  "continuity_flags": [
    {
      "code": "RUNTIME_FEASIBILITY_RISK",
      "message": "Story may be too complex for 30-second format"
    }
  ]
}
            """.strip(),
            version="1.0.0",
            is_active=True,
            priority=0
        )
        
        return await self.create_prompt_template(default_template)