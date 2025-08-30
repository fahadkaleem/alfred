"""MCP tool wrapper for get_next_phase."""

from alfred.core.workflow.operations.get_next_phase import get_next_phase_logic


def register(server) -> int:
    """Register the get_next_phase tool."""

    @server.tool
    async def get_next_phase(task_id: str) -> dict:
        """Get the next workflow phase to execute for lightweight task navigation.

        - Lightweight tool for determining next steps without full workflow execution
        - Perfect for resuming work in new chat sessions or checking progress
        - Automatically handles workflow assignment if task doesn't have one
        - Shows phase name, status, and brief guidance for proceeding
        - Works independently without loading full workflow context

        Parameters
        ----------
        task_id [string] (required) - The task ID to check for next phase:
            - External task keys: "PROJ-123", "AL-456"
            - Local Alfred task IDs: AL-1, AL-2, AL-3, etc.
            - Must be valid existing task identifier

        Usage scenarios:
        - Session resumption: Quick check of where you left off
        - Progress navigation: See what comes next without full context loading
        - Workflow validation: Verify task has proper workflow assignment
        - Light coordination: Check phase status for team handoffs
        - Troubleshooting: Diagnose workflow progression issues

        Navigation flow:
        1. Task without workflow → Suggests workflow assignment
        2. New task → Returns first phase (usually "claim" or "planning")
        3. In-progress task → Returns current or next incomplete phase
        4. Completed workflow → Reports completion status

        Returns
        -------
            ToolResponse with next phase guidance:
            - phase_name: The specific phase to work on next
            - phase_goal: Brief description of phase objectives
            - phase_status: Current completion state
            - workflow_progress: Overall task progress percentage
            - instructions: Next steps and recommended actions
            - prerequisites: Any dependencies or requirements

        Examples
        --------
            # Check next phase for existing task
            get_next_phase("PROJ-123")

            # Resume work after break
            get_next_phase("AL-456")

            # Verify workflow assignment
            get_next_phase("TASK-789")

        Usage notes:
        - Works in any chat session without prior context
        - Handles missing workflow assignment gracefully
        - Lightweight alternative to execute_phase() for navigation
        - Use before execute_phase() to confirm next steps
        - Safe to call repeatedly without side effects

        Error conditions:
        - Task ID not found or invalid
        - Workflow configuration missing or corrupted
        - Task storage access failures

        """
        result = await get_next_phase_logic(task_id)
        return result.model_dump()

    return 1  # Number of tools registered
