"""Assign workflow to task tool implementation."""

import contextlib
from datetime import datetime
import json
from pathlib import Path

from alfred.core.workflow.engine import WorkflowEngine
from alfred.models.workflow import ToolResponse
# State management handled directly by WorkflowEngine


async def assign_workflow_logic(
    workflow_id: str, task_id: str | None = None, force: bool = False
) -> ToolResponse:
    """Assigns a workflow to a task or stores as pending assignment.

    Args:
        workflow_id: The workflow to assign (e.g., "tech_spec", "task", "prd")
        task_id: Optional task ID to assign workflow to immediately
        force: If True, allows reassigning workflows to existing tasks

    Returns:
        ToolResponse with assignment result and next steps.

    """
    try:
        # Initialize workflow engine
        engine = WorkflowEngine()

        # Validate workflow exists and load it
        try:
            workflow = engine._get_workflow(workflow_id)
        except Exception:
            available_workflows = engine.loader.list_workflows()
            return ToolResponse.error(
                message=f"Unknown workflow '{workflow_id}'. Available: {', '.join(available_workflows)}",
                next_prompt=f"Use list_workflows() to see detailed descriptions of available workflows: {', '.join(available_workflows)}",
                data={"available_workflows": available_workflows},
            )

        # Case 1: No task_id provided - store as pending workflow
        if not task_id:
            _store_pending_workflow(engine.base_path, workflow_id)

            return ToolResponse.success(
                message=f"Workflow '{workflow_id}' stored as pending assignment",
                next_prompt=f"""# Workflow Assignment Pending

Workflow **{workflow.name}** has been stored for the next task you work on.

## What happens next:
- When you create a new task or continue working on an existing task, this workflow will be automatically assigned
- Use `continue_workflow(task_id, phase)` or `get_next_phase(task_id)` to trigger the assignment

## Workflow Details:
- **Name**: {workflow.name}
- **Purpose**: {workflow.goal}
- **Creates Task**: {"Yes" if workflow.create_task else "No"}
- **Phases**: {len(workflow.phases)} phases

To assign to a specific existing task instead, use: `assign_workflow("{workflow_id}", "AL-1")`""",
                data={
                    "workflow_id": workflow_id,
                    "workflow_name": workflow.name,
                    "is_pending": True,
                    "task_id": None,
                },
            )

        # Case 2: Task ID provided - direct assignment
        # Note: We don't validate Linear task existence here - the state manager will handle it

        # Check if task already has a workflow assigned
        state = engine.state_manager.get_state(task_id)
        if state and state.workflow_id and not force:
            return ToolResponse.error(
                message=f"Task '{task_id}' already has workflow '{state.workflow_id}' assigned",
                next_prompt=f"Use assign_workflow('{workflow_id}', '{task_id}', force=True) to force reassignment, or continue with existing workflow using get_next_phase('{task_id}')",
                data={
                    "task_id": task_id,
                    "current_workflow": state.workflow_id,
                    "requested_workflow": workflow_id,
                    "force_required": True,
                },
            )

        # Perform the assignment
        previous_workflow = state.workflow_id if state else None
        engine.state_manager.assign_workflow(task_id, workflow_id)

        # Clear any pending workflow (it's been consumed)
        _clear_pending_workflow(engine.base_path)

        # Create success message
        action = "reassigned" if previous_workflow else "assigned"
        message = f"Workflow '{workflow_id}' {action} to task '{task_id}'"

        next_prompt = f"""# Workflow Assignment Complete

Successfully {action} **{workflow.name}** to task **{task_id}**.

## Next Steps:
1. **Get next phase**: `get_next_phase("{task_id}")` - See what phase to work on
2. **Check progress**: `get_progress("{task_id}")` - View current status
3. **Start working**: `execute_phase("{task_id}", "phase_name")` - Begin specific phase

## Workflow Details:
- **Name**: {workflow.name}
- **Purpose**: {workflow.goal}
- **Phases**: {len(workflow.phases)} phases
- **Creates Task**: {"Yes" if workflow.create_task else "No"}

{"**Note**: Previous workflow was '" + previous_workflow + "'. Progress may be lost." if previous_workflow else ""}

Ready to begin work on this task!"""

        return ToolResponse.success(
            message=message,
            next_prompt=next_prompt,
            data={
                "workflow_id": workflow_id,
                "workflow_name": workflow.name,
                "task_id": task_id,
                "is_pending": False,
                "previous_workflow": previous_workflow,
                "action": action,
                "phase_count": len(workflow.phases),
            },
        )

    except Exception as e:
        return ToolResponse.error(
            message=f"Failed to assign workflow: {e!s}",
            next_prompt="Check that the task ID exists using list_all_tasks() and the workflow exists using list_workflows(). Check Alfred MCP server logs for details.",
        )


def _store_pending_workflow(base_path: Path, workflow_id: str) -> None:
    """Store a pending workflow assignment for when task is created."""
    base_path.mkdir(parents=True, exist_ok=True)
    pending_file = base_path / "pending_workflow.json"
    temp_file = base_path / "pending_workflow.json.tmp"

    data = {"workflow_id": workflow_id, "timestamp": datetime.now().isoformat()}

    # Atomic write
    with temp_file.open("w") as f:
        json.dump(data, f, indent=2)

    temp_file.rename(pending_file)


def _clear_pending_workflow(base_path: Path) -> None:
    """Clear any pending workflow assignment."""
    pending_file = base_path / "pending_workflow.json"

    if pending_file.exists():
        with contextlib.suppress(Exception):
            pending_file.unlink()
