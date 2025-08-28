"""MCP tool wrapper for list_epics."""

from alfred.core.epics.list import list_epics_logic
from alfred.config import get_config


def register(server) -> int:
    """Register the list_epics tool."""

    @server.tool
    async def list_epics() -> dict:
        """
        List all epics (projects) in the Linear workspace.

        This tool retrieves all epics/projects in the Linear workspace, which are
        high-level containers for organizing related tasks.

        Usage:
        - Use this tool to discover available epics for task organization
        - Use to get epic IDs for task assignment
        - Use to view epic metadata like descriptions and URLs
        - MUST have LINEAR_API_KEY configured in environment variables
        - Workspace must be initialized first using initialize_workspace

        IMPORTANT:
        - In Linear terminology, "projects" are mapped as "epics" in Alfred
        - Returns up to 100 epics (Linear API limit)
        - Requires valid LINEAR_API_KEY in environment
        - No filtering or search parameters available

        WARNING:
        - Tool will fail if LINEAR_API_KEY is not set in environment
        - Tool will fail if Linear API key is invalid or expired
        - May return empty array if no epics exist

        Returns:
        Dictionary with:
        - status: "ok" if successful
        - projects: Array of epic objects, each containing:
          - id: Epic ID
          - name: Epic name
          - description: Epic description (if available)
          - url: Linear URL for the epic (if available)
        - count: Total number of epics returned
        """
        config = get_config()

        return await list_epics_logic(api_key=config.linear_api_key)

    return 1  # One tool registered
