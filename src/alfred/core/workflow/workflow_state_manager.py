"""Workflow state manager for Alfred.

Manages workflow execution state stored locally in .alfred/workflow_state.json
while actual tasks remain in Linear/Jira.
"""

from datetime import datetime
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from alfred.models.workflow_state import WorkflowState, WorkflowStateStorage


class WorkflowStateManager:
    """Manages workflow state persistence."""

    def __init__(self, data_dir: Path):
        """Initialize with data directory."""
        self.data_dir = data_dir
        self.state_file = data_dir / "workflow_state.json"
        self.storage: WorkflowStateStorage = self._load_storage()

    def _load_storage(self) -> WorkflowStateStorage:
        """Load state storage from file or create new one."""
        if self.state_file.exists():
            try:
                with open(self.state_file) as f:
                    data = json.load(f)
                return WorkflowStateStorage.model_validate(data)
            except Exception:
                # If file is corrupted, start fresh
                pass

        # Ensure data directory exists
        self.data_dir.mkdir(parents=True, exist_ok=True)
        return WorkflowStateStorage()

    def _save_storage(self) -> None:
        """Save current storage to file."""
        try:
            with open(self.state_file, "w") as f:
                json.dump(self.storage.model_dump(), f, indent=2, default=str)
        except Exception as e:
            raise RuntimeError(f"Failed to save workflow state: {e}")

    # Workflow State Management
    def get_state(self, task_id: str) -> Optional[WorkflowState]:
        """Get workflow state for a task."""
        return self.storage.get_state(task_id)

    def get_or_create_state(self, task_id: str) -> WorkflowState:
        """Get or create workflow state for a task."""
        state = self.storage.get_or_create_state(task_id)
        self._save_storage()
        return state

    def assign_workflow(self, task_id: str, workflow_id: str) -> bool:
        """Assign a workflow to a task."""
        state = self.get_or_create_state(task_id)
        state.workflow_id = workflow_id
        state.updated_at = datetime.utcnow()
        self._save_storage()
        return True

    def mark_phase_started(self, task_id: str, phase: str) -> bool:
        """Mark a phase as started."""
        state = self.get_or_create_state(task_id)
        state.mark_phase_started(phase)
        self._save_storage()
        return True

    def mark_phase_completed(self, task_id: str, phase: str) -> bool:
        """Mark a phase as completed."""
        state = self.get_or_create_state(task_id)
        state.mark_phase_completed(phase)
        self._save_storage()
        return True

    def save_context(
        self,
        task_id: str,
        phase: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Save context for a workflow phase."""
        state = self.get_or_create_state(task_id)
        state.add_context(phase, content, metadata)
        self._save_storage()
        return True

    def load_context(
        self, task_id: str, phase: Optional[str] = None
    ) -> Optional[Dict[str, List[Dict[str, Any]]] | List[Dict[str, Any]]]:
        """Load saved context for a task."""
        state = self.get_state(task_id)
        if not state:
            return None

        if phase:
            return state.contexts.get(phase, [])
        return state.contexts

    def get_workflow_state(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get complete workflow state for a task."""
        state = self.get_state(task_id)
        if not state:
            return None

        return {
            "task_id": task_id,
            "workflow_id": state.workflow_id,
            "completed_phases": state.completed_phases,
            "started_phases": state.started_phases,
            "contexts": state.contexts,
            "artifacts": state.artifacts,
            "created_at": state.created_at.isoformat(),
            "updated_at": state.updated_at.isoformat(),
        }
