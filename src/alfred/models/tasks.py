"""Task management data models."""

from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Literal, Any, Set
from pydantic import BaseModel


class TaskStatus(str, Enum):
    """Alfred task status enum."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELLED = "cancelled"

    @classmethod
    def from_linear(cls, linear_status: str) -> "TaskStatus":
        """Convert Linear status to Alfred TaskStatus."""
        mapping = {
            "backlog": cls.PENDING,
            "todo": cls.PENDING,
            "in progress": cls.IN_PROGRESS,
            "in_progress": cls.IN_PROGRESS,  # Handle both formats
            "started": cls.IN_PROGRESS,
            "done": cls.DONE,
            "canceled": cls.CANCELLED,
            "cancelled": cls.CANCELLED,  # Handle both spellings
        }
        normalized = linear_status.lower() if linear_status else "backlog"
        if normalized not in mapping:
            # Default to PENDING for unknown statuses
            return cls.PENDING
        return mapping[normalized]

    def to_linear(self) -> str:
        """Convert Alfred TaskStatus to Linear status."""
        mapping = {
            TaskStatus.PENDING: "Backlog",
            TaskStatus.IN_PROGRESS: "In Progress",
            TaskStatus.DONE: "Done",
            TaskStatus.CANCELLED: "Canceled",
        }
        return mapping[self]


class TaskStatusGroups:
    """Groupings of task statuses for different operations."""

    ELIGIBLE: Set[TaskStatus] = {TaskStatus.PENDING, TaskStatus.IN_PROGRESS}
    COMPLETED: Set[TaskStatus] = {TaskStatus.DONE, TaskStatus.CANCELLED}
    ACTIVE: Set[TaskStatus] = {TaskStatus.IN_PROGRESS}

    @classmethod
    def is_eligible(cls, status: TaskStatus) -> bool:
        """Check if status is eligible for operations."""
        return status in cls.ELIGIBLE

    @classmethod
    def is_completed(cls, status: TaskStatus) -> bool:
        """Check if status represents completed work."""
        return status in cls.COMPLETED


# Keep for backward compatibility temporarily
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
    """Structured task response model matching Linear's Issue structure."""

    id: str
    title: str
    description: Optional[str] = None
    status: TaskStatus
    epic_id: Optional[str] = None
    assignee_id: Optional[str] = None
    labels: List[str] = []
    priority: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    url: Optional[str] = None
    parent_id: Optional[str] = None  # Maps to Linear's parentId


class TaskListResult(BaseModel):
    """Paginated task list response."""

    items: List[AlfredTask]
    page: int
    per_page: int
    total: Optional[int] = None
    has_next: bool
    next_cursor: Optional[str] = None


def map_status_linear_to_alfred(status: str) -> TaskStatus:
    """Map Linear status to Alfred status."""
    return TaskStatus.from_linear(status)


def map_status_alfred_to_linear(status: str) -> str:
    """Map Alfred status to Linear status."""
    # Handle both string and enum inputs
    if isinstance(status, TaskStatus):
        return status.to_linear()

    # Convert string to enum first
    try:
        task_status = TaskStatus(status.lower())
        return task_status.to_linear()
    except ValueError:
        raise ValueError(f"Unknown Alfred status: {status}")


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
        parent_id=task.get("parent_id"),
    )
