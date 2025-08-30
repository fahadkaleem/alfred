"""MCP tool wrapper for describe_workflow."""

from alfred.mcp import mcp
from alfred.core.workflow.operations.describe_workflow import describe_workflow_logic


@mcp.tool
async def describe_workflow(workflow_id: str) -> dict:
    """Describe a specific workflow showing all phases and their goals.

    - Provides detailed breakdown of workflow phases without requiring assignment
    - Shows phase names, objectives, personas, and special flags
    - Essential for understanding workflow structure before assignment
    - Displays complete phase sequence including review phases
    - Helps choose the right workflow for specific task requirements

    Parameters
    workflow_id [string] (required) - The workflow to describe:
        - Must be valid workflow ID from list_workflows()
        - Examples: "task", "tech_spec", "prd", "test_plan", "create_tasks_from_spec"
        - "task" - Standard development workflow with 6 phases
        - "tech_spec" - Technical specification creation workflow
        - "prd" - Product requirements document workflow
        - "test_plan" - Test planning and strategy workflow
        - "create_tasks_from_spec" - Task decomposition workflow

    Usage scenarios:
    - Workflow exploration: Understand phases before assignment
    - Team onboarding: Show workflow structure to new members
    - Process documentation: Export workflow details for docs
    - Workflow comparison: Compare different workflow approaches
    - Training: Learn what each phase accomplishes

    Returns
        ToolResponse with comprehensive workflow details:
        - workflow_info: Name, purpose, and configuration
        - phase_details: All phases with goals and personas
        - special_flags: Review requirements and checkpoints
        - usage_examples: How to assign and start workflow

    Examples
        # Describe task workflow
        describe_workflow("task")

        # Explore tech spec workflow
        describe_workflow("tech_spec")

        # Compare workflows
        list_workflows()  # See all options
        describe_workflow("prd")  # Deep dive into PRD workflow

    Error conditions:
    - Workflow ID not found or invalid
    - Workflow configuration corrupted
    - Phase files missing or malformed

    """
    result = await describe_workflow_logic(workflow_id)
    return result.model_dump()
