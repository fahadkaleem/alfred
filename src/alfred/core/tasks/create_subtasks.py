"""Business logic for creating subtasks."""

import logging
from typing import List, Optional
from alfred.adapters.linear_adapter import LinearAdapter
from alfred.adapters.base import NotFoundError
from alfred.models.tasks import to_alfred_task, AlfredTask
from alfred.models.subtask_responses import (
    SubtaskCreationResult,
    BatchSubtaskResult,
    BatchSubtaskCreationResult,
)
from alfred.ai_services import AIService
from alfred.ai_services.exceptions import AIServiceError
from alfred.core.tasks.constants import (
    MIN_SUBTASKS,
    MAX_SUBTASKS,
    DEFAULT_SUBTASKS,
    TITLE_WORD_DIVISOR,
    DEFAULT_COMPLEXITY_THRESHOLD,
    INELIGIBLE_STATUSES,
)

logger = logging.getLogger(__name__)


async def create_subtasks_logic(
    api_key: str,
    task_id: str,
    num_subtasks: int = DEFAULT_SUBTASKS,
    context: Optional[str] = None,
    force: bool = False,
) -> SubtaskCreationResult:
    """
    Create AI-generated subtasks for a task.

    Args:
        api_key: Linear API key
        task_id: Task ID to create subtasks for
        num_subtasks: Number of subtasks to generate (default: 3)
        context: Optional additional context for subtask generation
        force: Force creation even if subtasks exist

    Returns:
        Dict with subtask creation results
    """
    adapter = LinearAdapter(api_token=api_key)

    # Get the task from Linear
    task = adapter.get_task(task_id)
    if not task:
        raise NotFoundError(f"Task not found: {task_id}")

    # Convert to Alfred task format
    alfred_task = to_alfred_task(task)

    # Check if task is eligible for subtask creation
    if alfred_task.status in INELIGIBLE_STATUSES:
        raise ValueError(
            f"Cannot create subtasks for task with status '{alfred_task.status}'"
        )

    # Check if task already has subtasks
    try:
        children = adapter.get_task_children(task_id)
    except NotFoundError:
        children = []

    if children and not force:
        raise ValueError(
            f"Task {task_id} already has {len(children)} subtasks. Use force=True to override."
        )

    # Clear existing subtasks if force is True
    if children and force:
        logger.info(f"Clearing {len(children)} existing subtasks for task {task_id}")
        for child in children:
            adapter.delete_task(child["id"])

    # Use AI service to generate subtasks
    ai_service = AIService()

    # Prepare task context for AI
    task_context = {
        "title": alfred_task.title,
        "description": alfred_task.description or "",
        "epic_id": alfred_task.epic_id,
    }

    # Generate subtasks using AI
    generated_subtasks = await ai_service.decompose_task(
        task=task_context, num_subtasks=num_subtasks, context=context, stream=False
    )

    # Create subtasks in Linear
    created_subtasks: List[AlfredTask] = []
    for idx, subtask_data in enumerate(generated_subtasks, 1):
        # Create subtask in Linear
        subtask_title = subtask_data.get("title", f"Subtask {idx}")
        subtask_description = subtask_data.get("description", "")

        # Add technical details to description
        if "technical_details" in subtask_data:
            subtask_description += (
                f"\n\n**Technical Details:**\n{subtask_data['technical_details']}"
            )

        # Add acceptance criteria to description
        if "acceptance_criteria" in subtask_data:
            criteria = subtask_data.get("acceptance_criteria", [])
            if criteria:
                subtask_description += "\n\n**Acceptance Criteria:**\n"
                for criterion in criteria:
                    subtask_description += f"- {criterion}\n"

        # Create the subtask in Linear
        created_task = adapter.create_subtask(
            parent_id=task_id, title=subtask_title, description=subtask_description
        )

        # Convert to Alfred format
        alfred_subtask = to_alfred_task(created_task)
        created_subtasks.append(alfred_subtask)

    return SubtaskCreationResult(
        task_id=alfred_task.id,
        task_title=alfred_task.title,
        subtasks_created=created_subtasks,
        message=f"Task {task_id} decomposed into {len(created_subtasks)} subtasks",
    )


async def create_all_subtasks_logic(
    api_key: str,
    epic_id: Optional[str] = None,
    num_subtasks: Optional[int] = None,
    context: Optional[str] = None,
    force: bool = False,
    threshold: int = DEFAULT_COMPLEXITY_THRESHOLD,
) -> BatchSubtaskCreationResult:
    """
    Create subtasks for all eligible tasks in batch.

    Args:
        api_key: Linear API key
        epic_id: Optional epic ID to filter tasks
        num_subtasks: Optional number of subtasks per task
        context: Optional additional context for subtask generation
        force: Force creation even if tasks have subtasks
        threshold: Complexity threshold for auto-creation (default: 7)

    Returns:
        Dict with batch subtask creation results
    """
    adapter = LinearAdapter(api_token=api_key)

    # Get tasks (filtered by epic if specified)
    if epic_id:
        tasks = adapter.get_tasks(epic_id=epic_id)
    else:
        tasks = adapter.get_tasks()

    # Filter eligible tasks
    eligible_tasks = []
    for task in tasks:
        alfred_task = to_alfred_task(task)

        # Skip completed/cancelled tasks
        if alfred_task.status in INELIGIBLE_STATUSES:
            continue

        # Skip tasks with subtasks unless force is True
        try:
            children = adapter.get_task_children(alfred_task.id)
            if children and not force:
                continue
        except NotFoundError:
            # Task doesn't exist, skip
            continue

        eligible_tasks.append(alfred_task)

    if not eligible_tasks:
        return BatchSubtaskCreationResult(
            expanded_count=0,
            failed_count=0,
            skipped_count=len(tasks),
            message="No eligible tasks found for subtask creation",
            results=[],
        )

    # Initialize tracking
    expanded_count = 0
    failed_count = 0
    skipped_count = len(tasks) - len(eligible_tasks)
    results: List[BatchSubtaskResult] = []

    # Process each eligible task
    for task in eligible_tasks:
        # Use complexity assessment to determine subtask count if not specified
        task_num_subtasks = num_subtasks
        if not task_num_subtasks:
            # Default subtasks based on task title length as simple heuristic
            task_num_subtasks = min(
                MAX_SUBTASKS,
                max(MIN_SUBTASKS, len(task.title.split()) // TITLE_WORD_DIVISOR),
            )

        try:
            result = await create_subtasks_logic(
                api_key=api_key,
                task_id=task.id,
                num_subtasks=task_num_subtasks,
                context=context,
                force=force,
            )

            expanded_count += 1
            results.append(
                BatchSubtaskResult(
                    task_id=task.id,
                    success=True,
                    subtasks_created=len(result.subtasks_created),
                )
            )

        except (ValueError, NotFoundError, AIServiceError) as e:
            failed_count += 1
            logger.error(f"Failed to create subtasks for task {task.id}: {e}")
            results.append(
                BatchSubtaskResult(
                    task_id=task.id,
                    success=False,
                    error_code=e.__class__.__name__,
                    error_message=str(e),
                )
            )

    return BatchSubtaskCreationResult(
        expanded_count=expanded_count,
        failed_count=failed_count,
        skipped_count=skipped_count,
        message=f"Batch subtask creation complete: {expanded_count} expanded, {failed_count} failed, {skipped_count} skipped",
        results=results,
    )
