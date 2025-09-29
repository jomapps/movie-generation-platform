"""
Story Architect Service Configuration

Manages environment configuration with validation and defaults for story arc generation.
"""

import os
import logging
from typing import Optional
from pydantic import BaseSettings, Field, validator
from pydantic_settings import BaseSettings as PydanticBaseSettings


class StoryArchitectConfig(PydanticBaseSettings):
    """Configuration for the Story Architect Service"""
    
    # Service Configuration
    service_name: str = Field(default="mcp-story-architect-service", env="SERVICE_NAME")
    service_version: str = Field(default="1.0.0", env="SERVICE_VERSION")
    environment: str = Field(default="development", env="ENVIRONMENT")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    request_timeout_seconds: int = Field(default=30, env="REQUEST_TIMEOUT_SECONDS")
    
    # PayloadCMS Configuration
    payload_api_url: str = Field(..., env="PAYLOAD_API_URL")
    payload_api_secret: str = Field(..., env="PAYLOAD_API_SECRET")
    payload_timeout_seconds: int = Field(default=10, env="PAYLOAD_TIMEOUT_SECONDS")
    
    # OpenAI Configuration
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", env="OPENAI_MODEL")
    openai_max_tokens: int = Field(default=2000, env="OPENAI_MAX_TOKENS")
    openai_temperature: float = Field(default=0.7, env="OPENAI_TEMPERATURE")
    openai_timeout_seconds: int = Field(default=6, env="OPENAI_TIMEOUT_SECONDS")
    
    # LLM Override Configuration
    override_llm_provider: Optional[str] = Field(None, env="OVERRIDE_LLM_PROVIDER")
    override_llm_model: Optional[str] = Field(None, env="OVERRIDE_LLM_MODEL")
    override_llm_api_key: Optional[str] = Field(None, env="OVERRIDE_LLM_API_KEY")
    override_llm_max_tokens: Optional[int] = Field(None, env="OVERRIDE_LLM_MAX_TOKENS")
    override_llm_temperature: Optional[float] = Field(None, env="OVERRIDE_LLM_TEMPERATURE")
    
    # Observability
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    metrics_port: int = Field(default=8081, env="METRICS_PORT")
    enable_tracing: bool = Field(default=True, env="ENABLE_TRACING")
    
    # Story Architect Configuration
    max_retries: int = Field(default=1, env="MAX_RETRIES")
    word_limit_soft: int = Field(default=80, env="WORD_LIMIT_SOFT")
    word_limit_hard: int = Field(default=120, env="WORD_LIMIT_HARD")
    default_target_runtime: int = Field(default=30, env="DEFAULT_TARGET_RUNTIME")
    deterministic_seed_enabled: bool = Field(default=True, env="DETERMINISTIC_SEED_ENABLED")
    
    # Character Validation
    strict_character_validation: bool = Field(default=True, env="STRICT_CHARACTER_VALIDATION")
    allow_new_locations: bool = Field(default=False, env="ALLOW_NEW_LOCATIONS")
    
    # Continuity Flagging
    enable_continuity_flags: bool = Field(default=True, env="ENABLE_CONTINUITY_FLAGS")
    continuity_severity_threshold: str = Field(default="warning", env="CONTINUITY_SEVERITY_THRESHOLD")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @validator("log_level")
    def validate_log_level(cls, v):
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"log_level must be one of {valid_levels}")
        return v.upper()
    
    @validator("environment")
    def validate_environment(cls, v):
        valid_envs = ["development", "staging", "production"]
        if v.lower() not in valid_envs:
            raise ValueError(f"environment must be one of {valid_envs}")
        return v.lower()
    
    @validator("openai_temperature", "override_llm_temperature")
    def validate_temperature(cls, v):
        if v is not None and not (0.0 <= v <= 2.0):
            raise ValueError("temperature must be between 0.0 and 2.0")
        return v
    
    @validator("request_timeout_seconds", "payload_timeout_seconds", "openai_timeout_seconds")
    def validate_timeouts(cls, v):
        if v <= 0 or v > 300:
            raise ValueError("timeout must be between 1 and 300 seconds")
        return v
    
    @validator("max_retries")
    def validate_max_retries(cls, v):
        if v < 0 or v > 5:
            raise ValueError("max_retries must be between 0 and 5")
        return v
    
    @validator("word_limit_soft", "word_limit_hard")
    def validate_word_limits(cls, v):
        if v < 10 or v > 500:
            raise ValueError("word limits must be between 10 and 500")
        return v
    
    @validator("default_target_runtime")
    def validate_target_runtime(cls, v):
        if v < 5 or v > 300:
            raise ValueError("target_runtime must be between 5 and 300 seconds")
        return v
    
    @validator("continuity_severity_threshold")
    def validate_severity_threshold(cls, v):
        valid_severities = ["info", "warning", "error", "critical"]
        if v.lower() not in valid_severities:
            raise ValueError(f"continuity_severity_threshold must be one of {valid_severities}")
        return v.lower()
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.environment == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.environment == "development"
    
    @property
    def use_llm_override(self) -> bool:
        """Check if LLM override is configured"""
        return (
            self.override_llm_provider is not None and
            self.override_llm_model is not None and
            self.override_llm_api_key is not None
        )
    
    @property
    def effective_llm_config(self) -> dict:
        """Get effective LLM configuration (override if available, otherwise OpenAI)"""
        if self.use_llm_override:
            return {
                "provider": self.override_llm_provider,
                "model": self.override_llm_model,
                "api_key": self.override_llm_api_key,
                "max_tokens": self.override_llm_max_tokens or self.openai_max_tokens,
                "temperature": self.override_llm_temperature or self.openai_temperature,
                "timeout": self.openai_timeout_seconds
            }
        return {
            "provider": "openai",
            "model": self.openai_model,
            "api_key": self.openai_api_key,
            "max_tokens": self.openai_max_tokens,
            "temperature": self.openai_temperature,
            "timeout": self.openai_timeout_seconds
        }


def setup_logging(config: StoryArchitectConfig) -> None:
    """Configure structured logging"""
    import structlog
    
    # Configure stdlib logging
    logging.basicConfig(
        format="%(message)s",
        level=getattr(logging, config.log_level),
        force=True,
    )
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer() if config.is_development
            else structlog.processors.JSONRenderer()
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, config.log_level)
        ),
        context_class=dict,
        logger_factory=structlog.WriteLoggerFactory(),
        cache_logger_on_first_use=False,
    )


# Global configuration instance
_config: Optional[StoryArchitectConfig] = None


def get_config() -> StoryArchitectConfig:
    """Get the global configuration instance"""
    global _config
    if _config is None:
        _config = StoryArchitectConfig()
        setup_logging(_config)
    return _config


def reload_config() -> StoryArchitectConfig:
    """Reload configuration from environment"""
    global _config
    _config = StoryArchitectConfig()
    setup_logging(_config)
    return _config