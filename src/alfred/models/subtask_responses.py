"""Response models for subtask operations."""

from typing import List, Optional
from pydantic import BaseModel
from alfred.models.tasks import AlfredTask


class SubtaskCreationResult(BaseModel):
    """Result of creating subtasks for a single task."""

    task_id: str
    task_title: str
    subtasks_created: List[AlfredTask]
    message: str


class BatchSubtaskResult(BaseModel):
    """Individual task result in batch operation."""

    task_id: str
    success: bool
    subtasks_created: Optional[int] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None


class BatchSubtaskCreationResult(BaseModel):
    """Result of batch subtask creation."""

    expanded_count: int
    failed_count: int
    skipped_count: int
    message: str
    results: List[BatchSubtaskResult]
