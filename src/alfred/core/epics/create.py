"""Business logic for creating epics."""

from typing import Dict, Any, Optional
from alfred.adapters import get_adapter
from alfred.models.config import Config
from alfred.adapters.base import AuthError, APIConnectionError, ValidationError
from alfred.utils import get_logger

logger = get_logger("alfred.core.epics.create")


async def create_epic_logic(
    config: Config, name: str, description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a new epic (project) in configured platform.

    Args:
        config: Alfred configuration object
        name: Epic name
        description: Optional epic description

    Returns:
        Dictionary with created epic details

    Raises:
        AuthError: If API key is missing or invalid
        ValidationError: If name is empty
        APIConnectionError: If network issues occur
    """
    if not name or not name.strip():
        raise ValidationError("Epic name cannot be empty")

    try:
        adapter = get_adapter(config)

        # Create epic via adapter
        epic = adapter.create_epic(name=name.strip(), description=description)

        # Return the created epic with success status
        return {
            "status": "ok",
            "epic": {
                "id": epic["id"],
                "name": epic["name"],
                "description": epic.get("description"),
                "url": epic.get("url"),
                "created_at": epic.get("created_at"),
                "updated_at": epic.get("updated_at"),
            },
            "message": f"Successfully created epic: {epic['name']}",
        }

    except ValidationError:
        raise
    except AuthError:
        raise
    except Exception as e:
        logger.error(f"Failed to create epic: {e}")
        error_str = str(e).lower()
        if "401" in error_str or "unauthorized" in error_str:
            raise AuthError("Invalid Linear API key")
        elif "duplicate" in error_str or "already exists" in error_str:
            raise ValidationError(f"An epic with the name '{name}' already exists")
        raise APIConnectionError(f"Failed to create epic: {e}")
