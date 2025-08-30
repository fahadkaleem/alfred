"""Execute phase tool implementation."""

from alfred.core.workflow.engine import WorkflowEngine
from alfred.models.workflow import ToolResponse


async def execute_phase_logic(
    task_id: str, phase: str, need_context: bool = True, force: bool = False
) -> ToolResponse:
    """Executes a specific workflow phase with focused instructions and context.

    Args:
        task_id: The task ID to execute the phase for (e.g., "TASK-123")
        phase: The specific phase to execute (e.g., "plan", "implement", "test")
        need_context: Whether to load previous phase contexts (default: True)
        force: Force re-execution of a completed phase (default: False)
               Use this when you need to redo work in a phase that was already marked complete.
               This will not remove the completion status but allows you to work on it again.

    Returns:
        ToolResponse containing the phase execution prompt with:
        - Phase-specific role and goals
        - Previous context if requested
        - Hierarchical todo structure with instruction loading
        - Quality standards and completion criteria

    Uses just-in-time instruction loading to maintain focus on current phase work.

    """
    try:
        # Initialize workflow engine
        engine = WorkflowEngine()

        # Get workflow state for task
        state = engine.state_manager.get_state(task_id)
        if not state:
            return ToolResponse.error(
                message=f"No workflow assigned to task '{task_id}'",
                next_prompt=f"""# Workflow Assignment Required

Task **{task_id}** needs a workflow assignment before executing phases.

## Next Steps:
1. **See available workflows**: `list_workflows()` - View all workflow options
2. **Assign workflow**: `assign_workflow("workflow_type", "{task_id}")` - Assign specific workflow

Once a workflow is assigned, you can use `execute_phase("{task_id}", "phase_name")` to start execution.""",
                data={"task_id": task_id, "requires_workflow_assignment": True},
            )

        # Check for workflow assignment
        if not state.workflow_id:
            return ToolResponse.error(
                message=f"No workflow assigned to task '{task_id}'",
                next_prompt=f"""# Workflow Assignment Required

Task **{task_id}** needs a workflow assignment before executing phases.

## Next Steps:
1. **See available workflows**: `list_workflows()` - View all workflow options
2. **Assign workflow**: `assign_workflow("workflow_type", "{task_id}")` - Assign specific workflow
3. **Then execute phase**: `execute_phase("{task_id}", "{phase}")` - Run the phase

## Common Workflow Types:
- **task** - Regular development work (coding, bugs, features)
- **tech_spec** - Technical specification creation
- **prd** - Product requirements document

Once a workflow is assigned, you can execute any phase.""",
                data={
                    "task_id": task_id,
                    "requested_phase": phase,
                    "requires_workflow_assignment": True,
                },
            )

        # Get workflow definition
        workflow = engine._get_workflow(state.workflow_id)

        # Generate expanded phase sequence to validate phase exists
        expanded_sequence = engine.get_expanded_phase_sequence(
            state.workflow_id, state.completed_phases
        )
        valid_phases = [p[0] for p in expanded_sequence]

        # Check if phase is valid
        if phase not in valid_phases:
            return ToolResponse.error(
                message=f"Invalid phase '{phase}' for workflow '{state.workflow_id}'",
                next_prompt=f"""# Invalid Phase

Phase **{phase}** is not valid for the **{workflow.name}** workflow.

## Valid phases for this workflow:
{chr(10).join([f"- **{p[0]}**{' (review)' if p[1] else ''}" for p in expanded_sequence])}

## Next Steps:
- Use `get_next_phase("{task_id}")` to see the recommended next phase
- Or choose a valid phase from the list above

Try: `execute_phase("{task_id}", "VALID_PHASE_NAME")`""",
                data={
                    "task_id": task_id,
                    "requested_phase": phase,
                    "valid_phases": valid_phases,
                    "workflow_id": state.workflow_id,
                },
            )

        # Check if phase is already completed and force is not set
        if phase in state.completed_phases and not force:
            return ToolResponse.error(
                message=f"Phase '{phase}' is already completed",
                next_prompt=f"""# Phase Already Completed

Phase **{phase}** has already been completed for task **{task_id}**.

## Options:
1. **Force re-execution**: `execute_phase("{task_id}", "{phase}", force=True)`
   - Use this to redo work in the completed phase
   - Previous completion status will be preserved
   
2. **Continue to next phase**: `get_next_phase("{task_id}")`
   - See what phase to work on next
   
3. **Review progress**: `get_progress("{task_id}")`
   - See overall workflow status

## Note:
Force re-execution is useful when you need to:
- Fix issues found in a completed phase
- Update work based on new requirements
- Practice or demonstrate a phase again""",
                data={"task_id": task_id, "phase": phase, "is_completed": True},
            )

        # Check if this is a review phase
        phase_info = next((p for p in expanded_sequence if p[0] == phase), None)
        is_review_phase = phase_info[1] if phase_info else False
        original_phase = phase_info[2] if phase_info else phase

        # Execute the phase using existing engine logic
        if is_review_phase:
            # Handle review phase execution
            return await _execute_review_phase(
                engine, task_id, phase, original_phase, need_context
            )
        # Use existing engine logic for regular phases
        # Mark phase as started if not already
        if phase not in state.started_phases:
            engine.state_manager.mark_phase_started(task_id, phase)

        # Generate phase prompt using existing PromptEngine
        try:
            response = engine.execute_phase(
                task_id, phase, state.workflow_id, need_context
            )
            prompt = response.prompt
            prompt_data = response.model_dump()
        except ValueError as e:
            return ToolResponse.error(
                message=str(e), data={"task_id": task_id, "phase": phase}
            )

        # Create ToolResponse from the returned data
        prompt = response.prompt

        # If forcing re-execution, add a note
        if force and phase in state.completed_phases:
            prompt = f"""# Re-executing Completed Phase

**Note**: You are re-executing phase **{phase}** which was previously completed.
Previous work and context are preserved.

{prompt}"""
            prompt_data["is_force_reexecution"] = True

        return ToolResponse.success(
            message=f"Phase '{phase}' prompt generated",
            next_prompt=prompt,
            data=prompt_data,
        )

    except Exception as e:
        return ToolResponse.error(
            message=f"Failed to execute phase: {e!s}",
            next_prompt=f"Check that task '{task_id}' exists and phase '{phase}' is valid. Use get_next_phase('{task_id}') to see available phases. Check Alfred MCP server logs for details.",
        )


async def _execute_review_phase(
    engine: WorkflowEngine,
    task_id: str,
    review_phase: str,
    original_phase: str,
    need_context: bool,
) -> ToolResponse:
    """Execute a dynamically created review phase."""
    try:
        # Load workflow state
        state = engine.state_manager.get_state(task_id)
        if not state:
            return ToolResponse.error(
                message=f"No workflow state found for task '{task_id}'",
                next_prompt=f"Task '{task_id}' needs a workflow assignment. Use `assign_workflow()` first.",
                data={"task_id": task_id, "error_type": "no_workflow_state"},
            )

        # Mark review phase as started
        if review_phase not in state.started_phases:
            engine.state_manager.mark_phase_started(task_id, review_phase)
            # State saved automatically via task_manager

        # Create review phase configuration dynamically
        review_config = _create_review_phase_config(original_phase)

        # Get previous contexts if requested
        previous_contexts = ""
        if need_context and state.contexts:
            context_entries = []
            for phase_name, contexts in state.contexts.items():
                if contexts:  # Only include phases with actual contexts
                    latest_context = contexts[-1]  # Get most recent context
                    context_entries.append(
                        f"**{phase_name}**: {latest_context['content']}"
                    )

            if context_entries:
                previous_contexts = f"""

## Previous Work Context
{chr(10).join(context_entries)}"""

        # Generate review phase prompt
        review_prompt = f"""# {review_config.name}

## Role
You are a QA Engineer with expertise in quality assurance, code review, and validation testing.

## Core Principles
- Quality is non-negotiable - thorough review prevents future issues
- Focus on both technical correctness and requirements adherence
- Document findings clearly with specific examples
- Provide constructive feedback with improvement suggestions

## Goal
{review_config.goal}

## Current Task
Working on ticket: **{task_id}**
Reviewing phase: **{original_phase}**{previous_contexts}

## Execution Process

First, understand the hierarchical todo pattern:
load_instructions("claude/todowrite")

## Smart Todo Title Generation

When creating subtasks, use this format:
- '[{review_config.name}] - Brief action description'
- Keep titles concise (under 60 characters)
- Focus on the specific review action

Examples:
- '[{review_config.name}] - Load {original_phase} deliverables'
- '[{review_config.name}] - Validate requirements adherence'
- '[{review_config.name}] - Document review findings'

## Create these subtasks under the current parent todo:

X.1 **Load {original_phase} context** → load_instructions("common/load-context")
   Review all work completed in the {original_phase} phase
   Suggested title: '[{review_config.name}] - Load {original_phase} context'

X.2 **Review {original_phase} deliverables** → load_instructions("review/phase-review")
   Validate {original_phase} outputs meet quality standards and requirements
   Suggested title: '[{review_config.name}] - Review {original_phase} deliverables'

X.3 **Check requirements adherence** → load_instructions("review/requirements-check")
   Ensure all original requirements were addressed properly
   Suggested title: '[{review_config.name}] - Check requirements adherence'

X.4 **Document review findings** → load_instructions("common/save-context")
   Record review results, issues found, and recommendations
   Suggested title: '[{review_config.name}] - Document review findings'

Replace X with the current parent todo number. For example, if the parent todo is #3, create subtasks as 3.1, 3.2, etc.
# TODO: CONFUSING - This references Task Master's numbering system, not Alfred's Linear integration

Execute each subtask by:
1. Create todo with smart title
2. Mark as in_progress
3. Load and follow instructions
4. Mark as completed

Only mark the parent phase todo as completed after ALL subtasks are done.

## Context Management
IMPORTANT: Load the save_context instruction ONLY ONCE per conversation using: load_instructions("common/save-context")
After completing significant work (not every step), save context with the loaded instruction guidance.

## Quality Standards
- **Completeness**: All {original_phase} deliverables reviewed thoroughly
- **Accuracy**: Requirements adherence validated with specific examples
- **Clarity**: Review findings documented with actionable feedback
- **Consistency**: Standards applied uniformly across all deliverables

## Communication Style
Professional and constructive. Focus on improvement opportunities while
acknowledging good work. Use specific examples when identifying issues.
Provide clear recommendations for addressing any problems found.

## Phase Completion
- Complete all review steps before marking phase as COMPLETE
- Save final context with status="COMPLETE"
- Provide clear summary of review results and next steps"""

        return ToolResponse.success(
            message=f"Executing {review_phase} for task '{task_id}'",
            next_prompt=review_prompt,
            data={
                "task_id": task_id,
                "phase": review_phase,
                "original_phase": original_phase,
                "is_review_phase": True,
                "workflow_id": state.workflow_id,
                "is_resume": review_phase in state.started_phases,
            },
        )

    except Exception:
        raise


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
