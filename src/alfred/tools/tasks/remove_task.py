"""MCP tool wrapper for remove_task."""

from typing import Optional, List
from alfred.mcp import mcp
from alfred.core.tasks.remove import remove_task_logic


@mcp.tool
def remove_task(
    task_ids: List[str],
    cascade_delete: Optional[bool] = False,
) -> dict:
    """
    Delete tasks from Linear with optional cascade deletion of subtasks.

    This tool deletes tasks from Linear via GraphQL. If cascade_delete=true,
    deletes all subtasks. If cascade_delete=false and task has subtasks,
    returns error. Confirms deletion before executing and handles task not
    found gracefully.

    Key features:
    - Deletes tasks via Linear GraphQL API with confirmation
    - Optional cascade deletion of all subtasks under parent
    - Safety check prevents accidental deletion of tasks with subtasks
    - Batch deletion support for multiple tasks simultaneously
    - Detailed error reporting for each task deletion attempt

    Use this tool when:
    - You need to clean up completed or obsolete tasks
    - You want to remove test or temporary tasks from workspace
    - You need to delete entire task hierarchies including subtasks
    - You're reorganizing project structure by removing old tasks

    Crucial Guardrails:
    - Use get_task first to verify task exists and check for subtasks
    - Deletion is permanent and cannot be undone
    - Use cascade_delete=True only when you want to delete subtasks too
    - Don't use for status changes - use update_task_status instead

    Args:
        task_ids (List[str]): List of Linear task/issue IDs to delete. Each must be a
            valid existing task ID in your workspace. Format examples:
            ["AUTH-123", "PROJ-456", "LOGIN-789"]. Task IDs are case-sensitive
            and must match exactly. Invalid task IDs will be reported in results.
        cascade_delete (bool, optional): Whether to force deletion of task with subtasks.
            Default: false (as boolean, not string). When false, deletion fails if task has subtasks
            (safety mechanism). When true, deletes task and ALL subtasks without
            further confirmation. Use with extreme caution.
            IMPORTANT: Pass as boolean value (true/false), NOT as string ("true"/"false").

    Returns:
        Dictionary with deletion results including count of removed tasks,
        detailed results per task, and any errors encountered during deletion.
        Includes information about subtasks deleted when cascade_delete=true.

    Example Usage:
        remove_task(task_ids=["AUTH-123"])  # Delete single task (cascade_delete defaults to false)
        remove_task(task_ids=["AUTH-123", "PROJ-456"], cascade_delete=false)  # Delete multiple, fail if subtasks
        remove_task(task_ids=["AUTH-123"], cascade_delete=true)  # Delete task and all its subtasks
    """
    config = mcp.state.config

    return remove_task_logic(
        api_key=config.linear_api_key,
        task_ids=task_ids,
        cascade_delete=cascade_delete,
    )
