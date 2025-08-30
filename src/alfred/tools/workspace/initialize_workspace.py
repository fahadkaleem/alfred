"""MCP tool wrapper for initialize_workspace."""

from alfred.mcp import mcp
from alfred.core.workspace.initialize import initialize_workspace_logic


@mcp.tool
async def initialize_workspace(workspace_id: str, team_id: str) -> dict:
    """
    Connect to Linear workspace and save configuration.

    This tool validates the Linear API connection and saves the workspace
    configuration for future operations.

    Usage:
    - Use this tool when setting up Alfred for the first time
    - Use when switching to a different Linear workspace or team
    - MUST have LINEAR_API_KEY configured in environment variables
    - Both workspace_id and team_id are required and must be valid

    IMPORTANT:
    - This tool will overwrite any existing workspace configuration
    - The team_id must exist in the specified workspace
    - Connection validation happens automatically during initialization

    WARNING:
    - Tool will fail if LINEAR_API_KEY is not set in environment
    - Tool will fail if team_id doesn't exist in the workspace
    - Tool will fail if Linear API key is invalid or expired

    Parameters:
    workspace_id [string] (required) - Linear workspace/organization ID. This is typically
        your organization's identifier in Linear
    team_id [string] (required) - Linear team ID. Must be a valid team ID that exists
        in the specified workspace. You can get this from list_teams tool

    Returns:
    Dictionary with:
    - status: "ok" if successful
    - message: Success message
    - platform: Always "linear" for this adapter
    - workspace: Object with id and name
    - team: Object with id and name
    - config_path: Path where configuration was saved
    """
    config = mcp.state["config"]

    return await initialize_workspace_logic(
        workspace_id=workspace_id, team_id=team_id, api_key=config.linear_api_key
    )
