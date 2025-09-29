"""
Story Architect Service Data Models

Pydantic models for story arc generation, validation, and PayloadCMS integration.
"""

from datetime import datetime
from typing import List, Optional, Any, Dict, Union
from enum import Enum
from pydantic import BaseModel, Field, validator
import uuid


class ContinuitySeverity(str, Enum):
    """Severity levels for continuity flags"""
    INFO = "info"
    WARNING = "warning" 
    ERROR = "error"
    CRITICAL = "critical"


class ContinuityFlagCode(str, Enum):
    """Machine-readable continuity flag codes"""
    CHARACTER_NOT_FOUND = "CHARACTER_NOT_FOUND"
    LOCATION_UNSPECIFIED = "LOCATION_UNSPECIFIED"
    CONFLICT_DRIFT = "CONFLICT_DRIFT"
    RUNTIME_FEASIBILITY_RISK = "RUNTIME_FEASIBILITY_RISK"
    TONE_MISMATCH = "TONE_MISMATCH"
    PACING_ISSUE = "PACING_ISSUE"
    WORD_LIMIT_EXCEEDED = "WORD_LIMIT_EXCEEDED"
    GENRE_INCONSISTENCY = "GENRE_INCONSISTENCY"
    EMOTIONAL_BEAT_MISSING = "EMOTIONAL_BEAT_MISSING"


# Input/Output Models

class ConceptBrief(BaseModel):
    """Concept brief from Series Creator"""
    
    title: str = Field(..., description="Series title")
    logline: str = Field(..., description="One-sentence premise")
    core_conflict: str = Field(..., description="Central dramatic conflict")
    tone_keywords: List[str] = Field(..., description="Tone descriptors")
    genre_tags: List[str] = Field(..., description="Genre classifications")
    audience_promise: Optional[str] = Field(None, description="What audience can expect")
    success_criteria: Optional[List[str]] = Field(None, description="Success metrics")
    
    @validator("title", "logline", "core_conflict")
    def validate_required_strings(cls, v):
        if not v or not v.strip():
            raise ValueError("Required string fields cannot be empty")
        return v.strip()
    
    @validator("tone_keywords", "genre_tags")
    def validate_tag_arrays(cls, v):
        if not v:
            raise ValueError("Tag arrays must have at least one item")
        if len(v) > 3:
            v = v[:3]  # Limit to 3 items
        return [tag.strip() for tag in v if tag.strip()]


class TraceHeaders(BaseModel):
    """Trace headers from orchestrator"""
    
    x_trace_id: Optional[str] = Field(None, alias="x-trace-id", description="Trace ID")
    x_request_id: Optional[str] = Field(None, alias="x-request-id", description="Request ID")
    x_correlation_id: Optional[str] = Field(None, alias="x-correlation-id", description="Correlation ID")
    
    class Config:
        allow_population_by_field_name = True


class CreativeGuidelines(BaseModel):
    """Optional creative guidelines for story arc generation"""
    
    must_include: Optional[List[str]] = Field(None, description="Elements that must be included")
    must_avoid: Optional[List[str]] = Field(None, description="Elements to avoid")
    target_runtime_seconds: Optional[int] = Field(30, description="Target runtime in seconds")
    trace_headers: Optional[TraceHeaders] = Field(None, description="Orchestrator trace headers")
    
    @validator("target_runtime_seconds")
    def validate_runtime(cls, v):
        if v is not None and (v < 5 or v > 300):
            raise ValueError("target_runtime_seconds must be between 5 and 300")
        return v
    
    @validator("must_include", "must_avoid")
    def validate_guidelines_lists(cls, v):
        if v is not None:
            return [item.strip() for item in v if item.strip()]
        return v


class ContinuityFlag(BaseModel):
    """Machine-readable continuity flag"""
    
    code: ContinuityFlagCode = Field(..., description="Machine-readable flag code")
    message: str = Field(..., description="Human-readable description")
    severity: ContinuitySeverity = Field(default=ContinuitySeverity.WARNING, description="Flag severity")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context data")
    
    @validator("message")
    def validate_message(cls, v):
        if not v or not v.strip():
            raise ValueError("Continuity flag message cannot be empty")
        return v.strip()


class StoryArc(BaseModel):
    """Generated story arc structure"""
    
    setup: str = Field(..., description="Setup section (beginning)")
    escalation: str = Field(..., description="Escalation section (middle)")
    resolution: str = Field(..., description="Resolution section (end)")
    emotional_beats: List[str] = Field(..., description="Three emotional beats")
    continuity_flags: List[ContinuityFlag] = Field(default_factory=list, description="Continuity issues")
    seed: Optional[str] = Field(None, description="Deterministic seed used")
    
    @validator("setup", "escalation", "resolution")
    def validate_arc_sections(cls, v):
        if not v or not v.strip():
            raise ValueError("Arc sections cannot be empty")
        return v.strip()
    
    @validator("emotional_beats")
    def validate_emotional_beats(cls, v):
        if not v or len(v) != 3:
            raise ValueError("Must have exactly 3 emotional beats")
        return [beat.strip() for beat in v if beat.strip()]


# Request/Response Models

class DraftStoryArcRequest(BaseModel):
    """Request model for draft_story_arc MCP tool"""
    
    concept_brief: ConceptBrief = Field(..., description="Concept brief from Series Creator")
    creative_guidelines: Optional[CreativeGuidelines] = Field(None, description="Optional guidelines")
    
    @validator("concept_brief")
    def validate_concept_brief_required(cls, v):
        if not v.core_conflict:
            raise ValueError("concept_brief must have core_conflict")
        return v


class DraftStoryArcResponse(BaseModel):
    """Response model for draft_story_arc MCP tool"""
    
    story_arc: StoryArc = Field(..., description="Generated story arc")
    request_id: Optional[str] = Field(None, description="Unique request identifier")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Generation timestamp")
    model_used: Optional[str] = Field(None, description="LLM model used")
    processing_time_ms: Optional[int] = Field(None, description="Processing time in milliseconds")


# PayloadCMS Collection Models

class StoryArchitectPrompt(BaseModel):
    """Story architect prompt template stored in PayloadCMS"""
    
    id: Optional[str] = Field(None, description="PayloadCMS document ID")
    genre_tag: Optional[str] = Field(None, description="Primary genre this template targets")
    tone_tag: Optional[str] = Field(None, description="Primary tone this template targets")
    template_text: str = Field(..., description="Jinja2 template content")
    version: str = Field(..., description="Template version")
    is_active: bool = Field(default=True, description="Whether template is active")
    priority: int = Field(default=0, description="Selection priority (higher = preferred)")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    
    class Config:
        collection_name = "storyArchitectPrompts"


class StoryArchitectSeed(BaseModel):
    """Deterministic seed for story generation stored in PayloadCMS"""
    
    id: Optional[str] = Field(None, description="PayloadCMS document ID")
    project_id: str = Field(..., description="Project identifier")
    service_name: str = Field(default="story-architect", description="Service name")
    seed_value: str = Field(..., description="Deterministic seed value")
    concept_brief_hash: Optional[str] = Field(None, description="Hash of concept brief for uniqueness")
    last_used_at: datetime = Field(default_factory=datetime.utcnow, description="Last usage timestamp")
    usage_count: int = Field(default=0, description="Number of times used")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    
    class Config:
        collection_name = "storyArchitectSeeds"


class Character(BaseModel):
    """Character from shared roster stored in PayloadCMS"""
    
    id: Optional[str] = Field(None, description="PayloadCMS document ID")
    name: str = Field(..., description="Character name")
    description: Optional[str] = Field(None, description="Character description")
    role: Optional[str] = Field(None, description="Character role (protagonist, antagonist, etc.)")
    is_active: bool = Field(default=True, description="Whether character is available for stories")
    project_id: Optional[str] = Field(None, description="Associated project ID")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    
    class Config:
        collection_name = "characters"


class StoryArcRecord(BaseModel):
    """Story arc record stored in PayloadCMS"""
    
    id: Optional[str] = Field(None, description="PayloadCMS document ID")
    request_id: str = Field(..., description="Unique request identifier")
    project_id: Optional[str] = Field(None, description="Associated project ID")
    concept_brief_id: Optional[str] = Field(None, description="Reference to concept brief")
    story_arc: StoryArc = Field(..., description="Generated story arc")
    
    # Generation metadata
    prompt_template_id: Optional[str] = Field(None, description="Template used for generation")
    seed_used: Optional[str] = Field(None, description="Deterministic seed used")
    model_used: str = Field(..., description="LLM model used")
    processing_time_ms: Optional[int] = Field(None, description="Processing time")
    retry_count: int = Field(default=0, description="Number of retries required")
    
    # Trace metadata
    trace_id: Optional[str] = Field(None, description="Trace ID from orchestrator")
    request_correlation_id: Optional[str] = Field(None, description="Request correlation ID")
    
    # Validation metadata
    word_counts: Optional[Dict[str, int]] = Field(None, description="Word counts per section")
    validation_passed: bool = Field(default=True, description="Whether validation passed")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    
    class Config:
        collection_name = "storyArcs"


class StoryContinuityFlag(BaseModel):
    """Continuity flag record stored in PayloadCMS"""
    
    id: Optional[str] = Field(None, description="PayloadCMS document ID")
    arc_id: str = Field(..., description="Reference to story arc")
    code: ContinuityFlagCode = Field(..., description="Machine-readable flag code")
    message: str = Field(..., description="Human-readable message")
    severity: ContinuitySeverity = Field(..., description="Flag severity")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    
    # Resolution tracking
    is_resolved: bool = Field(default=False, description="Whether flag has been addressed")
    resolved_by: Optional[str] = Field(None, description="Who resolved the flag")
    resolved_at: Optional[datetime] = Field(None, description="When flag was resolved")
    resolution_notes: Optional[str] = Field(None, description="Resolution notes")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    
    class Config:
        collection_name = "storyContinuityFlags"


# Utility Models

class WordCountAnalysis(BaseModel):
    """Word count analysis for story arc sections"""
    
    setup_words: int = Field(0, description="Word count for setup section")
    escalation_words: int = Field(0, description="Word count for escalation section")
    resolution_words: int = Field(0, description="Word count for resolution section")
    total_words: int = Field(0, description="Total word count")
    
    soft_limit_exceeded: List[str] = Field(default_factory=list, description="Sections exceeding soft limit")
    hard_limit_exceeded: List[str] = Field(default_factory=list, description="Sections exceeding hard limit")
    
    @property
    def average_words_per_section(self) -> float:
        return self.total_words / 3 if self.total_words > 0 else 0
    
    @property
    def has_violations(self) -> bool:
        return bool(self.soft_limit_exceeded or self.hard_limit_exceeded)


class PromptSelectionCriteria(BaseModel):
    """Criteria for selecting prompt templates"""
    
    primary_genre: Optional[str] = Field(None, description="Primary genre tag")
    primary_tone: Optional[str] = Field(None, description="Primary tone keyword")
    target_runtime: Optional[int] = Field(None, description="Target runtime in seconds")
    fallback_to_default: bool = Field(default=True, description="Allow fallback to default template")


class TraceContext(BaseModel):
    """Trace context for request correlation"""
    
    trace_id: Optional[str] = Field(None, description="Trace ID")
    request_id: Optional[str] = Field(None, description="Request ID")
    correlation_id: Optional[str] = Field(None, description="Correlation ID")
    parent_span_id: Optional[str] = Field(None, description="Parent span ID")
    
    def to_headers(self) -> Dict[str, str]:
        """Convert to HTTP headers dictionary"""
        headers = {}
        if self.trace_id:
            headers["x-trace-id"] = self.trace_id
        if self.request_id:
            headers["x-request-id"] = self.request_id
        if self.correlation_id:
            headers["x-correlation-id"] = self.correlation_id
        if self.parent_span_id:
            headers["x-parent-span-id"] = self.parent_span_id
        return headers


class StoryArchitectMetrics(BaseModel):
    """Metrics for story architect operations"""
    
    total_requests: int = 0
    successful_generations: int = 0
    failed_generations: int = 0
    retries_attempted: int = 0
    
    continuity_flags_raised: int = 0
    character_validation_failures: int = 0
    word_limit_violations: int = 0
    
    average_processing_time_ms: float = 0.0
    p95_processing_time_ms: float = 0.0
    
    template_usage_count: Dict[str, int] = Field(default_factory=dict)
    
    @property
    def success_rate(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return self.successful_generations / self.total_requests
    
    @property
    def average_flags_per_request(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return self.continuity_flags_raised / self.total_requests