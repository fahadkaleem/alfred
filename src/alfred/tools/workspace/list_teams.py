"""MCP tool wrapper for list_teams."""

from alfred.mcp import mcp
from alfred.core.workspace.teams import list_teams_logic


@mcp.tool
async def list_teams() -> dict:
    """
    List all available teams in the configured platform (Linear/Jira) workspace.

    This tool retrieves all teams accessible with the current API key,
    useful for discovering team IDs needed for workspace initialization.

    Usage:
    - Use this tool before initialize_workspace to discover available team IDs
    - Use to verify which teams you have access to
    - Use to get team details like names and keys
    - MUST have API key configured in environment variables for your platform

    IMPORTANT:
    - Requires valid API key in environment for your configured platform
    - Returns all teams accessible to the API key
    - No filtering or pagination parameters available

    WARNING:
    - Tool will fail if API key is not set in environment for your platform
    - Tool will fail if API key is invalid or expired

    Returns:
    Dictionary with:
    - status: "ok" if successful
    - teams: Array of team objects, each containing:
      - id: Team ID (use this for initialize_workspace)
      - name: Human-readable team name
      - description: Team description (if available)
      - key: Team key/abbreviation (if available)
    - count: Total number of teams returned
    """
    config = mcp.state.config

    return await list_teams_logic(config=config)
