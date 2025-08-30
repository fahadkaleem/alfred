"""Business logic for creating tasks."""

from typing import Dict, Any, Optional, List
from alfred.adapters import get_adapter
from alfred.models.config import Config
from alfred.models.tasks import to_alfred_task


def create_task_logic(
    config: Config,
    title: str,
    description: Optional[str] = None,
    epic_id: Optional[str] = None,
    assignee_id: Optional[str] = None,
    labels: Optional[List[str]] = None,
    priority: Optional[str] = None,
) -> Dict[str, Any]:
    """Create new task in configured platform."""

    adapter = get_adapter(config)

    task = adapter.create_task(title=title, description=description, epic_id=epic_id)

    alfred_task = to_alfred_task(task)
    return alfred_task.model_dump(mode="json")
