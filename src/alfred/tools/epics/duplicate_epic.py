"""MCP tool wrapper for duplicate_epic."""

from typing import Optional
from alfred.mcp import mcp
from alfred.core.epics.duplicate import duplicate_epic_logic


@mcp.tool
async def duplicate_epic(epic_id: str, new_name: Optional[str] = None) -> dict:
    """
    Duplicate an epic (project) with all its tasks to create templates or variations.

    This tool creates a complete copy of an existing epic/project including all contained
    tasks. Useful for creating project templates, branching similar work, or setting up
    repeated project structures.

    Key features:
    - Creates exact copy of epic with new unique ID
    - Copies all tasks with titles, descriptions, and priorities
    - Resets all task statuses to "todo" for fresh start
    - Preserves task metadata but not dependencies
    - Generates new epic name automatically if not specified

    Use this tool when:
    - You need to create a project template from a successful epic
    - You want to branch off a variation of an existing project
    - You're setting up similar project structures for different teams/quarters
    - You need to experiment with changes without affecting the original
    - You want to create a backup before major modifications

    Crucial Guardrails:
    - Use list_epics first to verify source epic exists
    - Consider using get_tasks to review what will be copied
    - Be aware that large epics may take significant time to duplicate
    - Remember that task dependencies are NOT preserved in the copy

    Usage:

    Before using this tool:
    - MUST have LINEAR_API_KEY configured in environment variables
    - MUST have workspace initialized using initialize_workspace
    - SHOULD verify source epic_id exists using list_epics
    - CONSIDER checking task count with get_tasks if epic is large

    Duplication behavior:
    - Epic metadata (name, description) is copied
    - All tasks are copied with original titles and descriptions
    - Task priorities and labels are preserved where possible
    - ALL task statuses reset to "todo" (fresh start)
    - Task dependencies within the epic are NOT copied
    - Task IDs are regenerated (not preserved from original)

    IMPORTANT:
    - Duplicated tasks start with "todo" status regardless of original status
    - This is intentional to provide a clean slate for the new epic
    - Task dependencies are not preserved (Linear API limitation)
    - Large epics (>50 tasks) may take 10-30 seconds to duplicate
    - Each task is copied individually, so API rate limits may apply

    CRITICAL REQUIREMENTS:
    - Source epic_id must exist in your workspace
    - You must have permission to create epics and tasks
    - Sufficient API quota for creating epic + all tasks

    WARNING:
    - Tool will fail if LINEAR_API_KEY is not set in environment
    - Tool will fail if Linear API key is invalid or expired
    - Tool will fail if epic_id doesn't exist in workspace
    - Some tasks may fail to copy if API rate limits are exceeded
    - Very large epics (>100 tasks) may timeout or partially copy

    <example>
    User: Create a template from our Q1 authentication epic for Q2
    Assistant: I'll duplicate the Q1 authentication epic to create a Q2 template.
    *Uses list_epics to find "Q1 Authentication Improvements"*
    *Uses duplicate_epic with epic_id="abc-123" and new_name="Q2 Authentication Improvements"*
    Created "Q2 Authentication Improvements" with 24 tasks copied. All tasks are
    set to "todo" status for fresh start.
    </example>

    <reasoning>
    1. User wants to reuse Q1 epic structure for Q2
    2. duplicate_epic creates a complete copy with new ID
    3. Custom name provided to clearly identify Q2 version
    4. All tasks reset to "todo" for fresh Q2 planning
    </reasoning>

    <example>
    User: Make a backup copy of the mobile project before we restructure it
    Assistant: I'll create a backup copy of the mobile project epic.
    *Uses duplicate_epic with epic_id="mobile-123" (new_name defaults to "Mobile App (Copy)")*
    Created backup "Mobile App (Copy)" with 45 tasks. You can now safely
    restructure the original epic.
    </example>

    <reasoning>
    1. User wants backup before making changes
    2. No custom name needed - default "(Copy)" suffix is clear
    3. Duplicate serves as snapshot of current state
    4. Original epic can now be modified without data loss
    </reasoning>

    <example>
    User: Set up the standard onboarding project for the new team
    Assistant: I'll duplicate our standard onboarding template epic for the new team.
    *Uses list_epics to find "Onboarding Template"*
    *Uses duplicate_epic with epic_id="template-789" and new_name="Team Alpha Onboarding"*
    Created "Team Alpha Onboarding" project with 12 standard onboarding tasks.
    </example>

    <reasoning>
    1. Standard template epic exists for reuse
    2. duplicate_epic preserves all template structure
    3. Custom name identifies the specific team
    4. Tasks start fresh as "todo" for new team
    </reasoning>

    Parameters:

    epic_id [string] (required) - The unique identifier of the source epic to duplicate.
        Must be exact epic ID from Linear (e.g., "abc123-def456-789"). Get this using
        list_epics. The epic must exist and be accessible in your workspace.

    new_name [string] (optional) - Custom name for the duplicated epic. If not provided,
        defaults to "[Original Name] (Copy)". Should be descriptive and unique to avoid
        confusion. Maximum length typically 255 characters.

    Returns:
    Dictionary with:
    - status: "ok" if successful
    - epic: New epic object containing:
      - id: Unique ID of the new epic (different from source)
      - name: Name of the new epic
      - description: Epic description (copied from source)
      - url: Direct Linear URL for the new epic
    - source_epic: Information about the original epic:
      - id: Source epic ID
      - name: Source epic name
    - tasks_copied: Number of tasks successfully duplicated
    - message: Summary of the duplication operation
    """
    config = mcp.state.config

    return await duplicate_epic_logic(
        api_key=config.linear_api_key, epic_id=epic_id, new_name=new_name
    )
