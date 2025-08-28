"""MCP tool wrapper for create_epic."""

from typing import Optional
from alfred.core.epics.create import create_epic_logic
from alfred.config import get_config


def register(server) -> int:
    """Register the create_epic tool."""

    @server.tool
    async def create_epic(name: str, description: Optional[str] = None) -> dict:
        """
        Create a new epic (project) in Linear.

        This tool creates a new epic/project in your Linear workspace for organizing
        related tasks and features.

        Usage:
        - Use this tool to create new epics for feature groupings
        - Use to organize tasks into logical projects
        - Epic IDs from created epics can be used when creating tasks
        - MUST have LINEAR_API_KEY configured in environment variables
        - Workspace must be initialized first using initialize_workspace

        IMPORTANT:
        - Epic names should be unique within your workspace
        - Created epics are immediately available for task assignment
        - Epics map to Linear Projects in the underlying API

        WARNING:
        - Tool will fail if LINEAR_API_KEY is not set in environment
        - Tool will fail if Linear API key is invalid or expired
        - May fail if epic name already exists (depending on workspace settings)

        Args:
            name: Epic/project name (required). Should be descriptive and unique.
            description: Optional description providing more context about the epic.

        Returns:
        Dictionary with:
        - status: "ok" if successful
        - epic: Created epic object containing:
          - id: Epic ID for use in task assignment
          - name: Epic name
          - description: Epic description (if provided)
          - url: Linear URL for the epic
          - created_at: Creation timestamp
          - updated_at: Last update timestamp
        - message: Success message
        """
        config = get_config()

        return await create_epic_logic(
            api_key=config.linear_api_key, name=name, description=description
        )

    return 1  # One tool registered
