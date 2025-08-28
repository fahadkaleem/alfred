"""Task utilities and common functions."""

from alfred.config import get_config
from alfred.adapters.linear_adapter import LinearAdapter
from alfred.models.tasks import WorkspaceConfig


def load_workspace_config() -> WorkspaceConfig:
    """Load workspace configuration."""
    config = get_config()
    return WorkspaceConfig(
        api_key=config.linear_api_key,
        workspace_id=config.workspace_id,
        team_id=config.team_id,
    )


def get_linear_adapter() -> LinearAdapter:
    """Get configured Linear adapter."""
    config = load_workspace_config()
    return LinearAdapter(api_token=config.api_key)
