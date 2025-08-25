"""Business logic for team listing."""

from typing import Dict, Any, List
from alfred.adapters.linear_adapter import LinearAdapter
from alfred.adapters.base import AuthError, APIConnectionError
from alfred.utils import get_logger

logger = get_logger("alfred.core.workspace.teams")


async def list_teams_logic(api_key: str) -> Dict[str, Any]:
    """
    List all available teams in the Linear workspace.

    Args:
        api_key: Linear API key

    Returns:
        Dictionary with list of teams and their details

    Raises:
        AuthError: If API key is missing or invalid
        APIConnectionError: If network issues occur
    """
    if not api_key:
        raise AuthError(
            "LINEAR_API_KEY not configured. Please set it in environment variables or .env file"
        )

    try:
        adapter = LinearAdapter(api_token=api_key)
        teams = adapter.client.teams.get_all()

        # Format teams for response
        team_list: List[Dict[str, Any]] = []
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
