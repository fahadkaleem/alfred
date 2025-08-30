"""MCP tool wrapper for create_subtasks."""

from typing import Optional
from alfred.mcp import mcp
from alfred.core.tasks.create_subtasks import create_subtasks_logic
import asyncio


@mcp.tool
async def create_subtasks(
    task_id: str,
    num_subtasks: int = 3,
    context: Optional[str] = None,
    force: bool = False,
) -> dict:
    """
    Create AI-generated subtasks for a task.

    This tool creates detailed subtasks for a single Linear task using AI to analyze the task
    and generate actionable implementation steps. It creates actual Linear sub-issues with
    technical details and acceptance criteria.

    Key features:
    - AI-powered subtask generation with consistent structure
    - Automatic creation of subtasks as Linear sub-issues
    - Preserves parent task context and epic assignment
    - Includes technical implementation details and acceptance criteria
    - Supports forced regeneration of existing subtasks

    Use this tool when:
    - You need to break down a high-level task into implementable steps
    - You want to create a detailed work breakdown structure for a single task
    - You're planning sprint work and need to create subtasks for user stories
    - You need to regenerate subtasks with updated requirements

    Crucial Guardrails:
    - Use create_all_subtasks instead when you need to process multiple tasks
    - Use get_task first to verify task status if unsure about eligibility
    - Don't use this for completed or cancelled tasks
    - Don't use this tool repeatedly for the same task unless using force=True

    Usage:

    Before using this tool:
    - MUST have LINEAR_API_KEY configured in environment variables
    - MUST have ANTHROPIC_API_KEY configured for AI generation
    - SHOULD verify task exists and is eligible using get_task

    When creating subtasks:
    - Task must be in "pending" or "in_progress" status
    - Task cannot already have subtasks (unless force=True)
    - Each subtask will be created as a Linear sub-issue
    - Subtasks inherit the parent task's epic assignment
    - AI generates 3-7 subtasks based on complexity (or as specified)

    IMPORTANT:
    - Subtasks are actual Linear issues with parent relationships
    - Force parameter will DELETE all existing subtasks before creating new ones
    - Each subtask includes technical details and acceptance criteria
    - Generation may take 10-30 seconds depending on complexity

    WARNING:
    - Tool will fail if task_id doesn't exist
    - Tool will fail if task is completed or cancelled
    - Tool will fail if task has subtasks and force=False
    - Tool will fail if ANTHROPIC_API_KEY is not configured

    CRITICAL REQUIREMENTS:
    - task_id must be exact Linear issue identifier (e.g., "AUTH-123")
    - Task IDs are case-sensitive
    - Both LINEAR_API_KEY and ANTHROPIC_API_KEY must be valid

    Args:
        task_id: Linear task ID to create subtasks for. Must be exact task identifier
            like "AUTH-123", "PROJ-456". Case-sensitive and must exist in Linear.
            Task must be in "pending" or "in_progress" status.
        num_subtasks: Number of subtasks to generate. Default: 3. Recommended range: 3-7.
            Higher numbers may result in less detailed subtasks. AI will optimize based
            on task complexity.
        context: Additional context to guide subtask generation. Use to specify focus
            areas, technical constraints, or implementation preferences. Example:
            "Focus on test coverage and error handling" or "Use microservices architecture".
        force: Force creation even if subtasks exist. Default: false. When true, will
            DELETE all existing subtasks before creating new ones. Use with caution as
            this is irreversible.

    Returns:
        Dictionary with:
        - On success: Created subtasks with IDs and details
        - On error: Error code and message

    Error Codes:
        - TASK_NOT_FOUND: Specified task doesn't exist
        - TASK_HAS_SUBTASKS: Task already has subtasks and force=False
        - TASK_NOT_ELIGIBLE: Task is completed or cancelled
        - AI_SERVICE_ERROR: AI generation failed
        - LINEAR_API_KEY not configured
        - ANTHROPIC_API_KEY not configured

    Examples:
        # Basic usage with default settings
        create_subtasks(task_id="AUTH-123")

        # Specify number of subtasks
        create_subtasks(task_id="PROJ-456", num_subtasks=5)

        # Add context for specialized generation
        create_subtasks(
            task_id="SEC-789",
            num_subtasks=4,
            context="Focus on security best practices and threat modeling"
        )

        # Force regeneration of existing subtasks
        create_subtasks(
            task_id="API-321",
            force=True,
            context="Update for new API requirements"
        )
    """
    config = mcp.state["config"]

    # Validate API keys
    if not config.linear_api_key:
        return {"error": "LINEAR_API_KEY not configured"}

    if not config.anthropic_api_key:
        return {"error": "ANTHROPIC_API_KEY not configured for AI subtask generation"}

    try:
        result = await create_subtasks_logic(
            api_key=config.linear_api_key,
            task_id=task_id,
            num_subtasks=num_subtasks,
            context=context,
            force=force,
        )
        # Convert Pydantic model to dict for MCP response
        return {
            "success": True,
            "data": {
                "task_id": result.task_id,
                "task_title": result.task_title,
                "message": result.message,
                "subtasks": [
                    subtask.model_dump() for subtask in result.subtasks_created
                ],
            },
        }
    except ValueError as e:
        return {"error": "VALIDATION_ERROR", "message": str(e)}
    except Exception as e:
        return {"error": e.__class__.__name__, "message": str(e)}
