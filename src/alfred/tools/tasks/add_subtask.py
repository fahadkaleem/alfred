"""MCP tool wrapper for add_subtask."""

from typing import Optional
from alfred.mcp import mcp
from alfred.core.tasks.add_subtask import add_subtask_logic


@mcp.tool
def add_subtask(
    parent_id: str,
    title: str,
    description: Optional[str] = None,
    assignee_id: Optional[str] = None,
) -> dict:
    """
    Create subtasks under existing tasks for detailed implementation breakdown.

    This tool creates Linear sub-issues under parent tasks. Subtasks inherit
    epic and labels from parent task, are set to initial status "todo", and
    validate that parent task exists before creation.

    Key features:
    - Creates Linear sub-issue under parent task relationship
    - Inherits epic assignment and labels from parent automatically
    - Sets initial status to "todo" for new work items
    - Validates parent task exists before creating subtask
    - Returns created subtask with assigned ID for reference

    Use this tool when:
    - You need to break down a large task into smaller work items
    - You want to create specific implementation steps under a user story
    - You need to assign different aspects of work to different team members
    - You're creating a work breakdown structure for complex features

    Crucial Guardrails:
    - Use get_task first to verify parent task exists
    - Use create_subtasks for AI-powered subtask generation instead
    - Don't use this for creating independent tasks - use create_task
    - Parent task must be accessible and not completed

    Args:
        parent_id: Linear task/issue ID to add subtask under. Must be a valid
            existing task ID in your workspace. Format examples: "AUTH-123",
            "PROJ-456", "LOGIN-789". Task IDs are case-sensitive and must
            match exactly. This will become the parent of the new sub-issue.
        title: Title for the new subtask. Should be specific and actionable
            describing the work to be done. Examples: "Write unit tests for
            validation", "Implement error handling for API calls", "Create
            database migration for new schema".
        description: Detailed description of the subtask work including
            technical requirements, acceptance criteria, or implementation
            notes. Default: empty string. Can include markdown formatting
            for better readability.
        assignee_id: User ID to assign subtask to. Currently accepted but
            assignment may not be implemented in Linear integration. Default:
            null (unassigned). Use Linear web interface for assignment if
            needed.

    Returns:
        Dictionary with created subtask object including Linear sub-issue ID,
        parent relationship, and inherited properties from parent task.
    """
    config = mcp.state["config"]

    return add_subtask_logic(
        api_key=config.linear_api_key,
        parent_id=parent_id,
        title=title,
        description=description,
        assignee_id=assignee_id,
    )
