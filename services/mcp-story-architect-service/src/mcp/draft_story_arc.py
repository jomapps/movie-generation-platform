"""
Draft Story Arc MCP Tool

Main MCP tool implementation for transforming Series Creator concept briefs
into structured three-part story arcs with continuity validation.
"""

import uuid
import asyncio
import json
import hashlib
from typing import Dict, Any, Optional, List
from datetime import datetime
import structlog
from pydantic import ValidationError
import openai

try:
    from jinja2 import Environment, BaseLoader, select_autoescape, TemplateSyntaxError
except ImportError:
    Environment = None
    TemplateSyntaxError = Exception

from ..config import get_config
from ..models.story_models import (
    DraftStoryArcRequest,
    DraftStoryArcResponse,
    ConceptBrief,
    CreativeGuidelines,
    StoryArc,
    ContinuityFlag,
    ContinuityFlagCode,
    ContinuitySeverity,
    StoryArcRecord,
    StoryContinuityFlag,
    PromptSelectionCriteria,
    WordCountAnalysis,
    TraceContext
)
from ..services.payload_service import PayloadCMSService, PayloadCMSError
from ..services.character_validation_service import CharacterValidationService


logger = structlog.get_logger(__name__)


class StoryArcGenerationError(Exception):
    """Base exception for story arc generation"""
    pass


class LLMError(Exception):
    """LLM-related errors"""
    pass


class LLMTimeoutError(LLMError):
    """LLM request timeout"""
    pass


class LLMValidationError(LLMError):
    """LLM response validation error"""
    pass


class DraftStoryArcTool:
    """MCP Tool for drafting story arcs from concept briefs"""
    
    def __init__(self):
        self.config = get_config()
        
        # Initialize services
        self.payload_service = PayloadCMSService()
        self.character_validation_service = CharacterValidationService()
        
        # Initialize LLM client
        self._openai_client = None
        
        # Initialize Jinja2 if available
        if Environment:
            self.jinja_env = Environment(
                loader=BaseLoader(),
                autoescape=select_autoescape(['html', 'xml']),
                trim_blocks=True,
                lstrip_blocks=True
            )
        else:
            self.jinja_env = None
            logger.warning("Jinja2 not available, using basic string replacement")
    
    @property
    def openai_client(self):
        """Lazy-initialized OpenAI client"""
        if self._openai_client is None:
            effective_config = self.config.effective_llm_config
            self._openai_client = openai.AsyncOpenAI(
                api_key=effective_config["api_key"],
                timeout=effective_config["timeout"]
            )
        return self._openai_client
    
    def get_schema(self) -> Dict[str, Any]:
        """Get MCP tool schema"""
        return {
            "name": "draft_story_arc",
            "description": "Transform a concept brief into a structured three-part story arc for short-form video content",
            "input_schema": {
                "type": "object",
                "properties": {
                    "concept_brief": {
                        "type": "object",
                        "description": "Concept brief from Series Creator",
                        "properties": {
                            "title": {"type": "string", "description": "Series title"},
                            "logline": {"type": "string", "description": "One-sentence premise"},
                            "core_conflict": {"type": "string", "description": "Central dramatic conflict"},
                            "tone_keywords": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Tone descriptors"
                            },
                            "genre_tags": {
                                "type": "array", 
                                "items": {"type": "string"},
                                "description": "Genre classifications"
                            },
                            "audience_promise": {"type": "string", "description": "What audience can expect"},
                            "success_criteria": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Success metrics"
                            }
                        },
                        "required": ["title", "logline", "core_conflict", "tone_keywords", "genre_tags"]
                    },
                    "creative_guidelines": {
                        "type": "object",
                        "description": "Optional creative guidelines",
                        "properties": {
                            "must_include": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Elements that must be included"
                            },
                            "must_avoid": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Elements to avoid"
                            },
                            "target_runtime_seconds": {
                                "type": "integer",
                                "description": "Target runtime in seconds",
                                "minimum": 5,
                                "maximum": 300
                            },
                            "trace_headers": {
                                "type": "object",
                                "description": "Orchestrator trace headers",
                                "properties": {
                                    "x-trace-id": {"type": "string"},
                                    "x-request-id": {"type": "string"},
                                    "x-correlation-id": {"type": "string"}
                                }
                            }
                        }
                    },
                    "project_id": {
                        "type": "string",
                        "description": "Optional project identifier for character roster and seed management"
                    }
                },
                "required": ["concept_brief"]
            }
        }
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute story arc generation from concept brief
        
        Args:
            input_data: Tool input matching schema
            
        Returns:
            Generated story arc with continuity validation
        """
        request_id = str(uuid.uuid4())
        start_time = datetime.utcnow()
        
        # Extract trace context
        trace_context = self._extract_trace_context(input_data)
        
        try:
            logger.info(
                "Starting story arc generation",
                request_id=request_id,
                trace_id=trace_context.trace_id,
                has_guidelines="creative_guidelines" in input_data,
                project_id=input_data.get("project_id")
            )
            
            # Step 1: Validate input
            request = await self._validate_input(input_data)
            
            # Step 2: Retrieve configuration and resources
            prompt_template, character_roster, seed = await self._gather_resources(
                request, input_data.get("project_id")
            )
            
            # Step 3: Generate deterministic seed and render prompt
            rendered_prompt = await self._render_prompt(
                request, prompt_template, character_roster, seed
            )
            
            # Step 4: Generate story arc with LLM
            raw_story_arc = await self._generate_with_llm(
                rendered_prompt, seed, trace_context
            )
            
            # Step 5: Validate and process story arc
            validated_arc, continuity_flags = await self._validate_and_process_arc(
                raw_story_arc, request, character_roster, input_data.get("project_id")
            )
            
            # Step 6: Store arc record and continuity flags
            arc_record = await self._store_arc_record(
                request_id=request_id,
                request=request,
                story_arc=validated_arc,
                continuity_flags=continuity_flags,
                generation_metadata={
                    "prompt_template_id": prompt_template.id if prompt_template else None,
                    "seed_used": seed,
                    "processing_time_ms": int((datetime.utcnow() - start_time).total_seconds() * 1000),
                    "trace_context": trace_context
                },
                project_id=input_data.get("project_id")
            )
            
            # Step 7: Prepare response
            response = DraftStoryArcResponse(
                story_arc=validated_arc,
                request_id=request_id,
                generated_at=datetime.utcnow(),
                model_used=self.config.effective_llm_config["model"],
                processing_time_ms=int((datetime.utcnow() - start_time).total_seconds() * 1000)
            )
            
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            logger.info(
                "Story arc generation completed successfully",
                request_id=request_id,
                trace_id=trace_context.trace_id,
                processing_time_ms=processing_time,
                continuity_flags_count=len(continuity_flags),
                arc_stored=arc_record is not None
            )
            
            return response.dict(exclude_none=True)
            
        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            logger.error(
                "Story arc generation failed",
                request_id=request_id,
                trace_id=trace_context.trace_id,
                processing_time_ms=processing_time,
                error=str(e),
                error_type=type(e).__name__
            )
            
            # Return error response
            return {
                "error": {
                    "type": type(e).__name__,
                    "message": str(e),
                    "request_id": request_id,
                    "trace_id": trace_context.trace_id,
                    "processing_time_ms": processing_time
                }
            }
    
    def _extract_trace_context(self, input_data: Dict[str, Any]) -> TraceContext:
        """Extract trace context from input data"""
        trace_headers = {}
        
        if "creative_guidelines" in input_data and input_data["creative_guidelines"]:
            trace_headers = input_data["creative_guidelines"].get("trace_headers", {})
        
        return TraceContext(
            trace_id=trace_headers.get("x-trace-id"),
            request_id=trace_headers.get("x-request-id"),
            correlation_id=trace_headers.get("x-correlation-id")
        )
    
    async def _validate_input(self, input_data: Dict[str, Any]) -> DraftStoryArcRequest:
        """Validate and parse input data"""
        try:
            return DraftStoryArcRequest(**input_data)
        except ValidationError as e:
            error_messages = []
            for error in e.errors():
                field = " -> ".join(str(loc) for loc in error["loc"])
                message = error["msg"]
                error_messages.append(f"{field}: {message}")
            
            raise StoryArcGenerationError(
                f"Input validation failed: {'; '.join(error_messages)}"
            )
    
    async def _gather_resources(self, request: DraftStoryArcRequest, project_id: Optional[str]):
        """Gather required resources for story arc generation"""
        
        # Determine prompt selection criteria
        primary_genre = request.concept_brief.genre_tags[0] if request.concept_brief.genre_tags else None
        primary_tone = request.concept_brief.tone_keywords[0] if request.concept_brief.tone_keywords else None
        target_runtime = None
        
        if request.creative_guidelines:
            target_runtime = request.creative_guidelines.target_runtime_seconds
        
        criteria = PromptSelectionCriteria(
            primary_genre=primary_genre,
            primary_tone=primary_tone,
            target_runtime=target_runtime,
            fallback_to_default=True
        )
        
        # Gather resources concurrently
        results = await asyncio.gather(
            self.payload_service.get_prompt_template(criteria),
            self.payload_service.get_character_roster(project_id) if project_id else asyncio.coroutine(lambda: [])(),
            self._get_or_generate_seed(request.concept_brief, project_id),
            return_exceptions=True
        )
        
        prompt_template = results[0] if not isinstance(results[0], Exception) else None
        character_roster = results[1] if not isinstance(results[1], Exception) else []
        seed = results[2] if not isinstance(results[2], Exception) else None
        
        # Log any resource gathering issues
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                resource_names = ["prompt_template", "character_roster", "seed"]
                logger.warning(
                    f"Failed to gather {resource_names[i]}",
                    error=str(result),
                    error_type=type(result).__name__
                )
        
        if not prompt_template:
            raise StoryArcGenerationError("No suitable prompt template found")
        
        logger.info(
            "Resources gathered",
            template_id=prompt_template.id if prompt_template else None,
            character_count=len(character_roster),
            seed_available=seed is not None
        )
        
        return prompt_template, character_roster, seed
    
    async def _get_or_generate_seed(self, concept_brief: ConceptBrief, project_id: Optional[str]) -> Optional[str]:
        """Get or generate deterministic seed for concept brief"""
        if not self.config.deterministic_seed_enabled:
            return None
        
        try:
            # Create hash of concept brief for seed generation
            concept_hash = hashlib.sha256(
                f"{concept_brief.title}:{concept_brief.logline}:{concept_brief.core_conflict}".encode()
            ).hexdigest()[:16]
            
            if project_id:
                seed_record = await self.payload_service.get_or_create_seed(project_id, concept_hash)
                return seed_record.seed_value
            else:
                # Generate seed without persistence
                return hashlib.sha256(f"story-architect:{concept_hash}".encode()).hexdigest()[:16]
                
        except Exception as e:
            logger.warning("Failed to get/generate seed", error=str(e))
            return None
    
    async def _render_prompt(self, request, prompt_template, character_roster, seed):
        """Render the prompt template with request data"""
        
        template_vars = {
            "concept_brief": request.concept_brief,
            "creative_guidelines": request.creative_guidelines,
            "character_roster": character_roster,
            "target_runtime": (
                request.creative_guidelines.target_runtime_seconds 
                if request.creative_guidelines else self.config.default_target_runtime
            ),
            "word_limit_soft": self.config.word_limit_soft,
            "word_limit_hard": self.config.word_limit_hard,
            "deterministic_seed": f"SEED: {seed}" if seed else ""
        }
        
        try:
            if self.jinja_env:
                template = self.jinja_env.from_string(prompt_template.template_text)
                rendered = template.render(**template_vars)
            else:
                rendered = self._basic_template_render(prompt_template.template_text, template_vars)
            
            logger.debug(
                "Prompt rendered successfully",
                template_id=prompt_template.id,
                prompt_length=len(rendered)
            )
            
            return rendered
            
        except Exception as e:
            logger.error("Failed to render prompt template", error=str(e))
            raise StoryArcGenerationError(f"Prompt rendering failed: {e}")
    
    def _basic_template_render(self, template: str, variables: Dict[str, Any]) -> str:
        """Basic template rendering fallback when Jinja2 not available"""
        rendered = template
        
        # Replace simple variables
        for key, value in variables.items():
            if value is not None:
                placeholder = f"{{{{ {key} }}}}"
                rendered = rendered.replace(placeholder, str(value))
        
        # Handle concept brief object fields
        if variables.get("concept_brief"):
            cb = variables["concept_brief"]
            rendered = rendered.replace("{{ concept_brief.title }}", cb.title)
            rendered = rendered.replace("{{ concept_brief.logline }}", cb.logline)
            rendered = rendered.replace("{{ concept_brief.core_conflict }}", cb.core_conflict)
            rendered = rendered.replace(
                "{{ concept_brief.genre_tags | join(', ') }}", 
                ", ".join(cb.genre_tags)
            )
            rendered = rendered.replace(
                "{{ concept_brief.tone_keywords | join(', ') }}", 
                ", ".join(cb.tone_keywords)
            )
        
        # Handle character roster
        if variables.get("character_roster"):
            roster = variables["character_roster"]
            roster_text = "\n".join([
                f"- {char.name}: {char.description or char.role or 'Available character'}"
                for char in roster
            ])
            rendered = rendered.replace("{% for character in character_roster %}\n- {{ character.name }}: {{ character.description or character.role or 'Available character' }}\n{% endfor %}", roster_text)
        
        return rendered
    
    async def _generate_with_llm(self, prompt: str, seed: Optional[str], trace_context: TraceContext) -> Dict[str, Any]:
        """Generate story arc using LLM"""
        
        effective_config = self.config.effective_llm_config
        
        try:
            logger.info(
                "Starting LLM generation",
                provider=effective_config["provider"],
                model=effective_config["model"],
                seed=seed[:8] + "..." if seed else None
            )
            
            # Prepare messages
            messages = [
                {
                    "role": "system",
                    "content": "You are a professional story architect specializing in short-form content. Generate structured story arcs in valid JSON format."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            # Add trace headers to the request if available
            extra_headers = trace_context.to_headers() if trace_context else {}
            
            # Generate with OpenAI
            response = await self.openai_client.chat.completions.create(
                model=effective_config["model"],
                messages=messages,
                max_tokens=effective_config["max_tokens"],
                temperature=effective_config["temperature"],
                response_format={"type": "json_object"},
                seed=int(hashlib.sha256(seed.encode()).hexdigest()[:8], 16) if seed else None,
                extra_headers=extra_headers
            )
            
            if not response.choices:
                raise LLMError("No response choices received from LLM")
            
            content = response.choices[0].message.content
            if not content:
                raise LLMError("Empty response content from LLM")
            
            # Parse JSON response
            try:
                story_data = json.loads(content.strip())
                logger.info(
                    "LLM generation successful",
                    tokens_used=response.usage.total_tokens if response.usage else 0
                )
                return story_data
                
            except json.JSONDecodeError as e:
                raise LLMValidationError(f"Invalid JSON response: {e}")
            
        except openai.APITimeoutError as e:
            raise LLMTimeoutError(f"LLM request timeout: {e}")
        except openai.APIError as e:
            raise LLMError(f"LLM API error: {e}")
        except Exception as e:
            logger.error("LLM generation failed", error=str(e))
            raise LLMError(f"LLM generation failed: {e}")
    
    async def _validate_and_process_arc(self, raw_story_data, request, character_roster, project_id):
        """Validate story arc and generate continuity flags"""
        
        continuity_flags = []
        
        # Validate basic story arc structure
        try:
            story_arc = StoryArc(**raw_story_data)
        except ValidationError as e:
            error_messages = []
            for error in e.errors():
                field = " -> ".join(str(loc) for loc in error["loc"])
                message = error["msg"]
                error_messages.append(f"{field}: {message}")
            
            raise StoryArcGenerationError(
                f"Story arc validation failed: {'; '.join(error_messages)}"
            )
        
        # Extract continuity flags from LLM response
        if "continuity_flags" in raw_story_data:
            for flag_data in raw_story_data["continuity_flags"]:
                try:
                    flag = ContinuityFlag(**flag_data)
                    continuity_flags.append(flag)
                except ValidationError as e:
                    logger.warning("Invalid continuity flag from LLM", flag_data=flag_data, error=str(e))
        
        # Perform word count analysis
        word_analysis = self._analyze_word_counts(story_arc)
        if word_analysis.has_violations:
            continuity_flags.extend(self._create_word_limit_flags(word_analysis))
        
        # Validate characters if roster available and validation enabled
        if character_roster and self.config.strict_character_validation:
            char_flags, found_chars, unknown_chars = await self.character_validation_service.validate_story_arc(
                story_arc, character_roster, project_id
            )
            continuity_flags.extend(char_flags)
            
            # Add character consistency flags
            consistency_flags = self.character_validation_service.validate_character_consistency(
                story_arc, character_roster
            )
            continuity_flags.extend(consistency_flags)
        
        # Additional content validations
        content_flags = self._validate_content_quality(story_arc, request.concept_brief)
        continuity_flags.extend(content_flags)
        
        logger.info(
            "Story arc validation complete",
            total_flags=len(continuity_flags),
            error_flags=sum(1 for f in continuity_flags if f.severity == ContinuitySeverity.ERROR),
            warning_flags=sum(1 for f in continuity_flags if f.severity == ContinuitySeverity.WARNING)
        )
        
        return story_arc, continuity_flags
    
    def _analyze_word_counts(self, story_arc: StoryArc) -> WordCountAnalysis:
        """Analyze word counts in story arc sections"""
        
        # Count words in each section
        beginning_count = len(story_arc.beginning.split())
        middle_count = len(story_arc.middle.split())
        end_count = len(story_arc.end.split())
        total_count = beginning_count + middle_count + end_count
        
        # Check for violations
        has_violations = False
        section_violations = []
        
        # Soft limit checks
        if total_count > self.config.word_limit_soft:
            has_violations = True
            if total_count > self.config.word_limit_hard:
                section_violations.append("HARD_LIMIT_EXCEEDED")
            else:
                section_violations.append("SOFT_LIMIT_EXCEEDED")
        
        # Section balance checks
        expected_per_section = total_count / 3
        balance_threshold = expected_per_section * self.config.section_balance_threshold
        
        if abs(beginning_count - expected_per_section) > balance_threshold:
            has_violations = True
            section_violations.append("BEGINNING_IMBALANCE")
        
        if abs(middle_count - expected_per_section) > balance_threshold:
            has_violations = True
            section_violations.append("MIDDLE_IMBALANCE")
            
        if abs(end_count - expected_per_section) > balance_threshold:
            has_violations = True
            section_violations.append("END_IMBALANCE")
        
        return WordCountAnalysis(
            beginning_count=beginning_count,
            middle_count=middle_count,
            end_count=end_count,
            total_count=total_count,
            has_violations=has_violations,
            violation_codes=section_violations
        )
    
    def _create_word_limit_flags(self, analysis: WordCountAnalysis) -> List[ContinuityFlag]:
        """Create continuity flags from word count analysis"""
        flags = []
        
        if "HARD_LIMIT_EXCEEDED" in analysis.violation_codes:
            flags.append(ContinuityFlag(
                code=ContinuityFlagCode.WORD_LIMIT_HARD,
                message=f"Story arc exceeds hard word limit ({analysis.total_count}/{self.config.word_limit_hard} words)",
                section="all",
                severity=ContinuitySeverity.ERROR,
                details={
                    "limit": self.config.word_limit_hard,
                    "actual": analysis.total_count,
                    "overage_percent": round((analysis.total_count - self.config.word_limit_hard) / self.config.word_limit_hard * 100, 1)
                }
            ))
        elif "SOFT_LIMIT_EXCEEDED" in analysis.violation_codes:
            flags.append(ContinuityFlag(
                code=ContinuityFlagCode.WORD_LIMIT_SOFT,
                message=f"Story arc exceeds soft word limit ({analysis.total_count}/{self.config.word_limit_soft} words)",
                section="all",
                severity=ContinuitySeverity.WARNING,
                details={
                    "limit": self.config.word_limit_soft,
                    "actual": analysis.total_count,
                    "overage_percent": round((analysis.total_count - self.config.word_limit_soft) / self.config.word_limit_soft * 100, 1)
                }
            ))
        
        # Check section imbalance flags
        if "BEGINNING_IMBALANCE" in analysis.violation_codes:
            flags.append(self._create_section_imbalance_flag("beginning", analysis.beginning_count, analysis.total_count))
        
        if "MIDDLE_IMBALANCE" in analysis.violation_codes:
            flags.append(self._create_section_imbalance_flag("middle", analysis.middle_count, analysis.total_count))
            
        if "END_IMBALANCE" in analysis.violation_codes:
            flags.append(self._create_section_imbalance_flag("end", analysis.end_count, analysis.total_count))
        
        return flags
    
    def _create_section_imbalance_flag(self, section: str, word_count: int, total_words: int) -> ContinuityFlag:
        """Create a section imbalance flag"""
        expected = total_words / 3
        deviation = abs(word_count - expected) / expected
        
        return ContinuityFlag(
            code=ContinuityFlagCode.SECTION_IMBALANCE,
            message=f"The {section} section is {'too long' if word_count > expected else 'too short'} relative to other sections",
            section=section,
            severity=ContinuitySeverity.WARNING,
            details={
                "expected_words": round(expected),
                "actual_words": word_count,
                "deviation_percent": round(deviation * 100, 1)
            }
        )
    
    def _validate_content_quality(self, story_arc: StoryArc, concept_brief: ConceptBrief) -> List[ContinuityFlag]:
        """Validate content quality for thematic consistency"""
        flags = []
        
        # Check for excessively short sections
        min_words_per_section = self.config.min_words_per_section
        
        if len(story_arc.beginning.split()) < min_words_per_section:
            flags.append(ContinuityFlag(
                code=ContinuityFlagCode.SECTION_TOO_SHORT,
                message=f"Beginning section is too short (< {min_words_per_section} words)",
                section="beginning",
                severity=ContinuitySeverity.WARNING
            ))
            
        if len(story_arc.middle.split()) < min_words_per_section:
            flags.append(ContinuityFlag(
                code=ContinuityFlagCode.SECTION_TOO_SHORT,
                message=f"Middle section is too short (< {min_words_per_section} words)",
                section="middle", 
                severity=ContinuitySeverity.WARNING
            ))
            
        if len(story_arc.end.split()) < min_words_per_section:
            flags.append(ContinuityFlag(
                code=ContinuityFlagCode.SECTION_TOO_SHORT,
                message=f"End section is too short (< {min_words_per_section} words)",
                section="end",
                severity=ContinuitySeverity.WARNING
            ))
        
        # Check for thematic consistency with concept brief
        if not self._contains_thematic_elements(story_arc, concept_brief):
            flags.append(ContinuityFlag(
                code=ContinuityFlagCode.THEMATIC_INCONSISTENCY,
                message="Story arc may not fully capture the core conflict or themes from the concept brief",
                section="all",
                severity=ContinuitySeverity.WARNING
            ))
        
        return flags
    
    def _contains_thematic_elements(self, story_arc: StoryArc, concept_brief: ConceptBrief) -> bool:
        """Check if story arc contains thematic elements from concept brief"""
        # Simple check to see if core conflict is represented in the story
        combined_text = f"{story_arc.beginning} {story_arc.middle} {story_arc.end} {story_arc.summary or ''}"
        combined_text = combined_text.lower()
        
        # Extract key terms from concept brief
        key_terms = []
        
        # Add core conflict terms
        if concept_brief.core_conflict:
            # Extract nouns and significant terms from core conflict
            conflict_words = concept_brief.core_conflict.lower().split()
            key_terms.extend([w for w in conflict_words if len(w) > 5])
            
        # Add genre and tone keywords
        key_terms.extend([g.lower() for g in concept_brief.genre_tags])
        key_terms.extend([t.lower() for t in concept_brief.tone_keywords])
        
        # Check if key terms appear in the story
        found_terms = 0
        for term in key_terms:
            if term.lower() in combined_text:
                found_terms += 1
        
        # If at least 50% of key terms are represented, consider it thematically consistent
        return found_terms >= max(1, len(key_terms) // 2)
    
    async def _store_arc_record(
        self, 
        request_id: str,
        request: DraftStoryArcRequest,
        story_arc: StoryArc,
        continuity_flags: List[ContinuityFlag],
        generation_metadata: Dict[str, Any],
        project_id: Optional[str] = None
    ) -> Optional[StoryArcRecord]:
        """Store story arc and continuity flags in PayloadCMS"""
        
        if not self.config.persist_story_arcs:
            logger.info("Story arc persistence disabled, skipping storage")
            return None
        
        try:
            # Prepare story arc record
            arc_record = StoryArcRecord(
                id=request_id,
                concept_brief=request.concept_brief,
                story_arc=story_arc,
                creative_guidelines=request.creative_guidelines,
                project_id=project_id,
                generated_at=datetime.utcnow(),
                generation_metadata=generation_metadata
            )
            
            # Store story arc
            result = await self.payload_service.create_story_arc_record(arc_record)
            
            # Store continuity flags if any
            if continuity_flags:
                flag_records = []
                for flag in continuity_flags:
                    flag_record = StoryContinuityFlag(
                        story_arc_id=request_id,
                        flag=flag
                    )
                    flag_records.append(flag_record)
                
                await self.payload_service.create_continuity_flags(flag_records)
            
            logger.info(
                "Story arc record stored successfully",
                record_id=result.id,
                flags_stored=len(continuity_flags)
            )
            
            return result
            
        except PayloadCMSError as e:
            logger.error(
                "Failed to store story arc record",
                error=str(e),
                request_id=request_id
            )
            return None


# Create the actual tool instance for export
draft_story_arc_tool = DraftStoryArcTool()
