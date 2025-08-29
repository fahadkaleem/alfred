"""MCP tool wrapper for archive_subtasks."""

from typing import Optional
from alfred.core.tasks.archive_subtasks import archive_subtasks_logic
from alfred.config import get_config


def register(server) -> int:
    """Register the archive_subtasks tool."""

    @server.tool
    def archive_subtasks(
        parent_task_id: str,
        status: Optional[str] = "done",
    ) -> dict:
        """
        Mark all subtasks of a parent task as completed/archived.

        This tool batch updates all subtasks to "done" status in a single operation.
        It accepts parent_task_id, updates all subtasks in single batch operation,
        skips already completed subtasks, updates parent task progress indicator,
        and returns count of archived subtasks.

        Key features:
        - Efficient batch status updates for all subtasks under a parent
        - Skips subtasks that are already in the target status
        - Detailed reporting of successful and failed updates
        - Preserves subtask history and relationships
        - Updates parent task completion progress

        Use this tool when:
        - You've completed work on a parent task and want to close all subtasks
        - You need to bulk complete subtasks after a milestone is reached
        - You're cleaning up completed work by archiving related subtasks
        - You want to reset task breakdown by completing all current subtasks

        Crucial Guardrails:
        - Use get_task first to check current subtask statuses
        - Status change is permanent for all subtasks - cannot be undone easily
        - Only affects subtasks, not the parent task status
        - Use update_task_status for individual subtask status changes

        Args:
            parent_task_id: Linear task ID whose subtasks should be archived.
                Must be a valid existing task ID in your workspace. Format
                examples: "AUTH-123", "PROJ-456", "LOGIN-789". Task IDs are
                case-sensitive and must match exactly. Task must exist and
                be accessible.
            status: Status to apply to all subtasks. Default: "done". Valid
                values: "done", "completed", "cancelled", "archived". All map
                to appropriate Linear workflow states. "done" and "completed"
                mark subtasks as successfully finished. "cancelled" marks them
                as no longer needed.

        Returns:
            Dictionary with archiving results including count of archived subtasks,
            detailed results per subtask showing status changes, and any errors
            encountered during the batch update operation.
        """
        config = get_config()

        return archive_subtasks_logic(
            api_key=config.linear_api_key,
            parent_task_id=parent_task_id,
            status=status,
        )

    return 1
