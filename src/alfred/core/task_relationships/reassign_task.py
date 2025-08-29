"""Business logic for reassigning tasks between epics."""

from typing import Dict, Any
from alfred.adapters.linear_adapter import LinearAdapter
from alfred.adapters.base import NotFoundError
from .models import ReassignTaskResult


def reassign_task_logic(
    api_key: str, task_id: str, target_epic_id: str
) -> Dict[str, Any]:
    """
    Move a task from one epic to another.

    Args:
        api_key: Linear API key
        task_id: ID of task to reassign
        target_epic_id: ID of target epic

    Returns:
        ReassignTaskResult as dict
    """
    adapter = LinearAdapter(api_token=api_key)

    try:
        current_task = adapter.get_task(task_id)
    except NotFoundError:
        return ReassignTaskResult(
            success=False,
            message=f"Task not found: {task_id}",
            task_id=task_id,
            new_epic_id=target_epic_id,
        ).model_dump(mode="json")

    # Validate target epic exists
    epics = adapter.get_epics()
    target_epic = None
    for epic in epics:
        if epic["id"] == target_epic_id:
            target_epic = epic
            break

    if not target_epic:
        return ReassignTaskResult(
            success=False,
            message=f"Epic not found: {target_epic_id}",
            task_id=task_id,
            new_epic_id=target_epic_id,
        ).model_dump(mode="json")

    old_epic_id = current_task.get("epic_id")

    if old_epic_id == target_epic_id:
        return ReassignTaskResult(
            success=False,
            message=f"Task {task_id} is already in epic {target_epic_id}",
            task_id=task_id,
            old_epic_id=old_epic_id,
            new_epic_id=target_epic_id,
        ).model_dump(mode="json")

    try:
        updated_task = adapter.update_task(task_id, {"epic_id": target_epic_id})

        return ReassignTaskResult(
            success=True,
            message=f"Successfully moved task {current_task.get('title', task_id)} to epic {target_epic.get('name', target_epic_id)}",
            task_id=task_id,
            old_epic_id=old_epic_id,
            new_epic_id=target_epic_id,
            task_url=updated_task.get("url"),
        ).model_dump(mode="json")

    except Exception as e:
        return ReassignTaskResult(
            success=False,
            message=f"Error reassigning task: {str(e)}",
            task_id=task_id,
            new_epic_id=target_epic_id,
        ).model_dump(mode="json")
