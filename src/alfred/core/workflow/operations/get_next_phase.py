"""Get next phase tool implementation."""

from alfred.core.workflow.engine import WorkflowEngine
from alfred.models.workflow import ToolResponse


async def get_next_phase_logic(task_id: str) -> ToolResponse:
    """Returns the next phase Claude Code should work on for this task.

    Args:
        task_id: The task ID to get the next phase for (e.g., "TASK-123")

    Returns:
        ToolResponse containing the next phase information with:
        - Phase name and goal
        - Phase status and context
        - Instructions for proceeding

    Works in any chat session - handles workflow assignment automatically.

    """
    try:
        # Initialize workflow engine
        engine = WorkflowEngine()

        # Get workflow state for task
        state = engine.state_manager.get_state(task_id)
        if not state:
            # No workflow state exists yet
            return ToolResponse.error(
                message=f"No workflow assigned to task '{task_id}'",
                next_prompt=f"""# Workflow Assignment Required

Task **{task_id}** needs a workflow assignment before proceeding.

## Next Steps:
1. **See available workflows**: `list_workflows()` - View all workflow options
2. **Assign workflow**: `assign_workflow("workflow_type", "{task_id}")` - Assign specific workflow

## Common Workflow Types:
- **task** - Regular development work (coding, bugs, features)
- **tech_spec** - Technical specification creation
- **prd** - Product requirements document

Once a workflow is assigned, you can use `get_next_phase("{task_id}")` to see what to work on next.""",
                data={"task_id": task_id, "requires_workflow_assignment": True},
            )

        # Check for workflow assignment
        if not state.workflow_id:
            return ToolResponse.error(
                message=f"No workflow assigned to task '{task_id}'",
                next_prompt=f"""# Workflow Assignment Required

Task **{task_id}** needs a workflow assignment before proceeding.

## Next Steps:
1. **See available workflows**: `list_workflows()` - View all workflow options
2. **Assign workflow**: `assign_workflow("workflow_type", "{task_id}")` - Assign specific workflow

## Common Workflow Types:
- **task** - Regular development work (coding, bugs, features)
- **tech_spec** - Technical specification creation
- **prd** - Product requirements document

Once a workflow is assigned, you can use `get_next_phase("{task_id}")` to see what to work on next.""",
                data={"task_id": task_id, "requires_workflow_assignment": True},
            )

        # Get workflow definition
        workflow = engine._get_workflow(state.workflow_id)

        # Generate expanded phase sequence with dynamic review insertion
        expanded_sequence = engine.get_expanded_phase_sequence(
            state.workflow_id, state.completed_phases
        )

        # Find next phase
        next_phase_info = _find_next_phase(
            expanded_sequence, state.completed_phases, state.started_phases
        )

        if not next_phase_info:
            # All phases complete
            return ToolResponse.success(
                message=f"Workflow complete for task '{task_id}'",
                next_prompt=f"""# Workflow Complete!

Task **{task_id}** has completed all phases of the **{workflow.name}** workflow.

## Summary:
- **Workflow**: {workflow.name}
- **Completed phases**: {len(state.completed_phases)}/{len(expanded_sequence)}
- **Status**: [COMPLETE] Complete

## What's Next:
- Task is ready for final review and closure
- Check if any follow-up tasks need to be created
- Update Linear status to reflect completion

Great work completing this workflow!""",
                data={
                    "task_id": task_id,
                    "workflow_id": state.workflow_id,
                    "workflow_complete": True,
                    "completed_phases": state.completed_phases,
                    "total_phases": len(expanded_sequence),
                },
            )

        phase_name, is_review_phase, original_phase = next_phase_info

        # Load phase configuration
        if is_review_phase:
            # Use review phase template
            phase_config = _create_review_phase_config(original_phase)
            phase_goal = f"Review the completed {original_phase} work for quality and completeness"
        else:
            # Load regular phase configuration
            workflow = engine._get_workflow(state.workflow_id)
            phase_config = workflow.get_phase(phase_name)
            if not phase_config:
                return ToolResponse.error(
                    message=f"Phase '{phase_name}' not found in workflow",
                    next_prompt="Check workflow configuration",
                )
            phase_goal = phase_config.goal

        # Determine phase status
        is_started = phase_name in state.started_phases
        phase_status = "in_progress" if is_started else "ready"

        # Create focused next phase prompt
        next_prompt = f"""# Next Phase: {phase_config.name}

## Current Task
Working on ticket: **{task_id}**

## Phase Goal
{phase_goal}

## Status
- **Phase**: {phase_name} ({phase_status})
- **Workflow**: {workflow.name}
- **Progress**: {len(state.completed_phases)}/{len(expanded_sequence)} phases complete

## Next Steps
To work on this phase, use: `execute_phase("{task_id}", "{phase_name}")`

## Recently Completed
{f"Last completed: {state.completed_phases[-1]}" if state.completed_phases else "No phases completed yet"}

Ready to {"continue" if is_started else "begin"} this phase!"""

        return ToolResponse.success(
            message=f"Next phase for task '{task_id}': {phase_name}",
            next_prompt=next_prompt,
            data={
                "task_id": task_id,
                "workflow_id": state.workflow_id,
                "next_phase": phase_name,
                "phase_status": phase_status,
                "phase_goal": phase_goal,
                "is_review_phase": is_review_phase,
                "progress": f"{len(state.completed_phases)}/{len(expanded_sequence)}",
                "completed_phases": state.completed_phases,
                "started_phases": state.started_phases,
            },
        )

    except Exception as e:
        return ToolResponse.error(
            message=f"Failed to get next phase: {e!s}",
            next_prompt="Check that the task ID is valid and has a workflow assigned. Use list_workflows() to see available workflows.",
        )


def _find_next_phase(
    expanded_sequence: list[tuple[str, bool, str]],
    completed_phases: list[str],
    started_phases: list[str],
) -> tuple[str, bool, str] | None:
    """Find the next phase to work on from the expanded sequence."""
    for phase_name, is_review_phase, original_phase in expanded_sequence:
        if phase_name not in completed_phases:
            return (phase_name, is_review_phase, original_phase)
    return None


def _create_review_phase_config(original_phase: str):
    """Create a dynamic review phase configuration."""
    from alfred.models.workflow import Phase, PhaseStep

    return Phase(
        id="review",
        name=f"{original_phase.title()} Review",
        goal=f"Review the completed {original_phase} work for quality, completeness, and adherence to requirements.",
        persona_ref="reviewer",
        steps=[
            PhaseStep(
                name=f"Load {original_phase} context",
                description=f"Review all work completed in the {original_phase} phase",
                instruction="common/load-context",
            ),
            PhaseStep(
                name=f"Review {original_phase} deliverables",
                description=f"Validate {original_phase} outputs meet requirements",
                instruction="review/phase-review",
            ),
            PhaseStep(
                name="Document review findings",
                description="Record review results and any issues found",
                instruction="common/save-context",
            ),
        ],
    )
