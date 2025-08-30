"""Describe workflow tool implementation."""

from alfred.core.workflow.engine import WorkflowEngine
from alfred.models.workflow import ToolResponse


async def describe_workflow_logic(workflow_id: str) -> ToolResponse:
    """Describes a specific workflow by showing all its phases and their goals.

    Args:
        workflow_id: The workflow identifier (e.g., "task", "tech_spec", "prd")

    Returns:
        ToolResponse containing detailed workflow information with:
        - Workflow name, goal, and configuration
        - All phases with their names and objectives
        - Phase personas and key characteristics
        - Total phase count and JIRA creation behavior

    Provides comprehensive workflow overview without requiring assignment.

    """
    try:
        # Initialize workflow engine
        engine = WorkflowEngine()

        # Get workflow definition
        try:
            workflow = engine._get_workflow(workflow_id)
        except Exception:
            return ToolResponse.error(
                message=f"Workflow '{workflow_id}' not found",
                next_prompt="Use list_workflows() to see available workflows",
            )

        # Build phase details with expanded information
        phase_details = []
        for phase_config in workflow.phases:
            # Extract phase details directly from workflow
            phase_info = {
                "id": phase_config.id,
                "name": phase_config.name,
                "goal": phase_config.goal,
                "persona": phase_config.persona_ref,
                "requires_review": phase_config.requires_review,
                "auto_checkpoint": phase_config.auto_checkpoint,
                "steps": [
                    {
                        "name": step.name,
                        "description": step.description,
                        "instruction": step.instruction,
                        "checkpoint": step.checkpoint,
                    }
                    for step in phase_config.steps
                ],
            }
            phase_details.append(phase_info)

        # Generate readable description
        description_lines = [
            f"# Workflow: {workflow.name}",
            "",
            "## Overview",
            f"**ID**: `{workflow.id}`",
            f"**Purpose**: {workflow.goal.strip()}",
            f"**Creates Task**: {'Yes' if workflow.create_task else 'No'}",
            f"**Total Phases**: {len(phase_details)}",
            "",
            "## Phases",
        ]

        # Add phase descriptions
        for i, phase in enumerate(phase_details, 1):
            description_lines.extend(
                [
                    f"### {i}. {phase['name']}",
                    f"**Goal**: {phase['goal']}",
                    f"**Persona**: {phase['persona']}",
                ]
            )

            # Add special flags if present
            flags = []
            if phase["requires_review"]:
                flags.append("Requires Review")
            if phase["auto_checkpoint"]:
                flags.append("Auto-checkpoint")

            if flags:
                description_lines.append(f"**Flags**: {', '.join(flags)}")

            description_lines.append("")  # Empty line between phases

        # Add usage example
        description_lines.extend(
            [
                "## Usage",
                "```python",
                "# Assign this workflow to a task",
                f'assign_workflow("{workflow_id}", "AL-1")',
                "",
                "# Or assign for future use",
                f'assign_workflow("{workflow_id}")',
                "```",
                "",
                "## Next Steps",
                f'1. **Assign workflow**: `assign_workflow("{workflow_id}", "task_id")`',
                '2. **Check assignment**: `get_next_phase("task_id")`',
                '3. **Start execution**: `execute_phase("task_id", "phase_name")`',
            ]
        )

        description_prompt = "\n".join(description_lines)

        return ToolResponse.success(
            message=f"Workflow '{workflow_id}' has {len(phase_details)} phases",
            next_prompt=description_prompt,
            data={
                "workflow_id": workflow.id,
                "workflow_name": workflow.name,
                "workflow_goal": workflow.goal,
                "creates_task": workflow.create_task,
                "phase_count": len(phase_details),
                "phases": phase_details,
            },
        )

    except Exception as e:
        return ToolResponse.error(
            message=f"Failed to describe workflow: {e!s}",
            next_prompt="""# Error Loading Workflow

Failed to load workflow details.

## Recovery Steps:
1. Verify the workflow_id is correct
2. Use `list_workflows()` to see available workflows
3. Check Alfred MCP server logs for details

## Common Issues:
- Workflow YAML file may be corrupted
- Phase configuration files may be missing
- Invalid workflow ID provided
""",
        )
