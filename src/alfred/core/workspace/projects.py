"""Business logic for project/epic listing."""

from typing import Dict, Any, List
from alfred.adapters.linear_adapter import LinearAdapter
from alfred.adapters.base import AuthError, APIConnectionError
from alfred.utils import get_logger

logger = get_logger("alfred.core.workspace.projects")


async def list_projects_logic(api_key: str) -> Dict[str, Any]:
    """
    List all projects (epics) in the Linear workspace.

    Args:
        api_key: Linear API key

    Returns:
        Dictionary with list of projects and their details

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

        # Get projects/epics
        projects = adapter.get_epics(limit=100)

        # Format projects for response
        project_list: List[Dict[str, Any]] = []
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
