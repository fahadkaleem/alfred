"""Save context business logic."""

import json
from typing import Any, Dict, Optional
from alfred.core.workflow.engine import WorkflowEngine
from alfred.models.workflow import ToolResponse


async def save_context_logic(
    task_id: str,
    phase: str,
    content: str,
    status: str = "IN_PROGRESS",
    metadata: Dict[str, Any] | str | None = None,
) -> ToolResponse:
    """Save important context for future reference with optional metadata tracking.

    Args:
        task_id: The task/ticket ID (e.g., "AL-123", "PROJ-456")
        phase: The workflow phase name
        content: Detailed notes as a single string
        status: Phase completion status (default: "IN_PROGRESS")
        metadata: Optional structured tracking data

    Returns:
        ToolResponse with context save confirmation
    """
    if not isinstance(content, str):
        return ToolResponse.error(
            "Content must be a string",
            next_prompt="Pass your detailed notes as a string. Example: save_context('AL-123', 'plan', 'Analyzed requirements and decided to use React')",
        )

    if not content.strip():
        return ToolResponse.error(
            "Content cannot be empty",
            next_prompt="Include detailed notes about what you did and decisions made. This is your only memory for this phase!",
        )

    parsed_metadata = metadata
    if isinstance(metadata, str):
        try:
            parsed_metadata = json.loads(metadata)
        except (json.JSONDecodeError, TypeError) as e:
            return ToolResponse.error(
                f"Invalid metadata JSON: {e}",
                next_prompt='Metadata must be a valid JSON object. Example: {"step_completed": "analyze_codebase"}',
            )

    # Initialize workflow engine and save context
    workflow_engine = WorkflowEngine()
    response = workflow_engine.save_context(
        task_id=task_id,
        phase=phase,
        content=content,
        status=status,
        metadata=parsed_metadata,
    )

    return ToolResponse.success(
        message=f"Context saved for phase '{phase}'", data=response.model_dump()
    )
