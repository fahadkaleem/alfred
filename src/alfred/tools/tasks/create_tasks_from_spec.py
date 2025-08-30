"""MCP tool wrapper for create_tasks_from_spec."""

import asyncio
import logging
from typing import Optional
from alfred.mcp import mcp
from alfred.core.tasks.create_from_spec import create_tasks_from_spec_logic

logger = logging.getLogger(__name__)


@mcp.tool
async def create_tasks_from_spec(
    spec_path: str,
    num_tasks: int = 10,
    epic_id: Optional[str] = None,
    epic_name: Optional[str] = None,
    research_mode: bool = False,
    is_claude_code: bool = True,  # Default to true since MCP is primarily used by Claude Code
) -> dict:
    """
    Parse a specification document and create tasks in platform using AI-powered task generation.

    This tool transforms product requirements documents (PRDs), technical specifications, or
    any structured requirements text into well-formed development tasks in platform. It uses
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

    IMPORTANT: This tool requires BOTH platform API key and Anthropic API key to be configured.
    The platform API key enables task creation, while the Anthropic API key powers the AI
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
    - Epic and Project are synonymous in platform - this tool uses "epic" for consistency
    - You can either: (1) specify existing epic_id, (2) provide epic_name for new epic,
        or (3) let AI suggest an epic based on specification content
    - Tasks without epic association will be created in the team's backlog
    - Created epics will be visible in platform's Projects section immediately

    Task Generation Control:
    - num_tasks=0: Let AI determine optimal count based on specification complexity
    - num_tasks=1-50: Target specific number (AI may adjust ±20% for logical grouping)
    - num_tasks >50: Will be capped at 50 to prevent overwhelming task creation
    - Complex specs naturally generate more detailed subtasks and dependencies

    WARNING: Large Specifications Handling:
    - Specifications >50,000 characters may be truncated or chunked
    - Very complex specs may timeout - consider breaking into multiple calls
    - Each task creation is atomic - partial failures won't leave orphaned tasks

    File Format Support:
    - Supports .txt and .md/.markdown files
    - File must exist and be readable
    - Empty files will return EMPTY_FILE error
    - Invalid paths will return FILE_NOT_FOUND error

    Args:
        spec_path: Path to specification document (.txt or .md). Can be absolute or
            relative path. File must exist and contain the PRD, technical specification,
            or feature requirements to parse. Maximum recommended file size is ~50,000
            characters for optimal processing.

        num_tasks: Target number of tasks to generate (default: 10). Valid range
            is 0-50. Set to 0 to let AI determine the appropriate number based on
            specification complexity. AI will aim for this target but may adjust
            slightly for logical task grouping.

        epic_id: Optional platform project/epic ID to add tasks to. If provided,
            all created tasks will be associated with this epic. Use list_projects
            tool to discover available epic IDs. If not provided and epic_name is
            not set, tasks will be created without epic association.

        epic_name: Optional name for a new epic to create. Only used if epic_id
            is not provided. If specified, a new epic will be created with this
            name and all tasks will be associated with it. If neither epic_id
            nor epic_name is provided, AI may suggest creating an epic based on
            the specification content.

        research_mode: Enable research mode for enhanced task generation (default: False).
            When enabled, the AI will research current best practices, technologies,
            and libraries before generating tasks, resulting in more detailed and
            up-to-date implementation guidance.

        is_claude_code: Whether the tool is being called from Claude Code (default: True).
            When True, enables codebase analysis instructions in the prompt. Set to
            False when using from other environments like Cursor or VS Code.

    Returns:
        Dictionary containing:
        - success: Boolean indicating if operation succeeded
        - epic: Created/resolved epic info (id, title, url) if applicable
        - tasks: List of created tasks with their Linear IDs and URLs
        - summary: Statistics about the operation (requested, created, skipped counts)
        - errors: List of any errors encountered during processing

    Error Codes:
        - FILE_NOT_FOUND: Specification file doesn't exist
        - NOT_A_FILE: Path points to a directory, not a file
        - UNSUPPORTED_FORMAT: File format not supported (only .txt, .md, .markdown)
        - EMPTY_FILE: Specification file is empty
        - READ_ERROR: Failed to read file (permissions or other IO error)
        - INVALID_NUM_TASKS: num_tasks outside valid range (0-50)
        - AI_GENERATION_FAILED: AI couldn't generate tasks from spec
        - PLATFORM_CREATION_FAILED: Failed to create tasks in platform
        - API_AUTH_ERROR: Platform authentication failed
        - UNEXPECTED_ERROR: Other unexpected errors

    Examples:
        # Basic usage with default settings
        create_tasks_from_spec(
            spec_path="/project/docs/prd.txt"
        )

        # Let AI determine task count
        create_tasks_from_spec(
            spec_path="/project/specs/ecommerce.md",
            num_tasks=0
        )

        # Add to existing epic
        create_tasks_from_spec(
            spec_path="./requirements/mobile-features.txt",
            epic_id="LIN-PROJ-123"
        )

        # Create new epic
        create_tasks_from_spec(
            spec_path="/Users/alice/docs/q1-features.md",
            epic_name="Q1 2024 Development"
        )
    """
    config = mcp.state.config

    # Check workspace configuration
    if not config.team_name:
        return {
            "success": False,
            "error": {
                "code": "WORKSPACE_NOT_CONFIGURED",
                "message": "Workspace not configured. Run initialize_workspace first.",
            },
        }

    # Validate platform API key
    if not config.linear_api_key:
        return {
            "success": False,
            "error": {
                "code": "API_AUTH_ERROR",
                "message": "platform API key not configured",
            },
        }

    # Validate Anthropic API key for AI features
    if not config.anthropic_api_key:
        logger.warning("Anthropic API key not configured - AI generation may fail")
        # Don't return error, let it try and fail with fallback

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

    # Call business logic with spec_path and new parameters
    result = await create_tasks_from_spec_logic(
        spec_path=spec_path,
        num_tasks=num_tasks,
        api_key=config.linear_api_key,
        team_name=config.team_name,
        epic_name=epic_name,
        epic_id=epic_id,
        project_context=project_context,
        research_mode=research_mode,
        is_claude_code=is_claude_code,
    )

    return result
