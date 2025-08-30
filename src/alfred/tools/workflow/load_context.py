"""MCP tool wrapper for load_context."""

from alfred.mcp import mcp
from alfred.core.workflow.engine import WorkflowEngine

# Create workflow engine instance
workflow_engine = WorkflowEngine()


@mcp.tool
async def load_context(task_id: str, phase: str | None = None) -> dict:
    """Load saved context for a task to restore work state and decisions.

    - Retrieves all saved context from local storage
    - Organizes context by workflow phases for easy navigation
    - Essential for resuming work in new chat sessions
    - Returns comprehensive work history and decisions
    - Supports filtering by specific phase when needed

    Parameters
    task_id [string] (required) - The task/ticket ID to load context for (e.g., "AL-123", "PROJ-456")
    phase [string] - Optional specific phase to filter results:
        - Phase names vary by workflow - use get_next_phase() to see available phases
        - Example phases: "planning", "implement", "test", "review"
        - "planning" - Only planning phase context
        - "implement" - Only implementation context
        - "test" - Only testing context
        - "review" - Only review context
        - If omitted, returns ALL saved contexts

    Usage notes:
    - Use at start of new chat sessions to restore work state
    - Essential before continuing work on existing tasks
    - Context includes content, metadata, and timestamps
    - Data organized chronologically within each phase
    - Shows work progression and decision history

    Returns
        ToolResponse with comprehensive context data:
        - contexts: All saved contexts organized by phase
        - phase_summaries: Key accomplishments per phase
        - metadata: Workflow state and progress information
        - timestamps: When context was saved

    Examples
        # Load all context for task overview
        load_context("AL-123")

        # Load specific phase context
        load_context("AL-123", "planning")

        # Resume implementation work
        load_context("AL-123", "implement")

    Error conditions:
    - Task not found or no context saved
    - Invalid phase name specified
    - Storage access failures

    """
    response = workflow_engine.load_context(task_id, phase)
    return {
        "message": f"Context loaded for task '{task_id}'",
        "data": response.model_dump(),
    }
