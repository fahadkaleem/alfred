"""Configuration settings for Alfred Task Manager."""

import os
import logging
from typing import Optional
from pathlib import Path

logger = logging.getLogger("alfred.config")


class ConfigError(Exception):
    """Base exception for configuration errors."""

    pass


class ConfigValidationError(ConfigError):
    """Exception raised when configuration validation fails."""

    pass


# Environment variable mapping
ENV_VAR_MAPPING = {
    "LINEAR_API_KEY": "linear_api_key",
    "ANTHROPIC_API_KEY": "anthropic_api_key",
    "PERPLEXITY_API_KEY": "perplexity_api_key",
    "RESEARCH_PROVIDER": "research_provider",
    "PERPLEXITY_MODEL": "perplexity_model",
    "JIRA_API_KEY": "jira_api_key",
    "JIRA_URL": "jira_url",
    "JIRA_EMAIL": "jira_email",
    "ALFRED_WORKSPACE_ID": "workspace_id",
    "ALFRED_TEAM_ID": "team_id",
    "ALFRED_ACTIVE_EPIC_ID": "active_epic_id",
    "PLATFORM": "platform",
    "AI_PROVIDER": "ai_provider",
    "CLAUDE_MODEL": "claude_model",
    "MAX_TOKENS": "max_tokens",
    "TEMPERATURE": "temperature",
    "AI_REQUEST_TIMEOUT": "request_timeout",
    "AI_MAX_RETRIES": "max_retries",
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
