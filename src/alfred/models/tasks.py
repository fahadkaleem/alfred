"""Task management data models."""

from datetime import datetime
from typing import Dict, List, Optional, Literal, Any
from pydantic import BaseModel

AlfredTaskStatus = Literal["pending", "in_progress", "done", "cancelled"]


class WorkspaceConfig(BaseModel):
    """Workspace configuration model."""

    api_key: str
    workspace_id: Optional[str] = None
    team_id: Optional[str] = None


# Supported Alfred statuses (hardcoded for now, will be dynamic in future)
VALID_ALFRED_STATUSES = ["pending", "in_progress", "done", "cancelled"]

# Simple normalized mappings - all comparisons done in lowercase
STATUS_LINEAR_TO_ALFRED = {
    "backlog": "pending",
    "todo": "pending",
    "in progress": "in_progress",
    "done": "done",
    "canceled": "cancelled",
}

STATUS_ALFRED_TO_LINEAR = {
    "pending": "Backlog",
    "in_progress": "In Progress",
    "done": "Done",
    "cancelled": "Canceled",
}


class AlfredTask(BaseModel):
    """Structured task response model."""

    id: str
    title: str
    description: Optional[str] = None
    status: AlfredTaskStatus
    epic_id: Optional[str] = None
    assignee_id: Optional[str] = None
    labels: List[str] = []
    priority: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    url: Optional[str] = None


class TaskListResult(BaseModel):
    """Paginated task list response."""

    items: List[AlfredTask]
    page: int
    per_page: int
    total: Optional[int] = None
    has_next: bool
    next_cursor: Optional[str] = None


def map_status_linear_to_alfred(status: str) -> AlfredTaskStatus:
    """Map Linear status to Alfred status."""
    mapped = STATUS_LINEAR_TO_ALFRED.get(status.lower())
    if mapped is None:
        raise ValueError(f"Unknown Linear status: {status}")
    return mapped


def map_status_alfred_to_linear(status: str) -> str:
    """Map Alfred status to Linear status."""
    mapped = STATUS_ALFRED_TO_LINEAR.get(status.lower())
    if mapped is None:
        raise ValueError(f"Unknown Alfred status: {status}")
    return mapped


def to_alfred_task(task: Dict[str, Any]) -> AlfredTask:
    """Convert TaskDict to AlfredTask."""
    return AlfredTask(
        id=task.get("id", ""),
        title=task.get("title", ""),
        description=task.get("description"),
        status=map_status_linear_to_alfred(task.get("status", "todo")),
        epic_id=task.get("epic_id"),
        assignee_id=None,
        labels=[],
        priority=None,
        created_at=datetime.fromisoformat(
            task.get("created_at", "").replace("Z", "+00:00")
        )
        if task.get("created_at")
        else datetime.now(),
        updated_at=datetime.fromisoformat(
            task.get("updated_at", "").replace("Z", "+00:00")
        )
        if task.get("updated_at")
        else datetime.now(),
        url=task.get("url"),
    )
