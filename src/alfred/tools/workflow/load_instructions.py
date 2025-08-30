"""MCP tool wrapper for load_instructions."""

from alfred.core.workflow.operations.load_instructions import load_instructions_logic


def register(server) -> int:
    """Register the load_instructions tool."""

    @server.tool
    async def load_instructions(name: str) -> dict:
        """Load workflow instructions and task checklists for guided execution.

        - Provides access to curated instruction sets for specific workflows
        - Supports both filename-based discovery and direct path access
        - Instructions are organized by workflow type and execution phase
        - Essential for just-in-time guidance during workflow execution
        - Automatically validates instruction availability with fallbacks

        Parameters
        ----------
        name [string] (required) - Instruction identifier to load:
            - Simple name: "create-next-story" (searches across all directories)
            - Category path: "planning/request-review" (direct path access)
            - Workflow specific: "prd/gather-feedback", "test_plan/create_test_cases"
            - Task management: "task_management/create", "task_management/update"

        Usage notes:
        - Instructions discovered by filename across prompt directory tree
        - Supports both .md files and other instruction formats
        - Used internally by workflow execution tools for guidance
        - Falls back to auto-generated instructions if files missing
        - Case-sensitive filename matching

        Instruction categories:
        - planning/: Planning phase workflows and templates
        - prd/: Product requirements document creation
        - test_plan/: Testing strategy and execution planning
        - create_tasks_from_spec/: Task decomposition from specifications
        - task_management/: Local task operations and workflows

        Returns
        -------
            ToolResponse with instruction content:
            - content: Full instruction text with formatting
            - metadata: Instruction type and validation status
            - source_path: Location of loaded instruction file

        Examples
        --------
            # Load general instruction by name
            load_instructions("create-next-story")

            # Load category-specific instruction
            load_instructions("planning/request-review")

            # Load workflow phase instruction
            load_instructions("prd/gather-feedback")

            # Load task management guidance
            load_instructions("task_management/create")

        Error conditions:
        - Instruction file not found (falls back to auto-generated)
        - Invalid file path or permission issues
        - Malformed instruction content

        """
        result = await load_instructions_logic(name)
        return result.model_dump()

    return 1  # Number of tools registered
