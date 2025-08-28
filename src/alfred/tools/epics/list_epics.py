"""MCP tool wrapper for list_epics."""

from alfred.core.epics.list import list_epics_logic
from alfred.config import get_config


def register(server) -> int:
    """Register the list_epics tool."""

    @server.tool
    async def list_epics() -> dict:
        """
        List all epics (projects) in the Linear workspace for discovery and navigation.
        
        This tool retrieves a complete list of all epics/projects in your Linear workspace,
        providing essential metadata for epic discovery, task organization, and navigation.
        
        Key features:
        - Retrieves all epics/projects from your Linear workspace
        - Returns epic IDs needed for other operations (create_task, switch_epic, etc.)
        - Provides epic metadata including names, descriptions, and URLs
        - No pagination required - returns all epics up to API limit
        - Sorted by creation or modification date (Linear default)
        
        Use this tool when:
        - You need to discover what epics exist before creating tasks
        - You want to find an epic ID for task assignment or switching context
        - You need to verify an epic name before creating a new one
        - You want to audit or review all projects in your workspace
        - You're checking if an epic exists before other operations
        
        Crucial Guardrails:
        - Use this before create_epic to avoid duplicate names
        - Use this before delete_epic to verify correct epic ID
        - Use this to get epic_id values for create_task operations
        - Don't assume epic names - always verify with this tool first
        
        Usage:
        
        Before using this tool:
        - MUST have LINEAR_API_KEY configured in environment variables
        - MUST have workspace initialized using initialize_workspace
        
        When listing epics:
        - Results include ALL epics accessible in your workspace (up to 100)
        - No filtering or search parameters are available
        - Epic IDs from this tool can be used in all other epic operations
        - Empty result array means no epics exist in the workspace
        
        IMPORTANT:
        - "Epic" in Alfred terminology maps to "Project" in Linear's UI
        - Returns maximum of 100 epics due to Linear API limitations
        - If you have >100 epics, only the most recent 100 are returned
        - Epic IDs are permanent and unique within your workspace
        - Results are read-only - this tool cannot modify epics
        
        WARNING:
        - Tool will fail if LINEAR_API_KEY is not set in environment
        - Tool will fail if Linear API key is invalid or expired
        - Returns empty array (not error) if no epics exist
        - Tool will fail if workspace is not initialized
        
        <example>
        User: What projects do we have for Q1?
        Assistant: I'll list all the epics in your workspace to find Q1-related projects.
        *Uses list_epics tool*
        I found 15 epics total. The Q1-related projects are:
        - "Q1 Authentication Improvements" (id: abc-123)
        - "Q1 Performance Optimization" (id: def-456)
        - "Q1 Mobile Features" (id: ghi-789)
        </example>
        
        <reasoning>
        1. The user wants to see Q1-related projects
        2. list_epics is the tool for discovering all available epics
        3. After retrieval, I can filter and present Q1-specific epics
        4. The epic IDs can now be used for further operations
        </reasoning>
        
        <example>
        User: Create a task for the authentication project
        Assistant: Let me first list the epics to find the authentication project ID.
        *Uses list_epics tool*
        Found "Q1 Authentication Improvements" with ID abc-123. Now I'll create the task.
        *Uses create_task with epic_id="abc-123"*
        </example>
        
        <reasoning>
        1. To create a task in an epic, we need the epic_id
        2. list_epics provides all epic IDs and names
        3. Found the correct epic by name matching
        4. Used the discovered ID in the subsequent create_task operation
        </reasoning>
        
        <example>
        User: How many active projects do we have?
        Assistant: I'll list all epics to count the total projects in your workspace.
        *Uses list_epics tool*
        You have 23 active projects (epics) in your Linear workspace.
        </example>
        
        <reasoning>
        1. The user wants a count of all projects
        2. list_epics returns all epics with a count field
        3. The count provides the answer directly
        4. No filtering needed since user wants total count
        </reasoning>
        
        Parameters:
        
        No parameters required - this tool always returns all accessible epics.
        
        Returns:
        Dictionary with:
        - status: "ok" if successful
        - projects: Array of epic objects, each containing:
          - id: Unique epic identifier (use for other operations)
          - name: Human-readable epic name
          - description: Epic description if set (may be null)
          - url: Direct Linear URL to access the epic (may be null)
        - count: Total number of epics returned (0 to 100)
        """
        config = get_config()

        return await list_epics_logic(api_key=config.linear_api_key)

    return 1  # One tool registered
