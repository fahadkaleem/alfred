"""Business logic for creating tasks from specifications."""

import os
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

from alfred.core.tasks.models import CreateTasksFromSpecResult
from alfred.core.tasks.utilities import load_complexity_report
from alfred.core.tasks.ai_orchestration import TaskGenerationOrchestrator
from alfred.core.tasks.linear_integration import LinearTaskCreator
from alfred.ai_services.service import AIService
from alfred.config import get_config

logger = logging.getLogger(__name__)


async def create_tasks_from_spec_logic(
    spec_path: str,
    num_tasks: int,
    api_key: str,
    team_id: str,
    epic_name: Optional[str] = None,
    epic_id: Optional[str] = None,
    project_context: Optional[str] = None,
    research_mode: bool = False,
    is_claude_code: bool = False,
) -> Dict[str, Any]:
    """Create tasks from specification with AI assistance.

    This is the main business logic for parsing a specification document
    and creating tasks in Linear using AI to analyze and structure the content.

    Args:
        spec_path: Path to specification file (PRD, tech spec, etc.)
        num_tasks: Number of tasks to generate (0 = AI decides)
        api_key: Linear API key
        team_id: Linear team ID
        epic_name: Optional name for new epic if created
        epic_id: Optional existing epic ID to add tasks to
        project_context: Optional project context for AI
        research_mode: Enable research mode for enhanced analysis
        is_claude_code: Whether running in Claude Code environment

    Returns:
        Dictionary with creation results
    """
    try:
        # Read specification file
        file_result = read_spec_file(spec_path)
        if "error" in file_result:
            return {
                "success": False,
                "error": {
                    "code": file_result["error"],
                    "message": file_result["message"],
                },
            }

        spec_content = file_result["content"]

        if num_tasks < 0 or num_tasks > 50:
            return {
                "success": False,
                "error": {
                    "code": "INVALID_NUM_TASKS",
                    "message": "Number of tasks must be between 0 and 50",
                },
            }

        # Set default if 0
        if num_tasks == 0:
            # Let AI decide based on complexity
            num_tasks = 10  # Default, AI may adjust

        # Load complexity report if available
        complexity_report = load_complexity_report()

        # Initialize AI service
        ai_service = AIService()
        orchestrator = TaskGenerationOrchestrator(ai_service)

        # Initialize Linear integration
        linear_creator = LinearTaskCreator(api_key=api_key, team_id=team_id)

        # Step 1: Generate task plan with AI
        logger.info(f"Generating {num_tasks} tasks from specification")

        generation_result = await orchestrator.generate_task_plan(
            spec_content=spec_content,
            num_tasks=num_tasks,
            complexity_report=complexity_report,
            project_context=project_context,
            research_mode=research_mode,
            is_claude_code=is_claude_code,
        )

        if not generation_result.tasks:
            return {
                "success": False,
                "error": {
                    "code": "AI_GENERATION_FAILED",
                    "message": "AI failed to generate tasks from specification",
                },
            }

        logger.info(f"AI generated {len(generation_result.tasks)} tasks")

        # Step 2: Handle epic creation/resolution
        epic_created = None
        final_epic_id = epic_id

        if not epic_id and generation_result.epic:
            # AI suggests creating an epic
            epic_created = await linear_creator.ensure_epic_if_needed(
                epic=generation_result.epic, team_id=team_id
            )
            if epic_created:
                final_epic_id = epic_created.id
        elif not epic_id and epic_name:
            # User requested new epic with specific name
            from alfred.core.tasks.models import EpicSuggestion

            epic_suggestion = EpicSuggestion(
                title=epic_name,
                description=f"Epic for tasks generated from specification",
                create_epic=True,
            )
            epic_created = await linear_creator.ensure_epic_if_needed(
                epic=epic_suggestion, team_id=team_id
            )
            if epic_created:
                final_epic_id = epic_created.id

        # Step 3: Create tasks in Linear
        logger.info("Creating tasks in Linear")
        created_tasks = await linear_creator.batch_create_tasks(
            tasks=generation_result.tasks, team_id=team_id, epic_id=final_epic_id
        )

        if not created_tasks:
            return {
                "success": False,
                "error": {
                    "code": "LINEAR_CREATION_FAILED",
                    "message": "Failed to create tasks in Linear",
                },
            }

        logger.info(f"Created {len(created_tasks)} tasks in Linear")

        # Step 4: Create dependencies
        dependencies_created = []
        try:
            dependencies_created = await linear_creator.create_task_dependencies(
                tasks=generation_result.tasks, created_tasks=created_tasks
            )
            logger.info(f"Created {len(dependencies_created)} task dependencies")
        except Exception as e:
            logger.warning(f"Failed to create some dependencies: {e}")

        # Build response
        logger.info(f"Building response with {len(created_tasks)} tasks")
        for task in created_tasks:
            logger.info(f"Task in response: ID={task.id}, Title={task.title}")

        result = CreateTasksFromSpecResult(
            success=True,
            epic=epic_created,
            tasks=created_tasks,
            summary={
                "requested": num_tasks,
                "created": len(created_tasks),
                "skipped": len(generation_result.tasks) - len(created_tasks),
                "team_id": team_id,
                "epic_created": epic_created is not None,
                "dependencies_created": len(dependencies_created),
                "platform": "linear",
            },
            errors=[],
        )

        response_dict = result.model_dump()
        logger.info(f"Final response tasks: {response_dict.get('tasks', [])}")
        return response_dict

    except Exception as e:
        logger.error(f"Failed to create tasks from spec: {e}")
        return {
            "success": False,
            "error": {"code": "UNEXPECTED_ERROR", "message": str(e)},
        }


def read_spec_file(spec_path: str) -> Dict[str, Any]:
    """Read specification file content.

    Args:
        spec_path: Path to specification file

    Returns:
        Dict with either 'content' or 'error' key
    """
    try:
        path = Path(spec_path)

        if not path.exists():
            logger.error(f"Specification file not found: {spec_path}")
            return {
                "error": "FILE_NOT_FOUND",
                "message": f"Specification file does not exist: {spec_path}",
            }

        if not path.is_file():
            logger.error(f"Specification path is not a file: {spec_path}")
            return {
                "error": "NOT_A_FILE",
                "message": f"Path is not a file: {spec_path}",
            }

        # Check file extension
        valid_extensions = [".txt", ".md", ".markdown"]
        if path.suffix.lower() not in valid_extensions:
            logger.error(f"Unsupported file extension: {path.suffix}")
            return {
                "error": "UNSUPPORTED_FORMAT",
                "message": f"File format not supported: {path.suffix}. Supported formats: .txt, .md, .markdown",
            }

        # Read file
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        if not content.strip():
            logger.error("Specification file is empty")
            return {"error": "EMPTY_FILE", "message": "Specification file is empty"}

        return {"content": content}

    except PermissionError as e:
        logger.error(f"Permission denied reading file: {e}")
        return {
            "error": "READ_ERROR",
            "message": f"Permission denied: Cannot read file {spec_path}",
        }
    except Exception as e:
        logger.error(f"Failed to read specification file: {e}")
        return {"error": "READ_ERROR", "message": f"Failed to read file: {str(e)}"}
