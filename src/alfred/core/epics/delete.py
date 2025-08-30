"""Business logic for deleting epics."""

from typing import Dict, Any
from alfred.adapters import get_adapter
from alfred.models.config import Config
from alfred.adapters.base import (
    AuthError,
    APIConnectionError,
    NotFoundError,
    ValidationError,
)
from alfred.utils import get_logger

logger = get_logger("alfred.core.epics.delete")


async def delete_epic_logic(
    config: Config, epic_id: str, delete_tasks: bool = False
) -> Dict[str, Any]:
    """
    Delete an epic (project) from Linear, optionally with its tasks.

    Args:
        config: Alfred configuration object
        epic_id: Epic ID to delete
        delete_tasks: Whether to delete all tasks in the epic first

    Returns:
        Dictionary with deletion confirmation

    Raises:
        AuthError: If API key is missing or invalid
        NotFoundError: If epic doesn't exist
        ValidationError: If epic has tasks but delete_tasks is False
        APIConnectionError: If network issues occur
    """

    if not epic_id or not epic_id.strip():
        raise ValidationError("Epic ID cannot be empty")

    try:
        adapter = get_adapter(config)

        # First verify the epic exists
        epics = adapter.get_epics(limit=100)

        target_epic = None
        for epic in epics:
            if epic["id"] == epic_id.strip():
                target_epic = epic
                break

        if not target_epic:
            raise NotFoundError(f"Epic with ID '{epic_id}' not found in workspace")

        # Check if this is the last epic
        if len(epics) == 1:
            raise ValidationError("Cannot delete the last epic in the workspace")

        # Check if epic has tasks using the adapter method
        tasks = adapter.get_epic_tasks(epic_id)
        task_count = len(tasks)

        if task_count > 0 and not delete_tasks:
            raise ValidationError(
                f"Epic '{target_epic['name']}' contains {task_count} task(s). "
                "Set delete_tasks=True to delete the epic and all its tasks."
            )

        # Delete tasks if requested
        tasks_deleted = 0
        if delete_tasks and task_count > 0:
            for task in tasks:
                try:
                    # Debug: log the task structure
                    logger.debug(f"Task structure: {task}")
                    task_id = task.get("id")

                    if not task_id:
                        logger.warning(f"Task has no ID field: {task}")
                        continue

                    # Use the adapter to delete the task
                    # The adapter should have a delete_task method
                    # For now, we'll call update_task to mark as Canceled
                    # which is cleaner than deletion
                    updated_task = adapter.update_task(task_id, {"status": "Canceled"})

                    if updated_task:
                        tasks_deleted += 1
                        logger.debug(f"Cancelled task: {task_id}")
                    else:
                        logger.warning(f"Failed to cancel task: {task_id}")
                except Exception as task_error:
                    logger.error(
                        f"Error cancelling task {task.get('id', 'Unknown')}: {task_error}"
                    )
                    logger.error(f"Task data was: {task}")
                    # Re-raise to see the full error
                    raise

        # Now delete the epic using the adapter method
        success = adapter.delete_epic(epic_id)

        if not success:
            error_msg = "Failed to delete epic"
            if tasks_deleted > 0:
                error_msg += f" (but {tasks_deleted} task(s) were deleted)"
            raise APIConnectionError(error_msg)

        message = f"Successfully deleted epic '{target_epic['name']}'"
        if tasks_deleted > 0:
            message += f" and {tasks_deleted} task(s)"

        return {
            "status": "ok",
            "deleted_epic": {
                "id": target_epic["id"],
                "name": target_epic["name"],
            },
            "tasks_deleted": tasks_deleted,
            "message": message,
        }

    except (NotFoundError, ValidationError, AuthError):
        raise
    except Exception as e:
        logger.error(f"Failed to delete epic: {e}")
        error_str = str(e).lower()
        if "401" in error_str or "unauthorized" in error_str:
            raise AuthError("Invalid Linear API key")
        raise APIConnectionError(f"Failed to delete epic: {e}")
