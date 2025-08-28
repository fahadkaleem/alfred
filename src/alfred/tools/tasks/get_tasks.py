"""MCP tool wrapper for get_tasks."""

from typing import Optional
from alfred.core.tasks.list import get_tasks_logic
from alfred.config import get_config


def register(server) -> int:
    """Register the get_tasks tool."""

    @server.tool
    def get_tasks(
        status: Optional[str] = None,
        epic_id: Optional[str] = None,
        page: int = 1,
        per_page: int = 50,
    ) -> dict:
        """
        List tasks with optional filters (status, epic) and pagination.

        This tool retrieves tasks from Linear with filtering capabilities and structured
        pagination support. Tasks are automatically mapped from Linear's data model to
        Alfred's standardized task format.

        Key features:
        - Supports multiple status filtering with comma-separated values
        - Epic-based task organization and filtering
        - Efficient pagination for large task datasets
        - Automatic Linear ↔ Alfred status mapping
        - Structured response format for easy processing

        Use this tool when:
        - You need to view tasks across one or more statuses
        - You want to see all tasks within a specific epic/project
        - You need paginated results for large task sets
        - You want to get an overview of task distribution

        Crucial Guardrails:
        - Use get_task instead when you need complete details for a single, specific task
        - Use epic management tools first if you need to discover available epics
        - Don't use this for task creation or updates - use create_task or update_task_status

        Usage Guidance:

        IMPORTANT: This tool automatically maps Linear status names to Alfred's standardized
        format. You should always filter by Alfred status names (pending, in_progress, done,
        cancelled), never by Linear's internal names.

        CRITICAL: The per_page parameter has a maximum limit of 100 items. For large datasets,
        use pagination rather than requesting all items at once to avoid timeouts.

        When using status filtering:
        - Use comma-separated Alfred status names: "pending,in_progress"
        - Status filtering is case-insensitive but stick to lowercase for consistency
        - Empty or invalid statuses in the comma list are ignored silently

        For large datasets:
        - Start with per_page=50 (default) for good balance of performance and completeness
        - Use page parameter for sequential pagination: page 1, then page 2, etc.
        - Check has_next in response to determine if more pages exist
        - Consider filtering by epic_id first to reduce result set size

        Performance Considerations:
        - Filtering by epic_id significantly improves response time for large workspaces
        - Status filtering is performed on the Linear side, not client-side
        - Pagination cursors are handled automatically - you only need to increment page

        Status Mapping:
        - Linear: backlog/todo → Alfred: pending
        - Linear: in_progress → Alfred: in_progress
        - Linear: done → Alfred: done
        - Linear: canceled → Alfred: cancelled

        Args:
            status: Comma-separated list of Alfred task statuses to filter by. Valid values:
                "pending", "in_progress", "done", "cancelled". Example: "pending,in_progress"
                returns tasks in either status. Default: returns all statuses. Case-insensitive
                but lowercase recommended. Invalid status names in the list are silently ignored.
            epic_id: Filter by specific Linear project/epic ID. Must be a valid epic ID from
                your workspace. Use list_projects tool to discover available epic IDs.
                Default: returns tasks from all epics. Empty string is treated as no filter.
            page: Page number for pagination, starting at 1. Must be positive integer.
                Default: 1. Use with has_next response field to determine if more pages exist.
                Pages beyond available data return empty results without error.
            per_page: Number of items per page, between 1-100. Default: 50. Higher values may
                cause slower response times. Consider using 25 for faster responses or 100 for
                fewer API calls when processing large datasets.

        Returns:
            Dictionary with:
            - items: Array of AlfredTask objects
            - page: Current page number
            - per_page: Items per page
            - total: Total count (if available)
            - has_next: Whether more pages exist
            - next_cursor: Cursor for next page
        """
        config = get_config()

        return get_tasks_logic(
            api_key=config.linear_api_key,
            status=status,
            epic_id=epic_id,
            page=page,
            per_page=per_page,
        )

    return 1
