"""List available workflows tool implementation."""

from alfred.core.workflow.engine import WorkflowEngine
from alfred.models.workflow import ToolResponse


async def list_workflows_logic() -> ToolResponse:
    """Lists all available workflow types.

    Returns:
        ToolResponse containing available workflows with descriptions and usage examples.

    """
    try:
        # Initialize workflow engine to load all workflows
        engine = WorkflowEngine()

        # Get all available workflows using list_workflows
        workflows = engine.list_workflows()

        if not workflows:
            return ToolResponse.error(
                message="No workflows found. No workflow configuration files were found in the prompts/workflows directory.",
                next_prompt="Check that the prompts/workflows directory exists and contains valid YAML files.",
            )

        # Generate the workflow list prompt using builder
        prompt = engine.builder.build_workflow_list_prompt(workflows)

        return ToolResponse.success(
            message=f"Found {len(workflows)} available workflows",
            next_prompt=prompt,
            data={
                "workflows": list(workflows.keys()),
                "count": len(workflows),
                "workflow_details": {
                    workflow_id: {
                        "name": workflow.name,
                        "goal": workflow.goal,
                        "creates_task": workflow.create_task,
                        "phase_count": len(workflow.phases),
                    }
                    for workflow_id, workflow in workflows.items()
                },
            },
        )

    except Exception as e:
        return ToolResponse.error(
            message=f"Failed to load workflows: {e!s}",
            next_prompt="""# Error Loading Workflows

## Recovery Steps:
1. Check that the prompts/workflows directory exists
2. Verify workflow YAML files are properly formatted
3. Check the Alfred MCP server logs for details

## Common Issues:
- Missing workflow directory
- Malformed YAML syntax
- Permission issues reading files
""",
        )
