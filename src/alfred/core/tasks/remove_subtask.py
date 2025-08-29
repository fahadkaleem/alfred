"""Business logic for removing subtasks."""

import logging
from typing import Dict, Any
from alfred.adapters.linear_adapter import LinearAdapter
from alfred.models.tasks import to_alfred_task

logger = logging.getLogger(__name__)


def remove_subtask_logic(
    api_key: str,
    subtask_id: str,
    convert_to_task: bool = False,
) -> Dict[str, Any]:
    """
    Remove a subtask or convert it to a standalone task.

    Args:
        api_key: Linear API key
        subtask_id: ID of subtask to remove (Linear sub-issue ID)
        convert_to_task: Whether to convert to standalone task instead of deleting

    Returns:
        Dictionary with removal or conversion results
    """
    adapter = LinearAdapter(api_token=api_key)

    if convert_to_task:
        # Get the subtask details first
        subtask = adapter.get_task(subtask_id)
        subtask_alfred = to_alfred_task(subtask)

        # In Linear, converting a sub-issue to a regular issue means removing the parent relationship
        # We do this by updating the task to have no parent
        converted_task = adapter.update_task(
            subtask_id,
            {
                "parent_id": None  # Remove parent relationship
            },
        )

        result_task = to_alfred_task(converted_task)

        return {
            "converted": True,
            "task_id": subtask_id,
            "message": f"Subtask {subtask_id} successfully converted to standalone task",
            "task": result_task.model_dump(mode="json"),
        }
    else:
        # Simply delete the subtask (it's just a Linear issue)
        success = adapter.delete_task(subtask_id)

        if success:
            return {
                "deleted": True,
                "task_id": subtask_id,
                "message": f"Subtask {subtask_id} successfully deleted",
            }
        else:
            return {
                "deleted": False,
                "task_id": subtask_id,
                "error": "Failed to delete subtask",
            }
