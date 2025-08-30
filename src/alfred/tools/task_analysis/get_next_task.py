"""MCP tool wrapper for get_next_task."""

from typing import Optional
from alfred.mcp import mcp
from alfred.core.task_analysis.get_next_task import get_next_task_logic


@mcp.tool
async def get_next_task(
    epic_id: Optional[str] = None,
    assignee_id: Optional[str] = None,
    include_blocked: bool = False,
) -> dict:
    """
    Intelligently find the next Linear/Jira task or subtask to work on based on priorities, dependencies, and task statuses within the platform's workflow.

    Business Value:
    - **Who uses this**: Developers needing to know what to work on next
    - **What problem it solves**: Eliminates decision paralysis by automatically selecting the most appropriate task based on dependencies and priorities
    - **Why it's better than manual approach**: Considers complex dependency graphs, prioritizes work already in progress, and ensures prerequisites are met before suggesting tasks

    Key features:
    - Algorithmic task selection (no AI calls - fast response)
    - Prioritizes subtasks of in-progress tasks to maintain focus
    - Respects task dependencies and blocking relationships
    - Considers priority levels (high > medium > low)
    - Provides reasoning for task selection
    - Returns alternative suggestions

    Use this tool when:
    - You're ready to start working and need to know what task to pick
    - You want to ensure you're working on the highest priority available task
    - You need to respect task dependencies and avoid blocked work
    - You want to maintain focus by continuing in-progress work

    Crucial Guardrails:
    - This tool only reads data - it doesn't modify task status
    - Use update_task_status after selecting a task to mark it "in_progress"
    - Tool respects Linear's dependency structure and blocking relationships
    - Only suggests tasks where all prerequisites are completed

    Usage Guidance:

    IMPORTANT: This tool uses algorithmic selection, not AI, so it returns results immediately. It analyzes task priority, dependencies, and status to make smart recommendations.

    CRITICAL: The tool prioritizes tasks already in progress to encourage finishing work before starting new tasks. If no in-progress work has available subtasks, it falls back to pending tasks.

    Selection Algorithm:
    1. **First Priority**: Subtasks of in-progress parent tasks (maintains focus)
    2. **Fallback**: Highest priority pending tasks with satisfied dependencies
    3. **Sorting**: Priority level → Fewer dependencies → Task ID (consistent ordering)

    Task Eligibility:
    - Status must be "pending" or "in_progress"
    - All dependency tasks must be completed ("done" status)
    - Task must be accessible to the current user
    - Blocked tasks excluded unless include_blocked=true

    Args:
        epic_id: Optional epic/project ID to limit search scope. If provided, only
            considers tasks within this epic. Use list_epics to find valid epic IDs.
        assignee_id: Optional user ID to filter by assignee. If provided, only
            considers tasks assigned to this user. Default: considers all tasks.
        include_blocked: Whether to include blocked tasks in consideration. Default: false.
            Blocked tasks are normally excluded but can be included for special cases.

    Returns:
        Dictionary with:
        - success: Boolean indicating if operation completed
        - next_task: Selected task object with full details (null if none available)
        - is_subtask: Boolean indicating if selected task is a subtask
        - reasoning: Explanation of why this task was selected
        - alternatives: Array of other viable task options
        - error: Error message if operation failed

    Task Selection Priority:
    1. **High priority** tasks with satisfied dependencies
    2. **Medium priority** tasks with satisfied dependencies
    3. **Low priority** tasks with satisfied dependencies
    4. Within same priority: fewer dependencies preferred
    5. Consistent ordering by task ID for predictability

    Response Includes:
    - Complete task information (ID, title, description, status, priority)
    - Dependency information and satisfaction status
    - Epic assignment and URL for easy access
    - Clear reasoning explaining the selection logic
    - Up to 2 alternative task suggestions
    """
    config = mcp.state.config

    result = await get_next_task_logic(
        api_key=config.linear_api_key,
        epic_id=epic_id,
        assignee_id=assignee_id,
        include_blocked=include_blocked,
    )

    return result.dict()
