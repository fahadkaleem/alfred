"""Business logic for adding subtasks to parent tasks."""

from typing import Dict, Any, Optional
from alfred.adapters.linear_adapter import LinearAdapter
from alfred.models.tasks import to_alfred_task


def add_subtask_logic(
    api_key: str,
    parent_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    assignee_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create a subtask under an existing parent task.

    Args:
        api_key: Linear API key
        parent_id: ID of parent task to add subtask to
        title: Title for new subtask
        description: Description for new subtask
        assignee_id: Optional assignee ID

    Returns:
        Dictionary with created subtask data
    """
    adapter = LinearAdapter(api_token=api_key)

    if not title:
        title = "New Subtask"

    # Create the subtask using the dedicated create_subtask method
    created_subtask = adapter.create_subtask(
        parent_id=parent_id, title=title, description=description
    )

    alfred_subtask = to_alfred_task(created_subtask)
    return alfred_subtask.model_dump(mode="json")
