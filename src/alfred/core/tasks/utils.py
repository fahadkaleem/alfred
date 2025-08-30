"""Task utilities and common functions."""

from alfred.config import get_config
from alfred.adapters import get_adapter
from alfred.models.config import Config
from alfred.models.tasks import WorkspaceConfig


def load_workspace_config() -> WorkspaceConfig:
    """Load workspace configuration."""
    config = get_config()
    return WorkspaceConfig(
        api_key=config.linear_api_key,
        workspace_id=config.workspace_id,
        team_name=config.team_name,
    )


def get_task_adapter():
    """Get configured task adapter."""
    config = get_config()
    return get_adapter(config)
