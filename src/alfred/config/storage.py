"""Configuration storage and persistence for Alfred."""

import os
import json
import logging
import tempfile
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger("alfred.config.storage")


def get_config_dir() -> Path:
    """Get the configuration directory path.

    Checks in order:
    1. ALFRED_CONFIG_DIR environment variable
    2. XDG_CONFIG_HOME/alfred (on Linux)
    3. ~/.alfred (default)

    Returns:
        Path to configuration directory
    """
    # Check for override
    config_dir_env = os.getenv("ALFRED_CONFIG_DIR")
    if config_dir_env:
        return Path(config_dir_env).expanduser().resolve()

    # Check XDG on Linux
    if os.name != "nt":  # Not Windows
        xdg_config = os.getenv("XDG_CONFIG_HOME")
        if xdg_config:
            return Path(xdg_config).expanduser() / "alfred"

    # Default to ~/.alfred
    return Path.home() / ".alfred"


def ensure_config_dir() -> Path:
    """Ensure configuration directory exists with proper permissions.

    Returns:
        Path to configuration directory
    """
    config_dir = get_config_dir()

    if not config_dir.exists():
        logger.info(f"Creating configuration directory: {config_dir}")
        config_dir.mkdir(parents=True, exist_ok=True)

        # Set restrictive permissions on POSIX systems
        if os.name != "nt":
            config_dir.chmod(0o700)

    return config_dir


def get_config_file_path() -> Path:
    """Get the path to config.json file.

    Returns:
        Path to config.json
    """
    return ensure_config_dir() / "config.json"


def read_config_file() -> Dict[str, Any]:
    """Read configuration from config.json file.

    Returns:
        Dictionary of configuration values, empty dict if file doesn't exist
        or is malformed.
    """
    config_file = get_config_file_path()

    if not config_file.exists():
        logger.debug(f"Config file does not exist: {config_file}")
        return {}

    try:
        with open(config_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            logger.debug(f"Loaded config from: {config_file}")
            return data if isinstance(data, dict) else {}
    except json.JSONDecodeError as e:
        # Backup corrupted file
        backup_path = config_file.with_suffix(
            f".json.bak.{datetime.now():%Y%m%d_%H%M%S}"
        )
        logger.warning(f"Config file is malformed, backing up to: {backup_path}")
        config_file.rename(backup_path)
        return {}
    except Exception as e:
        logger.error(f"Error reading config file: {e}")
        return {}


def write_config_file(config_data: Dict[str, Any]) -> None:
    """Write configuration to config.json file atomically.

    Args:
        config_data: Configuration dictionary to write
    """
    config_file = get_config_file_path()
    config_dir = config_file.parent

    # Ensure directory exists
    ensure_config_dir()

    # Filter out None values and empty strings
    filtered_data = {k: v for k, v in config_data.items() if v is not None and v != ""}

    # Write to temporary file first (atomic write)
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=config_dir, delete=False, suffix=".tmp"
        ) as tmp_file:
            json.dump(filtered_data, tmp_file, indent=2, sort_keys=True)
            tmp_path = Path(tmp_file.name)

        # Set restrictive permissions on POSIX systems
        if os.name != "nt":
            tmp_path.chmod(0o600)

        # Atomically replace the config file
        tmp_path.replace(config_file)
        logger.debug(f"Config written to: {config_file}")

    except Exception as e:
        logger.error(f"Error writing config file: {e}")
        # Clean up temp file if it exists
        if "tmp_path" in locals() and tmp_path.exists():
            tmp_path.unlink()
        raise


def merge_env_overrides(base_config: Dict[str, Any]) -> Dict[str, Any]:
    """Merge environment variable overrides into base configuration.

    Environment variables take precedence over file-based config.

    Args:
        base_config: Base configuration from file

    Returns:
        Merged configuration with environment overrides
    """
    from .settings import ENV_VAR_MAPPING

    merged = base_config.copy()

    for env_var, config_key in ENV_VAR_MAPPING.items():
        env_value = os.getenv(env_var)
        if env_value is not None and env_value.strip():
            # Convert types as needed
            if config_key in [
                "max_tokens",
                "auto_decompose_threshold",
                "default_subtask_count",
            ]:
                try:
                    merged[config_key] = int(env_value)
                except ValueError:
                    logger.warning(f"Invalid integer value for {env_var}: {env_value}")
            elif config_key == "temperature":
                try:
                    merged[config_key] = float(env_value)
                except ValueError:
                    logger.warning(f"Invalid float value for {env_var}: {env_value}")
            else:
                merged[config_key] = env_value.strip()

    return merged


def get_workspace_file_path() -> Path:
    """Get the path to workspace.json file.

    Returns:
        Path to workspace.json
    """
    return ensure_config_dir() / "workspace.json"


def read_workspace_config() -> Dict[str, Any]:
    """Read workspace configuration from workspace.json.

    Returns:
        Dictionary of workspace configuration
    """
    workspace_file = get_workspace_file_path()

    if not workspace_file.exists():
        return {}

    try:
        with open(workspace_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error reading workspace file: {e}")
        return {}


def write_workspace_config(workspace_data: Dict[str, Any]) -> None:
    """Write workspace configuration to workspace.json.

    Args:
        workspace_data: Workspace configuration to write
    """
    workspace_file = get_workspace_file_path()

    try:
        with open(workspace_file, "w", encoding="utf-8") as f:
            json.dump(workspace_data, f, indent=2)

        # Set restrictive permissions on POSIX systems
        if os.name != "nt":
            workspace_file.chmod(0o600)

        logger.debug(f"Workspace config written to: {workspace_file}")
    except Exception as e:
        logger.error(f"Error writing workspace file: {e}")
        raise
