"""Business logic for renaming epics."""

from typing import Dict, Any
from alfred.adapters.linear_adapter import LinearAdapter
from alfred.adapters.base import (
    AuthError,
    APIConnectionError,
    NotFoundError,
    ValidationError,
)
from alfred.utils import get_logger

logger = get_logger("alfred.core.epics.rename")


async def rename_epic_logic(
    api_key: str, epic_id: str, new_name: str
) -> Dict[str, Any]:
    """
    Rename an existing epic (project) in Linear.

    Args:
        api_key: Linear API key
        epic_id: Epic ID to rename
        new_name: New name for the epic

    Returns:
        Dictionary with renamed epic details

    Raises:
        AuthError: If API key is missing or invalid
        NotFoundError: If epic doesn't exist
        ValidationError: If new name is invalid
        APIConnectionError: If network issues occur
    """
    if not api_key:
        raise AuthError(
            "LINEAR_API_KEY not configured. Please set it in environment variables or .env file"
        )

    if not epic_id or not epic_id.strip():
        raise ValidationError("Epic ID cannot be empty")

    if not new_name or not new_name.strip():
        raise ValidationError("New epic name cannot be empty")

    try:
        adapter = LinearAdapter(api_token=api_key)

        # First verify the epic exists and get its old name
        epics = adapter.get_epics(limit=100)

        target_epic = None
        old_name = None
        for epic in epics:
            if epic["id"] == epic_id.strip():
                target_epic = epic
                old_name = epic["name"]
                break

        if not target_epic:
            raise NotFoundError(f"Epic with ID '{epic_id}' not found in workspace")

        # Use the adapter's rename_epic method
        renamed_epic = adapter.rename_epic(epic_id, new_name)

        return {
            "status": "ok",
            "epic": renamed_epic,
            "message": f"Successfully renamed epic from '{old_name}' to '{renamed_epic['name']}'",
            "old_name": old_name,
        }

    except (NotFoundError, ValidationError, AuthError):
        raise
    except Exception as e:
        logger.error(f"Failed to rename epic: {e}")
        error_str = str(e).lower()
        if "401" in error_str or "unauthorized" in error_str:
            raise AuthError("Invalid Linear API key")
        elif "duplicate" in error_str or "already exists" in error_str:
            raise ValidationError(f"An epic with the name '{new_name}' already exists")
        raise APIConnectionError(f"Failed to rename epic: {e}")
