"""Business logic for switching active epic."""

from typing import Dict, Any
from alfred.adapters import get_adapter
from alfred.models.config import Config
from alfred.adapters.base import AuthError, APIConnectionError, NotFoundError
from alfred.config import get_config, set_config
from alfred.utils import get_logger

logger = get_logger("alfred.core.epics.switch")


async def switch_epic_logic(config: Config, epic_id: str) -> Dict[str, Any]:
    """
    Switch the active epic context for task operations.

    Args:
        config: Alfred configuration object
        epic_id: Epic ID to switch to

    Returns:
        Dictionary with switch confirmation and epic details

    Raises:
        AuthError: If API key is missing or invalid
        NotFoundError: If epic doesn't exist
        APIConnectionError: If network issues occur
    """

    if not epic_id or not epic_id.strip():
        raise ValueError("Epic ID cannot be empty")

    try:
        adapter = get_adapter(config)

        # Verify the epic exists by fetching all epics
        epics = adapter.get_epics(limit=100)

        target_epic = None
        for epic in epics:
            if epic["id"] == epic_id.strip():
                target_epic = epic
                break

        if not target_epic:
            raise NotFoundError(f"Epic with ID '{epic_id}' not found in workspace")

        # Update the config with the new active epic
        config = get_config()
        previous_epic_id = config.active_epic_id

        # Update the active epic ID
        config.active_epic_id = epic_id.strip()

        # Save the updated config
        set_config(config)

        logger.info(f"Switched active epic to: {target_epic['name']} ({epic_id})")

        return {
            "status": "ok",
            "epic": {
                "id": target_epic["id"],
                "name": target_epic["name"],
                "description": target_epic.get("description"),
                "url": target_epic.get("url"),
            },
            "message": f"Successfully switched to epic: {target_epic['name']}",
            "previous_epic_id": previous_epic_id,
        }

    except NotFoundError:
        raise
    except AuthError:
        raise
    except Exception as e:
        logger.error(f"Failed to switch epic: {e}")
        error_str = str(e).lower()
        if "401" in error_str or "unauthorized" in error_str:
            raise AuthError("Invalid API key")
        raise APIConnectionError(f"Failed to switch epic: {e}")
