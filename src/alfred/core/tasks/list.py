"""Business logic for listing tasks."""

from typing import Optional, Dict, Any
from alfred.adapters import get_adapter
from alfred.models.config import Config
from alfred.models.tasks import (
    TaskListResult,
    map_status_alfred_to_linear,
    to_alfred_task,
)


def get_tasks_logic(
    config: Config,
    status: Optional[str] = None,
    epic_id: Optional[str] = None,
    page: int = 1,
    per_page: int = 50,
) -> Dict[str, Any]:
    """List tasks with filtering and pagination."""

    adapter = get_adapter(config)

    linear_status = None
    if status:
        status_list = [s.strip().lower() for s in status.split(",") if s.strip()]
        linear_status = [map_status_alfred_to_linear(s) for s in status_list]

    tasks = adapter.get_tasks(epic_id=epic_id, status=linear_status, limit=per_page * 2)

    alfred_tasks = [to_alfred_task(task) for task in tasks]

    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    paginated_tasks = alfred_tasks[start_idx:end_idx]

    task_result = TaskListResult(
        items=paginated_tasks,
        page=page,
        per_page=per_page,
        total=len(alfred_tasks),
        has_next=end_idx < len(alfred_tasks),
        next_cursor=None,
    )

    return task_result.model_dump(mode="json")
