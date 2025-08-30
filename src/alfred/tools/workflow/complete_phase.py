"""MCP tool wrapper for complete_phase."""

from alfred.core.workflow.operations.complete_phase import complete_phase_logic


def register(server) -> int:
    """Register the complete_phase tool."""

    @server.tool
    async def complete_phase(task_id: str, phase: str, summary: str) -> dict:
        """Mark a workflow phase as complete and automatically advance to next phase.

        - Finalizes current phase work and persists context for future reference
        - Automatically determines and advances to next phase in workflow sequence
        - Saves comprehensive phase summary and accomplishments
        - Triggers workflow progression with proper state management
        - Provides clear guidance for next steps and phase transitions

        Parameters
        ----------
        task_id [string] (required) - The task to complete the phase for:
            - External task keys: "PROJ-123", "AL-456"
            - Local Alfred tasks: AL-1, AL-2, AL-3, etc.
            - Must have active workflow with current phase in progress
        phase [string] (required) - The phase being completed:
            - Phase name must match currently active phase for your workflow
            - Example phases: "claim", "plan", "implement", "test", "review"
            - "claim" - Task assignment and setup completed
            - "plan" - Planning and requirements analysis finished
            - "implement" - Implementation and development completed
            - "test" - Testing and validation finished
            - "review" - Review and quality assurance completed
            - Must match currently active phase
        summary [string] (required) - Brief summary of phase accomplishments:
            - Key deliverables created or completed
            - Important decisions made and rationale
            - Critical insights or discoveries
            - Status of phase objectives and outcomes
            - Any blockers resolved or remaining issues

        Usage scenarios:
        - Phase completion: When all phase objectives have been achieved
        - Milestone marking: Recording significant progress and achievements
        - Team handoffs: Documenting work for next team member or phase
        - Progress tracking: Maintaining comprehensive workflow history
        - Quality gates: Formal completion with validation and review

        Automatic behaviors:
        - Saves context with status="COMPLETE" for permanent record
        - Determines next phase based on workflow configuration
        - Updates task progress and completion percentages
        - Triggers review phase insertion if required by workflow
        - Advances workflow state to next phase automatically

        Returns
        -------
            ToolResponse with completion confirmation and next steps:
            - completion_status: Phase marked complete with timestamp
            - phase_summary: Saved summary and accomplishments
            - next_phase: What phase comes next in the workflow
            - progress_update: Overall task progress and completion percentage
            - next_steps: Recommended actions for continuing work
            - workflow_status: Overall workflow health and timeline

        Examples
        --------
            # Complete planning phase
            complete_phase("PROJ-123", "plan", "Completed requirements analysis and created technical design. Decided to use microservices architecture.")

            # Finish implementation work
            complete_phase("AL-456", "implement", "Implemented authentication system with JWT tokens. All unit tests passing.")

            # Complete testing phase
            complete_phase("TASK-789", "test", "Created comprehensive test suite with 95% coverage. All integration tests passing.")

        Workflow progression:
        - Phase completion triggers automatic advance to next phase
        - Review phases automatically inserted where required
        - Context preserved and made available to subsequent phases
        - Progress tracking updated with completion timestamps

        Prerequisites:
        - Task must have assigned workflow
        - Phase must be currently active (not already completed)
        - Valid summary describing phase accomplishments

        Error conditions:
        - Phase not currently active or already completed
        - Task has no assigned workflow
        - Invalid phase name for workflow type
        - Context saving failures or storage issues

        """
        result = await complete_phase_logic(task_id, phase, summary)
        return result.model_dump()

    return 1  # Number of tools registered
