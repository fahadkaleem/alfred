"""MCP tool wrapper for delete_epic."""

from alfred.core.epics.delete import delete_epic_logic
from alfred.config import get_config


def register(server) -> int:
    """Register the delete_epic tool."""

    @server.tool
    async def delete_epic(epic_id: str, delete_tasks: bool = False) -> dict:
        """
        Delete an epic (project) from Linear, optionally with its tasks.

        This tool removes an epic/project from your Linear workspace. By default,
        it will fail if the epic contains tasks unless you explicitly set
        delete_tasks=True.

        Usage:
        - Use this tool to remove completed or obsolete epics
        - Use to clean up test or temporary epics
        - Use with caution as deletion cannot be undone
        - MUST have LINEAR_API_KEY configured in environment variables
        - Workspace must be initialized first using initialize_workspace

        IMPORTANT:
        - The epic must exist in your Linear workspace
        - Cannot delete the last epic in the workspace
        - By default, fails if epic contains tasks (safety feature)
        - Setting delete_tasks=True will permanently delete all tasks
        - Deletion is permanent and cannot be undone

        WARNING:
        - Tool will fail if LINEAR_API_KEY is not set in environment
        - Tool will fail if Linear API key is invalid or expired
        - Tool will fail if epic_id doesn't exist in workspace
        - Tool will fail if epic has tasks and delete_tasks is False
        - Tool will fail if trying to delete the last epic

        Args:
            epic_id: The ID of the epic to delete (required). Get this from list_epics.
            delete_tasks: Whether to delete all tasks in the epic (default: False).
                         If False and epic has tasks, the operation will fail.
                         If True, all tasks in the epic will be permanently deleted.

        Returns:
        Dictionary with:
        - status: "ok" if successful
        - deleted_epic: Information about the deleted epic:
          - id: Epic ID that was deleted
          - name: Epic name that was deleted
        - tasks_deleted: Number of tasks deleted (0 if delete_tasks was False)
        - message: Confirmation message with details
        """
        config = get_config()

        return await delete_epic_logic(
            api_key=config.linear_api_key, epic_id=epic_id, delete_tasks=delete_tasks
        )

    return 1  # One tool registered
