"""MCP tool wrapper for bulk_update_tasks."""

from typing import Optional, List
from alfred.mcp import mcp
from alfred.core.tasks.bulk_update import bulk_update_tasks_logic


@mcp.tool
async def bulk_update_tasks(
    task_ids: List[str],
    prompt: str,
    research: Optional[bool] = False,
) -> dict:
    """
    Apply AI-generated updates to multiple tasks based on context changes.

    This tool applies AI-generated updates to multiple tasks in a single operation.
    It processes all provided task IDs and applies appropriate updates per task based
    on the context prompt. AI determines appropriate updates per task, batches
    platform API calls for efficiency, and provides progress updates during operation.

    Key features:
    - Bulk AI-powered updates to multiple tasks simultaneously
    - Efficient batching of platform API calls for performance
    - Individual task processing with error handling per task
    - Progress reporting and detailed results for each task
    - Preserves existing content while applying contextual updates

    Use this tool when:
    - You need to apply the same context change across multiple tasks
    - Requirements have changed affecting several related tasks
    - You want to enhance multiple tasks with new technical information
    - You need to update task priorities or descriptions in bulk

    Crucial Guardrails:
    - Use get_tasks first to verify task IDs exist before bulk updating
    - Large batches (>20 tasks) may take significant time to process
    - Each task is processed independently - partial failures don't affect others
    - Use update_task for single task updates instead of bulk operations

    Args:
        task_ids (List[str]): List of platform task IDs to update. Each must be a valid existing
            task ID in your workspace. Format examples: ["AUTH-123", "PROJ-456",
            "LOGIN-789"]. Task IDs are case-sensitive and must match exactly.
            Invalid task IDs will be skipped with warnings.
        prompt (str): Description of changes to apply to all tasks. Should describe the
            context change that affects all tasks. Examples: "Update to use new
            authentication API", "Add error handling requirements", "Include
            performance optimization considerations". Will be applied contextually
            to each task by AI.
        research (bool, optional): Whether to use research mode for enhanced updates with current
            best practices. Default: false (as boolean, not string). When true, AI will research current
            practices before applying updates to each task.
            IMPORTANT: Pass as boolean value (true/false), NOT as string ("true"/"false").

    Returns:
        Dictionary with bulk update results including count of updated tasks,
        detailed results per task showing what was updated, and any errors
        encountered during processing.

    Example Usage:
        bulk_update_tasks(task_ids=["AUTH-123", "PROJ-456"], prompt="Add security requirements")
        bulk_update_tasks(task_ids=["AUTH-123"], prompt="Update for new API", research=true)
    """
    config = mcp.state.config

    return await bulk_update_tasks_logic(
        config=config,
        task_ids=task_ids,
        prompt=prompt,
        research=research,
    )
