"""MCP tool wrappers for task enhancement operations."""

from typing import Optional
from alfred.core.tasks.enhance import (
    enhance_task_scope_logic,
    simplify_task_logic,
)
from alfred.config import get_config


def register(server) -> int:
    """Register task enhancement tools (enhance_task_scope and simplify_task only)."""
    tools_registered = 0

    @server.tool
    async def enhance_task_scope(
        task_id: str,
        enhancement_prompt: Optional[str] = None,
    ) -> dict:
        """
        Enhance a task's scope by adding comprehensive requirements.

        This tool uses AI to expand a task with additional requirements, edge cases,
        non-functional requirements, and testing considerations. It preserves existing
        requirements while making the task more comprehensive.

        Key features:
        - Adds functional and non-functional requirements
        - Identifies edge cases and error scenarios
        - Includes testing and validation requirements
        - Increases task priority if appropriate
        - Preserves original requirements

        Use this tool when:
        - You need to make a task more comprehensive
        - You want to ensure all edge cases are covered
        - You need to add quality requirements to a task
        - You're preparing tasks for sprint planning

        Args:
            task_id: Linear task ID to enhance (e.g., "AUTH-123")
            enhancement_prompt: Optional specific guidance for enhancement

        Returns:
            Enhanced task with additional requirements
        """
        config = get_config()

        return await enhance_task_scope_logic(
            api_key=config.linear_api_key,
            task_id=task_id,
            enhancement_prompt=enhancement_prompt,
        )

    tools_registered += 1

    @server.tool
    async def simplify_task(
        task_id: str,
        simplification_prompt: Optional[str] = None,
    ) -> dict:
        """
        Simplify a task to its core requirements.

        This tool uses AI to reduce a task to its essential requirements, moving
        nice-to-have features to a "future enhancements" section. It helps create
        MVP-focused tasks.

        Key features:
        - Identifies core vs nice-to-have requirements
        - Moves advanced features to future enhancements
        - Simplifies implementation approach
        - Reduces task priority if appropriate
        - Maintains essential value

        Use this tool when:
        - You need to create an MVP version of a task
        - A task has become too complex to implement
        - You want to defer advanced features
        - You're managing limited sprint capacity

        Args:
            task_id: Linear task ID to simplify (e.g., "AUTH-123")
            simplification_prompt: Optional specific guidance for simplification

        Returns:
            Simplified task with core requirements only
        """
        config = get_config()

        return await simplify_task_logic(
            api_key=config.linear_api_key,
            task_id=task_id,
            simplification_prompt=simplification_prompt,
        )

    tools_registered += 1

    return tools_registered
