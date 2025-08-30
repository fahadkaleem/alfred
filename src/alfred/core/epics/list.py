"""Business logic for listing epics."""

from typing import Dict, Any
from alfred.adapters import get_adapter
from alfred.models.config import Config
from alfred.adapters.base import AuthError, APIConnectionError
from alfred.models.workspace import ProjectsListResponse, ProjectInfo
from alfred.utils import get_logger

logger = get_logger("alfred.core.epics.list")


async def list_epics_logic(config: Config) -> Dict[str, Any]:
    """
    List all epics (projects) in configured platform workspace.

    Args:
        config: Alfred configuration object

    Returns:
        Dictionary with list of epics and their details

    Raises:
        AuthError: If API key is missing or invalid
        APIConnectionError: If network issues occur
    """
    try:
        adapter = get_adapter(config)

        # Get epics - adapter returns List[EpicDict]
        epics = adapter.get_epics(limit=100)

        # Convert to Pydantic models
        epic_list = []
        for epic in epics:
            # EpicDict from adapter has: id, name, description, url (all can be None)
            epic_info = ProjectInfo(
                id=epic["id"],
                name=epic["name"],
                description=epic.get("description"),
                url=epic.get("url"),
            )
            epic_list.append(epic_info)

        response = ProjectsListResponse(
            status="ok", projects=epic_list, count=len(epic_list)
        )
        # Serialize excluding None values for clean API responses
        return response.model_dump(exclude_none=True)

    except AuthError:
        raise
    except Exception as e:
        logger.error(f"Failed to list epics: {e}")
        error_str = str(e).lower()
        if "401" in error_str or "unauthorized" in error_str:
            raise AuthError("Invalid Linear API key")
        raise APIConnectionError(f"Failed to list epics: {e}")
