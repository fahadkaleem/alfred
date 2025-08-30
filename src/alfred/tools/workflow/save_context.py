"""MCP tool wrapper for save_context."""

import json
from typing import Dict, Any

from alfred.core.workflow.engine import WorkflowEngine

# Create workflow engine instance
workflow_engine = WorkflowEngine()


def register(server) -> int:
    """Register the save_context tool."""

    @server.tool
    async def save_context(
        task_id: str,
        phase: str,
        content: str,
        status: str = "IN_PROGRESS",
        metadata: dict[str, Any] | str | None = None,
    ) -> dict:
        """Save important context for future reference with optional metadata tracking.

        - Persists work context and decisions for continuity across chat sessions
        - Supports rich metadata tracking for workflow coordination
        - Content must be a comprehensive string - this is your only memory
        - Status controls workflow phase transitions
        - Local-first storage with JSON state persistence

        Parameters
        ----------
        task_id [string] (required) - The task/ticket ID (e.g., "AL-123", "PROJ-456")
        phase [string] (required) - The workflow phase name (varies by workflow):
            - Example phases: "planning", "implement", "test", "review", "claim"
            - "planning" - Requirements gathering and design
            - "implement" - Code development and implementation
            - "test" - Testing and validation
            - "review" - Code review and feedback
            - "claim" - Task assignment and setup
            - Custom phases based on assigned workflow type
        content [string] (required) - YOUR DETAILED NOTES AS A SINGLE STRING:
            - What you accomplished in detail
            - Key decisions and WHY you made them
            - Important constraints mentioned by user
            - Exact next steps and dependencies
            - Any deadlines, names, or critical context
        status [string] - Phase completion status (default: "IN_PROGRESS"):
            - "IN_PROGRESS" - Work continuing, saves intermediate state
            - "COMPLETE" - Phase finished, triggers workflow transition
        metadata [object|string|null] - Optional structured tracking data:
            - step_completed: Which specific step was finished
            - artifacts_created: List of files, tasks, or deliverables created
            - key_decisions: Important architectural or implementation choices
            - Any other phase-specific tracking information

        Usage notes:
        - Content cannot be empty - include detailed notes about your work
        - Metadata can be passed as JSON string or object for MCP compatibility
        - Status="COMPLETE" automatically advances workflow to next phase
        - Context is organized by task_id and phase for easy retrieval
        - Use frequently to maintain state across long-running tasks

        Examples
        --------
            save_context("AL-123", "planning", "Analyzed codebase and identified key components. Decided to use React hooks pattern for state management.")
            save_context(
                "AL-123",
                "planning",
                "Completed task setup and created initial structure",
                "COMPLETE",
                metadata={
                    "step_completed": "create_task",
                    "artifacts_created": [
                        {"type": "task", "id": "PROJ-100", "title": "Mobile App"},
                        {"type": "task", "id": "PROJ-101", "title": "[PRD] Mobile App"}
                    ]
                }
            )
            save_context("AL-123", "implement", "Implemented authentication flow using JWT tokens. Chose bcrypt for password hashing due to security requirements.")

        Error conditions:
        - Content must be non-empty string
        - Invalid JSON in metadata string parameter
        - Task storage initialization failures

        """
        if not isinstance(content, str):
            raise ValueError("Content must be a string")

        if not content.strip():
            raise ValueError("Content cannot be empty")

        parsed_metadata = metadata
        if isinstance(metadata, str):
            try:
                parsed_metadata = json.loads(metadata)
            except (json.JSONDecodeError, TypeError) as e:
                raise ValueError(f"Invalid metadata JSON: {e}")

        response = workflow_engine.save_context(
            task_id=task_id,
            phase=phase,
            content=content,
            status=status,
            metadata=parsed_metadata,
        )
        return {
            "message": f"Context saved for phase '{phase}'",
            "data": response.model_dump(),
        }

    return 1  # Number of tools registered
