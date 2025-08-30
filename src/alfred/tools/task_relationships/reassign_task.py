"""MCP tool wrapper for reassign_task."""

from alfred.mcp import mcp
from alfred.core.task_relationships.reassign_task import reassign_task_logic


@mcp.tool
def reassign_task(task_id: str, target_epic_id: str) -> dict:
    """
    Move a task from one epic to another in Linear.

    This tool reassigns tasks between epics (projects) in Linear, allowing for
    task organization and project restructuring while preserving task relationships
    and metadata.

    Key features:
    - Moves tasks between Linear projects/epics
    - Preserves task relationships and subtasks
    - Updates project assignment in Linear
    - Returns updated task information with new epic
    - Validates both task and target epic exist

    Use this tool when:
    - Project scope changes require task reorganization
    - Tasks need to be moved to different epics for better organization
    - You're restructuring projects and need to redistribute tasks
    - Tasks were created in wrong epic and need relocation

    Crucial Guardrails:
    - Validates both task and target epic exist before moving
    - Prevents unnecessary moves (task already in target epic)
    - Preserves all task relationships and dependencies
    - Maintains task history and metadata

    Args:
        task_id: Linear issue ID of the task to move
        target_epic_id: Linear project/epic ID where task should be moved

    Returns:
        Dictionary with success status, message, and updated task details
    """
    config = mcp.state.config

    return reassign_task_logic(
        api_key=config.linear_api_key,
        task_id=task_id,
        target_epic_id=target_epic_id,
    )
