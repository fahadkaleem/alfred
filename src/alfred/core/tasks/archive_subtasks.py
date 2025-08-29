"""Business logic for archiving all subtasks under parent tasks."""

import logging
from typing import Dict, Any
from alfred.adapters.linear_adapter import LinearAdapter
from alfred.models.tasks import to_alfred_task, TaskStatus

logger = logging.getLogger(__name__)


def archive_subtasks_logic(
    api_key: str,
    parent_task_id: str,
    status: str = "done",
) -> Dict[str, Any]:
    """
    Mark all subtasks of a parent task as completed/archived.

    Args:
        api_key: Linear API key
        parent_task_id: ID of parent task whose subtasks to archive
        status: Status to set for subtasks ("done", "cancelled")

    Returns:
        Dictionary with archiving results
    """
    adapter = LinearAdapter(api_token=api_key)

    # Get all subtasks (children) of the parent task
    try:
        subtasks = adapter.get_task_children(parent_task_id)
    except Exception as e:
        return {
            "error": f"Could not fetch subtasks for task {parent_task_id}: {str(e)}",
            "archived_count": 0,
        }

    if not subtasks:
        return {
            "message": f"No subtasks found for task {parent_task_id}",
            "archived_count": 0,
            "parent_task_id": parent_task_id,
        }

    # Map status to Linear status using TaskStatus enum
    if status.lower() in ["done", "completed", "archived"]:
        task_status = TaskStatus.DONE
    elif status.lower() == "cancelled":
        task_status = TaskStatus.CANCELLED
    else:
        task_status = TaskStatus.DONE  # Default to done

    linear_status = task_status.to_linear()

    archived_subtasks = []
    failed_subtasks = []

    # Update each subtask to the specified status
    for subtask in subtasks:
        try:
            subtask_id = subtask["id"]
            alfred_subtask = to_alfred_task(subtask)

            # Skip if already in target status
            if alfred_subtask.status == task_status:
                continue

            # Update subtask status
            updated_subtask = adapter.update_task(subtask_id, {"status": linear_status})

            updated_alfred = to_alfred_task(updated_subtask)
            archived_subtasks.append(
                {
                    "id": subtask_id,
                    "title": updated_alfred.title,
                    "old_status": alfred_subtask.status.value,
                    "new_status": task_status.value,
                }
            )

        except Exception as e:
            failed_subtasks.append(
                {
                    "id": subtask.get("id", "unknown"),
                    "title": subtask.get("title", "Unknown"),
                    "error": str(e),
                }
            )

    return {
        "parent_task_id": parent_task_id,
        "archived_count": len(archived_subtasks),
        "failed_count": len(failed_subtasks),
        "total_subtasks": len(subtasks),
        "archived_subtasks": archived_subtasks,
        "failed_subtasks": failed_subtasks,
        "status_applied": linear_status,
        "message": f"Successfully archived {len(archived_subtasks)} of {len(subtasks)} subtasks for task {parent_task_id}",
    }
