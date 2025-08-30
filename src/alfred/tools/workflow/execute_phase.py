"""MCP tool wrapper for execute_phase."""

from alfred.core.workflow.operations.execute_phase import execute_phase_logic


def register(server) -> int:
    """Register the execute_phase tool."""

    @server.tool
    async def execute_phase(
        task_id: str, phase: str, need_context: bool = True, force: bool = False
    ) -> dict:
        """Execute a specific workflow phase with rich context and focused instructions.

        - Primary tool for intensive workflow phase execution with full context
        - Loads comprehensive phase-specific guidance, roles, and objectives
        - Provides hierarchical todo structure with just-in-time instruction loading
        - Integrates previous phase context for continuity and informed decisions
        - Generates focused execution environment for productive phase work

        Parameters
        ----------
        task_id [string] (required) - The task to execute the phase for:
            - External task keys: "PROJ-123", "AL-456"
            - Local Alfred tasks: AL-1, AL-2, AL-3, etc.
            - Must have assigned workflow for phase execution
        phase [string] (required) - The specific workflow phase to execute:
            - Phase names depend on assigned workflow - use get_next_phase() to see available phases
            - Example phases: "claim", "plan", "implement", "test", "review"
            - "claim" - Task assignment and initial setup
            - "plan" - Requirements analysis and implementation planning
            - "implement" - Code development and feature implementation
            - "test" - Testing strategy and validation execution
            - "review" - Code review and quality assurance
            - Custom phases based on assigned workflow type
        need_context [boolean] - Load previous phase contexts for continuity (default: true):
            - true: Includes context from all completed phases for informed decisions
            - false: Starts fresh without prior context (useful for independent phases)
        force [boolean] - Force re-execution of a completed phase (default: false):
            - false: Prevents re-execution of completed phases (normal behavior)
            - true: Allows working on a phase that was already marked complete
            - Useful for fixing issues, updating work, or practicing phases
            - Previous completion status and context are preserved

        Usage scenarios:
        - Deep work: When you need focused, immersive environment for phase execution
        - Context-dependent phases: When current phase builds on previous work
        - Complex phases: When phase requires detailed guidance and structured approach
        - Quality execution: When you need comprehensive instructions and standards
        - Team handoffs: When resuming work started by others

        Execution features:
        - Phase-specific role assumption (e.g., Technical Planner, Implementation Engineer)
        - Hierarchical todo structure with clear objectives and sub-tasks
        - Just-in-time instruction loading for specific guidance
        - Quality standards and completion criteria definition
        - Integration with previous phase outputs and decisions

        Returns
        -------
            ToolResponse with comprehensive execution environment:
            - role_context: Phase-specific role and responsibilities
            - objectives: Clear goals and expected outcomes
            - todo_structure: Hierarchical tasks with instruction references
            - previous_context: Relevant context from completed phases
            - quality_standards: Completion criteria and validation requirements
            - resources: Available tools and instruction references

        Examples
        --------
            # Execute planning phase with full context
            execute_phase("PROJ-123", "plan")

            # Start implementation without prior context
            execute_phase("AL-456", "implement", need_context=False)

            # Resume testing phase with context
            execute_phase("TASK-789", "test")

            # Force re-execution of completed phase
            execute_phase("PROJ-123", "plan", force=True)

        Workflow integration:
        - Use after get_next_phase() to confirm phase and get detailed execution
        - Follow with complete_phase() when phase work is finished
        - Context automatically saved and made available to future phases
        - Phase completion triggers automatic progression to next phase

        Prerequisites:
        - Task must have assigned workflow (use assign_workflow() first)
        - Phase must be valid for the assigned workflow type
        - Alfred workspace properly initialized

        Error conditions:
        - Task has no assigned workflow
        - Invalid phase for the workflow type
        - Missing phase configuration or instruction files
        - Context loading failures if need_context=true

        """
        result = await execute_phase_logic(task_id, phase, need_context, force)
        return result.model_dump()

    return 1  # Number of tools registered
