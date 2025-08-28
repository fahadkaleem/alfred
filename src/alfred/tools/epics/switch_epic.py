"""MCP tool wrapper for switch_epic."""

from alfred.core.epics.switch import switch_epic_logic
from alfred.config import get_config


def register(server) -> int:
    """Register the switch_epic tool."""

    @server.tool
    async def switch_epic(epic_id: str) -> dict:
        """
        Switch the active epic context for task operations.

        This tool changes the active epic/project context, which affects where new
        tasks are created by default and which epic is shown as "active" in status.

        Usage:
        - Use this tool to change your working context to a different epic
        - Use when you want new tasks to be assigned to a specific epic by default
        - Use to focus on a particular project/feature area
        - MUST have LINEAR_API_KEY configured in environment variables
        - Workspace must be initialized first using initialize_workspace

        IMPORTANT:
        - The epic must exist in your Linear workspace
        - Active epic is persisted in config and survives session restarts
        - Some tools may use the active epic as default when epic_id not specified
        - Switching epic does not move existing tasks

        WARNING:
        - Tool will fail if LINEAR_API_KEY is not set in environment
        - Tool will fail if Linear API key is invalid or expired
        - Tool will fail if epic_id doesn't exist in workspace

        Args:
            epic_id: The ID of the epic to switch to (required). Get this from list_epics.

        Returns:
        Dictionary with:
        - status: "ok" if successful
        - epic: Active epic object containing:
          - id: Epic ID
          - name: Epic name
          - description: Epic description (if available)
          - url: Linear URL for the epic
        - message: Success message
        - previous_epic_id: ID of the previously active epic (if any)
        """
        config = get_config()

        return await switch_epic_logic(api_key=config.linear_api_key, epic_id=epic_id)

    return 1  # One tool registered
