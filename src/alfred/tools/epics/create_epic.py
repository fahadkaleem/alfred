"""MCP tool wrapper for create_epic."""

from typing import Optional
from alfred.mcp import mcp
from alfred.core.epics.create import create_epic_logic


@mcp.tool
async def create_epic(name: str, description: Optional[str] = None) -> dict:
    """
    Create a new epic (project) in Linear for organizing related tasks and features.

    This tool creates a new epic/project container in your Linear workspace, which serves
    as a high-level grouping mechanism for related tasks, features, or initiatives.

    Key features:
    - Creates a new project container in Linear (called "epic" in Alfred terminology)
    - Returns the epic ID immediately for use in task assignment
    - Supports optional description for context and documentation
    - Automatically integrates with your Linear team workspace

    Use this tool when:
    - You need to start a new feature, initiative, or project area
    - You want to group related tasks under a common container
    - You're setting up project structure before creating tasks
    - You need to organize work into logical units for tracking

    Crucial Guardrails:
    - Use list_epics first to verify the name doesn't already exist
    - Use rename_epic instead if you need to modify an existing epic
    - Don't use this for creating individual tasks - use create_task instead

    Usage:

    Before using this tool:
    - MUST have LINEAR_API_KEY configured in environment variables
    - MUST have workspace initialized using initialize_workspace
    - Consider using list_epics first to check for existing similar epics

    When creating epics:
    - Choose descriptive, unique names that clearly indicate the epic's purpose
    - Add descriptions to provide context for team members
    - Epic names should follow your team's naming conventions
    - Created epics are immediately available for task assignment

    IMPORTANT:
    - Epics in Alfred map directly to Projects in Linear's terminology
    - Epic names should be unique within your workspace to avoid confusion
    - Once created, the epic ID is permanent and cannot be changed
    - Created epics appear immediately in Linear's UI and are accessible to all team members

    WARNING:
    - Tool will fail if LINEAR_API_KEY is not set in environment
    - Tool will fail if Linear API key is invalid or expired
    - Tool may fail if epic name already exists (depends on workspace settings)
    - Tool will fail if workspace is not initialized

    <example>
    User: Create a new epic for our Q1 authentication improvements
    Assistant: I'll create a new epic for the Q1 authentication improvements.
    *Uses create_epic tool with name="Q1 Authentication Improvements" and
    description="Security and UX improvements for authentication system in Q1 2024"*
    </example>

    <reasoning>
    1. The user needs a new project container for organizing authentication work
    2. create_epic is the correct tool for creating high-level project containers
    3. A descriptive name and context-providing description were included
    4. This epic can now be used as epic_id when creating related tasks
    </reasoning>

    <example>
    User: I need to create a task for implementing JWT tokens
    Assistant: To create a task, I should use the create_task tool, not create_epic.
    *Uses create_task tool instead, potentially with epic_id if one exists*
    </example>

    <reasoning>
    1. The user wants to create a task, not an epic/project container
    2. create_epic is for high-level project organization, not individual tasks
    3. create_task is the appropriate tool for individual work items
    4. Tasks can be assigned to epics using the epic_id parameter
    </reasoning>

    Parameters:

    name [string] (required) - The epic/project name. Should be descriptive, unique, and
        follow your team's naming conventions. Examples: "Q1 Authentication", "Mobile App v2",
        "Performance Optimization Sprint". Maximum length typically 255 characters.

    description [string] (optional) - Detailed description providing context about the epic's
        purpose, goals, or scope. Supports markdown formatting for better readability.
        Default: None (epic created without description). Include information like objectives,
        timeline, key stakeholders, or success criteria.

    Returns:
    Dictionary with:
    - status: "ok" if successful
    - epic: Created epic object containing:
        - id: Unique epic ID (use for task assignment and other operations)
        - name: Epic name as created
        - description: Epic description (if provided)
        - url: Direct Linear URL to view the epic
        - created_at: ISO timestamp of creation
        - updated_at: ISO timestamp of last modification
    - message: Human-readable success message
    """
    config = mcp.state["config"]

    return await create_epic_logic(
        api_key=config.linear_api_key, name=name, description=description
    )
