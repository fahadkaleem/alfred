"""Alfred configuration management.

Configuration precedence (highest to lowest):
- Runtime parameters
- Environment variables
- config.json file
- Default values
"""

import logging
from typing import Optional, Dict, Any
from pathlib import Path

from .settings import Config, ConfigError, ConfigValidationError, load_env
from .storage import (
    ensure_config_dir,
    read_config_file,
    write_config_file,
    merge_env_overrides,
    write_workspace_config,
)

logger = logging.getLogger("alfred.config")

# Module-level cache
_config_cache: Optional[Config] = None


def get_config(refresh: bool = False) -> Config:
    """Get the application configuration.

    Args:
        refresh: If True, rebuild configuration from sources

    Returns:
        Application configuration
    """
    global _config_cache

    if refresh or _config_cache is None:
        # Load environment variables from .env
        load_env()

        # Start with config.json as base
        file_config = read_config_file()

        # Merge with environment overrides
        merged_config = merge_env_overrides(file_config)

        # Create Config from merged data
        _config_cache = Config.from_dict(merged_config)

    return _config_cache


def set_config(config: Config) -> None:
    """Set and persist configuration.

    Args:
        config: Configuration to save
    """
    global _config_cache

    # Write to file
    write_config_file(config.to_dict())

    # Update cache
    _config_cache = config

    logger.info("Configuration saved")


def set_active_workspace(
    workspace_id: Optional[str] = None,
    team_id: Optional[str] = None,
    active_epic_id: Optional[str] = None,
) -> Config:
    """Set the active workspace configuration.

    Args:
        workspace_id: Workspace/instance ID
        team_id: Team/project ID
        active_epic_id: Default epic for new tasks

    Returns:
        Updated configuration
    """
    config = get_config()

    if workspace_id is not None:
        config.workspace_id = workspace_id
    if team_id is not None:
        config.team_id = team_id
    if active_epic_id is not None:
        config.active_epic_id = active_epic_id

    # Save to config.json
    set_config(config)

    # Also save to workspace.json
    workspace_data = {
        "platform": config.platform,
        "workspace_id": config.workspace_id,
        "team_id": config.team_id,
        "active_epic_id": config.active_epic_id,
    }
    write_workspace_config(workspace_data)

    logger.info(f"Active workspace updated: {workspace_id or config.workspace_id}")

    return config


def current_workspace() -> Dict[str, Any]:
    """Get current workspace information.

    Returns:
        Dictionary with workspace details
    """
    config = get_config()

    return {
        "platform": config.platform,
        "workspace_id": config.workspace_id,
        "team_id": config.team_id,
        "active_epic_id": config.active_epic_id,
        "has_linear_config": bool(config.linear_api_key),
        "has_jira_config": bool(config.jira_api_key and config.jira_url),
        "has_ai_config": bool(config.anthropic_api_key),
    }


# Export public API
__all__ = [
    "Config",
    "ConfigError",
    "ConfigValidationError",
    "get_config",
    "set_config",
    "set_active_workspace",
    "current_workspace",
]
