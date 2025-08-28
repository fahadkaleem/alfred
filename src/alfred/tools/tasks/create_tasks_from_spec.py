"""MCP tool wrapper for create_tasks_from_spec."""

import asyncio
import logging
from typing import Optional
from alfred.core.tasks.create_from_spec import (
    create_tasks_from_spec_logic,
    read_spec_file,
)
from alfred.config import get_config

logger = logging.getLogger(__name__)


def register(server) -> int:
    """Register the create_tasks_from_spec tool."""

    @server.tool
    async def create_tasks_from_spec(
        spec_content: str,
        num_tasks: int = 10,
        epic_id: Optional[str] = None,
        epic_name: Optional[str] = None,
    ) -> dict:
        """
        Parse a specification document and create tasks in Linear using AI-powered task generation.

        This tool transforms product requirements documents (PRDs), technical specifications, or
        any structured requirements text into well-formed development tasks in Linear. It uses
        AI to understand requirements, break them down into actionable work items, and creates
        them with proper project association, dependencies, and structured metadata.

        Key features:
        - AI-powered requirement analysis with intelligent task decomposition
        - Automatic project/epic creation or association for organized task management
        - Smart chunking for large specifications (>3000 tokens) with context preservation
        - Dependency detection and automatic linking between related tasks
        - Acceptance criteria and technical notes generation for each task
        - Complexity scoring and priority assignment based on requirement analysis

        Use this tool when:
        - You need to transform a PRD or specification into actionable development tasks
        - You want to quickly populate a project backlog from requirements documentation
        - You're starting a new project and need to create an initial task breakdown
        - You have a feature specification that needs to be decomposed into work items
        - You need to ensure all requirements are captured as trackable tasks

        Crucial Guardrails:
        - Use initialize_workspace FIRST if workspace is not configured
        - Use list_projects to discover existing epic IDs before specifying epic_id
        - Use create_task for single, well-defined tasks instead of this tool
        - Don't use this for updating existing tasks - use update_task_status instead
        - Don't use this for simple task lists - this tool is for comprehensive specifications

        Usage Guidance and Specification Requirements:

        IMPORTANT: This tool requires BOTH Linear API key and Anthropic API key to be configured.
        The Linear API key enables task creation, while the Anthropic API key powers the AI
        analysis. Without Anthropic API key, the tool will fail with AI_GENERATION_FAILED.

        CRITICAL: The specification content must be substantial enough for meaningful analysis.
        Single-line descriptions or vague requirements will produce poor results. Include user
        stories, acceptance criteria, technical constraints, and success metrics for best outcomes.

        Specification Best Practices:
        - Use markdown formatting with clear sections (## Features, ## Requirements, etc.)
        - Include user stories in the format: "As a [user], I want [feature] so that [benefit]"
        - Specify technical requirements, constraints, and non-functional requirements
        - Break down complex features into logical groupings or phases
        - Include acceptance criteria for major features when known

        Epic/Project Management:
        - Epic and Project are synonymous in Linear - this tool uses "epic" for consistency
        - You can either: (1) specify existing epic_id, (2) provide epic_name for new epic,
          or (3) let AI suggest an epic based on specification content
        - Tasks without epic association will be created in the team's backlog
        - Created epics will be visible in Linear's Projects section immediately

        Task Generation Control:
        - num_tasks=0: Let AI determine optimal count based on specification complexity
        - num_tasks=1-50: Target specific number (AI may adjust ±20% for logical grouping)
        - num_tasks >50: Will be capped at 50 to prevent overwhelming task creation
        - Complex specs naturally generate more detailed subtasks and dependencies

        WARNING: Large Specifications Handling:
        - Specifications >50,000 characters may be truncated or chunked
        - Very complex specs may timeout - consider breaking into multiple calls
        - Each task creation is atomic - partial failures won't leave orphaned tasks

        File Path Detection:
        - If spec_content appears to be a file path (ends with .txt, .md, .markdown and <500 chars),
          the tool will attempt to read it as a file first
        - If file reading fails, it treats the content as literal specification text
        - This allows flexibility in passing either content or file paths

        Args:
            spec_content: The specification document content to parse. Can be a PRD,
                technical specification, feature requirements, or any structured text
                describing work to be done. Supports markdown formatting. Maximum
                recommended size is ~50,000 characters for optimal processing.

            num_tasks: Target number of tasks to generate (default: 10). Valid range
                is 0-50. Set to 0 to let AI determine the appropriate number based on
                specification complexity. AI will aim for this target but may adjust
                slightly for logical task grouping.

            epic_id: Optional Linear project/epic ID to add tasks to. If provided,
                all created tasks will be associated with this epic. Use list_projects
                tool to discover available epic IDs. If not provided and epic_name is
                not set, tasks will be created without epic association.

            epic_name: Optional name for a new epic to create. Only used if epic_id
                is not provided. If specified, a new epic will be created with this
                name and all tasks will be associated with it. If neither epic_id
                nor epic_name is provided, AI may suggest creating an epic based on
                the specification content.

        Returns:
            Dictionary containing:
            - success: Boolean indicating if operation succeeded
            - epic: Created/resolved epic info (id, title, url) if applicable
            - tasks: List of created tasks with their Linear IDs and URLs
            - summary: Statistics about the operation (requested, created, skipped counts)
            - errors: List of any errors encountered during processing

        Error Codes:
            - EMPTY_SPEC: Specification content is empty
            - INVALID_NUM_TASKS: num_tasks outside valid range (0-50)
            - AI_GENERATION_FAILED: AI couldn't generate tasks from spec
            - LINEAR_CREATION_FAILED: Failed to create tasks in Linear
            - API_AUTH_ERROR: Linear authentication failed
            - UNEXPECTED_ERROR: Other unexpected errors

        Examples:
            # Basic usage with default settings
            create_tasks_from_spec(
                spec_content="Build user authentication system with email/password..."
            )

            # Let AI determine task count
            create_tasks_from_spec(
                spec_content="Complex e-commerce platform requirements...",
                num_tasks=0
            )

            # Add to existing epic
            create_tasks_from_spec(
                spec_content="Mobile app features...",
                epic_id="LIN-PROJ-123"
            )

            # Create new epic
            create_tasks_from_spec(
                spec_content="Q1 2024 Features...",
                epic_name="Q1 2024 Development"
            )
        """
        config = get_config()

        # Check workspace configuration
        if not config.team_id:
            return {
                "success": False,
                "error": {
                    "code": "WORKSPACE_NOT_CONFIGURED",
                    "message": "Workspace not configured. Run initialize_workspace first.",
                },
            }

        # Validate Linear API key
        if not config.linear_api_key:
            return {
                "success": False,
                "error": {
                    "code": "API_AUTH_ERROR",
                    "message": "Linear API key not configured",
                },
            }

        # Validate Anthropic API key for AI features
        if not config.anthropic_api_key:
            logger.warning("Anthropic API key not configured - AI generation may fail")
            # Don't return error, let it try and fail with fallback

        # If spec_content looks like a file path, try to read it
        if len(spec_content) < 500 and (
            spec_content.endswith(".txt")
            or spec_content.endswith(".md")
            or spec_content.endswith(".markdown")
        ):
            file_content = read_spec_file(spec_content)
            if file_content:
                spec_content = file_content
            # If read fails, proceed with original content
            # (might be actual spec content that happens to end with .txt)

        # Get project context if available
        project_context = None
        try:
            # Try to get project README or description for context
            import os

            readme_path = os.path.join(os.getcwd(), "README.md")
            if os.path.exists(readme_path):
                with open(readme_path, "r") as f:
                    project_context = f.read()[:2000]  # First 2000 chars
        except Exception:
            pass

        # Call business logic
        result = await create_tasks_from_spec_logic(
            spec_content=spec_content,
            num_tasks=num_tasks,
            api_key=config.linear_api_key,
            team_id=config.team_id,
            epic_name=epic_name,
            epic_id=epic_id,
            project_context=project_context,
        )

        return result

    return 1
