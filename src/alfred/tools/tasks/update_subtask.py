"""MCP tool wrapper for update_subtask."""

from typing import Optional
from alfred.mcp import mcp
from alfred.core.tasks.update_subtask import update_subtask_logic


@mcp.tool
async def update_subtask(
    subtask_id: str,
    prompt: str,
    research: Optional[bool] = False,
) -> dict:
    """
    Appends timestamped information to a specific subtask without replacing existing content.

    This tool appends new information to subtask description with timestamps to preserve
    history. Does not overwrite existing content, only adds new timestamped entries.
    Updates subtask modified timestamp and returns updated subtask.

    Key features:
    - Appends new information to subtask description with timestamp
    - Preserves all existing content without overwriting
    - AI-enhanced content generation with contextual awareness
    - Updates subtask modified timestamp
    - Optional research mode for enhanced information

    Use this tool when:
    - You need to log implementation progress on a subtask
    - You want to add notes or findings without losing existing content
    - You need to document issues or solutions discovered during implementation
    - You want to append research findings or updated requirements

    Crucial Guardrails:
    - Use get_task to check current subtask state first
    - This only appends content - use update_task for full subtask updates
    - Don't use for changing subtask status - use update_task_status
    - Subtask ID must be a valid platform sub-issue ID

    Args:
        subtask_id: platform sub-issue ID to update. Must be a valid platform sub-issue
            identifier. Sub-issues in platform are regular issues with a parent relationship.
            Format examples: "AUTH-124", "PROJ-457", "LOGIN-790". Case-sensitive and
            must match exactly.
        prompt: Information to add to the subtask. Should describe what information
            to append. Examples: "Found performance issue with current approach",
            "Implemented validation using Joi library", "Need to handle edge case for
            empty input arrays". Will be enhanced with AI context if research=True.
        research: Whether to use research mode for enhanced content generation.
            Default: False. When enabled, AI will research current practices and
            enhance the appended content with up-to-date technical information.

    Returns:
        Dictionary with updated subtask object containing the appended information
        and updated timestamp showing when the information was added.
    """
    config = mcp.state.config

    return await update_subtask_logic(
        config=config,
        subtask_id=subtask_id,
        prompt=prompt,
        research=research,
    )
