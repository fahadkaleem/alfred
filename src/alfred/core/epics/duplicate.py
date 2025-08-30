"""Business logic for duplicating epics."""

from typing import Dict, Any, Optional
from alfred.adapters import get_adapter
from alfred.models.config import Config
from alfred.adapters.base import (
    AuthError,
    APIConnectionError,
    NotFoundError,
    ValidationError,
)
from alfred.utils import get_logger

logger = get_logger("alfred.core.epics.duplicate")


async def duplicate_epic_logic(
    config: Config, epic_id: str, new_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Duplicate an epic (project) with all its tasks in Linear.

    Args:
        config: Alfred configuration object
        epic_id: Epic ID to duplicate
        new_name: Optional name for the new epic (defaults to "Original Name (Copy)")

    Returns:
        Dictionary with new epic details and copy statistics

    Raises:
        AuthError: If API key is missing or invalid
        NotFoundError: If epic doesn't exist
        APIConnectionError: If network issues occur
    """

    if not epic_id or not epic_id.strip():
        raise ValidationError("Epic ID cannot be empty")

    try:
        adapter = get_adapter(config)

        # Get the source epic
        epics = adapter.get_epics(limit=100)

        source_epic = None
        for epic in epics:
            if epic["id"] == epic_id.strip():
                source_epic = epic
                break

        if not source_epic:
            raise NotFoundError(f"Epic with ID '{epic_id}' not found in workspace")

        # Generate new epic name if not provided
        if not new_name:
            new_name = f"{source_epic['name']} (Copy)"

        # Create the new epic with the same description
        new_epic = adapter.create_epic(
            name=new_name, description=source_epic.get("description")
        )

        if not new_epic:
            raise APIConnectionError("Failed to create duplicate epic")

        # Get tasks from source epic using the adapter
        source_tasks = adapter.get_epic_tasks(epic_id)
        tasks_created = 0

        # Copy each task to the new epic
        for task in source_tasks:
            try:
                # Create task in new epic using the adapter
                # The adapter's create_task method should handle epic assignment
                new_task = adapter.create_task(
                    title=task["title"],
                    description=task.get("description"),
                    epic_id=new_epic["id"],
                    priority=task.get("priority", "medium"),
                    # Note: Labels would need to be handled separately if needed
                )

                if new_task:
                    tasks_created += 1
                    logger.debug(f"Copied task: {task['title']}")
                else:
                    logger.warning(f"Failed to copy task: {task['title']}")

            except Exception as task_error:
                logger.warning(
                    f"Error copying task '{task.get('title', 'Unknown')}': {task_error}"
                )
                continue

        return {
            "status": "ok",
            "epic": {
                "id": new_epic["id"],
                "name": new_epic["name"],
                "description": new_epic.get("description"),
                "url": new_epic.get("url"),
            },
            "source_epic": {
                "id": source_epic["id"],
                "name": source_epic["name"],
            },
            "tasks_copied": tasks_created,
            "message": f"Successfully duplicated epic '{source_epic['name']}' as '{new_epic['name']}' with {tasks_created} task(s)",
        }

    except (NotFoundError, ValidationError, AuthError):
        raise
    except Exception as e:
        logger.error(f"Failed to duplicate epic: {e}")
        error_str = str(e).lower()
        if "401" in error_str or "unauthorized" in error_str:
            raise AuthError("Invalid API key")
        raise APIConnectionError(f"Failed to duplicate epic: {e}")
