"""MCP tool wrapper for initialize_workspace."""

from alfred.mcp import mcp
from alfred.core.workspace.initialize import initialize_workspace_logic


@mcp.tool
async def initialize_workspace(workspace_id: str, team_name: str) -> dict:
    """
    Connect to platform (Linear/Jira) workspace and save configuration.

    This tool validates the platform API connection and saves the workspace
    configuration for future operations.

    Usage:
    - Use this tool when setting up Alfred for the first time
    - Use when switching to a different platform workspace or team
    - MUST have platform API key configured in environment variables
    - Both workspace_id and team_name are required and must be valid

    IMPORTANT:
    - This tool will overwrite any existing workspace configuration
    - The team_name must exist in the specified workspace
    - Connection validation happens automatically during initialization

    WARNING:
    - Tool will fail if platform API key is not set in environment
    - Tool will fail if team_name doesn't exist in the workspace
    - Tool will fail if platform API key is invalid or expired

    Parameters:
    workspace_id [string] (required) - Platform workspace/organization ID. This is typically
        your organization's identifier in your platform
    team_name [string] (required) - Platform team name. Must be a valid team name that exists
        in the specified workspace. You can get this from list_teams tool

    Returns:
    Dictionary with:
    - status: "ok" if successful
    - message: Success message
    - platform: Current platform (linear/jira) from configuration
    - workspace: Object with id and name
    - team: Object with id and name
    - config_path: Path where configuration was saved
    """
    config = mcp.state.config

    return await initialize_workspace_logic(
        workspace_id=workspace_id, team_name=team_name, config=config
    )
