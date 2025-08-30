"""MCP tool wrapper for create_all_subtasks."""

from typing import Optional
from alfred.mcp import mcp
from alfred.core.tasks.create_subtasks import create_all_subtasks_logic
import asyncio


@mcp.tool
async def create_all_subtasks(
    epic_id: Optional[str] = None,
    num_subtasks: Optional[int] = None,
    context: Optional[str] = None,
    force: bool = False,
) -> dict:
    """
    Create subtasks for all eligible tasks using AI.

    This tool automatically creates subtasks for multiple tasks in a single operation. It
    processes all eligible tasks (pending/in-progress) and creates appropriate subtasks for
    each using AI analysis.

    Key features:
    - Batch processes all eligible tasks automatically
    - Filters by epic/project if specified
    - Skips completed/cancelled tasks automatically
    - Respects existing subtasks unless forced
    - Provides detailed progress reporting with statistics
    - Uses AI to generate context-appropriate subtasks

    Use this tool when:
    - You need to create subtasks for multiple tasks at project start
    - You want to prepare an entire epic for sprint planning
    - You're breaking down a backlog of high-level tasks
    - You need to standardize task granularity across a project

    Crucial Guardrails:
    - Use create_subtasks instead for single, specific task decomposition
    - Use get_tasks first to understand scope if filtering by epic
    - Don't use force=True without reviewing existing subtasks first
    - Don't use this for completed projects (will skip all tasks)

    Usage:

    Before using this tool:
    - MUST have platform API key configured in environment variables
    - MUST have ANTHROPIC_API_KEY configured for AI generation
    - CONSIDER using epic_id to limit scope for large projects
    - CONSIDER reviewing task list with get_tasks first

    Batch processing behavior:
    - Only processes tasks with status "pending" or "in_progress"
    - Skips tasks that already have subtasks (unless force=True)
    - Skips completed and cancelled tasks automatically
    - Processes tasks sequentially, not in parallel
    - Continues processing even if individual tasks fail

    IMPORTANT:
    - Processing time increases linearly with task count (5-15 seconds per task)
    - Large batches (>20 tasks) may take several minutes
    - Each task is processed independently - partial failures don't affect others
    - Results include detailed breakdown of success/skip/fail counts

    WARNING:
    - Tool will process ALL eligible tasks if no filters applied
    - Tool may take significant time for large task sets
    - force=True will DELETE existing subtasks for ALL processed tasks
    - Both API keys must remain valid for entire operation duration

    CRITICAL REQUIREMENTS:
    - platform API key and ANTHROPIC_API_KEY must both be configured
    - At least one eligible task must exist for processing
    - Epic ID (if provided) must be valid

    Args:
        epic_id: Filter tasks to specific epic/project. Only tasks in this epic will be
            processed. Must be valid platform project ID. If omitted, processes tasks from
            all epics.
        num_subtasks: Number of subtasks per task. Default: auto (3-5 based on heuristics).
            Applies same count to all tasks. Range: 1-10. Higher values may reduce detail
            quality.
        context: Additional context for all subtask generation. Applies to every task
            processed. Use for consistent themes like "Focus on testing" or "Emphasize
            documentation".
        force: Force regeneration even if tasks have subtasks. Default: false. When true,
            DELETES all existing subtasks before creating new ones for every processed
            task. Use with extreme caution.


    Returns:
        Dictionary with:
        - expanded_count: Number of tasks successfully processed
        - failed_count: Number of tasks that failed
        - skipped_count: Number of tasks skipped (completed/has subtasks)
        - results: Detailed results for each task processed with status and errors

    Error Codes:
        - platform API key not configured
        - ANTHROPIC_API_KEY not configured
        - Individual task errors included in results array

    Examples:
        # Create subtasks for all eligible tasks
        create_all_subtasks()

        # Process tasks in specific epic
        create_all_subtasks(epic_id="epic-auth-123")

        # Set consistent subtask count with context
        create_all_subtasks(
            num_subtasks=5,
            context="Focus on test coverage and documentation"
        )

        # Force regeneration for all tasks in epic
        create_all_subtasks(
            epic_id="epic-redesign-456",
            force=True,
            context="Updated requirements for v2"
        )
    """
    config = mcp.state.config

    # Validate API keys
    if not config.linear_api_key:
        return {"error": "platform API key not configured"}

    if not config.anthropic_api_key:
        return {"error": "ANTHROPIC_API_KEY not configured for AI subtask generation"}

    try:
        result = await create_all_subtasks_logic(
            config=config,
            epic_id=epic_id,
            num_subtasks=num_subtasks,
            context=context,
            force=force,
        )
        # Convert Pydantic model to dict for MCP response
        return {
            "success": True,
            "data": {
                "expanded_count": result.expanded_count,
                "failed_count": result.failed_count,
                "skipped_count": result.skipped_count,
                "message": result.message,
                "results": [r.model_dump() for r in result.results],
            },
        }
    except ValueError as e:
        return {"error": "VALIDATION_ERROR", "message": str(e)}
    except Exception as e:
        return {"error": e.__class__.__name__, "message": str(e)}
