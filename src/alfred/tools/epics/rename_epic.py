"""MCP tool wrapper for rename_epic."""

from alfred.core.epics.rename import rename_epic_logic
from alfred.config import get_config


def register(server) -> int:
    """Register the rename_epic tool."""

    @server.tool
    async def rename_epic(epic_id: str, new_name: str) -> dict:
        """
        Rename an existing epic (project) to better reflect its purpose or scope.

        This tool updates the name of an existing epic/project in your Linear workspace,
        allowing you to keep epic names current as project scope evolves or to fix
        naming issues.

        Key features:
        - Updates epic name immediately in Linear
        - Preserves epic ID and all associated tasks
        - Returns both old and new names for confirmation
        - Change is instantly visible to all team members
        - Maintains all epic relationships and metadata

        Use this tool when:
        - Project scope or focus has changed requiring a name update
        - You need to fix typos or naming convention issues
        - You want to clarify epic purpose with a better name
        - You're reorganizing projects and need consistent naming
        - Stakeholders request a different project name

        Crucial Guardrails:
        - Use list_epics first to verify the epic exists and get its ID
        - Check for naming conflicts before renaming
        - Consider impact on team members currently working in the epic
        - Remember that epic ID remains unchanged (only name changes)

        Usage:

        Before using this tool:
        - MUST have LINEAR_API_KEY configured in environment variables
        - MUST have workspace initialized using initialize_workspace
        - SHOULD use list_epics to verify epic_id and current name
        - CONSIDER checking for name conflicts with existing epics

        When renaming epics:
        - Choose clear, descriptive names that reflect current scope
        - Follow your team's naming conventions consistently
        - Avoid duplicate names to prevent confusion
        - Consider adding version numbers or dates for clarity

        IMPORTANT:
        - Epic ID never changes - only the display name is updated
        - All tasks remain in the epic with no changes
        - Change is immediate and visible to all team members
        - Previous name is returned for audit/confirmation purposes
        - URL to the epic remains the same (ID-based)

        WARNING:
        - Tool will fail if LINEAR_API_KEY is not set in environment
        - Tool will fail if Linear API key is invalid or expired
        - Tool will fail if epic_id doesn't exist in workspace
        - Tool may fail if new name already exists (workspace dependent)
        - Tool will fail if new name exceeds character limit (255)

        <example>
        User: Rename the authentication epic to include Q2 instead of Q1
        Assistant: I'll rename the authentication epic to reflect the Q2 timeline.
        *Uses list_epics to find "Q1 Authentication Improvements" with ID "abc-123"*
        *Uses rename_epic with epic_id="abc-123" and new_name="Q2 Authentication Improvements"*
        Successfully renamed from "Q1 Authentication Improvements" to "Q2 Authentication Improvements".
        </example>

        <reasoning>
        1. User needs to update epic name for timeline change
        2. list_epics used to verify epic and get correct ID
        3. rename_epic updates only the name, preserving everything else
        4. Tasks and ID remain unchanged, maintaining continuity
        </reasoning>

        <example>
        User: Fix the typo in the "Moblie App" project name
        Assistant: I'll fix the typo in the Mobile App epic name.
        *Uses rename_epic with epic_id="mobile-123" and new_name="Mobile App"*
        Fixed typo: renamed from "Moblie App" to "Mobile App".
        </example>

        <reasoning>
        1. Simple typo correction needed
        2. rename_epic is the appropriate tool for name changes
        3. Only the display name changes, all else preserved
        4. Quick fix with immediate effect
        </reasoning>

        <example>
        User: The "Project X" epic needs a more descriptive name now that we know what it is
        Assistant: I'll rename "Project X" to a more descriptive name.
        What should we call it now that the project scope is clear?
        User: "Customer Analytics Dashboard"
        Assistant: *Uses rename_epic with epic_id="proj-x-789" and new_name="Customer Analytics Dashboard"*
        Renamed from "Project X" to "Customer Analytics Dashboard" for better clarity.
        </example>

        <reasoning>
        1. Placeholder name needs to be replaced with descriptive name
        2. User input needed for appropriate new name
        3. rename_epic updates the name while preserving project history
        4. Better name improves project discoverability and understanding
        </reasoning>

        Parameters:

        epic_id [string] (required) - The unique identifier of the epic to rename. Must be
            the exact epic ID from Linear (e.g., "abc123-def456-789"). Get this using
            list_epics. Case-sensitive and must exist in your workspace.

        new_name [string] (required) - The new name for the epic. Should be descriptive,
            unique within your workspace, and follow team naming conventions. Maximum length
            typically 255 characters. Avoid special characters that might cause issues.

        Returns:
        Dictionary with:
        - status: "ok" if successful
        - epic: Updated epic object containing:
          - id: Epic ID (unchanged)
          - name: New epic name as set
          - description: Epic description (unchanged)
          - url: Linear URL for the epic (unchanged)
          - updated_at: Timestamp of the rename operation
        - message: Confirmation of successful rename
        - old_name: Previous epic name (for audit trail)
        """
        config = get_config()

        return await rename_epic_logic(
            api_key=config.linear_api_key, epic_id=epic_id, new_name=new_name
        )

    return 1  # One tool registered
