"""MCP tool wrapper for list_workflows."""

from alfred.core.workflow.operations.list_workflows import list_workflows_logic


def register(server) -> int:
    """Register the list_workflows tool."""

    @server.tool
    async def list_workflows() -> dict:
        """Discover all available workflow types with detailed descriptions and requirements.

        - Lists all configured workflows with their capabilities and phase structures
        - Essential first step before assigning workflows to tasks
        - Shows workflow complexity, task creation requirements, and use cases
        - Provides workflow IDs needed for assign_workflow() operations
        - Helps choose the right workflow approach for your specific task type

        Usage scenarios:
        - Starting new work: Explore available workflow approaches and methodologies
        - Workflow selection: Compare different workflow types to pick optimal approach
        - Reference lookup: Check requirements like task creation vs existing task assignment
        - Team coordination: Understand standardized workflows available across organization
        - Troubleshooting: Verify workflow availability and configuration status

        Returns:
            ToolResponse with comprehensive workflow catalog:
            - workflow_ids: Identifiers for use with assign_workflow()
            - descriptions: What each workflow accomplishes and when to use it
            - phase_structure: Number and types of phases in each workflow
            - complexity_indicators: Estimated effort and skill requirements
            - task_integration: Whether workflow creates tasks or requires existing ones
            - usage_examples: Practical scenarios and syntax examples
            - prerequisites: Required configurations, permissions, or dependencies

        Example workflow types (use list_workflows() for current available options):
        - "task" - Standard development workflow with planning, implementation, testing phases
        - "tech_spec" - Technical specification creation with research, design, review phases
        - "prd" - Product requirements document workflow with discovery, analysis, validation
        - "test_plan" - Testing strategy workflow with requirements, strategy, execution planning
        - "create_tasks_from_spec" - Task decomposition from specifications into local tasks
        - Additional workflows may be available based on your Alfred configuration

        Examples:
            # Discover all available workflows
            list_workflows()

            # Typical workflow assignment flow
            list_workflows()                           # 1. See all options
            assign_workflow("tech_spec", "PROJ-123")   # 2. Assign chosen workflow
            get_next_phase("PROJ-123")                 # 3. Start execution

        Usage notes:
        - No parameters required - always returns complete workflow catalog
        - Workflow availability depends on Alfred configuration and prompt files
        - Some workflows create new local tasks, others work with existing tasks
        - Phase counts and complexity help estimate effort and timeline
        - Use workflow IDs exactly as shown for assign_workflow() calls

        Error conditions:
        - Workflow configuration files missing or malformed
        - Prompt directory structure issues
        - YAML parsing errors in workflow definitions

        """
        result = await list_workflows_logic()
        return result.model_dump()

    return 1  # Number of tools registered
