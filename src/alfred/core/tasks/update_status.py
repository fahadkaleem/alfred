"""Business logic for updating task status."""

from typing import Dict, Any
from alfred.adapters.linear_adapter import LinearAdapter
from alfred.adapters.base import NotFoundError
from alfred.models.tasks import (
    TaskStatus,
    map_status_alfred_to_linear,
    to_alfred_task,
)


def update_task_status_logic(api_key: str, task_id: str, status: str) -> Dict[str, Any]:
    """Update task status with Alfred to Linear mapping."""

    # Belt and suspenders validation (should be caught at MCP layer)
    try:
        # Validate status by trying to create enum instance
        task_status = TaskStatus(status.lower())
    except ValueError:
        valid_statuses = [s.value for s in TaskStatus]
        return {
            "error": "invalid_status",
            "message": f"Status must be one of: {valid_statuses}",
            "provided": status,
            "valid_statuses": valid_statuses,
        }

    adapter = LinearAdapter(api_token=api_key)

    linear_status = map_status_alfred_to_linear(status)

    try:
        task = adapter.update_task(task_id, {"status": linear_status})
        alfred_task = to_alfred_task(task)
        return alfred_task.model_dump(mode="json")
    except NotFoundError:
        return {"error": "not_found", "task_id": task_id}
