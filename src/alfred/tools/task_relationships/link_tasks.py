"""MCP tool wrapper for link_tasks."""

from alfred.core.task_relationships.link_tasks import link_tasks_logic
from alfred.clients.linear.domain.enums import IssueRelationType
from alfred.config import get_config


def register(server) -> int:
    """Register the link_tasks tool."""

    @server.tool
    def link_tasks(
        blocker_task_id: str,
        blocked_task_id: str,
        relation_type: str = IssueRelationType.BLOCKS,
    ) -> dict:
        """
        Create a blocking relationship between two tasks in Linear.

        This tool creates task dependencies using Linear's native blocking/blocked relationships
        with automatic cycle detection to prevent circular dependencies.

        Key features:
        - Creates Linear issue relations with validation
        - Prevents circular dependencies with graph traversal
        - Validates both tasks exist before linking
        - Supports different relationship types (blocks, relates, duplicates)
        - Returns detailed relationship information

        Use this tool when:
        - You need to establish task prerequisites and execution order
        - You want to create blocking relationships between tasks
        - You need to define dependencies for project planning
        - You're organizing work with clear task ordering

        Crucial Guardrails:
        - Tool prevents self-linking (task cannot block itself)
        - Automatic cycle detection prevents circular dependencies
        - Both tasks must exist before linking
        - Duplicate relationships are detected and rejected

        Args:
            blocker_task_id: Linear issue ID of the task that will block (prerequisite)
            blocked_task_id: Linear issue ID of the task that will be blocked (dependent)
            relation_type: Type of relationship - "blocks" (default), "relates", or "duplicates"

        Returns:
            Dictionary with success status, message, and relationship details
        """
        config = get_config()

        return link_tasks_logic(
            api_key=config.linear_api_key,
            blocker_task_id=blocker_task_id,
            blocked_task_id=blocked_task_id,
            relation_type=relation_type,
        )

    return 1
