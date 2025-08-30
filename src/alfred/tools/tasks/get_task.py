"""MCP tool wrapper for get_task."""

from alfred.mcp import mcp
from alfred.core.tasks.get import get_task_logic


@mcp.tool
def get_task(task_id: str) -> dict:
    """
    Fetch a single task by ID.

    This tool retrieves a specific task from Linear by its ID and returns complete
    task details mapped to Alfred's standardized format. It provides comprehensive
    task information including status, description, epic assignment, and all
    associated metadata.

    Key features:
    - Retrieves complete task details with all available fields
    - Automatic Linear → Alfred data model mapping
    - Detailed error reporting for non-existent or inaccessible tasks
    - Returns structured task object compatible with other Alfred tools
    - Includes task relationships and epic assignment information

    Use this tool when:
    - You need complete details for a specific task you know the ID of
    - You want to verify task status, description, or epic assignment before taking action
    - You're investigating task details for debugging or planning purposes
    - You need task information for reporting or documentation

    Crucial Guardrails:
    - Use get_tasks instead when you need to discover tasks by status, epic, or other criteria
    - Use create_task for creating new tasks, not retrieving existing ones
    - Don't use this for bulk task retrieval - use get_tasks with pagination instead
    - Task IDs must be exact matches - this tool doesn't search by partial IDs or titles

    Usage Guidance and Task ID Requirements:

    IMPORTANT: Task IDs in Linear follow specific naming conventions (e.g., "AUTH-123",
    "PROJ-456"). They are case-sensitive and must match exactly. Use discovery tools like
    get_tasks or list_projects if you need to find task IDs.

    CRITICAL: This tool returns comprehensive task data including potentially sensitive
    information like assignee details, internal notes, and project context. Ensure you
    have appropriate access permissions for the requested task.

    Task ID Format Requirements:
    - Must be complete Linear task identifier (e.g., "AUTH-123", not "123" or "auth-123")
    - Case-sensitive - "AUTH-123" is different from "auth-123"
    - Must exist in your accessible workspace/team context
    - Cannot be partial matches - exact ID required

    Response Data Completeness:
    - Includes all Linear task fields mapped to Alfred format
    - Contains epic/project assignment information if applicable
    - Includes current status with Alfred standardized naming
    - Provides creation and modification timestamps
    - May include assignee and label information when available

    Error Scenarios:
    - Non-existent task ID: Returns structured error with the attempted ID
    - Access denied: Returns error if task exists but you lack permissions
    - Invalid format: Returns error for malformed task IDs
    - Linear API issues: Returns error with Linear's specific error message

    Args:
        task_id: Linear task/issue ID to retrieve. Must be complete, exact task identifier
            following Linear's naming convention. Examples: "AUTH-123", "PROJ-456", "LOGIN-789".
            Case-sensitive and must match exactly - no partial matching or search capability.
            Task must exist in your accessible workspace/team. Use get_tasks or project
            management tools to discover task IDs if unknown.

    Returns:
        Dictionary with:
        - On success: Complete AlfredTask object with all fields
        - On not found: {'error': 'not_found', 'task_id': '<id>'}
    """
    config = mcp.state.config

    return get_task_logic(api_key=config.linear_api_key, task_id=task_id)
