"""Workspace management tools for Alfred MCP server."""

from typing import Dict, Any, Optional
from alfred.adapters.linear_adapter import LinearAdapter
from alfred.adapters.base import (
    AuthError,
    ValidationError,
    APIConnectionError,
    NotFoundError,
)
from alfred.config import get_config, set_active_workspace, current_workspace
from alfred.utils import get_logger

logger = get_logger("alfred.tools.workspace")


def register(server) -> int:
    """
    Register workspace management tools with the MCP server.

    Args:
        server: FastMCP server instance

    Returns:
        Number of tools registered
    """

    @server.tool
    async def initialize_workspace(workspace_id: str, team_id: str) -> dict:
        """
        Connect to Linear workspace and save configuration.

        This tool validates the Linear API connection and saves the workspace
        configuration for future operations.

        Args:
            workspace_id: Linear workspace/organization ID
            team_id: Linear team ID

        Returns:
            Dictionary with status and workspace details

        Raises:
            ValidationError: If inputs are invalid
            AuthError: If Linear API key is missing or invalid
        """
        return await _initialize_workspace_impl(workspace_id, team_id)

    @server.tool
    async def get_workspace_info() -> dict:
        """
        Get current workspace configuration and status.

        Returns:
            Dictionary with current workspace settings and connection status
        """
        return await _get_workspace_info_impl()

    @server.tool
    async def list_teams() -> dict:
        """
        List all available teams in the Linear workspace.

        Returns:
            Dictionary with list of teams and their details

        Raises:
            AuthError: If Linear API key is missing or invalid
        """
        return await _list_teams_impl()

    @server.tool
    async def list_projects() -> dict:
        """
        List all projects (epics) in the Linear workspace.

        Returns:
            Dictionary with list of projects and their details

        Raises:
            AuthError: If Linear API key is missing or invalid
        """
        return await _list_projects_impl()

    # Return number of tools registered
    return 4


# Implementation functions
async def _initialize_workspace_impl(workspace_id: str, team_id: str) -> Dict[str, Any]:
    """Implementation for initialize_workspace tool."""

    # Input validation
    if not workspace_id or not team_id:
        raise ValidationError("Both workspace_id and team_id are required")

    workspace_id = workspace_id.strip()
    team_id = team_id.strip()

    logger.info(f"Initializing workspace {workspace_id} with team {team_id}")

    # Get configuration
    config = get_config()

    # Check for Linear API key
    if not config.linear_api_key:
        raise AuthError(
            "LINEAR_API_KEY not configured. Please set it in environment variables or .env file"
        )

    # Test connection and validate team
    try:
        adapter = LinearAdapter(api_token=config.linear_api_key)

        # Get all teams to validate
        logger.debug("Fetching teams from Linear")
        teams = adapter.client.teams.get_all()

        team_found = False
        team_name = None
        workspace_name = workspace_id  # Default to ID if we can't get name

        for tid, team in teams.items():
            if team.id == team_id or tid == team_id:
                team_found = True
                team_name = team.name

                # Try to get organization/workspace name
                if hasattr(team, "organization"):
                    org = team.organization
                    if hasattr(org, "id") and org.id == workspace_id:
                        if hasattr(org, "name"):
                            workspace_name = org.name
                    # Note: Some Linear setups might not expose org ID
                    # In that case, we trust the user-provided workspace_id
                break

        if not team_found:
            # List available teams for helpful error message
            available_teams = [{"id": tid, "name": t.name} for tid, t in teams.items()][
                :5
            ]  # Show first 5
            raise ValidationError(
                f"Team '{team_id}' not found. Available teams: {available_teams}"
            )

    except AuthError:
        raise
    except ValidationError:
        raise
    except APIConnectionError as e:
        logger.error(f"Network error connecting to Linear: {e}")
        raise
    except Exception as e:
        logger.error(f"Failed to connect to Linear: {e}")
        # Check if it's an auth error from the Linear client
        error_str = str(e).lower()
        if "401" in error_str or "unauthorized" in error_str or "api_key" in error_str:
            raise AuthError("Invalid Linear API key")
        raise APIConnectionError(f"Failed to connect to Linear: {e}")

    # Save configuration
    try:
        updated_config = set_active_workspace(
            workspace_id=workspace_id, team_id=team_id
        )
        logger.info(f"Workspace configuration saved successfully")
    except Exception as e:
        logger.error(f"Failed to save workspace configuration: {e}")
        raise ValidationError(f"Failed to save configuration: {e}")

    # Return success response
    return {
        "status": "ok",
        "message": "Workspace initialized successfully",
        "platform": "linear",
        "workspace": {"id": workspace_id, "name": workspace_name},
        "team": {"id": team_id, "name": team_name},
        "config_path": ".alfred/config.json",
    }


async def _get_workspace_info_impl() -> Dict[str, Any]:
    """Get current workspace configuration."""

    workspace_info = current_workspace()

    # Check if workspace is configured
    if not workspace_info.get("workspace_id") or not workspace_info.get("team_id"):
        return {
            "status": "not_configured",
            "message": "No workspace configured. Use initialize_workspace to set up.",
            "platform": workspace_info.get("platform", "linear"),
        }

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
                adapter = LinearAdapter(api_token=config.linear_api_key)
                # Quick check - just see if we can get teams
                adapter.client.teams.get_all()
                connection_status = "connected"
        except Exception as e:
            logger.debug(f"Connection test failed: {e}")
            connection_status = "connection_failed"

    return {
        "status": "configured",
        "connection_status": connection_status,
        "platform": workspace_info.get("platform"),
        "workspace": {
            "id": workspace_info.get("workspace_id"),
            "name": workspace_info.get("workspace_id"),  # Would need API call for name
        },
        "team": {
            "id": workspace_info.get("team_id"),
            "name": workspace_info.get("team_id"),  # Would need API call for name
        },
        "active_epic_id": workspace_info.get("active_epic_id"),
        "has_api_key": has_api_key,
        "has_ai_config": workspace_info.get("has_ai_config", False),
    }


async def _list_teams_impl() -> Dict[str, Any]:
    """List available teams."""

    config = get_config()

    if not config.linear_api_key:
        raise AuthError(
            "LINEAR_API_KEY not configured. Please set it in environment variables or .env file"
        )

    try:
        adapter = LinearAdapter(api_token=config.linear_api_key)
        teams = adapter.client.teams.get_all()

        # Format teams for response
        team_list = []
        for tid, team in teams.items():
            team_info = {
                "id": team.id if hasattr(team, "id") else tid,
                "name": team.name if hasattr(team, "name") else "Unknown",
            }

            # Add optional fields if available
            if hasattr(team, "description"):
                team_info["description"] = team.description
            if hasattr(team, "key"):
                team_info["key"] = team.key

            team_list.append(team_info)

        return {"status": "ok", "teams": team_list, "count": len(team_list)}

    except Exception as e:
        logger.error(f"Failed to list teams: {e}")
        error_str = str(e).lower()
        if "401" in error_str or "unauthorized" in error_str:
            raise AuthError("Invalid Linear API key")
        raise APIConnectionError(f"Failed to list teams: {e}")


async def _list_projects_impl() -> Dict[str, Any]:
    """List available projects/epics."""

    config = get_config()

    if not config.linear_api_key:
        raise AuthError(
            "LINEAR_API_KEY not configured. Please set it in environment variables or .env file"
        )

    try:
        adapter = LinearAdapter(api_token=config.linear_api_key)

        # Get projects/epics
        projects = adapter.get_epics(limit=100)

        # Format projects for response
        project_list = []
        for project in projects:
            project_info = {
                "id": project.get("id"),
                "name": project.get("name"),
            }

            # Add optional fields
            if project.get("description"):
                project_info["description"] = project.get("description")
            if project.get("url"):
                project_info["url"] = project.get("url")

            project_list.append(project_info)

        return {"status": "ok", "projects": project_list, "count": len(project_list)}

    except AuthError:
        raise
    except Exception as e:
        logger.error(f"Failed to list projects: {e}")
        error_str = str(e).lower()
        if "401" in error_str or "unauthorized" in error_str:
            raise AuthError("Invalid Linear API key")
        raise APIConnectionError(f"Failed to list projects: {e}")
