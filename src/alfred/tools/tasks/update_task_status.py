"""MCP tool wrapper for update_task_status."""

from alfred.core.tasks.update_status import update_task_status_logic
from alfred.config import get_config
from alfred.models.tasks import VALID_ALFRED_STATUSES


def register(server) -> int:
    """Register the update_task_status tool."""

    @server.tool
    def update_task_status(task_id: str, status: str) -> dict:
        """
        Change a task's status with Alfred to Linear status mapping.

        This tool updates a task's status in Linear, automatically mapping Alfred status 
        values to the corresponding Linear workflow states. It provides input validation 
        and detailed error reporting for invalid operations.

        Key features:
        - Automatic Alfred ↔ Linear status mapping with validation
        - Input validation prevents invalid status transitions
        - Detailed error responses with corrective guidance
        - Atomic updates - either succeeds completely or fails safely
        - Returns updated task object for verification

        Use this tool when:
        - You need to advance a task through your workflow (e.g., pending → in_progress → done)
        - You want to mark tasks as completed after finishing work
        - You need to cancel or defer tasks that are no longer relevant
        - You're updating task status as part of a larger workflow

        Crucial Guardrails:
        - Use get_task first if you need to verify current task status before updating
        - Use update_task instead for changing task content, descriptions, or other fields
        - Don't use this for creating new tasks - use create_task
        - Don't use for bulk operations - this tool handles one task at a time

        Usage Guidance and Workflow Context:

        IMPORTANT: Alfred enforces strict input validation. Only these 4 status values are 
        accepted: "pending", "in_progress", "done", "cancelled". Any other values will return 
        a detailed error explaining valid options.

        CRITICAL WORKFLOW CONSIDERATIONS:
        - Status transitions should follow logical progression: pending → in_progress → done
        - Moving from "done" back to "in_progress" is allowed for reopening completed work
        - "cancelled" is final - tasks cannot be moved out of cancelled status via this tool
        - Each status change is immediately persisted to Linear - no undo functionality

        Status Mapping Details:
        - pending → Linear "Backlog" (task is ready to work on)
        - in_progress → Linear "In Progress" (task is actively being worked)
        - done → Linear "Done" (task is completed and verified)
        - cancelled → Linear "Canceled" (task is no longer needed)

        Best Practices:
        - Always verify task exists before attempting status update
        - Check current status if unsure about valid transitions
        - Use meaningful commit messages when this is part of development workflow
        - Consider notifying team members for significant status changes

        Error Handling:
        - Invalid status: Returns detailed error with valid status list
        - Task not found: Returns error with the attempted task_id for debugging
        - Linear API errors: Returns error with Linear's specific error message

        Args:
            task_id: Linear task/issue ID to update. Must be a valid existing task ID in your 
                workspace. Format examples: "AUTH-123", "PROJ-456", "LOGIN-789". Task IDs are 
                case-sensitive and must match exactly. Use get_tasks or list_projects to discover 
                valid task IDs if unsure.
            status: New Alfred status to assign to the task. Must be exactly one of: "pending", 
                "in_progress", "done", "cancelled". Case-sensitive - use lowercase only. Invalid 
                values return detailed error with list of valid statuses. Status is automatically 
                mapped to corresponding Linear workflow state.

        Returns:
            Dictionary with:
            - On success: Updated AlfredTask object
            - On not found: {'error': 'not_found', 'task_id': '<id>'}
            - On invalid status: {'error': 'invalid_status', 'message': '...', 'provided': '<status>'}
        """
        # Validate status first
        if status not in VALID_ALFRED_STATUSES:
            return {
                'error': 'invalid_status',
                'message': f'Status must be one of: {VALID_ALFRED_STATUSES}',
                'provided': status,
                'valid_statuses': VALID_ALFRED_STATUSES
            }
        
        config = get_config()

        return update_task_status_logic(
            api_key=config.linear_api_key,
            task_id=task_id,
            status=status
        )

    return 1