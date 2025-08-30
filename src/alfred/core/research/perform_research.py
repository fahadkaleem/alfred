"""Core research business logic."""

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

from .models import (
    ResearchContext,
    ResearchRequest,
    ResearchResponse,
    FuzzySearchResult,
)
from alfred.ai_services.service import AIService
from alfred.ai_services.base import AIProvider
from alfred.config import get_config


class ContextGatherer:
    """Gathers context for research queries."""

    @staticmethod
    def gather_task_context(
        task_ids: List[str], project_root: str
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Gather context from Task Master tasks."""
        # TODO: BROKEN - Replace Task Master imports with Alfred's Linear integration
        # Should use: from alfred.core.tasks.get import get_task_logic
        # Linear task IDs are like "AUTH-123", not "1.2" format
        try:
            from alfred_task_manager.mcp import mcp__taskmaster_ai__get_task

            tasks = []
            total_tokens = 0

            for task_id in task_ids:
                try:
                    # TODO: BROKEN - Should call get_task_logic(api_key=config.linear_api_key, task_id=task_id)
                    result = mcp__taskmaster_ai__get_task(
                        id=task_id, projectRoot=project_root
                    )
                    if result.get("data", {}).get("task"):
                        task_data = result["data"]["task"]
                        tasks.append(task_data)

                        task_text = f"{task_data.get('title', '')} {task_data.get('description', '')} {task_data.get('details', '')}"
                        total_tokens += len(task_text) // 4
                except Exception:
                    continue

            return tasks, total_tokens

        except ImportError:
            return [], 0

    @staticmethod
    def gather_file_context(
        file_paths: List[str], project_root: str
    ) -> Tuple[List[Dict[str, str]], int]:
        """Gather context from files."""
        files = []
        total_tokens = 0

        for file_path in file_paths:
            try:
                if not os.path.isabs(file_path):
                    full_path = os.path.join(project_root, file_path)
                else:
                    full_path = file_path

                if os.path.exists(full_path) and os.path.isfile(full_path):
                    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()

                    files.append(
                        {
                            "path": file_path,
                            "content": content[:10000],  # Limit file content
                        }
                    )

                    total_tokens += len(content) // 4

            except Exception:
                continue

        return files, total_tokens

    @staticmethod
    def gather_project_tree(project_root: str, max_depth: int = 3) -> Tuple[str, int]:
        """Gather project tree structure."""
        try:
            tree_lines = []

            def add_tree_entry(path: Path, prefix: str = "", depth: int = 0):
                if depth > max_depth:
                    return

                if path.name.startswith(".") and path.name not in [".env.example"]:
                    return

                if path.name in [
                    "__pycache__",
                    "node_modules",
                    ".git",
                    ".venv",
                    "venv",
                ]:
                    return

                if path.is_file():
                    tree_lines.append(f"{prefix}├── {path.name}")
                elif path.is_dir():
                    tree_lines.append(f"{prefix}├── {path.name}/")

                    try:
                        children = sorted(
                            path.iterdir(), key=lambda x: (x.is_file(), x.name)
                        )
                        for child in children[:20]:  # Limit entries
                            add_tree_entry(child, prefix + "│   ", depth + 1)
                    except PermissionError:
                        pass

            root_path = Path(project_root)
            tree_lines.append(f"{root_path.name}/")

            try:
                children = sorted(
                    root_path.iterdir(), key=lambda x: (x.is_file(), x.name)
                )
                for child in children[:30]:
                    add_tree_entry(child, "")
            except PermissionError:
                pass

            tree_content = "\n".join(tree_lines)
            tokens = len(tree_content) // 4

            return tree_content, tokens

        except Exception:
            return "", 0

    @classmethod
    def gather_context(
        cls, request: ResearchRequest, project_root: str
    ) -> ResearchContext:
        """Gather all context for a research request."""
        context = ResearchContext()
        token_breakdown = {}

        # Parse task IDs
        if request.task_ids:
            task_ids = [
                tid.strip() for tid in request.task_ids.split(",") if tid.strip()
            ]
            if task_ids:
                tasks, task_tokens = cls.gather_task_context(task_ids, project_root)
                context.tasks = tasks
                token_breakdown["tasks"] = task_tokens

        # Parse file paths
        if request.file_paths:
            file_paths = [
                fp.strip() for fp in request.file_paths.split(",") if fp.strip()
            ]
            if file_paths:
                files, file_tokens = cls.gather_file_context(file_paths, project_root)
                context.files = files
                token_breakdown["files"] = file_tokens

        # Custom context
        if request.custom_context:
            context.custom_context = request.custom_context
            token_breakdown["custom_context"] = len(request.custom_context) // 4

        # Project tree
        if request.include_project_tree:
            tree, tree_tokens = cls.gather_project_tree(project_root)
            context.project_tree = tree
            token_breakdown["project_tree"] = tree_tokens

        # Calculate total
        token_breakdown["total"] = sum(token_breakdown.values())
        context.token_breakdown = token_breakdown

        return context


class FuzzyTaskSearch:
    """Fuzzy search for relevant tasks."""

    @staticmethod
    def find_relevant_tasks(
        query: str, project_root: str, max_results: int = 8
    ) -> List[FuzzySearchResult]:
        """Find tasks relevant to the query using fuzzy search."""
        # TODO: BROKEN - Replace Task Master imports with Alfred's Linear integration
        # Should use: from alfred.core.tasks.list import get_tasks_logic
        # Then call get_tasks_logic(api_key=config.linear_api_key)
        try:
            from alfred_task_manager.mcp import mcp__taskmaster_ai__get_tasks

            # Get all tasks
            # TODO: BROKEN - Should call get_tasks_logic() instead
            result = mcp__taskmaster_ai__get_tasks(projectRoot=project_root)
            if not result.get("data", {}).get("tasks"):
                return []

            tasks = result["data"]["tasks"]
            query_lower = query.lower()
            scored_tasks = []

            for task in tasks:
                score = 0.0
                task_id = task.get("id")
                title = task.get("title", "").lower()
                description = task.get("description", "").lower()
                details = task.get("details", "").lower()

                # Title matches get highest score
                if query_lower in title:
                    score += 3.0

                # Description matches get medium score
                if query_lower in description:
                    score += 2.0

                # Details matches get low score
                if query_lower in details:
                    score += 1.0

                # Word-level matching
                query_words = query_lower.split()
                all_text = f"{title} {description} {details}"

                for word in query_words:
                    if len(word) > 2:  # Skip very short words
                        if word in all_text:
                            score += 0.5

                if score > 0:
                    scored_tasks.append(
                        FuzzySearchResult(
                            task_id=task_id, relevance_score=score, match_type="fuzzy"
                        )
                    )

            # Sort by score and return top results
            scored_tasks.sort(key=lambda x: x.relevance_score, reverse=True)
            return scored_tasks[:max_results]

        except ImportError:
            return []
        except Exception:
            return []


class ResearchSaver:
    """Saves research results to tasks or files."""

    @staticmethod
    def save_to_task(task_id: str, research_result: str, project_root: str) -> bool:
        """Save research result to a task as an update."""
        # TODO: BROKEN - Replace Task Master imports with Alfred's Linear integration
        # Should use: from alfred.core.tasks.update import update_task_logic
        # Linear doesn't have subtask concept with "." format - all are regular tasks
        try:
            from alfred_task_manager.mcp import mcp__taskmaster_ai__update_subtask

            # Check if it's a subtask ID
            # TODO: BROKEN - Linear uses task IDs like "AUTH-123", not "1.2" format
            if "." in task_id:
                # TODO: BROKEN - Should call update_task_logic() for Linear tasks
                result = mcp__taskmaster_ai__update_subtask(
                    id=task_id,
                    prompt=f"Research findings: {research_result}",
                    projectRoot=project_root,
                )
            else:
                # Use update_task for main tasks
                # TODO: BROKEN - Replace with Alfred's Linear integration
                from alfred_task_manager.mcp import mcp__taskmaster_ai__update_task

                # TODO: BROKEN - Should call update_task_logic(api_key, task_id, prompt, append=True)
                result = mcp__taskmaster_ai__update_task(
                    id=task_id,
                    prompt=f"Research findings: {research_result}",
                    projectRoot=project_root,
                    append=True,
                )

            return result.get("data") is not None

        except ImportError:
            return False
        except Exception:
            return False

    @staticmethod
    def save_to_file(
        research_result: str, query: str, project_root: str
    ) -> Optional[str]:
        """Save research result to a file."""
        try:
            # Create research directory
            # TODO: BROKEN - Using Task Master directory structure instead of Alfred's
            # Should be something like: os.path.join(project_root, ".alfred", "research")
            research_dir = os.path.join(project_root, ".taskmaster", "docs", "research")
            os.makedirs(research_dir, exist_ok=True)

            # Generate filename
            timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
            clean_query = re.sub(r"[^\w\s-]", "", query)[:30]
            clean_query = re.sub(r"\s+", "-", clean_query.strip())
            filename = f"research-{timestamp}-{clean_query}.md"

            file_path = os.path.join(research_dir, filename)

            # Write file
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"# Research: {query}\n\n")
                f.write(f"Generated: {datetime.now().isoformat()}\n\n")
                f.write("## Results\n\n")
                f.write(research_result)

            return file_path

        except Exception:
            return None


async def perform_research(
    request: ResearchRequest, project_root: str, provider: Optional[AIProvider] = None
) -> ResearchResponse:
    """Perform AI-powered research with context gathering."""

    # Validate request
    if not request.query or not request.query.strip():
        raise ValueError("Query is required and must be non-empty")

    if request.detail_level not in ["low", "medium", "high"]:
        raise ValueError("Detail level must be 'low', 'medium', or 'high'")

    # Auto-discover relevant tasks
    relevant_tasks = FuzzyTaskSearch.find_relevant_tasks(request.query, project_root)
    auto_discovered_ids = [str(task.task_id) for task in relevant_tasks]

    # Combine with provided task IDs
    all_task_ids = []
    if request.task_ids:
        provided_ids = [
            tid.strip() for tid in request.task_ids.split(",") if tid.strip()
        ]
        all_task_ids.extend(provided_ids)

    all_task_ids.extend(auto_discovered_ids)
    # Remove duplicates while preserving order
    seen = set()
    unique_task_ids = []
    for tid in all_task_ids:
        if tid not in seen:
            seen.add(tid)
            unique_task_ids.append(tid)

    # Update request with combined task IDs
    enhanced_request = request.model_copy()
    enhanced_request.task_ids = ",".join(unique_task_ids) if unique_task_ids else None

    # Gather context
    context = ContextGatherer.gather_context(enhanced_request, project_root)

    # Build context string
    context_parts = []

    if context.tasks:
        context_parts.append("## Tasks\n")
        for task in context.tasks:
            context_parts.append(
                f"### Task {task.get('id')}: {task.get('title', 'Untitled')}"
            )
            if task.get("description"):
                context_parts.append(f"Description: {task['description']}")
            if task.get("details"):
                context_parts.append(f"Details: {task['details']}")
            context_parts.append("")

    if context.files:
        context_parts.append("## Files\n")
        for file_info in context.files:
            context_parts.append(f"### {file_info['path']}")
            context_parts.append(f"```\n{file_info['content'][:2000]}...\n```")
            context_parts.append("")

    if context.custom_context:
        context_parts.append("## Additional Context\n")
        context_parts.append(context.custom_context)
        context_parts.append("")

    if context.project_tree:
        context_parts.append("## Project Structure\n")
        context_parts.append(f"```\n{context.project_tree}\n```")

    gathered_context = "\n".join(context_parts).strip()

    # Use configured research provider or fallback to general AI provider
    if provider is not None:
        target_provider = provider
    else:
        config = get_config()
        research_provider_name = config.research_provider

        if research_provider_name:
            # Map string to AIProvider enum
            provider_map = {
                "perplexity": AIProvider.PERPLEXITY,
                "anthropic": AIProvider.ANTHROPIC,
            }
            target_provider = provider_map.get(
                research_provider_name.lower(), config.ai_provider
            )
        else:
            # Use same as general AI provider
            target_provider = config.ai_provider
    ai_service = AIService(provider=target_provider)

    # Perform research
    research_result = await ai_service.research(
        query=request.query, context=gathered_context, detail_level=request.detail_level
    )

    # Extract result text
    if isinstance(research_result, dict):
        result_text = research_result.get("summary", str(research_result))
    else:
        result_text = str(research_result)

    # Calculate token counts
    prompt_data = ai_service.prompts.render_research(
        request.query, gathered_context, request.detail_level
    )
    system_tokens = ai_service.provider.estimate_tokens(prompt_data["system"] or "")
    user_tokens = ai_service.provider.estimate_tokens(prompt_data["user"])

    # Save results if requested
    saved_file_path = None
    if request.save_to_file:
        saved_file_path = ResearchSaver.save_to_file(
            result_text, request.query, project_root
        )

    if request.save_to:
        ResearchSaver.save_to_task(request.save_to, result_text, project_root)

    return ResearchResponse(
        query=request.query,
        result=result_text,
        context_size=len(gathered_context),
        context_tokens=context.token_breakdown.get("total", 0),
        token_breakdown=context.token_breakdown,
        system_prompt_tokens=system_tokens,
        user_prompt_tokens=user_tokens,
        total_input_tokens=system_tokens
        + user_tokens
        + context.token_breakdown.get("total", 0),
        detail_level=request.detail_level,
        saved_file_path=saved_file_path,
        telemetry_data={
            "auto_discovered_tasks": len(auto_discovered_ids),
            "total_tasks": len(context.tasks),
            "total_files": len(context.files),
            "has_project_tree": bool(context.project_tree),
        },
    )
