"""Business logic for updating tasks with AI-enhanced modifications."""

import logging
from datetime import datetime
from typing import Dict, Any
from alfred.adapters.linear_adapter import LinearAdapter
from alfred.models.tasks import to_alfred_task
from alfred.ai_services import AIService

logger = logging.getLogger(__name__)


async def update_task_logic(
    api_key: str,
    task_id: str,
    prompt: str,
    research: bool = False,
    append: bool = False,
) -> Dict[str, Any]:
    """
    Update a single task by ID with AI-enhanced modifications.

    Args:
        api_key: Linear API key
        task_id: ID of task to update
        prompt: Description of changes to make
        research: Whether to use research mode for enhanced updates
        append: Whether to append info instead of full update

    Returns:
        Dictionary with updated task data
    """
    adapter = LinearAdapter(api_token=api_key)

    # Get current task
    current_task = adapter.get_task(task_id)
    alfred_task = to_alfred_task(current_task)

    if append:
        # Simple append mode - just add timestamped content to description
        timestamp = datetime.now().isoformat()

        current_description = current_task.get("description")
        if not current_description:
            current_description = ""

        updated_description = (
            f"{current_description}\n\n--- Update {timestamp} ---\n{prompt}"
            if current_description
            else f"--- Update {timestamp} ---\n{prompt}"
        )

        # Update task with new description
        updated_task = adapter.update_task(
            task_id, {"description": updated_description}
        )
    else:
        # Use AI service to enhance the task
        ai_service = AIService()

        enhancement_type = "research" if research else "general"
        enhanced_task = await ai_service.enhance_task(
            task=alfred_task.model_dump(mode="json"),
            context=prompt,
            enhancement_type=enhancement_type,
        )

        # Extract updates from AI response
        update_data = {}

        if (
            enhanced_task.get("description")
            and enhanced_task["description"] != alfred_task.description
        ):
            update_data["description"] = enhanced_task["description"]

        if (
            enhanced_task.get("priority")
            and enhanced_task["priority"] != alfred_task.priority
        ):
            # Priority is a string field, just use it directly
            update_data["priority"] = enhanced_task["priority"]

        # Only update if there are actual changes
        if update_data:
            updated_task = adapter.update_task(task_id, update_data)
        else:
            updated_task = current_task

    alfred_result = to_alfred_task(updated_task)
    return alfred_result.model_dump(mode="json")
