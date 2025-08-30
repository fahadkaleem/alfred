"""MCP tool wrapper for assign_workflow."""

from alfred.mcp import mcp
from alfred.core.workflow.operations.assign_workflow import assign_workflow_logic


@mcp.tool
async def assign_workflow(
    workflow_id: str, task_id: str | None = None, force: bool = False
) -> dict:
    """Assign a workflow type to a task to define execution phases and approach.

    - Associates a specific workflow with a task to control phase execution
    - Workflows determine the phases, tools, and methodologies for completing work
    - Essential prerequisite before starting workflow execution with phase tools
    - Supports both immediate assignment and pending assignment for future tasks
    - Validates workflow existence and prevents accidental overwrites

    Parameters
    ----------
    workflow_id [string] (required) - The workflow type to assign:
        - Use list_workflows() to see all available options with descriptions
        - Example workflows: "task", "tech_spec", "prd", "test_plan", "create_tasks_from_spec"
        - "task" - Standard development workflow (e.g., claim → plan → implement → test → review)
        - "tech_spec" - Technical specification creation with research and validation
        - "prd" - Product requirements document with discovery and stakeholder validation
        - "test_plan" - Testing strategy development with environment and execution planning
        - "create_tasks_from_spec" - Task decomposition workflow from specifications
    task_id [string] - Optional task ID for immediate assignment (e.g., "PROJ-123", "AL-456"):
        - If provided, assigns workflow to specific existing task
        - If omitted, stores as pending assignment for next task you work on
        - Task ID can be external key or local Alfred task identifier
    force [boolean] - Overwrite existing workflow assignment (default: false):
        - false: Prevents accidental reassignment of already-assigned workflows
        - true: Force reassignment when requirements change or initial choice was wrong
        - WARNING: Reassigning may lose progress from completed phases

    Usage scenarios:
    - Direct assignment: Assign workflow to existing task for immediate execution
    - Pending assignment: Store workflow preference for next task you work on
    - Workflow changes: Update workflow when task requirements evolve
    - Team standardization: Ensure consistent workflow usage across projects
    - Troubleshooting: Reset workflow assignment when execution gets stuck

    Example workflow selection guidance (see list_workflows() for complete options):
    - "task": General development work, bug fixes, feature implementation
    - "tech_spec": Architecture decisions, system design, technical documentation
    - "prd": Product features, user requirements, business specifications
    - "test_plan": QA strategy, testing approach, quality assurance planning
    - "create_tasks_from_spec": Breaking down large specifications into actionable tasks
    - Additional workflows may be available based on your configuration

    Returns
    -------
        ToolResponse with assignment confirmation:
        - assignment_status: Success or error details
        - next_steps: Recommended actions to start workflow execution
        - workflow_info: Phase structure and execution guidance
        - task_context: Current task state and readiness

    Examples
    --------
        # Assign tech_spec workflow to existing task
        assign_workflow("tech_spec", "PROJ-123")

        # Store task workflow for next work session
        assign_workflow("task")

        # Force reassign when requirements change
        assign_workflow("prd", "PROJ-456", force=True)

        # Check available workflows first
        list_workflows()  # See options
        assign_workflow("create_tasks_from_spec", "TASK-789")

    Prerequisites:
    - Valid workflow_id from list_workflows()
    - Task must exist if task_id provided
    - Alfred workspace properly initialized

    Error conditions:
    - Unknown workflow_id specified
    - Task already has workflow assigned and force=False
    - Invalid task_id or missing task
    - Workflow configuration files missing or corrupted

    """
    result = await assign_workflow_logic(workflow_id, task_id, force)
    return result.model_dump()
