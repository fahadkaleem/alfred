"""MCP tool wrapper for duplicate_epic."""

from typing import Optional
from alfred.core.epics.duplicate import duplicate_epic_logic
from alfred.config import get_config


def register(server) -> int:
    """Register the duplicate_epic tool."""

    @server.tool
    async def duplicate_epic(epic_id: str, new_name: Optional[str] = None) -> dict:
        """
        Duplicate an epic (project) with all its tasks in Linear.

        This tool creates a copy of an existing epic/project including all its tasks.
        The duplicated tasks will have the same titles, descriptions, and priorities
        but will start with "todo" status.

        Usage:
        - Use this tool to create templates from existing epics
        - Use to branch off a new version of a project
        - Use to create similar project structures
        - MUST have LINEAR_API_KEY configured in environment variables
        - Workspace must be initialized first using initialize_workspace

        IMPORTANT:
        - The source epic must exist in your Linear workspace
        - All tasks are copied with "todo" status regardless of original status
        - Task dependencies within the epic are NOT preserved
        - Labels and priorities are preserved where possible
        - Large epics may take time to duplicate

        WARNING:
        - Tool will fail if LINEAR_API_KEY is not set in environment
        - Tool will fail if Linear API key is invalid or expired
        - Tool will fail if epic_id doesn't exist in workspace
        - Some tasks may fail to copy if there are API limits

        Args:
            epic_id: The ID of the epic to duplicate (required). Get this from list_epics.
            new_name: Optional name for the new epic. Defaults to "Original Name (Copy)".

        Returns:
        Dictionary with:
        - status: "ok" if successful
        - epic: New epic object containing:
          - id: New epic ID
          - name: New epic name
          - description: Epic description (if available)
          - url: Linear URL for the new epic
        - source_epic: Original epic information
        - tasks_copied: Number of tasks successfully copied
        - message: Success message with details
        """
        config = get_config()

        return await duplicate_epic_logic(
            api_key=config.linear_api_key, epic_id=epic_id, new_name=new_name
        )

    return 1  # One tool registered
