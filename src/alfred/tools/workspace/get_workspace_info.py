"""MCP tool wrapper for get_workspace_info."""

from alfred.core.workspace.info import get_workspace_info_logic


def register(server) -> int:
    """Register the get_workspace_info tool."""

    @server.tool
    async def get_workspace_info() -> dict:
        """
        Get current workspace configuration and status.

        This tool retrieves the current workspace configuration and validates the
        connection status to Linear.

        Usage:
        - Use this tool to check if Alfred is properly configured
        - Use to verify workspace connection before performing operations
        - Use to debug configuration issues
        - No parameters required - reads from saved configuration

        IMPORTANT:
        - Returns different status values based on configuration state
        - Will attempt to validate Linear connection if API key is available
        - Does not require any parameters

        Returns:
        Dictionary with:
        - status: "configured" or "not_configured"
        - connection_status: "connected", "not_connected", or "connection_failed"
        - platform: Current platform ("linear" or "jira")
        - workspace: Object with id and name of current workspace
        - team: Object with id and name of current team
        - active_epic_id: Currently active epic/project ID if set
        - has_api_key: Boolean indicating if API key is configured
        - has_ai_config: Boolean indicating if AI services are configured
        """
        return await get_workspace_info_logic()

    return 1  # One tool registered
