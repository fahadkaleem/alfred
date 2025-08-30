"""Business logic for task enhancement operations."""

import logging
from typing import Dict, Any, List, Optional
from alfred.adapters import get_adapter
from alfred.models.config import Config
from alfred.models.tasks import to_alfred_task
from alfred.ai_services import AIService

logger = logging.getLogger(__name__)


async def enhance_task_scope_logic(
    config: Config,
    task_id: str,
    enhancement_prompt: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Enhance a task's scope by adding comprehensive requirements.

    Args:
        config: Alfred configuration object
        task_id: ID of task to enhance
        enhancement_prompt: Optional specific enhancement guidance

    Returns:
        Dictionary with enhanced task data
    """
    adapter = get_adapter(config)

    current_task = adapter.get_task(task_id)
    alfred_task = to_alfred_task(current_task)

    ai_service = AIService()
    enhanced_task = await ai_service.enhance_scope(
        task=alfred_task.model_dump(mode="json"),
        enhancement_prompt=enhancement_prompt or "",
    )

    update_data = {}

    additional_reqs = enhanced_task.get("additional_requirements", [])
    non_functional_reqs = enhanced_task.get("non_functional_requirements", [])
    edge_cases = enhanced_task.get("edge_cases", [])
    testing_reqs = enhanced_task.get("testing_requirements", [])

    if any([additional_reqs, non_functional_reqs, edge_cases, testing_reqs]):
        current_desc = alfred_task.description or ""
        enhanced_description = current_desc

        if additional_reqs:
            enhanced_description += "\n\n**Additional Requirements:**\n"
            enhanced_description += "\n".join(f"- {req}" for req in additional_reqs)

        if non_functional_reqs:
            enhanced_description += "\n\n**Non-Functional Requirements:**\n"
            enhanced_description += "\n".join(f"- {req}" for req in non_functional_reqs)

        if edge_cases:
            enhanced_description += "\n\n**Edge Cases to Handle:**\n"
            enhanced_description += "\n".join(f"- {case}" for case in edge_cases)

        if testing_reqs:
            enhanced_description += "\n\n**Testing Requirements:**\n"
            enhanced_description += "\n".join(f"- {req}" for req in testing_reqs)

        update_data["description"] = enhanced_description

    if enhanced_task.get("priority") == "high":
        update_data["priority"] = 1

    if update_data:
        updated_task = adapter.update_task(task_id, update_data)
    else:
        updated_task = current_task

    alfred_result = to_alfred_task(updated_task)
    return alfred_result.model_dump(mode="json")


async def simplify_task_logic(
    config: Config,
    task_id: str,
    simplification_prompt: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Simplify a task to its core requirements.

    Args:
        config: Alfred configuration object
        task_id: ID of task to simplify
        simplification_prompt: Optional specific simplification guidance

    Returns:
        Dictionary with simplified task data
    """
    adapter = get_adapter(config)

    current_task = adapter.get_task(task_id)
    alfred_task = to_alfred_task(current_task)

    ai_service = AIService()
    simplified_task = await ai_service.simplify_task(
        task=alfred_task.model_dump(mode="json"),
        simplification_prompt=simplification_prompt or "",
    )

    update_data = {}

    core_reqs = simplified_task.get("core_requirements", [])
    simplified_approach = simplified_task.get("simplified_approach", "")
    future_enhancements = simplified_task.get("future_enhancements", [])

    if any([core_reqs, simplified_approach, future_enhancements]):
        simplified_description = ""

        if core_reqs:
            simplified_description = "**Core Requirements:**\n"
            simplified_description += "\n".join(f"- {req}" for req in core_reqs)

        if simplified_approach:
            simplified_description += (
                f"\n\n**Implementation Approach:**\n{simplified_approach}"
            )

        if future_enhancements:
            simplified_description += "\n\n**Future Enhancements (Deferred):**\n"
            simplified_description += "\n".join(
                f"- {enh}" for enh in future_enhancements
            )

        update_data["description"] = simplified_description

    if simplified_task.get("priority") == "medium":
        update_data["priority"] = 2

    if update_data:
        updated_task = adapter.update_task(task_id, update_data)
    else:
        updated_task = current_task

    alfred_result = to_alfred_task(updated_task)
    return alfred_result.model_dump(mode="json")


async def bulk_enhance_tasks_logic(
    config: Config,
    task_ids: List[str],
    enhancement_prompt: str,
    enhancement_type: str = "scope",
) -> Dict[str, Any]:
    """
    Enhance multiple tasks in bulk.

    Args:
        config: Alfred configuration object
        task_ids: List of task IDs to enhance
        enhancement_prompt: Enhancement guidance to apply
        enhancement_type: Type of enhancement ("scope" or "simplify")

    Returns:
        Dictionary with bulk enhancement results
    """
    results = []
    success_count = 0
    error_count = 0

    for task_id in task_ids:
        try:
            if enhancement_type == "scope":
                result = await enhance_task_scope_logic(
                    config=config,
                    task_id=task_id,
                    enhancement_prompt=enhancement_prompt,
                )
            else:
                result = await simplify_task_logic(
                    config=config,
                    task_id=task_id,
                    simplification_prompt=enhancement_prompt,
                )

            results.append({"task_id": task_id, "status": "success", "task": result})
            success_count += 1
        except Exception as e:
            logger.error(f"Failed to enhance task {task_id}: {e}")
            results.append({"task_id": task_id, "status": "error", "error": str(e)})
            error_count += 1

    return {
        "total": len(task_ids),
        "success": success_count,
        "errors": error_count,
        "results": results,
    }
