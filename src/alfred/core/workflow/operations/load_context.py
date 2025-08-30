"""Load context business logic."""

from alfred.core.workflow.engine import WorkflowEngine
from alfred.models.workflow import ToolResponse


async def load_context_logic(task_id: str, phase: str | None = None) -> ToolResponse:
    """Load saved context for a task to restore work state and decisions.

    Args:
        task_id: The task/ticket ID to load context for
        phase: Optional specific phase to filter results

    Returns:
        ToolResponse with comprehensive context data
    """
    workflow_engine = WorkflowEngine()
    response = workflow_engine.load_context(task_id, phase)
    return ToolResponse.success(
        message=f"Context loaded for task '{task_id}'", data=response.model_dump()
    )
