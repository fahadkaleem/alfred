"""Configuration settings for Alfred Task Manager."""

import os
import logging
from typing import Optional, Dict, Any, Literal
from pathlib import Path
from dataclasses import asdict
from pydantic.dataclasses import dataclass

logger = logging.getLogger("alfred.config")


class ConfigError(Exception):
    """Base exception for configuration errors."""

    pass


class ConfigValidationError(ConfigError):
    """Exception raised when configuration validation fails."""

    pass


@dataclass
class Config:
    """Configuration data model for Alfred."""

    # API Keys
    linear_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    jira_api_key: Optional[str] = None
    jira_url: Optional[str] = None
    jira_email: Optional[str] = None

    # Additional AI Provider Keys
    openai_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None

    # Workspace Configuration
    workspace_id: Optional[str] = None
    team_id: Optional[str] = None
    active_epic_id: Optional[str] = None

    # Platform Selection
    platform: Literal["linear", "jira"] = "linear"

    # AI Configuration
    ai_provider: Literal["anthropic", "openai", "gemini"] = "anthropic"
    claude_model: str = "claude-3-5-sonnet-20241022"
    openai_model: str = "gpt-4-turbo-preview"
    gemini_model: str = "gemini-pro"
    max_tokens: int = 4096
    temperature: float = 0.7

    # AI Advanced Settings
    request_timeout: int = 60  # seconds
    max_retries: int = 3
    rate_limit_rpm: int = 50  # requests per minute
    chunk_overlap_tokens: int = 200
    max_context_percentage: float = 0.6

    # Behavior Configuration
    auto_decompose_threshold: int = 5
    default_subtask_count: int = 3

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary, excluding None values."""
        data = asdict(self)
        return {k: v for k, v in data.items() if v is not None and v != ""}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Config":
        """Create config from dictionary, ignoring unknown keys."""
        # Filter only known fields
        known_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered_data = {k: v for k, v in data.items() if k in known_fields}
        # Convert empty strings to None
        for key, value in filtered_data.items():
            if value == "":
                filtered_data[key] = None
        return cls(**filtered_data)


# Environment variable mapping
ENV_VAR_MAPPING = {
    "LINEAR_API_KEY": "linear_api_key",
    "ANTHROPIC_API_KEY": "anthropic_api_key",
    "JIRA_API_KEY": "jira_api_key",
    "JIRA_URL": "jira_url",
    "JIRA_EMAIL": "jira_email",
    "OPENAI_API_KEY": "openai_api_key",
    "GEMINI_API_KEY": "gemini_api_key",
    "ALFRED_WORKSPACE_ID": "workspace_id",
    "ALFRED_TEAM_ID": "team_id",
    "ALFRED_ACTIVE_EPIC_ID": "active_epic_id",
    "PLATFORM": "platform",
    "AI_PROVIDER": "ai_provider",
    "CLAUDE_MODEL": "claude_model",
    "OPENAI_MODEL": "openai_model",
    "GEMINI_MODEL": "gemini_model",
    "MAX_TOKENS": "max_tokens",
    "TEMPERATURE": "temperature",
    "AI_REQUEST_TIMEOUT": "request_timeout",
    "AI_MAX_RETRIES": "max_retries",
    "AI_RATE_LIMIT_RPM": "rate_limit_rpm",
    "AI_CHUNK_OVERLAP": "chunk_overlap_tokens",
    "AI_MAX_CONTEXT_PCT": "max_context_percentage",
}


def load_env(env_file: Optional[Path] = None) -> None:
    """Load environment variables from .env file.

    Args:
        env_file: Optional path to .env file
    """
    from dotenv import load_dotenv

    if env_file and env_file.exists():
        logger.debug(f"Loading environment from: {env_file}")
        load_dotenv(env_file, override=False)
        return

    # Search for .env in standard locations
    search_paths = [
        Path.cwd() / ".env",
        Path.cwd().parent / ".env",
        Path.home() / ".alfred" / ".env",
    ]

    for path in search_paths:
        if path.exists():
            logger.debug(f"Loading environment from: {path}")
            load_dotenv(path, override=False)
            return

    logger.debug("No .env file found in standard locations")
