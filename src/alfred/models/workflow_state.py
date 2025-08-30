"""Workflow state models for tracking workflow execution state.

This stores only workflow-related state for tasks that exist in Linear/Jira.
Actual task data (title, description, status) lives in Linear/Jira.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field


class WorkflowState(BaseModel):
    """Workflow execution state for a Linear/Jira task."""

    task_id: str  # Linear/Jira task ID (e.g., "TASK-123")
    workflow_id: Optional[str] = None
    completed_phases: List[str] = Field(default_factory=list)
    started_phases: List[str] = Field(default_factory=list)
    contexts: Dict[str, List[Dict[str, Any]]] = Field(default_factory=dict)
    artifacts: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def mark_phase_started(self, phase: str) -> None:
        """Mark a phase as started."""
        if phase not in self.started_phases:
            self.started_phases.append(phase)
            self.updated_at = datetime.utcnow()

    def mark_phase_completed(self, phase: str) -> None:
        """Mark a phase as completed."""
        if phase not in self.completed_phases:
            self.completed_phases.append(phase)
            self.updated_at = datetime.utcnow()

    def add_context(
        self, phase: str, content: str, metadata: Optional[Dict] = None
    ) -> None:
        """Add context entry for a phase."""
        if phase not in self.contexts:
            self.contexts[phase] = []

        entry = {
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {},
        }
        self.contexts[phase].append(entry)
        self.updated_at = datetime.utcnow()


class WorkflowStateStorage(BaseModel):
    """Storage container for all workflow states."""

    states: Dict[str, WorkflowState] = Field(default_factory=dict)

    def get_state(self, task_id: str) -> Optional[WorkflowState]:
        """Get workflow state for a task."""
        return self.states.get(task_id)

    def create_state(self, task_id: str) -> WorkflowState:
        """Create a new workflow state for a task."""
        if task_id not in self.states:
            self.states[task_id] = WorkflowState(task_id=task_id)
        return self.states[task_id]

    def get_or_create_state(self, task_id: str) -> WorkflowState:
        """Get existing state or create new one."""
        if task_id not in self.states:
            return self.create_state(task_id)
        return self.states[task_id]
