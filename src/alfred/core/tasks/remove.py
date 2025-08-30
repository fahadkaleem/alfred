"""Business logic for removing tasks."""

import logging
from typing import Dict, Any, List
from alfred.adapters import get_adapter
from alfred.models.config import Config

logger = logging.getLogger(__name__)


def remove_task_logic(
    config: Config,
    task_ids: List[str],
    cascade_delete: bool = False,
) -> Dict[str, Any]:
    """
    Remove tasks from Linear.

    Args:
        config: Alfred configuration object
        task_ids: List of task IDs to remove
        cascade_delete: Whether to delete subtasks if they exist

    Returns:
        Dictionary with removal results
    """
    adapter = get_adapter(config)

    removed_tasks = []
    failed_tasks = []

    for task_id in task_ids:
        try:
            # Check if task has subtasks (children)
            children = adapter.get_task_children(task_id)

            if children and not cascade_delete:
                failed_tasks.append(
                    {
                        "task_id": task_id,
                        "error": f"Task has {len(children)} subtasks. Use cascade_delete=True to delete them too.",
                    }
                )
                continue

            # If cascade delete, remove all children first
            if children and cascade_delete:
                for child in children:
                    try:
                        adapter.delete_task(child["id"])
                    except Exception as e:
                        logger.warning(f"Could not delete subtask {child['id']}: {e}")

            # Delete the main task
            success = adapter.delete_task(task_id)

            if success:
                removed_tasks.append(
                    {
                        "task_id": task_id,
                        "removed": True,
                        "subtasks_deleted": len(children) if cascade_delete else 0,
                    }
                )
            else:
                failed_tasks.append(
                    {"task_id": task_id, "error": "Task deletion returned false"}
                )

        except Exception as e:
            failed_tasks.append({"task_id": task_id, "error": str(e)})

    return {
        "removed_count": len(removed_tasks),
        "failed_count": len(failed_tasks),
        "removed_tasks": removed_tasks,
        "failed_tasks": failed_tasks,
        "total_processed": len(task_ids),
    }
