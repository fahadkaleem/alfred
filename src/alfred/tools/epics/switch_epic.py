"""MCP tool wrapper for switch_epic."""

from alfred.core.epics.switch import switch_epic_logic
from alfred.config import get_config


def register(server) -> int:
    """Register the switch_epic tool."""

    @server.tool
    async def switch_epic(epic_id: str) -> dict:
        """
        Switch the active epic context to focus work on a specific project area.
        
        This tool changes your active epic/project context, which affects default epic
        assignment for new tasks and helps maintain focus on a specific project area.
        The setting persists across sessions.
        
        Key features:
        - Sets the default epic for new task creation (when epic_id not specified)
        - Persists active epic selection across sessions and restarts
        - Validates epic exists before switching
        - Returns previous epic ID for context tracking
        - Updates workspace configuration immediately
        
        Use this tool when:
        - You're starting work on a specific project and want focused context
        - You want new tasks to default to a particular epic
        - You're switching between different project areas
        - You need to set up context before a series of task operations
        - You want to ensure consistent epic assignment for a work session
        
        Crucial Guardrails:
        - Use list_epics first to get valid epic IDs
        - Switching epic does NOT move existing tasks between epics
        - Only affects DEFAULT epic for new tasks (explicit epic_id overrides)
        - Consider current active epic before switching to avoid confusion
        
        Usage:
        
        Before using this tool:
        - MUST have LINEAR_API_KEY configured in environment variables
        - MUST have workspace initialized using initialize_workspace
        - SHOULD use list_epics to verify epic_id exists
        
        Active epic behavior:
        - When set, new tasks created without epic_id use this epic
        - Persists in configuration file (~/.alfred/config.json)
        - Survives session restarts and terminal closes
        - Can be overridden by explicit epic_id in create_task
        - Shows in workspace status as "Active Epic"
        
        IMPORTANT:
        - Switching epic is a context change only - no tasks are moved
        - The epic must exist in your workspace (validate with list_epics)
        - Some tools may use active epic as default (check tool documentation)
        - Active epic is workspace-specific, not global
        - Multiple sessions can have different active epics
        
        WARNING:
        - Tool will fail if LINEAR_API_KEY is not set in environment
        - Tool will fail if Linear API key is invalid or expired
        - Tool will fail if epic_id doesn't exist in workspace
        - Tool will fail if epic_id format is invalid
        
        <example>
        User: I'm going to work on the authentication features now
        Assistant: I'll switch the active epic context to the authentication project.
        Let me first find the authentication epic ID.
        *Uses list_epics to find "Q1 Authentication Improvements"*
        Now I'll switch to that epic.
        *Uses switch_epic with epic_id="abc-123"*
        Switched to "Q1 Authentication Improvements". New tasks will default to this epic.
        </example>
        
        <reasoning>
        1. User is starting focused work on authentication
        2. Setting active epic ensures consistent task organization
        3. list_epics was used to verify the epic exists and get its ID
        4. Future create_task calls without epic_id will use this epic
        </reasoning>
        
        <example>
        User: What epic am I currently working in?
        Assistant: Let me check the current workspace configuration.
        *Uses get_workspace_info to check active_epic_id*
        You're currently working in "Q1 Authentication Improvements" (ID: abc-123).
        </example>
        
        <reasoning>
        1. User wants to know current context
        2. get_workspace_info shows the active epic, not switch_epic
        3. switch_epic is only for CHANGING the active epic
        4. Reading current state doesn't require switching
        </reasoning>
        
        <example>
        User: Set up the workspace for mobile development work
        Assistant: I'll set the active epic to the mobile development project.
        *Uses list_epics to find mobile-related epics*
        Found "Mobile App v2.0" epic. Switching to it now.
        *Uses switch_epic with epic_id="mobile-v2-id"*
        Workspace now focused on "Mobile App v2.0". Tasks created without specifying
        an epic will be added to this project.
        </example>
        
        <reasoning>
        1. User wants to configure workspace for specific project area
        2. switch_epic sets the default context for new work
        3. This affects all subsequent task creation in the session
        4. Explicit epic_id in create_task would still override this default
        </reasoning>
        
        Parameters:
        
        epic_id [string] (required) - The unique identifier of the epic to switch to. Must be
            an exact epic ID from Linear (e.g., "abc123-def456-789"). Get valid IDs using
            list_epics. Case-sensitive and must exist in your workspace.
        
        Returns:
        Dictionary with:
        - status: "ok" if successful
        - epic: Active epic object containing:
          - id: The epic ID now active
          - name: Human-readable epic name
          - description: Epic description if available
          - url: Direct Linear URL for the epic
        - message: Confirmation of context switch
        - previous_epic_id: ID of the previously active epic (null if none)
        """
        config = get_config()

        return await switch_epic_logic(api_key=config.linear_api_key, epic_id=epic_id)

    return 1  # One tool registered
