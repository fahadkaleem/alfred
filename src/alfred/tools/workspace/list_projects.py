"""MCP tool wrapper for list_projects."""

from alfred.mcp import mcp
from alfred.core.workspace.projects import list_projects_logic


@mcp.tool
async def list_projects() -> dict:
    """
    List all projects (epics) in the Linear workspace.

    This tool retrieves all projects/epics in the Linear workspace, which are
    high-level containers for organizing related tasks.

    Usage:
    - Use this tool to discover available projects for task organization
    - Use to get project IDs for task assignment
    - Use to view project metadata like descriptions and URLs
    - MUST have LINEAR_API_KEY configured in environment variables
    - Workspace must be initialized first using initialize_workspace

    IMPORTANT:
    - In Linear terminology, "projects" are often called "epics"
    - Returns up to 100 projects (Linear API limit)
    - Requires valid LINEAR_API_KEY in environment
    - No filtering or search parameters available

    WARNING:
    - Tool will fail if LINEAR_API_KEY is not set in environment
    - Tool will fail if Linear API key is invalid or expired
    - May return empty array if no projects exist

    Returns:
    Dictionary with:
    - status: "ok" if successful
    - projects: Array of project objects, each containing:
      - id: Project/Epic ID
      - name: Project name
      - description: Project description (if available)
      - url: Linear URL for the project (if available)
    - count: Total number of projects returned
    """
    config = mcp.state["config"]

    return await list_projects_logic(api_key=config.linear_api_key)
