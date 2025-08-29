"""Business logic for bulk updating multiple tasks with AI-enhanced modifications."""

import logging
from typing import Dict, Any, List
from alfred.adapters.linear_adapter import LinearAdapter
from alfred.models.tasks import to_alfred_task
from alfred.ai_services import AIService

logger = logging.getLogger(__name__)


async def bulk_update_tasks_logic(
    api_key: str,
    task_ids: List[str],
    prompt: str,
    research: bool = False,
) -> Dict[str, Any]:
    """
    Update multiple tasks with AI-generated updates based on context.

    Args:
        api_key: Linear API key
        task_ids: List of task IDs to update
        prompt: Description of changes to apply to all tasks
        research: Whether to use research mode for enhanced updates

    Returns:
        Dictionary with update summary and results
    """
    adapter = LinearAdapter(api_token=api_key)

    # Get current tasks
    tasks = []
    for task_id in task_ids:
        try:
            task = adapter.get_task(task_id)
            alfred_task = to_alfred_task(task)
            tasks.append(alfred_task.model_dump(mode="json"))
        except Exception as e:
            # Skip tasks that can't be found
            logger.warning(f"Could not fetch task {task_id}: {e}")
            continue

    if not tasks:
        return {"error": "No valid tasks found to update", "updated_count": 0}

    # Use AI service to enhance all tasks
    ai_service = AIService()

    # For bulk updates, we'll process each task individually to avoid context limits
    updated_tasks = []
    update_results = []

    for task_data in tasks:
        try:
            enhancement_type = "research" if research else "general"
            enhanced_task = await ai_service.enhance_task(
                task=task_data, context=prompt, enhancement_type=enhancement_type
            )

            # Extract updates from AI response
            update_data = {}

            if enhanced_task.get("description") and enhanced_task[
                "description"
            ] != task_data.get("description"):
                update_data["description"] = enhanced_task["description"]

            if enhanced_task.get("priority") and enhanced_task[
                "priority"
            ] != task_data.get("priority"):
                # Priority is a string field, just use it directly
                update_data["priority"] = enhanced_task["priority"]

            # Only update if there are actual changes
            if update_data:
                updated_task = adapter.update_task(task_data["id"], update_data)
                updated_alfred = to_alfred_task(updated_task)
                updated_tasks.append(updated_alfred.model_dump(mode="json"))
                update_results.append(
                    {
                        "task_id": task_data["id"],
                        "updated": True,
                        "changes": list(update_data.keys()),
                    }
                )
            else:
                updated_tasks.append(task_data)
                update_results.append(
                    {"task_id": task_data["id"], "updated": False, "changes": []}
                )

        except Exception as e:
            logger.warning(f"Could not update task {task_data['id']}: {e}")
            updated_tasks.append(task_data)
            update_results.append(
                {"task_id": task_data["id"], "updated": False, "error": str(e)}
            )

    updated_count = sum(1 for result in update_results if result.get("updated", False))

    return {
        "updated_count": updated_count,
        "total_processed": len(updated_tasks),
        "results": update_results,
        "tasks": updated_tasks,
    }
