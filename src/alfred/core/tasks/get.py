"""Business logic for getting a single task."""

from typing import Dict, Any
from alfred.adapters import get_adapter
from alfred.models.config import Config
from alfred.adapters.base import NotFoundError
from alfred.models.tasks import to_alfred_task


def get_task_logic(config: Config, task_id: str) -> Dict[str, Any]:
    """Get single task by ID from configured platform."""

    adapter = get_adapter(config)

    try:
        task = adapter.get_task(task_id)
        alfred_task = to_alfred_task(task)
        return alfred_task.model_dump(mode="json")
    except NotFoundError:
        return {"error": "not_found", "task_id": task_id}
