"""Utilities for task generation from specifications."""

import json
import re
from typing import List, Optional, Dict, Any, Union
from alfred.core.tasks.models import TaskSuggestion, EpicSuggestion, GenerationResult


def estimate_tokens(text: str) -> int:
    """Estimate token count for text.

    Args:
        text: Text to estimate tokens for

    Returns:
        Estimated token count
    """
    # Use simple heuristic: ~4 characters per token
    # This is a rough estimate that works reasonably well for English
    return len(text) // 4


def chunk_markdown(
    text: str, target_tokens: int = 3000, overlap_tokens: int = 200
) -> List[str]:
    """Split markdown/text into chunks with overlap.

    Args:
        text: Text to chunk
        target_tokens: Target tokens per chunk
        overlap_tokens: Tokens to overlap between chunks

    Returns:
        List of text chunks
    """
    chunks = []

    # Split by double newlines (paragraphs) or headers
    sections = re.split(r"\n\n+|(?=^#{1,6}\s)", text, flags=re.MULTILINE)

    current_chunk = []
    current_tokens = 0

    for section in sections:
        section_tokens = estimate_tokens(section)

        # If single section is too large, split it further
        if section_tokens > target_tokens:
            # Split by sentences
            sentences = re.split(r"(?<=[.!?])\s+", section)
            for sentence in sentences:
                sentence_tokens = estimate_tokens(sentence)
                if current_tokens + sentence_tokens > target_tokens and current_chunk:
                    # Save current chunk
                    chunks.append("\n\n".join(current_chunk))
                    # Start new chunk with overlap
                    overlap_text = (
                        "\n\n".join(current_chunk[-2:])
                        if len(current_chunk) > 1
                        else current_chunk[-1]
                        if current_chunk
                        else ""
                    )
                    current_chunk = [overlap_text] if overlap_text else []
                    current_tokens = (
                        estimate_tokens(overlap_text) if overlap_text else 0
                    )

                current_chunk.append(sentence)
                current_tokens += sentence_tokens
        else:
            # Add section to current chunk
            if current_tokens + section_tokens > target_tokens and current_chunk:
                # Save current chunk
                chunks.append("\n\n".join(current_chunk))
                # Start new chunk with overlap
                overlap_text = (
                    "\n\n".join(current_chunk[-2:])
                    if len(current_chunk) > 1
                    else current_chunk[-1]
                    if current_chunk
                    else ""
                )
                current_chunk = [overlap_text] if overlap_text else []
                current_tokens = estimate_tokens(overlap_text) if overlap_text else 0

            current_chunk.append(section)
            current_tokens += section_tokens

    # Add remaining chunk
    if current_chunk:
        chunks.append("\n\n".join(current_chunk))

    return chunks


def safe_extract_json(text: str) -> Dict[str, Any]:
    """Extract JSON from text, handling various formats.

    Args:
        text: Text potentially containing JSON

    Returns:
        Parsed JSON as dictionary

    Raises:
        ValueError: If no valid JSON can be extracted
    """
    # Try direct parsing first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try fixing common issues first on the raw text
        fixed = text
        # Remove trailing commas
        fixed = re.sub(r",\s*([}\]])", r"\1", fixed)
        try:
            return json.loads(fixed)
        except json.JSONDecodeError:
            pass

    # Try extracting from code blocks
    code_block_patterns = [
        r"```json\s*\n(.*?)\n```",
        r"```\s*\n(.*?)\n```",
        r"`([^`]+)`",
    ]

    for pattern in code_block_patterns:
        matches = re.findall(pattern, text, re.DOTALL)
        for match in matches:
            try:
                return json.loads(match)
            except json.JSONDecodeError:
                # Try fixing common issues
                fixed = match
                # Remove trailing commas
                fixed = re.sub(r",\s*([}\]])", r"\1", fixed)
                # Try again
                try:
                    return json.loads(fixed)
                except json.JSONDecodeError:
                    continue

    # Try finding JSON-like structure
    json_patterns = [
        r"(\{[^{}]*\})",  # Simple object
        r"(\[[^\[\]]*\])",  # Simple array
        r"(\{.*\})",  # Complex object
        r"(\[.*\])",  # Complex array
    ]

    for pattern in json_patterns:
        matches = re.findall(pattern, text, re.DOTALL)
        for match in matches:
            try:
                result = json.loads(match)
                # Ensure it's a dict or has expected structure
                if isinstance(result, (dict, list)):
                    return result
            except json.JSONDecodeError:
                # Try fixing trailing commas
                fixed = re.sub(r",\s*([}\]])", r"\1", match)
                try:
                    result = json.loads(fixed)
                    if isinstance(result, (dict, list)):
                        return result
                except json.JSONDecodeError:
                    continue

    raise ValueError("No valid JSON found in text")


def parse_ai_response(payload: Union[str, dict]) -> GenerationResult:
    """Parse AI response into GenerationResult.

    Args:
        payload: AI response as string or dict

    Returns:
        Parsed GenerationResult

    Raises:
        ValueError: If response cannot be parsed
    """
    # Handle string payload
    if isinstance(payload, str):
        try:
            data = safe_extract_json(payload)
        except ValueError as e:
            raise ValueError(f"Failed to extract JSON from response: {e}")
    else:
        data = payload

    # Handle different response formats
    tasks_data = []
    epic_data = None

    # Check for tasks array
    if isinstance(data, list):
        tasks_data = data
    elif isinstance(data, dict):
        if "tasks" in data:
            tasks_data = data["tasks"]
        else:
            # Single task
            tasks_data = [data]

        # Check for epic
        if "epic" in data:
            epic_data = data["epic"]

    # Parse tasks
    tasks = []
    for task_data in tasks_data:
        # Normalize priority
        priority = task_data.get("priority", "P2")
        if priority in ["critical", "high", "medium", "low"]:
            priority_map = {"critical": "P0", "high": "P1", "medium": "P2", "low": "P3"}
            priority = priority_map.get(priority, "P2")
        elif priority not in ["P0", "P1", "P2", "P3"]:
            priority = "P2"

        # Create task suggestion
        task = TaskSuggestion(
            title=task_data.get("title", ""),
            description=task_data.get("description", ""),
            priority=priority,
            labels=task_data.get("labels", []),
            dependencies=task_data.get("dependencies", []),
            estimate=task_data.get("estimate") or task_data.get("estimated_hours"),
            acceptance_criteria=task_data.get("acceptance_criteria", []),
            technical_notes=task_data.get("technical_notes")
            or task_data.get("technical_details"),
        )
        tasks.append(task)

    # Parse epic if present
    epic = None
    if epic_data:
        epic = EpicSuggestion(
            title=epic_data.get("title", "Generated Epic"),
            description=epic_data.get("description", ""),
            create_epic=epic_data.get("create_epic", True),
        )

    # Get metadata
    metadata = {}
    if isinstance(data, dict) and "metadata" in data:
        metadata = data["metadata"]

    return GenerationResult(epic=epic, tasks=tasks, metadata=metadata)


def merge_task_candidates(
    candidates: List[TaskSuggestion],
    limit: int,
) -> List[TaskSuggestion]:
    """Merge and deduplicate task candidates.

    Args:
        candidates: List of task suggestions
        limit: Maximum number of tasks to return

    Returns:
        Merged and prioritized list of tasks
    """

    # Normalize titles for comparison
    def normalize_title(title: str) -> str:
        # Remove punctuation and convert to lowercase
        normalized = re.sub(r"[^\w\s]", "", title.lower())
        return " ".join(normalized.split())

    # Deduplicate by normalized title
    seen_titles = set()
    unique_tasks = []

    for task in candidates:
        normalized = normalize_title(task.title)
        if normalized not in seen_titles:
            seen_titles.add(normalized)
            unique_tasks.append(task)

    # Sort by priority
    def task_score(task: TaskSuggestion) -> int:
        # Lower priority number = higher priority (P0 > P1 > P2 > P3)
        return int(task.priority[1])

    unique_tasks.sort(key=task_score)

    # Return up to limit
    return unique_tasks[:limit]


def map_priority_to_linear(priority: str) -> int:
    """Map priority string to Linear priority number.

    Args:
        priority: Priority string (P0-P3)

    Returns:
        Linear priority number (0-3, where higher is more urgent)
    """
    mapping = {
        "P0": 3,  # Urgent
        "P1": 2,  # High
        "P2": 1,  # Medium
        "P3": 0,  # Low
    }
    return mapping.get(priority, 1)
