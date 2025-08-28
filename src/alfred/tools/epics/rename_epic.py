"""MCP tool wrapper for rename_epic."""

from alfred.core.epics.rename import rename_epic_logic
from alfred.config import get_config


def register(server) -> int:
    """Register the rename_epic tool."""

    @server.tool
    async def rename_epic(epic_id: str, new_name: str) -> dict:
        """
        Rename an existing epic (project) in Linear.

        This tool updates the name of an existing epic/project in your Linear workspace.

        Usage:
        - Use this tool to rename epics for better clarity
        - Use when project scope or focus changes
        - Use to fix typos or improve naming conventions
        - MUST have LINEAR_API_KEY configured in environment variables
        - Workspace must be initialized first using initialize_workspace

        IMPORTANT:
        - The epic must exist in your Linear workspace
        - New name should be unique within your workspace
        - Renaming doesn't affect tasks already in the epic
        - Change is immediate and visible in Linear

        WARNING:
        - Tool will fail if LINEAR_API_KEY is not set in environment
        - Tool will fail if Linear API key is invalid or expired
        - Tool will fail if epic_id doesn't exist in workspace
        - May fail if new name already exists (depending on workspace settings)

        Args:
            epic_id: The ID of the epic to rename (required). Get this from list_epics.
            new_name: The new name for the epic (required). Should be descriptive and unique.

        Returns:
        Dictionary with:
        - status: "ok" if successful
        - epic: Updated epic object containing:
          - id: Epic ID
          - name: New epic name
          - description: Epic description (if available)
          - url: Linear URL for the epic
          - updated_at: Last update timestamp
        - message: Success message
        - old_name: Previous name of the epic
        """
        config = get_config()

        return await rename_epic_logic(
            api_key=config.linear_api_key, epic_id=epic_id, new_name=new_name
        )

    return 1  # One tool registered
