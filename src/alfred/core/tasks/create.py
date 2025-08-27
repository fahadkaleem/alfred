"""Business logic for creating tasks."""

from typing import Dict, Any, Optional, List
from alfred.adapters.linear_adapter import LinearAdapter
from alfred.models.tasks import to_alfred_task


def create_task_logic(
    api_key: str,
    title: str,
    description: Optional[str] = None,
    epic_id: Optional[str] = None,
    assignee_id: Optional[str] = None,
    labels: Optional[List[str]] = None,
    priority: Optional[str] = None
) -> Dict[str, Any]:
    """Create new task in Linear."""
    
    adapter = LinearAdapter(api_token=api_key)
    
    task = adapter.create_task(
        title=title,
        description=description,
        epic_id=epic_id
    )
    
    alfred_task = to_alfred_task(task)
    return alfred_task.model_dump()