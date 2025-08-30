"""Business logic for workspace initialization."""

from typing import Dict, Any
from alfred.adapters import get_adapter
from alfred.adapters.base import AuthError, ValidationError, APIConnectionError
from alfred.models.config import Config
from alfred.models.workspace import WorkspaceInitResponse, WorkspaceInfo, TeamInfo
from alfred.config import set_active_workspace
from alfred.utils import get_logger

logger = get_logger("alfred.core.workspace.initialize")


async def initialize_workspace_logic(
    workspace_id: str, team_name: str, config: Config
) -> Dict[str, Any]:
    """
    Pure business logic for workspace initialization.

    Args:
        workspace_id: Platform workspace/organization ID
        team_name: Platform team name (e.g., "Engineering", "Design")
        config: Alfred configuration object

    Returns:
        Dictionary with status and workspace details

    Raises:
        ValidationError: If inputs are invalid
        AuthError: If API key is invalid
        APIConnectionError: If network issues occur
    """
    # Input validation
    if not workspace_id or not team_name:
        raise ValidationError("Both workspace_id and team_name are required")

    workspace_id = workspace_id.strip()
    team_name = team_name.strip()

    logger.info(f"Initializing workspace {workspace_id} with team {team_name}")

    # Test connection and validate team
    try:
        adapter = get_adapter(config)

        # Get all teams to validate
        logger.debug("Fetching teams from Linear")
        teams = adapter.client.teams.get_all()

        team_found = False
        team_id = None
        workspace_name = workspace_id  # Default to ID if we can't get name

        for tid, team in teams.items():
            # LinearTeam is a Pydantic model with id and name attributes
            if team.name == team_name:
                team_found = True
                team_id = team.id  # Get the ID for internal use
                # Workspace name is not exposed by Linear API, use the ID
                break

        if not team_found:
            # List available teams for helpful error message
            available_teams = [{"id": tid, "name": t.name} for tid, t in teams.items()][
                :5
            ]  # Show first 5
            raise ValidationError(
                f"Team '{team_name}' not found. Available teams: {available_teams}"
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
            workspace_id=workspace_id, team_name=team_name
        )
        logger.info(f"Workspace configuration saved successfully")
    except Exception as e:
        logger.error(f"Failed to save workspace configuration: {e}")
        raise ValidationError(f"Failed to save configuration: {e}")

    # Return success response using Pydantic
    response = WorkspaceInitResponse(
        status="ok",
        message="Workspace initialized successfully",
        platform="linear",
        workspace=WorkspaceInfo(id=workspace_id, name=workspace_name),
        team=TeamInfo(id=team_id, name=team_name),
        config_path=".alfred/config.json",
    )
    return response.model_dump()
