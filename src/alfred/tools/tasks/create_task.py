"""MCP tool wrapper for create_task."""

from typing import Optional, List
from alfred.mcp import mcp
from alfred.core.tasks.create import create_task_logic


@mcp.tool
def create_task(
    title: str,
    description: Optional[str] = None,
    epic_id: Optional[str] = None,
    assignee_id: Optional[str] = None,
    labels: Optional[List[str]] = None,
    priority: Optional[str] = None,
) -> dict:
    """
    Create a new task in the configured platform (Linear/Jira).

    This tool creates a new task with specified details and returns the
    created task mapped to Alfred's standardized format. It handles task creation
    with optional epic assignment, descriptions, and future extensibility for labels
    and priorities.

    Key features:
    - Creates tasks with platform API integration and immediate persistence
    - Automatic task ID generation following platform naming conventions
    - Epic/project assignment for organized task management
    - Extensible design for future label and priority support
    - Returns complete created task object for verification and reference

    Use this tool when:
    - You need to create new work items or feature requests
    - You want to break down larger epics into specific implementable tasks
    - You're capturing requirements or bugs as actionable tasks
    - You need to create tasks during planning or specification processes

    Crucial Guardrails:
    - Use get_tasks or list_projects first to discover epic IDs if assigning to specific projects
    - Use update_task_status afterward if you need to immediately change the status from default
    - Don't use this for updating existing tasks - use update_task or update_task_status
    - Don't use this for creating epics/projects - use epic management tools instead

    Usage Guidance and Task Creation Best Practices:

    IMPORTANT: Tasks are created with the platform's default status ("todo") which maps to Alfred's
    "pending" status. Use update_task_status immediately after creation if you need a different
    initial status.

    CRITICAL: The title parameter is the only required field. However, providing a clear
    description significantly improves task usefulness and reduces ambiguity for team members.

    Epic Assignment Guidelines:
    - Epic assignment is optional but highly recommended for organized workspaces
    - Use list_projects tool first to discover available epic IDs
    - Epic IDs must be valid and accessible to your team
    - Tasks without epic assignment go to the default team backlog

    Field Limitations (Current Implementation):
    - assignee_id: Parameter accepted but assignment not yet implemented
    - labels: Parameter accepted but label assignment not yet implemented
    - priority: Parameter accepted but priority setting not yet implemented
    - These fields are preserved for future versions - they won't cause errors

    Best Practices for Task Creation:
    - Use descriptive, actionable titles: "Implement user login validation" not "Login stuff"
    - Include technical context in descriptions for development tasks
    - Reference related tasks or epics in descriptions when applicable
    - Create atomic tasks that can be completed in reasonable timeframes

    Args:
        title: Task title that clearly describes the work to be done. Should be concise but
            specific enough to understand the scope. Examples: "Implement user login validation",
            "Fix password reset email template", "Add error handling for API timeouts". Avoid
            vague titles like "Fix stuff" or "Update code". Maximum length follows Linear's
            limits (typically 255 characters).
        description: Detailed description of the task including technical requirements, acceptance
            criteria, or implementation notes. Supports markdown formatting. Include context that
            helps team members understand the work without additional research. Default: empty string.
            Can be updated later using update_task tool.
        epic_id: Project/epic ID to assign this task to. Must be a valid project ID accessible
            to your team. Use list_projects tool to discover available epic IDs. Format varies
            by platform. Default: task goes to team's default backlog. Invalid epic IDs will
            cause task creation to fail.
        assignee_id: User ID to assign task to. Currently accepted but assignment not yet implemented
            in platform integration. Parameter preserved for future versions. Default: null (unassigned).
            Use platform web interface for assignment until API integration is complete.
        labels: Array of label names to apply to task. Currently accepted but labels not yet applied
            in platform integration. Parameter preserved for future versions. Default: empty list.
            Example: ["bug", "frontend", "high-priority"]. Use platform web interface for labeling
            until API integration is complete.
        priority: Task priority level. Currently accepted but priority not yet set in platform integration.
            Parameter preserved for future versions. Valid values: "low", "medium", "high", "urgent".
            Default: null (platform default). Use platform web interface for priority setting until API
            integration is complete.

    Returns:
        Dictionary with complete AlfredTask object representing the created task
    """
    config = mcp.state.config

    return create_task_logic(
        config=config,
        title=title,
        description=description,
        epic_id=epic_id,
        assignee_id=assignee_id,
        labels=labels,
        priority=priority,
    )
