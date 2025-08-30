"""MCP tool wrapper for unlink_tasks."""

from typing import Optional
from alfred.mcp import mcp
from alfred.core.task_relationships.unlink_tasks import unlink_tasks_logic


@mcp.tool
def unlink_tasks(
    task_id_1: str, task_id_2: str, relation_type: Optional[str] = None
) -> dict:
    """
    Remove a relationship between two tasks in Linear.

    This tool removes existing task relationships, such as blocking dependencies
    or other types of links between tasks.

    Key features:
    - Removes Linear issue relations between tasks
    - Searches both forward and inverse relationships
    - Optional filtering by relationship type
    - Handles bidirectional relationship removal
    - Returns confirmation of removed relationship

    Use this tool when:
    - You need to remove blocking relationships between tasks
    - Dependencies have changed and links are no longer needed
    - You want to clean up outdated task relationships
    - Task relationships need to be reorganized

    Crucial Guardrails:
    - Both tasks must exist for validation
    - Tool searches both directions for relationships
    - Returns clear message if no relationship exists
    - Safely handles non-existent relationships

    Args:
        task_id_1: Linear issue ID of the first task in the relationship
        task_id_2: Linear issue ID of the second task in the relationship
        relation_type: Optional filter for specific relation type (blocks, relates, duplicates)

    Returns:
        Dictionary with success status, message, and removed relationship details
    """
    config = mcp.state.config

    return unlink_tasks_logic(
        api_key=config.linear_api_key,
        task_id_1=task_id_1,
        task_id_2=task_id_2,
        relation_type=relation_type,
    )
