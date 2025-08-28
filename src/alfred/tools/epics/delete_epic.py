"""MCP tool wrapper for delete_epic."""

from alfred.core.epics.delete import delete_epic_logic
from alfred.config import get_config


def register(server) -> int:
    """Register the delete_epic tool."""

    @server.tool
    async def delete_epic(epic_id: str, delete_tasks: bool = False) -> dict:
        """
        Delete an epic (project) from Linear with built-in safety mechanism for task preservation.

        This tool permanently removes an epic/project from your Linear workspace. It includes
        a safety mechanism that prevents accidental deletion of epics containing tasks unless
        explicitly authorized.

        Key features:
        - Deletes epics/projects from Linear workspace permanently
        - Safety mechanism prevents accidental task deletion (fails if epic has tasks)
        - Optional force deletion of epic with all contained tasks
        - Returns count of deleted tasks for audit purposes
        - Validates epic exists before attempting deletion

        Use this tool when:
        - You need to remove completed or obsolete epics that are no longer needed
        - You want to clean up test or temporary epics after experiments
        - You're reorganizing project structure and removing redundant containers
        - You need to delete an epic and all its tasks (with explicit permission)

        Crucial Guardrails:
        - Use list_epics first to verify the epic exists and check its contents
        - Use get_tasks with epic_id filter to review tasks before deletion
        - Never use delete_tasks=True without reviewing the task list first
        - Consider using duplicate_epic to backup before deletion if unsure

        Usage:

        Before using this tool:
        - MUST have LINEAR_API_KEY configured in environment variables
        - MUST have workspace initialized using initialize_workspace
        - ALWAYS use list_epics to verify epic_id and review epic name
        - STRONGLY RECOMMENDED to check tasks with get_tasks(epic_id=...) first

        Safety mechanism:
        - By default (delete_tasks=False), the tool will FAIL if epic contains any tasks
        - This prevents accidental data loss from deleting epics with active work
        - To delete an epic with tasks, you must explicitly set delete_tasks=True
        - When delete_tasks=True, ALL tasks in the epic are permanently deleted

        IMPORTANT:
        - Deletion is PERMANENT and cannot be undone - there is no recovery mechanism
        - Cannot delete the last remaining epic in the workspace (Linear requirement)
        - All task data including comments, attachments, and history is lost
        - Deleted epic IDs cannot be reused
        - Team members will immediately lose access to deleted epics and tasks

        CRITICAL REQUIREMENTS:
        - The epic_id must exist in your Linear workspace
        - The epic_id must be exact - partial matches are not supported
        - You cannot delete an epic that other users are actively working in

        WARNING:
        - Tool will fail if LINEAR_API_KEY is not set in environment
        - Tool will fail if Linear API key is invalid or expired
        - Tool will fail if epic_id doesn't exist in workspace
        - Tool will fail if epic has tasks and delete_tasks=False (safety mechanism)
        - Tool will fail if attempting to delete the last epic in workspace
        - Tool will fail if epic is locked or protected by workspace settings

        <example>
        User: Delete the test epic we created yesterday (id: abc-123)
        Assistant: I'll first check if the test epic has any tasks before deleting it.
        *Uses get_tasks with epic_id="abc-123" to check for tasks*
        The epic has no tasks, so I can safely delete it.
        *Uses delete_epic with epic_id="abc-123" and delete_tasks=False*
        </example>

        <reasoning>
        1. The user wants to delete a test epic that's no longer needed
        2. Before deletion, checking for tasks prevents accidental data loss
        3. Since no tasks exist, using delete_tasks=False is appropriate
        4. The safety mechanism would prevent deletion if tasks were found
        </reasoning>

        <example>
        User: Remove the old Q3 project and all its completed tasks (id: xyz-789)
        Assistant: I'll delete the Q3 project epic along with all its tasks as requested.
        Since you explicitly want to delete all tasks, I'll use the force deletion option.
        *Uses delete_epic with epic_id="xyz-789" and delete_tasks=True*
        </example>

        <reasoning>
        1. The user explicitly requested deletion of both epic and tasks
        2. delete_tasks=True is required to delete an epic with tasks
        3. The user's clear intent to delete "all its completed tasks" authorizes this
        4. No additional checking needed since deletion is explicitly requested
        </reasoning>

        <example>
        User: Clean up our workspace by removing empty epics
        Assistant: I'll list all epics first, then check each for tasks before deletion.
        *Uses list_epics to get all epic IDs*
        *For each epic, uses get_tasks to check if empty*
        *Only uses delete_epic with delete_tasks=False on truly empty epics*
        </example>

        <reasoning>
        1. Multiple epics need to be checked before deletion
        2. Using list_epics provides the complete list to work through
        3. Checking each epic for tasks ensures no accidental data loss
        4. delete_tasks=False ensures safety - will fail if tasks are found
        </reasoning>

        Parameters:

        epic_id [string] (required) - The unique identifier of the epic to delete. Must be the
            exact epic ID from Linear (e.g., "abc123-def456-789"). Get this from list_epics
            or from previous epic creation. Case-sensitive and must match exactly.

        delete_tasks [boolean] (optional) - Controls whether to force deletion of epic with tasks.
            Default: False (safety mechanism active). When False, deletion fails if epic contains
            any tasks. When True, permanently deletes the epic and ALL contained tasks without
            further confirmation. Use with extreme caution.

        Returns:
        Dictionary with:
        - status: "ok" if successful
        - deleted_epic: Object containing:
          - id: The ID of the deleted epic
          - name: The name of the deleted epic (for confirmation)
        - tasks_deleted: Number of tasks that were deleted (0 if delete_tasks=False)
        - message: Human-readable confirmation with deletion details
        """
        config = get_config()

        return await delete_epic_logic(
            api_key=config.linear_api_key, epic_id=epic_id, delete_tasks=delete_tasks
        )

    return 1  # One tool registered
