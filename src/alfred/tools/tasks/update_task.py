"""MCP tool wrapper for update_task."""

from typing import Optional
from alfred.mcp import mcp
from alfred.core.tasks.update import update_task_logic


@mcp.tool
async def update_task(
    task_id: str,
    prompt: str,
    research: Optional[bool] = False,
    append: Optional[bool] = False,
) -> dict:
    """
    Updates a single task by ID with new information or context provided in the prompt.

    This tool uses AI to enhance task with additional context. It accepts task_id and
    update_prompt, then uses AI to analyze the prompt and intelligently update task fields.
    Can update description, labels, priority, and custom fields while preserving existing
    content and adding new information.

    Key features:
    - AI-enhanced task updates with intelligent field modification
    - Preserves existing content while adding new information
    - Supports both full updates and append-only mode
    - Optional research mode for enhanced context
    - Returns updated task with change summary

    Use this tool when:
    - You need to update task details based on new requirements
    - You want to add implementation notes or context to existing tasks
    - You need to modify task priority or labels based on changing needs
    - You want to enhance task descriptions with additional research

    Crucial Guardrails:
    - Use get_task first to understand current task state
    - Use update_task_status for status changes only
    - Don't use this for creating new tasks - use create_task
    - Use append=True to add info without overwriting existing content

    Args:
        task_id (str): Linear task/issue ID to update. Must be a valid existing task ID in your
            workspace. Format examples: "AUTH-123", "PROJ-456", "LOGIN-789". Task IDs are
            case-sensitive and must match exactly.
        prompt (str): Description of changes to make or new context to incorporate. Should be
            specific about what aspects of the task need updating. Examples: "Add error
            handling requirements", "Update to use new authentication API", "Include
            performance optimization notes".
        research (bool, optional): Whether to use research mode. Default: false (as boolean, not string).
            When true, AI will research current practices before applying updates.
            IMPORTANT: Pass as boolean value (true/false), NOT as string ("true"/"false").
        append (bool, optional): Whether to append information instead of full update. Default: false (as boolean).
            When true, adds timestamped information to task description. When false,
            performs full AI analysis and updates multiple task fields.
            IMPORTANT: Pass as boolean value (true/false), NOT as string ("true"/"false").

    Returns:
        Dictionary with updated AlfredTask object containing all modified fields and
        change summary showing what was updated.

    Example Usage:
        update_task(task_id="AUTH-123", prompt="Add error handling", research=false, append=false)
        update_task(task_id="AUTH-123", prompt="Implementation notes", append=true)  # research defaults to false
    """
    config = mcp.state["config"]

    return await update_task_logic(
        api_key=config.linear_api_key,
        task_id=task_id,
        prompt=prompt,
        research=research,
        append=append,
    )
