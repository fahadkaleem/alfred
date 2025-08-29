"""AI orchestration for task generation from specifications."""

import asyncio
import logging
from typing import List, Optional, Dict, Any

from alfred.core.tasks.models import GenerationResult, TaskSuggestion
from alfred.core.tasks.utilities import (
    chunk_markdown,
    parse_ai_response,
    merge_task_candidates,
    safe_extract_json,
)
from alfred.ai_services.exceptions import RateLimitError, AIServiceError

logger = logging.getLogger(__name__)


class TaskGenerationOrchestrator:
    """Orchestrates AI-powered task generation from specifications."""

    def __init__(self, ai_service):
        """Initialize orchestrator.

        Args:
            ai_service: AI service instance for making API calls
        """
        self.ai_service = ai_service

    async def generate_task_plan(
        self,
        spec_content: str,
        num_tasks: int,
        project_context: Optional[str] = None,
        research_mode: bool = False,
        is_claude_code: bool = False,
    ) -> GenerationResult:
        """Generate task plan from specification.

        Args:
            spec_content: Specification content
            num_tasks: Number of tasks to generate
            project_context: Optional project context
            research_mode: Enable research mode for enhanced analysis
            is_claude_code: Whether running in Claude Code environment

        Returns:
            GenerationResult with tasks and optional epic
        """
        # Check if we need to chunk
        chunks = chunk_markdown(spec_content, target_tokens=3000, overlap_tokens=200)

        if len(chunks) == 1:
            # Single chunk - direct generation
            return await self._generate_from_single_chunk(
                chunks[0], num_tasks, project_context, research_mode, is_claude_code
            )
        else:
            # Multiple chunks - need synthesis
            return await self._generate_from_multiple_chunks(
                chunks,
                num_tasks,
                project_context,
                research_mode,
                is_claude_code,
            )

    async def _generate_from_single_chunk(
        self,
        content: str,
        num_tasks: int,
        project_context: Optional[str] = None,
        research_mode: bool = False,
        is_claude_code: bool = False,
    ) -> GenerationResult:
        """Generate tasks from a single chunk.

        Args:
            content: Specification content
            num_tasks: Number of tasks to generate
            project_context: Optional project context

        Returns:
            GenerationResult
        """
        try:
            logger.info(f"Calling AI service to generate {num_tasks} tasks")

            # Use the AI service's existing method with new parameters
            response = await self.ai_service.create_tasks_from_spec(
                spec_content=content,
                num_tasks=num_tasks,
                project_context=project_context,
                research_mode=research_mode,
                is_claude_code=is_claude_code,
                stream=False,
            )

            # Parse response
            if isinstance(response, list):
                # Direct task list
                logger.info(f"Got {len(response)} tasks from AI")
                tasks = [self._normalize_task(task) for task in response]
                return GenerationResult(tasks=tasks)
            elif isinstance(response, dict):
                return parse_ai_response(response)
            else:
                return parse_ai_response(str(response))

        except Exception as e:
            logger.warning(f"Initial parsing failed: {e}")
            return await self._fix_and_retry(
                content, num_tasks, project_context, str(e)
            )

    async def _generate_from_multiple_chunks(
        self,
        chunks: List[str],
        num_tasks: int,
        project_context: Optional[str] = None,
        research_mode: bool = False,
        is_claude_code: bool = False,
    ) -> GenerationResult:
        """Generate tasks from multiple chunks with synthesis.

        Args:
            chunks: List of content chunks
            num_tasks: Number of tasks to generate
            project_context: Optional project context

        Returns:
            GenerationResult
        """
        # Generate candidates from each chunk
        all_candidates = []
        epic_suggestion = None

        for i, chunk in enumerate(chunks):
            logger.info(f"Processing chunk {i + 1}/{len(chunks)}")

            # Adjust task count per chunk
            tasks_per_chunk = max(num_tasks // len(chunks) + 2, 3)

            try:
                result = await self._generate_from_single_chunk(
                    chunk, tasks_per_chunk, project_context
                )

                all_candidates.extend(result.tasks)

                # Keep epic suggestion from first chunk that suggests one
                if result.epic and not epic_suggestion:
                    epic_suggestion = result.epic

            except Exception as e:
                logger.warning(f"Failed to process chunk {i + 1}: {e}")
                continue

        # If we have too many chunks, run synthesis
        if len(chunks) > 3:
            synthesized = await self._synthesize_candidates(
                all_candidates, num_tasks, project_context
            )
            return GenerationResult(epic=epic_suggestion, tasks=synthesized)
        else:
            # Simple merge for small number of chunks
            merged = merge_task_candidates(all_candidates, num_tasks)
            return GenerationResult(epic=epic_suggestion, tasks=merged)

    async def _synthesize_candidates(
        self,
        candidates: List[TaskSuggestion],
        num_tasks: int,
        project_context: Optional[str] = None,
    ) -> List[TaskSuggestion]:
        """Synthesize task candidates into final list.

        Args:
            candidates: All task candidates
            num_tasks: Target number of tasks
            project_context: Optional project context

        Returns:
            Final list of tasks
        """
        # Prepare synthesis prompt
        candidates_json = [
            {
                "title": task.title,
                "description": task.description,
                "priority": task.priority,
                "dependencies": task.dependencies,
            }
            for task in candidates
        ]

        synthesis_prompt = f"""
You have {len(candidates)} task candidates generated from a specification.
Consolidate these into exactly {num_tasks} high-quality tasks.

Requirements:
1. Remove duplicates (tasks with very similar titles/purposes)
2. Prioritize tasks that appear multiple times (indicates importance)
3. Maintain logical dependency order
4. Keep the most detailed versions of duplicate tasks
5. Ensure comprehensive coverage of the specification

Candidates:
{candidates_json}

{f"Project Context: {project_context}" if project_context else ""}

Return exactly {num_tasks} tasks as a JSON array with the same structure.
"""

        try:
            messages = [
                {"role": "system", "content": "You are a task consolidation expert."},
                {"role": "user", "content": synthesis_prompt},
            ]

            response = await self.ai_service.provider.complete_json(
                messages=messages, temperature=0.3
            )

            # Parse synthesized tasks
            synthesized = []
            task_list = (
                response if isinstance(response, list) else response.get("tasks", [])
            )

            for task_data in task_list:
                synthesized.append(self._normalize_task(task_data))

            return synthesized[:num_tasks]

        except Exception as e:
            logger.warning(f"Synthesis failed, using simple merge: {e}")
            return merge_task_candidates(candidates, num_tasks)

    async def _fix_and_retry(
        self, content: str, num_tasks: int, project_context: Optional[str], error: str
    ) -> GenerationResult:
        """Fix parsing error and retry generation.

        Args:
            content: Original content
            num_tasks: Number of tasks
            project_context: Optional context
            error: Error message

        Returns:
            GenerationResult
        """
        fix_prompt = f"""
Your previous response had an error: {error}

Please regenerate {num_tasks} tasks from this specification in valid JSON format.
Each task must have: title, description, priority (P0-P3), dependencies (array), 
acceptance_criteria (array).

Specification:
{content[:4000]}

Return ONLY valid JSON array of tasks.
"""

        messages = [
            {
                "role": "system",
                "content": "Fix the JSON formatting and return valid task array.",
            },
            {"role": "user", "content": fix_prompt},
        ]

        try:
            response = await self.ai_service.provider.complete_json(
                messages=messages, temperature=0.3
            )

            return parse_ai_response(response)
        except Exception as e:
            # Final fallback - return minimal tasks
            logger.error(f"Failed to fix and retry: {e}")

            return GenerationResult(
                tasks=[
                    TaskSuggestion(
                        title=f"Task {i + 1}",
                        description="Generated task - please review specification for details",
                        priority="P2",
                    )
                    for i in range(min(num_tasks, 3))
                ]
            )

    def _normalize_task(self, task_data: dict) -> TaskSuggestion:
        """Normalize task data into TaskSuggestion.

        Args:
            task_data: Raw task data

        Returns:
            TaskSuggestion
        """
        # Map priority if needed
        priority = task_data.get("priority", "P2")
        if priority in ["critical", "high", "medium", "low"]:
            priority_map = {"critical": "P0", "high": "P1", "medium": "P2", "low": "P3"}
            priority = priority_map.get(priority, "P2")

        return TaskSuggestion(
            title=task_data.get("title", "Untitled Task"),
            description=task_data.get("description", ""),
            priority=priority,
            labels=task_data.get("labels", []),
            dependencies=task_data.get("dependencies", []),
            estimate=task_data.get("estimate") or task_data.get("estimated_hours"),
            acceptance_criteria=task_data.get("acceptance_criteria", []),
            technical_notes=task_data.get("technical_notes")
            or task_data.get("technical_details"),
        )
