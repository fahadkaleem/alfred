"""Data models for task generation from specifications."""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field, field_validator
from datetime import datetime


class TaskSuggestion(BaseModel):
    """Model for a suggested task from AI analysis."""

    title: str = Field(..., description="Clear, action-oriented task title")
    description: str = Field(
        ..., description="Detailed description of what needs to be done"
    )
    priority: Literal["P0", "P1", "P2", "P3"] = Field("P2", description="Task priority")
    labels: List[str] = Field(default_factory=list, description="Task labels/tags")
    dependencies: List[str] = Field(
        default_factory=list, description="Task titles this depends on"
    )
    estimate: Optional[int] = Field(None, description="Estimated hours")
    acceptance_criteria: List[str] = Field(
        default_factory=list, description="Success criteria"
    )
    technical_notes: Optional[str] = Field(
        None, description="Implementation approach and patterns"
    )
    complexity: int = Field(5, ge=1, le=10, description="Complexity score 1-10")

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Task title cannot be empty")
        return v.strip()

    @field_validator("acceptance_criteria")
    @classmethod
    def acceptance_criteria_not_empty_strings(cls, v):
        return [ac.strip() for ac in v if ac.strip()]


class EpicSuggestion(BaseModel):
    """Model for a suggested epic/project from AI analysis."""

    title: str = Field(..., description="Epic/project title")
    description: str = Field(..., description="Epic description")
    create_epic: bool = Field(True, description="Whether to create the epic")

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Epic title cannot be empty")
        return v.strip()


class GenerationResult(BaseModel):
    """Result of AI task generation."""

    epic: Optional[EpicSuggestion] = None
    tasks: List[TaskSuggestion]
    metadata: dict = Field(default_factory=dict, description="Additional metadata")

    @field_validator("tasks")
    @classmethod
    def tasks_not_empty(cls, v):
        if not v:
            raise ValueError("At least one task must be generated")
        return v


class LinearTaskCreated(BaseModel):
    """Result of creating a task in Linear."""

    id: str
    title: str
    url: Optional[str] = None
    priority: Optional[int] = None


class LinearEpicCreated(BaseModel):
    """Result of creating an epic in Linear."""

    id: str
    title: str
    url: Optional[str] = None


class CreateTasksFromSpecResult(BaseModel):
    """Final result of create_tasks_from_spec operation."""

    success: bool
    epic: Optional[LinearEpicCreated] = None
    tasks: List[LinearTaskCreated]
    summary: dict
    errors: List[dict] = Field(default_factory=list)

    @field_validator("summary")
    @classmethod
    def summary_has_required_fields(cls, v):
        required_fields = ["requested", "created", "team_id"]
        for field in required_fields:
            if field not in v:
                raise ValueError(f"Summary must include {field}")
        return v
