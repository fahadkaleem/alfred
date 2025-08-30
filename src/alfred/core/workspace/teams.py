"""Business logic for team listing."""

from typing import Dict, Any
from alfred.adapters import get_adapter
from alfred.adapters.base import AuthError, APIConnectionError
from alfred.models.config import Config
from alfred.models.workspace import TeamsListResponse, TeamInfo
from alfred.utils import get_logger

logger = get_logger("alfred.core.workspace.teams")


async def list_teams_logic(config: Config) -> Dict[str, Any]:
    """
    List all available teams in the Linear workspace.

    Args:
        config: Alfred configuration object

    Returns:
        Dictionary with list of teams and their details

    Raises:
        AuthError: If API key is missing or invalid
        APIConnectionError: If network issues occur
    """
    try:
        adapter = get_adapter(config)
        teams = adapter.client.teams.get_all()

        # Linear API returns Dict[str, LinearTeam] where LinearTeam is a Pydantic model
        # We can directly access the attributes without defensive checks
        team_list = []
        for team_id, team in teams.items():
            # LinearTeam has: id, name, key, description (all properly typed)
            team_info = TeamInfo(
                id=team.id,
                name=team.name,
                description=team.description,  # Can be None, that's fine
                key=team.key,  # Can be None, that's fine
            )
            team_list.append(team_info)

        response = TeamsListResponse(status="ok", teams=team_list, count=len(team_list))
        # Serialize excluding None values for clean API responses
        return response.model_dump(exclude_none=True)

    except Exception as e:
        logger.error(f"Failed to list teams: {e}")
        error_str = str(e).lower()
        if "401" in error_str or "unauthorized" in error_str:
            raise AuthError("Invalid Linear API key")
        raise APIConnectionError(f"Failed to list teams: {e}")
