"""Business logic for workspace information retrieval."""

from typing import Dict, Any
from alfred.adapters import get_adapter
from alfred.models.workspace import WorkspaceStatusResponse, WorkspaceInfo, TeamInfo
from alfred.config import current_workspace, get_config
from alfred.utils import get_logger

logger = get_logger("alfred.core.workspace.info")


async def get_workspace_info_logic() -> Dict[str, Any]:
    """
    Get current workspace configuration and status.

    Returns:
        Dictionary with current workspace settings and connection status
    """
    workspace_info = current_workspace()

    # Check if workspace is configured
    if not workspace_info.get("workspace_id") or not workspace_info.get("team_name"):
        response = WorkspaceStatusResponse(
            status="not_configured",
            message="No workspace configured. Use initialize_workspace to set up.",
            platform=workspace_info.get("platform", "linear"),
        )
        return response.model_dump(exclude_unset=True)

    # Check connection status
    has_api_key = False
    connection_status = "not_connected"

    if workspace_info.get("platform") == "linear":
        has_api_key = workspace_info.get("has_linear_config", False)
    elif workspace_info.get("platform") == "jira":
        has_api_key = workspace_info.get("has_jira_config", False)

    if has_api_key:
        # Try to validate connection
        config = get_config()
        try:
            if workspace_info.get("platform") == "linear" and config.linear_api_key:
                adapter = get_adapter(config)
                # Quick check - just see if we can get teams
                adapter.client.teams.get_all()
                connection_status = "connected"
        except Exception as e:
            logger.debug(f"Connection test failed: {e}")
            connection_status = "connection_failed"

    response = WorkspaceStatusResponse(
        status="configured",
        connection_status=connection_status,
        platform=workspace_info.get("platform"),
        workspace=WorkspaceInfo(
            id=workspace_info.get("workspace_id"),
            name=workspace_info.get("workspace_id"),  # Would need API call for name
        ),
        team=TeamInfo(
            id=workspace_info.get(
                "team_name"
            ),  # Using team_name as both id and name for now
            name=workspace_info.get("team_name"),
        ),
        active_epic_id=workspace_info.get("active_epic_id"),
        has_api_key=has_api_key,
        has_ai_config=workspace_info.get("has_ai_config", False),
    )
    return response.model_dump(exclude_unset=True)
