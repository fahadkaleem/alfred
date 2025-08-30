"""Business logic for updating subtasks with timestamped information."""

import logging
from datetime import datetime
from typing import Dict, Any
from alfred.adapters import get_adapter
from alfred.models.config import Config
from alfred.models.tasks import to_alfred_task
from alfred.ai_services import AIService

logger = logging.getLogger(__name__)


async def update_subtask_logic(
    config: Config,
    subtask_id: str,
    prompt: str,
    research: bool = False,
) -> Dict[str, Any]:
    """
    Append timestamped information to a subtask without replacing existing content.

    Args:
        config: Alfred configuration object
        subtask_id: ID of subtask to update (must be a Linear sub-issue ID)
        prompt: Information to add to the subtask
        research: Whether to use research mode for enhanced updates

    Returns:
        Dictionary with updated subtask data
    """
    adapter = get_adapter(config)

    # Get current subtask (subtasks are just Linear issues with parentId)
    current_subtask = adapter.get_task(subtask_id)
    alfred_subtask = to_alfred_task(current_subtask)

    # For simple append mode, we'll use AI to enhance the content contextually
    ai_service = AIService()

    enhancement_type = "research" if research else "subtask_update"
    enhanced_content = await ai_service.enhance_task(
        task=alfred_subtask.model_dump(mode="json"),
        context=f"Add this information: {prompt}",
        enhancement_type=enhancement_type,
    )

    # Extract the content to append from AI response
    if isinstance(enhanced_content, dict) and enhanced_content.get("details"):
        append_content = enhanced_content["details"]
    else:
        # Fallback to using the prompt directly
        append_content = prompt

    # Create timestamped update
    timestamp = datetime.now().isoformat()

    current_description = current_subtask.get("description")
    if not current_description:
        current_description = ""

    # Add timestamped content
    formatted_update = f"\n\n--- Update {timestamp} ---\n{append_content}"
    updated_description = current_description + formatted_update

    # Update subtask with new description
    updated_subtask = adapter.update_task(
        subtask_id, {"description": updated_description}
    )

    alfred_result = to_alfred_task(updated_subtask)
    return alfred_result.model_dump(mode="json")
