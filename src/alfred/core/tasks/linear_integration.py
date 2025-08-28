"""Linear integration for task creation from specifications."""

import asyncio
import logging
from typing import List, Optional, Dict, Any

from alfred.adapters.linear_adapter import LinearAdapter
from alfred.core.tasks.models import (
    TaskSuggestion,
    EpicSuggestion,
    LinearTaskCreated,
    LinearEpicCreated,
)
from alfred.core.tasks.utilities import map_priority_to_linear

logger = logging.getLogger(__name__)


class LinearTaskCreator:
    """Handles task and epic creation in Linear."""

    def __init__(self, api_key: str, team_id: Optional[str] = None):
        """Initialize Linear task creator.

        Args:
            api_key: Linear API key
            team_id: Optional team ID
        """
        self.adapter = LinearAdapter(api_token=api_key)
        self.team_id = team_id

    async def ensure_epic_if_needed(
        self, epic: Optional[EpicSuggestion], team_id: Optional[str] = None
    ) -> Optional[LinearEpicCreated]:
        """Create or find epic if needed.

        Args:
            epic: Epic suggestion from AI
            team_id: Team ID for epic creation

        Returns:
            Created/found epic or None
        """
        if not epic or not epic.create_epic:
            return None

        # Search for existing epic by title
        try:
            existing_epics = self.adapter.get_epics()
            for existing in existing_epics:
                if existing.get("name", "").lower() == epic.title.lower():
                    logger.info(f"Found existing epic: {existing['name']}")
                    return LinearEpicCreated(
                        id=existing["id"],
                        title=existing["name"],
                        url=existing.get("url"),
                    )
        except Exception as e:
            logger.warning(f"Failed to search for existing epic: {e}")

        # Create new epic
        try:
            created = self.adapter.create_epic(
                name=epic.title, description=epic.description
            )
            logger.info(f"Created new epic: {epic.title}")
            return LinearEpicCreated(
                id=created["id"], title=created["name"], url=created.get("url")
            )
        except Exception as e:
            logger.error(f"Failed to create epic: {e}")
            return None

    def task_to_linear_input(
        self, task: TaskSuggestion, team_id: str, epic_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Convert TaskSuggestion to Linear issue input.

        Args:
            task: Task suggestion
            team_id: Team ID
            epic_id: Optional epic/project ID

        Returns:
            Linear issue input dict
        """
        # Build description with acceptance criteria and notes
        description_parts = [task.description]

        if task.acceptance_criteria:
            description_parts.append("\n\n**Acceptance Criteria:**")
            for criterion in task.acceptance_criteria:
                description_parts.append(f"- {criterion}")

        if task.technical_notes:
            description_parts.append(
                f"\n\n**Technical Notes:**\n{task.technical_notes}"
            )

        if task.estimate:
            description_parts.append(f"\n\n**Estimated Hours:** {task.estimate}")

        full_description = "\n".join(description_parts)

        return {
            "title": task.title,
            "description": full_description,
            "priority": map_priority_to_linear(task.priority),
            "epic_id": epic_id,
            "labels": task.labels,
        }

    async def _create_single_task(
        self, task_input: Dict[str, Any], retry_count: int = 3
    ) -> LinearTaskCreated:
        """Create a single task with retry logic.

        Args:
            task_input: Task input dict
            retry_count: Number of retries

        Returns:
            Created task info
        """
        for attempt in range(retry_count):
            try:
                created = self.adapter.create_task(
                    title=task_input["title"],
                    description=task_input.get("description"),
                    epic_id=task_input.get("epic_id"),
                )

                result = LinearTaskCreated(
                    id=created["id"],
                    title=created["title"],
                    url=created.get("url"),
                    priority=task_input.get("priority"),
                )
                logger.debug(f"Created task - ID: {result.id}, Title: {result.title}")
                return result
            except Exception as e:
                if attempt == retry_count - 1:
                    raise
                await asyncio.sleep(2**attempt)  # Exponential backoff

    async def batch_create_tasks(
        self,
        tasks: List[TaskSuggestion],
        team_id: str,
        epic_id: Optional[str] = None,
        batch_size: int = 10,
    ) -> List[LinearTaskCreated]:
        """Batch create tasks in Linear.

        Args:
            tasks: List of task suggestions
            team_id: Team ID
            epic_id: Optional epic/project ID
            batch_size: Number of tasks to create concurrently

        Returns:
            List of created tasks
        """
        created_tasks = []
        errors = []

        # Convert tasks to Linear inputs
        task_inputs = [
            self.task_to_linear_input(task, team_id, epic_id) for task in tasks
        ]

        # Create semaphore for rate limiting
        semaphore = asyncio.Semaphore(batch_size)

        async def create_with_semaphore(task_input: Dict[str, Any], index: int):
            """Create task with semaphore control."""
            async with semaphore:
                try:
                    created = await self._create_single_task(task_input)
                    return (index, created, None)
                except Exception as e:
                    logger.error(f"Failed to create task '{task_input['title']}': {e}")
                    return (index, None, str(e))

        # Create all tasks concurrently with semaphore
        results = await asyncio.gather(
            *[
                create_with_semaphore(input_data, i)
                for i, input_data in enumerate(task_inputs)
            ],
            return_exceptions=False,
        )

        # Process results in order
        for index, created, error in sorted(results, key=lambda x: x[0]):
            if created:
                created_tasks.append(created)
            else:
                # Try to create a minimal task on failure
                try:
                    minimal_input = {
                        "title": task_inputs[index]["title"],
                        "description": f"Failed to create with full details. Error: {error}",
                    }
                    created = await self._create_single_task(minimal_input)
                    created_tasks.append(created)
                except Exception as e:
                    logger.error(f"Failed to create minimal task: {e}")
                    errors.append(
                        {"task": task_inputs[index]["title"], "error": str(e)}
                    )

        if errors:
            logger.warning(f"Failed to create {len(errors)} tasks")

        return created_tasks

    async def create_task_dependencies(
        self, tasks: List[TaskSuggestion], created_tasks: List[LinearTaskCreated]
    ) -> List[Dict[str, str]]:
        """Create dependency relationships between tasks.

        Args:
            tasks: Original task suggestions with dependency info
            created_tasks: Created tasks in Linear

        Returns:
            List of created dependencies
        """
        dependencies_created = []

        # Build title to ID mapping
        title_to_id = {created.title.lower(): created.id for created in created_tasks}

        # Also support references by index (e.g., "Task 1", "#1")
        for i, created in enumerate(created_tasks):
            title_to_id[f"task {i + 1}"] = created.id
            title_to_id[f"#{i + 1}"] = created.id
            title_to_id[f"t{i + 1}"] = created.id

        # Create dependencies
        for task, created_task in zip(tasks, created_tasks):
            if not task.dependencies:
                continue

            for dep_ref in task.dependencies:
                dep_id = None

                # Try to find dependency by normalized title
                dep_ref_lower = dep_ref.lower()
                if dep_ref_lower in title_to_id:
                    dep_id = title_to_id[dep_ref_lower]
                else:
                    # Try partial matching
                    for title, task_id in title_to_id.items():
                        if dep_ref_lower in title or title in dep_ref_lower:
                            dep_id = task_id
                            break

                if dep_id and dep_id != created_task.id:
                    try:
                        # Create blocking relationship in Linear
                        # created_task depends on dep_id, so dep_id blocks created_task
                        success = self.adapter.link_tasks(
                            task_id=created_task.id, depends_on_id=dep_id
                        )
                        if success:
                            logger.info(
                                f"Created dependency: {created_task.title} depends on {dep_id}"
                            )
                            dependencies_created.append(
                                {
                                    "from": created_task.id,
                                    "to": dep_id,
                                    "type": "blocks",
                                }
                            )
                        else:
                            logger.warning(
                                f"Failed to create dependency between {created_task.id} and {dep_id}"
                            )
                    except Exception as e:
                        logger.warning(f"Failed to create dependency: {e}")
                else:
                    logger.warning(
                        f"Could not resolve dependency '{dep_ref}' for task '{task.title}'"
                    )

        return dependencies_created
