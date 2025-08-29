"""Business logic for finding the next task to work on."""

import logging
from typing import Dict, List, Optional, Any
from pydantic import BaseModel

from alfred.adapters.linear_adapter import LinearAdapter
from alfred.adapters.base import NotFoundError
from alfred.models.tasks import AlfredTask, TaskStatus, TaskStatusGroups

logger = logging.getLogger(__name__)


class NextTaskResult(BaseModel):
    """Result of next task selection."""

    success: bool
    next_task: Optional[Dict[str, Any]] = None
    is_subtask: bool = False
    reasoning: Optional[str] = None
    alternatives: List[Dict[str, Any]] = []
    error: Optional[str] = None


async def get_next_task_logic(
    api_key: str,
    epic_id: Optional[str] = None,
    assignee_id: Optional[str] = None,
    include_blocked: bool = False,
) -> NextTaskResult:
    """
    Intelligently find the next task to work on based on priorities and dependencies.

    Args:
        api_key: Linear API key
        epic_id: Filter by specific epic (optional)
        assignee_id: Filter by assignee (optional)
        include_blocked: Include blocked tasks in consideration

    Returns:
        NextTaskResult with selected task and reasoning
    """
    try:
        adapter = LinearAdapter(api_token=api_key)

        # Get tasks from Linear
        if epic_id:
            tasks = adapter.get_tasks(epic_id=epic_id)
        else:
            tasks = adapter.get_tasks()

        if not tasks:
            return NextTaskResult(success=True, reasoning="No tasks found in workspace")

        # Filter tasks by assignee if specified
        if assignee_id:
            tasks = [task for task in tasks if task.get("assignee_id") == assignee_id]

        # Build completed task set for dependency checking
        completed_ids = set()
        for task in tasks:
            task_status = TaskStatus.from_linear(task.get("status", ""))
            if task_status in TaskStatusGroups.COMPLETED:
                completed_ids.add(task.get("id"))

        # Priority values for sorting
        priority_values = {"high": 3, "medium": 2, "low": 1}

        # 1. First priority: Find subtasks of in-progress tasks
        subtask_candidates = []
        in_progress_tasks = [
            task
            for task in tasks
            if TaskStatus.from_linear(task.get("status", "")) in TaskStatusGroups.ACTIVE
        ]

        for parent_task in in_progress_tasks:
            # Note: This assumes Linear has subtask relationships
            # In actual implementation, you'd need to check for Linear's sub-issue structure
            # For now, we'll skip this and go to main task prioritization
            pass

        # 2. Find eligible top-level tasks
        eligible_tasks = []
        for task in tasks:
            task_status = TaskStatus.from_linear(task.get("status", ""))

            # Skip completed tasks
            if task_status in TaskStatusGroups.COMPLETED:
                continue

            # Skip blocked tasks unless requested
            # Note: We don't have a BLOCKED status in the enum yet
            # For now, include all non-completed tasks
            if not task_status in TaskStatusGroups.ELIGIBLE:
                continue

            # Check if all dependencies are satisfied
            dependencies = task.get("dependencies", [])
            if dependencies:
                # Check if all dependency tasks are completed
                deps_satisfied = all(dep_id in completed_ids for dep_id in dependencies)
                if not deps_satisfied:
                    continue

            eligible_tasks.append(task)

        if not eligible_tasks:
            return NextTaskResult(
                success=True,
                reasoning="No eligible tasks found. All tasks are either completed or have unmet dependencies.",
            )

        # Sort eligible tasks by priority, then by fewer dependencies, then by ID
        def task_sort_key(task):
            priority = task.get("priority", "medium")
            priority_value = priority_values.get(priority.lower(), 2)
            dependency_count = len(task.get("dependencies", []))
            task_id = task.get("id", "")

            return (
                -priority_value,  # Higher priority first (negative for reverse sort)
                dependency_count,  # Fewer dependencies first
                task_id,  # Consistent ordering by ID
            )

        sorted_tasks = sorted(eligible_tasks, key=task_sort_key)

        # Select the best task
        next_task = sorted_tasks[0]
        alternatives = sorted_tasks[1:3]  # Up to 2 alternatives

        # Generate reasoning
        priority = next_task.get("priority", "medium")
        dep_count = len(next_task.get("dependencies", []))

        reasoning_parts = [f"Selected task with {priority} priority"]
        if dep_count == 0:
            reasoning_parts.append("no dependencies")
        else:
            reasoning_parts.append(f"{dep_count} satisfied dependencies")

        task_status = TaskStatus.from_linear(next_task.get("status", ""))
        if task_status in TaskStatusGroups.ACTIVE:
            reasoning_parts.append("already in progress")

        reasoning = f"Task {next_task.get('id')}: " + ", ".join(reasoning_parts)

        return NextTaskResult(
            success=True,
            next_task={
                "id": next_task.get("id"),
                "title": next_task.get("title"),
                "description": next_task.get("description"),
                "status": next_task.get("status"),
                "priority": next_task.get("priority"),
                "epic_id": next_task.get("epic_id"),
                "dependencies": next_task.get("dependencies", []),
                "url": next_task.get("url"),
            },
            is_subtask=False,  # TODO: Detect if this is a subtask
            reasoning=reasoning,
            alternatives=[
                {
                    "id": alt.get("id"),
                    "title": alt.get("title"),
                    "priority": alt.get("priority"),
                    "status": alt.get("status"),
                }
                for alt in alternatives
            ],
        )

    except Exception as e:
        logger.error(f"Error finding next task: {e}")
        return NextTaskResult(
            success=False, error=f"Failed to find next task: {str(e)}"
        )
