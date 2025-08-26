"""Business logic for project/epic listing."""

from typing import Dict, Any
from alfred.adapters.linear_adapter import LinearAdapter
from alfred.adapters.base import AuthError, APIConnectionError
from alfred.models.workspace import ProjectsListResponse, ProjectInfo
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

        # Get projects/epics - adapter returns List[EpicDict]
        projects = adapter.get_epics(limit=100)

        # Convert to Pydantic models
        project_list = []
        for project in projects:
            # EpicDict from adapter has: id, name, description, url (all can be None)
            project_info = ProjectInfo(
                id=project["id"],
                name=project["name"],
                description=project.get("description"),
                url=project.get("url"),
            )
            project_list.append(project_info)

        response = ProjectsListResponse(
            status="ok", projects=project_list, count=len(project_list)
        )
        # Serialize excluding None values for clean API responses
        return response.model_dump(exclude_none=True)

    except AuthError:
        raise
    except Exception as e:
        logger.error(f"Failed to list projects: {e}")
        error_str = str(e).lower()
        if "401" in error_str or "unauthorized" in error_str:
            raise AuthError("Invalid Linear API key")
        raise APIConnectionError(f"Failed to list projects: {e}")
