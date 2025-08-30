"""Get progress tool implementation."""

from alfred.core.workflow.engine import WorkflowEngine
from alfred.models.workflow import ToolResponse


async def get_progress_logic(task_id: str) -> ToolResponse:
    """Shows current workflow progress and status for a state.

    Args:
        task_id: The task ID to get progress for (e.g., "TASK-123")

    Returns:
        ToolResponse containing comprehensive progress information with:
        - Current phase status and completion percentage
        - Completed phases with summaries
        - Next steps and phase recommendations
        - Workflow health and timeline information

    Provides complete visibility into task progress across all workflow phases.

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
            return ToolResponse.success(
                message=f"Task '{task_id}' has no workflow assigned",
                next_prompt=f"""# Task Status: No Workflow

Task **{task_id}** exists but has no workflow assigned yet.

## Current Status:
- **Workflow**: None assigned
- **Progress**: Not started
- **Created**: {state.created_at}

## Next Steps:
1. **See workflow options**: `list_workflows()` - View available workflow types
2. **Assign workflow**: `assign_workflow("workflow_type", "{task_id}")` - Choose appropriate workflow
3. **Begin work**: `get_next_phase("{task_id}")` - Start first phase

## Common Workflow Types:
- **task** - Regular development work (coding, bugs, features)
- **tech_spec** - Technical specification creation
- **prd** - Product requirements document

Ready to assign a workflow and begin work!""",
                data={
                    "task_id": task_id,
                    "workflow_assigned": False,
                    "progress_percentage": 0,
                    "created_at": state.created_at,
                },
            )

        # Get workflow definition
        workflow = engine._get_workflow(state.workflow_id)

        # Get the FULL sequence with all potential review phases for accurate total
        full_sequence = engine.get_full_phase_sequence(state.workflow_id)
        total_phases = len(full_sequence)

        # Get the current expanded sequence (only shows reviews for completed phases)
        expanded_sequence = engine.get_expanded_phase_sequence(
            state.workflow_id, state.completed_phases
        )
        completed_count = len(state.completed_phases)
        progress_percentage = (
            int((completed_count / total_phases) * 100) if total_phases > 0 else 0
        )

        # Find current phase
        current_phase_info = _find_next_phase(
            expanded_sequence, state.completed_phases, state.started_phases
        )
        current_phase = current_phase_info[0] if current_phase_info else None
        is_current_review = current_phase_info[1] if current_phase_info else False

        # Determine overall status
        if not current_phase:
            overall_status = "[COMPLETE] Complete"
            status_emoji = "[COMPLETE]"
        elif current_phase in state.started_phases:
            overall_status = f"[IN_PROGRESS] In Progress ({current_phase})"
            status_emoji = "[IN_PROGRESS]"
        else:
            overall_status = f"[READY] Ready ({current_phase})"
            status_emoji = "[READY]"

        # Build phase status list - use FULL sequence to show all potential phases
        phase_status_lines = []
        for phase_name, is_review, _original_phase in full_sequence:
            if phase_name in state.completed_phases:
                # Get completion summary if available
                phase_contexts = state.contexts.get(phase_name, [])
                completion_context = next(
                    (
                        ctx
                        for ctx in reversed(phase_contexts)
                        if "completed" in ctx["content"].lower()
                    ),
                    None,
                )
                summary = (
                    completion_context["content"] if completion_context else "Completed"
                )

                phase_status_lines.append(
                    f"[X] **{phase_name}**{' (review)' if is_review else ''}: {summary}"
                )
            elif phase_name in state.started_phases:
                phase_status_lines.append(
                    f"[IN_PROGRESS] **{phase_name}**{' (review)' if is_review else ''}: In progress"
                )
            else:
                phase_status_lines.append(
                    f"[ ] **{phase_name}**{' (review)' if is_review else ''}: Pending"
                )

        # Build recent activity
        recent_activity = []
        if state.contexts:
            # Get latest context entries across all phases
            all_contexts = []
            for phase_name, contexts in state.contexts.items():
                for ctx in contexts:
                    all_contexts.append((phase_name, ctx))

            # Sort by timestamp (most recent first)
            all_contexts.sort(key=lambda x: x[1].get("timestamp", ""), reverse=True)

            # Take the 3 most recent
            for phase_name, ctx in all_contexts[:3]:
                recent_activity.append(
                    f"- **{phase_name}**: {ctx.get('content', '')[:80]}..."
                )

        if not recent_activity:
            recent_activity = ["- No recent activity recorded"]

        # Create progress prompt
        progress_prompt = f"""# Progress Report: {task_id}

{status_emoji} **Status**: {overall_status}

## Workflow Overview
- **Workflow**: {workflow.name}
- **Progress**: {completed_count}/{total_phases} phases ({progress_percentage}%)
- **Created**: {state.created_at}

## Phase Status
{chr(10).join(phase_status_lines)}

## Recent Activity
{chr(10).join(recent_activity)}

## Next Steps
{_generate_next_steps(current_phase, is_current_review, task_id, overall_status)}

## Quick Actions
- **Get next phase details**: `get_next_phase("{task_id}")`
- **Continue working**: `execute_phase("{task_id}", "{current_phase}")`
{f"- **Complete current phase**: `complete_phase('{task_id}', '{current_phase}', 'summary')`" if current_phase and current_phase in state.started_phases else ""}"""

        return ToolResponse.success(
            message=f"Progress for task '{task_id}': {completed_count}/{total_phases} phases complete ({progress_percentage}%)",
            next_prompt=progress_prompt,
            data={
                "task_id": task_id,
                "workflow_id": state.workflow_id,
                "workflow_name": workflow.name,
                "progress_percentage": progress_percentage,
                "completed_phases": completed_count,
                "total_phases": total_phases,
                "current_phase": current_phase,
                "is_current_review_phase": is_current_review,
                "overall_status": overall_status,
                "completed_phase_list": state.completed_phases,
                "started_phase_list": state.started_phases,
                "created_at": state.created_at,
                "has_contexts": bool(state.contexts),
            },
        )

    except Exception as e:
        return ToolResponse.error(
            message=f"Failed to get progress: {e!s}",
            next_prompt=f"Check that task ID '{task_id}' is valid. Check Alfred MCP server logs for details.",
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


def _generate_next_steps(
    current_phase: str | None,
    is_current_review: bool,
    task_id: str,
    overall_status: str,
) -> str:
    """Generate contextual next steps based on current state."""
    if not current_phase:
        return """**Workflow Complete!**
- Task is ready for final review and closure
- Update JIRA status to reflect completion
- Consider creating follow-up tasks if needed"""

    if is_current_review:
        return f"""**Review Phase Active**
- Currently reviewing previous work for quality
- Use `execute_phase("{task_id}", "{current_phase}")` to continue review
- Focus on validation and quality assurance"""

    if "In Progress" in overall_status:
        return f"""**Continue Current Work**
- You're actively working on the {current_phase} phase
- Use `execute_phase("{task_id}", "{current_phase}")` to continue
- When done, use `complete_phase("{task_id}", "{current_phase}", "summary")`"""

    return f"""**Ready to Begin**
- Next phase to work on: {current_phase}
- Use `execute_phase("{task_id}", "{current_phase}")` to start
- Or use `get_next_phase("{task_id}")` for more details"""
