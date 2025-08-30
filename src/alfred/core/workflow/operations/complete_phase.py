"""Complete phase tool implementation."""

from alfred.core.workflow.engine import WorkflowEngine
from alfred.models.workflow import ToolResponse


async def complete_phase_logic(task_id: str, phase: str, summary: str) -> ToolResponse:
    """Marks a workflow phase as complete and shows what comes next.

    Args:
        task_id: The task ID to complete the phase for (e.g., "TASK-123")
        phase: The phase to mark as complete (e.g., "plan", "implement", "test")
        summary: Brief summary of what was accomplished in this phase

    Returns:
        ToolResponse containing phase completion confirmation with:
        - Summary of completed work
        - Next phase information or workflow completion status
        - Progress tracking and context persistence
        - Clear guidance for next steps

    Automatically saves context and determines the next phase in the workflow sequence.

    """
    try:
        # Initialize workflow engine
        engine = WorkflowEngine()

        # Load current task state
        state = engine.state_manager.get_state(task_id)
        if not state:
            return ToolResponse.error(
                message=f"Task '{task_id}' not found",
                next_prompt=f"Task '{task_id}' does not exist. Use list_all_tasks() to see available tasks.",
                data={"task_id": task_id, "error_type": "task_not_found"},
            )

        # Check for workflow assignment
        if not state.workflow_id:
            return ToolResponse.error(
                message=f"No workflow assigned to task '{task_id}'",
                next_prompt=f"""# Workflow Assignment Required

Cannot complete phase for task **{task_id}** without a workflow assignment.

## Next Steps:
1. **Assign workflow first**: `assign_workflow("workflow_type", "{task_id}")`
2. **Then complete phase**: `complete_phase("{task_id}", "{phase}", "summary")`

Use `list_workflows()` to see available workflow types.""",
                data={
                    "task_id": task_id,
                    "requested_phase": phase,
                    "requires_workflow_assignment": True,
                },
            )

        # Get workflow definition
        workflow = engine._get_workflow(state.workflow_id)

        # Generate expanded phase sequence to validate phase
        expanded_sequence = engine.get_expanded_phase_sequence(
            state.workflow_id, state.completed_phases
        )
        valid_phases = [p[0] for p in expanded_sequence]

        # Check if phase is valid
        if phase not in valid_phases:
            return ToolResponse.error(
                message=f"Invalid phase '{phase}' for workflow '{state.workflow_id}'",
                next_prompt=f"""# Invalid Phase

Cannot complete phase **{phase}** - it's not valid for the **{workflow.name}** workflow.

## Valid phases for this workflow:
{chr(10).join([f"- **{p[0]}**{' (review)' if p[1] else ''}" for p in expanded_sequence])}

## Current Status:
- **Completed**: {", ".join(state.completed_phases) if state.completed_phases else "None"}
- **Started**: {", ".join(state.started_phases) if state.started_phases else "None"}

Use `get_next_phase("{task_id}")` to see the recommended next phase to work on.""",
                data={
                    "task_id": task_id,
                    "requested_phase": phase,
                    "valid_phases": valid_phases,
                    "completed_phases": state.completed_phases,
                    "started_phases": state.started_phases,
                },
            )

        # Check if phase is already completed - handle gracefully
        if phase in state.completed_phases:
            # Phase was already completed (possibly via save_context with status="COMPLETE")
            # Return success anyway with next phase info to maintain smooth workflow

            # Generate expanded sequence to find next phase
            updated_sequence = engine.get_expanded_phase_sequence(
                state.workflow_id, state.completed_phases
            )
            next_phase_info = _find_next_phase(
                updated_sequence, state.completed_phases, state.started_phases
            )

            if not next_phase_info:
                # Workflow is complete
                return ToolResponse.success(
                    message=f"Phase '{phase}' was already completed - workflow finished!",
                    next_prompt=f"""# Workflow Already Complete!

Phase **{phase}** was already marked complete for task **{task_id}**.

## Workflow Results:
- **Workflow**: {workflow.name}
- **Total phases completed**: {len(state.completed_phases)}/{len(updated_sequence)}
- **Final status**: [COMPLETE] Complete

## All Completed Phases:
{chr(10).join([f"[X] **{p}**" for p in state.completed_phases])}

The entire workflow has been completed successfully!""",
                    data={
                        "task_id": task_id,
                        "phase": phase,
                        "already_completed": True,
                        "workflow_complete": True,
                        "completed_phases": state.completed_phases,
                    },
                )

            # There's a next phase to work on
            next_phase_name, is_review_phase, original_phase = next_phase_info

            # Get next phase details
            if is_review_phase:
                next_phase_goal = f"Review the completed {original_phase} work for quality and completeness"
                next_phase_display_name = f"{original_phase.title()} Review"
            else:
                try:
                    next_phase_config = workflow.get_phase(next_phase_name)
                    if next_phase_config:
                        next_phase_goal = next_phase_config.goal
                        next_phase_display_name = next_phase_config.name
                    else:
                        next_phase_goal = f"Continue with {next_phase_name} phase"
                        next_phase_display_name = next_phase_name.title()
                except Exception:
                    next_phase_goal = f"Continue with {next_phase_name} phase"
                    next_phase_display_name = next_phase_name.title()

            return ToolResponse.success(
                message=f"Phase '{phase}' was already completed",
                next_prompt=f"""# Phase Already Complete

Phase **{phase}** was already marked complete for task **{task_id}**.

## Progress Status:
- **Completed phases**: {len(state.completed_phases)}/{len(updated_sequence)}
- **Already completed**: {", ".join(state.completed_phases)}

## Next Phase: {next_phase_display_name}
**Goal**: {next_phase_goal}

## Ready to Continue:
- **Get details**: `get_next_phase("{task_id}")` - See next phase details
- **Start working**: `execute_phase("{task_id}", "{next_phase_name}")` - Begin next phase

Moving forward with the workflow!""",
                data={
                    "task_id": task_id,
                    "phase": phase,
                    "already_completed": True,
                    "next_phase": next_phase_name,
                    "next_phase_goal": next_phase_goal,
                    "is_next_review_phase": is_review_phase,
                    "completed_phases": state.completed_phases,
                },
            )

        # Mark phase as completed and save context
        engine.save_context(
            task_id=task_id,
            phase=phase,
            content=f"Phase completed: {summary}",
            status="COMPLETE",
            metadata={"phase_completion": True, "completion_summary": summary},
        )

        # Reload state to get updated completion status
        state = engine.state_manager.get_state(task_id)
        if not state:
            return ToolResponse.error(
                message=f"Task '{task_id}' not found",
                next_prompt=f"Task '{task_id}' does not exist. Use list_all_tasks() to see available tasks.",
                data={"task_id": task_id, "error_type": "task_not_found"},
            )

        # Generate new expanded sequence with potential new review phases
        updated_sequence = engine.get_expanded_phase_sequence(
            state.workflow_id, state.completed_phases
        )

        # Find next phase
        next_phase_info = _find_next_phase(
            updated_sequence, state.completed_phases, state.started_phases
        )

        if not next_phase_info:
            # Workflow complete!
            return ToolResponse.success(
                message=f"Phase '{phase}' completed - workflow finished!",
                next_prompt=f"""# Workflow Complete!

Successfully completed phase **{phase}** for task **{task_id}**.

## Final Summary:
**{summary}**

## Workflow Results:
- **Workflow**: {workflow.name}
- **Total phases completed**: {len(state.completed_phases)}/{len(updated_sequence)}
- **Final status**: [COMPLETE] Complete

## All Completed Phases:
{chr(10).join([f"[X] **{p}**" for p in state.completed_phases])}

## Next Steps:
- Task is ready for final review and closure
- Update JIRA status to reflect completion
- Consider creating follow-up tasks if needed

Excellent work completing this entire workflow!""",
                data={
                    "task_id": task_id,
                    "completed_phase": phase,
                    "completion_summary": summary,
                    "workflow_id": state.workflow_id,
                    "workflow_complete": True,
                    "total_phases_completed": len(state.completed_phases),
                    "all_completed_phases": state.completed_phases,
                },
            )

        # There's a next phase
        next_phase_name, is_review_phase, original_phase = next_phase_info

        # Load next phase info
        if is_review_phase:
            next_phase_goal = f"Review the completed {original_phase} work for quality and completeness"
            next_phase_display_name = f"{original_phase.title()} Review"
        else:
            try:
                workflow = engine._get_workflow(state.workflow_id)
                next_phase_config = workflow.get_phase(next_phase_name)
                if next_phase_config:
                    next_phase_goal = next_phase_config.goal
                    next_phase_display_name = next_phase_config.name
                else:
                    next_phase_goal = f"Continue with {next_phase_name} phase"
                    next_phase_display_name = next_phase_name.title()
            except Exception:
                next_phase_goal = f"Continue with {next_phase_name} phase"
                next_phase_display_name = next_phase_name.title()

        return ToolResponse.success(
            message=f"Phase '{phase}' completed successfully",
            next_prompt=f"""# Phase Complete!

Successfully completed phase **{phase}** for task **{task_id}**.

## Completion Summary:
**{summary}**

## Progress Update:
- **Completed phases**: {len(state.completed_phases)}/{len(updated_sequence)}
- **Just finished**: {phase}
- **Up next**: {next_phase_display_name}

## Next Phase: {next_phase_display_name}
**Goal**: {next_phase_goal}

## Ready to Continue:
- **Get details**: `get_next_phase("{task_id}")` - See next phase details
- **Start working**: `execute_phase("{task_id}", "{next_phase_name}")` - Begin next phase

{f"**Note**: This will be a review phase for the {original_phase} work you just completed." if is_review_phase else ""}

Great progress! Ready for the next phase.""",
            data={
                "task_id": task_id,
                "completed_phase": phase,
                "completion_summary": summary,
                "next_phase": next_phase_name,
                "next_phase_goal": next_phase_goal,
                "is_next_review_phase": is_review_phase,
                "progress": f"{len(state.completed_phases)}/{len(updated_sequence)}",
                "completed_phases": state.completed_phases,
                "workflow_id": state.workflow_id,
            },
        )

    except Exception as e:
        return ToolResponse.error(
            message=f"Failed to complete phase: {e!s}",
            next_prompt=f"Check that task '{task_id}' exists and phase '{phase}' is valid. Check Alfred MCP server logs for details.",
        )


def _generate_expanded_phase_sequence(
    engine: WorkflowEngine, workflow, completed_phases: list[str]
) -> list[tuple[str, bool, str]]:
    """Generate expanded phase sequence with dynamic review insertion."""
    expanded_sequence = []

    for phase_ref in workflow.phases:
        phase_name = phase_ref.phase_name
        expanded_sequence.append((phase_name, False, phase_name))

        # Check if this phase needs review and is completed
        if phase_name in completed_phases:
            try:
                phase_config = workflow.get_phase(phase_name)
                # Check for requires_review flag in phase
                if phase_config and phase_config.requires_review:
                    review_phase_name = f"{phase_name}_review"
                    expanded_sequence.append((review_phase_name, True, phase_name))
            except Exception:
                continue

    return expanded_sequence


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
