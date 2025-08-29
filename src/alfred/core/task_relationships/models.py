"""Models for task relationship operations."""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class TaskRelationship(BaseModel):
    """Represents a relationship between two tasks."""

    id: str
    type: str = Field(..., description="Relationship type: blocks, relates, duplicates")
    blocker_task_id: str = Field(..., description="ID of task that blocks")
    blocked_task_id: str = Field(..., description="ID of task that is blocked")
    blocker_title: Optional[str] = None
    blocked_title: Optional[str] = None


class LinkTasksResult(BaseModel):
    """Result of linking two tasks."""

    success: bool
    message: str
    relationship: Optional[TaskRelationship] = None
    blocker_url: Optional[str] = None
    blocked_url: Optional[str] = None


class UnlinkTasksResult(BaseModel):
    """Result of unlinking two tasks."""

    success: bool
    message: str
    removed_relationship: Optional[TaskRelationship] = None


class ReassignTaskResult(BaseModel):
    """Result of reassigning a task to a different epic."""

    success: bool
    message: str
    task_id: str
    old_epic_id: Optional[str] = None
    new_epic_id: str
    task_url: Optional[str] = None
