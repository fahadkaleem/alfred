"""MCP tool wrapper for remove_subtask."""

from typing import Optional
from alfred.mcp import mcp
from alfred.core.tasks.remove_subtask import remove_subtask_logic


@mcp.tool
def remove_subtask(
    subtask_id: str,
    convert_to_task: Optional[bool] = False,
) -> dict:
    """
    Delete a subtask or convert it to a standalone task.

    This tool deletes subtasks from Linear or converts them to standalone tasks.
    Updates parent task's subtask count, handles subtask not found gracefully,
    does not affect sibling subtasks, and returns confirmation of deletion.

    Key features:
    - Deletes Linear sub-issues or converts them to regular issues
    - Option to convert subtask to standalone task instead of deletion
    - Automatically removes parent relationship when converting
    - Updates parent task relationships appropriately
    - Handles subtask not found gracefully with clear error messages

    Use this tool when:
    - You need to remove completed or obsolete subtasks
    - You want to promote a subtask to become an independent task
    - You're reorganizing task hierarchy and structure
    - You need to clean up subtasks that are no longer relevant

    Crucial Guardrails:
    - Use get_task first to verify subtask exists and check its status
    - Deletion is permanent and cannot be undone unless converted
    - Converting preserves subtask as standalone task with same ID
    - Don't use for changing subtask status - use update_task_status

    Args:
        subtask_id (str): Linear sub-issue ID to delete or convert. Must be a valid
            Linear sub-issue identifier. Sub-issues are regular Linear issues
            with a parent relationship. Format examples: "AUTH-124", "PROJ-457",
            "LOGIN-790". Case-sensitive and must match exactly.
        convert_to_task (bool, optional): Whether to convert subtask to standalone task instead
            of deleting. Default: false (as boolean, not string). When true, removes
            parent relationship making it a regular task. When false, permanently
            deletes the subtask from Linear.
            IMPORTANT: Pass as boolean value (true/false), NOT as string ("true"/"false").

    Returns:
        Dictionary with operation results. For deletion: confirmation of removal.
        For conversion: details of new standalone task including preserved ID
        and updated relationships.

    Example Usage:
        remove_subtask(subtask_id="AUTH-124")  # Delete subtask (convert_to_task defaults to false)
        remove_subtask(subtask_id="AUTH-124", convert_to_task=true)  # Convert to standalone task
        remove_subtask(subtask_id="AUTH-124", convert_to_task=false)  # Explicitly delete
    """
    config = mcp.state["config"]

    return remove_subtask_logic(
        api_key=config.linear_api_key,
        subtask_id=subtask_id,
        convert_to_task=convert_to_task,
    )
