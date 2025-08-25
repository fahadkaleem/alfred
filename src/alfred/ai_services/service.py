"""High-level AI service for Alfred operations.

This service provides a unified interface for AI operations, abstracting
away provider-specific details and handling common tasks like chunking,
JSON parsing, and error handling.
"""

import json
import logging
from typing import Any, AsyncGenerator, Dict, List, Optional, Union

from .base import AIProvider, BaseAIProvider, AIResponse, TokenUsage, StreamEvent
from .prompts import PromptTemplates
from .provider_factory import create_provider
from alfred.config import get_config
from .exceptions import AIServiceError, JSONParseError, TokenLimitError

logger = logging.getLogger(__name__)


class AIService:
    """High-level AI service for Alfred operations.

    This service provides methods for all AI-powered operations in Alfred,
    using the configured provider and handling common patterns like chunking
    and JSON parsing.
    """

    def __init__(
        self,
        provider: Optional[AIProvider] = None,
        custom_provider: Optional[BaseAIProvider] = None,
    ):
        """Initialize AI service.

        Args:
            provider: Provider to use (defaults to configured provider)
            custom_provider: Custom provider instance to use
        """
        self.config = get_config()

        if custom_provider:
            self.provider = custom_provider
        else:
            self.provider = create_provider(provider)

        self.prompts = PromptTemplates()

        # Track total usage across requests
        self.total_usage = TokenUsage(0, 0, 0)

    async def create_tasks_from_spec(
        self,
        spec_content: str,
        num_tasks: int = 5,
        project_context: Optional[str] = None,
        stream: bool = False,
    ) -> Union[List[Dict[str, Any]], AsyncGenerator[StreamEvent, None]]:
        """Create tasks from a specification.

        Args:
            spec_content: The specification content
            num_tasks: Number of tasks to generate
            project_context: Optional project context
            stream: Whether to stream the response

        Returns:
            List of task dictionaries or stream of events
        """
        # Check if spec needs chunking
        prompt_data = self.prompts.render_create_tasks_from_spec(
            spec_content, num_tasks, project_context
        )

        # Estimate tokens
        estimated_tokens = self._estimate_prompt_tokens(prompt_data["messages"])
        max_context = self._get_max_context_tokens()

        if estimated_tokens > max_context * self.config.max_context_percentage:
            # Chunk the spec if too large
            return await self._create_tasks_from_spec_chunked(
                spec_content, num_tasks, project_context, stream
            )

        if stream:
            return self._stream_json_response(prompt_data["messages"])
        else:
            response = await self.provider.complete_json(
                messages=prompt_data["messages"], temperature=0.7
            )
            # complete_json returns parsed JSON directly, not a response object

            # Ensure we return a list
            if isinstance(response, dict) and "tasks" in response:
                return response["tasks"]
            elif isinstance(response, list):
                return response
            else:
                return [response]

    async def decompose_task(
        self,
        task: Union[str, Dict[str, Any]],
        num_subtasks: int = 3,
        context: Optional[str] = None,
        stream: bool = False,
    ) -> Union[List[Dict[str, Any]], AsyncGenerator[StreamEvent, None]]:
        """Decompose a task into subtasks.

        Args:
            task: Task to decompose (string or dict)
            num_subtasks: Number of subtasks to generate
            context: Optional additional context
            stream: Whether to stream the response

        Returns:
            List of subtask dictionaries or stream of events
        """
        prompt_data = self.prompts.render_decompose_task(task, num_subtasks, context)

        if stream:
            return self._stream_json_response(prompt_data["messages"])
        else:
            response = await self.provider.complete_json(
                messages=prompt_data["messages"], temperature=0.6
            )
            # complete_json returns parsed JSON directly, not a response object

            # Ensure we return a list
            if isinstance(response, dict) and "subtasks" in response:
                return response["subtasks"]
            elif isinstance(response, list):
                return response
            else:
                return [response]

    async def assess_complexity(
        self,
        task: Union[str, Dict[str, Any], List[Dict[str, Any]]],
        include_recommendations: bool = True,
    ) -> Dict[str, Any]:
        """Assess task complexity.

        Args:
            task: Task(s) to assess
            include_recommendations: Whether to include recommendations

        Returns:
            Complexity assessment dictionary
        """
        prompt_data = self.prompts.render_assess_complexity(
            task, include_recommendations
        )

        response = await self.provider.complete_json(
            messages=prompt_data["messages"], temperature=0.5
        )
        # complete_json returns parsed JSON directly, not a response object

        return response

    async def enhance_task(
        self,
        task: Union[str, Dict[str, Any]],
        context: str,
        enhancement_type: str = "general",
        stream: bool = False,
    ) -> Union[Dict[str, Any], AsyncGenerator[StreamEvent, None]]:
        """Enhance a task with additional details.

        Args:
            task: Task to enhance
            context: Enhancement context
            enhancement_type: Type of enhancement
            stream: Whether to stream the response

        Returns:
            Enhanced task dictionary or stream of events
        """
        prompt_data = self.prompts.render_enhance_task(task, context, enhancement_type)

        if stream:
            return self._stream_json_response(prompt_data["messages"])
        else:
            response = await self.provider.complete_json(
                messages=prompt_data["messages"], temperature=0.6
            )
            # complete_json returns parsed JSON directly, not a response object

            return response

    async def research(
        self,
        query: str,
        context: str = "",
        detail_level: str = "medium",
        stream: bool = False,
    ) -> Union[Dict[str, Any], str, AsyncGenerator[StreamEvent, None]]:
        """Perform research on a topic.

        Args:
            query: Research query
            context: Additional context
            detail_level: Level of detail (low, medium, high)
            stream: Whether to stream the response

        Returns:
            Research results as dict/string or stream of events
        """
        prompt_data = self.prompts.render_research(query, context, detail_level)

        if stream:
            return self._stream_response(prompt_data["messages"])
        else:
            # Try to get JSON response first
            try:
                response = await self.provider.complete_json(
                    messages=prompt_data["messages"],
                    temperature=0.8,
                    max_tokens=8192,  # More tokens for research
                )
                # complete_json returns parsed JSON directly, not a response object
                return response
            except (JSONParseError, Exception):
                # Fall back to plain text if JSON fails
                response = await self.provider.complete(
                    messages=prompt_data["messages"], temperature=0.8, max_tokens=8192
                )
                self.total_usage += response.usage
                return response.text

    async def _create_tasks_from_spec_chunked(
        self,
        spec_content: str,
        num_tasks: int,
        project_context: Optional[str],
        stream: bool,
    ) -> List[Dict[str, Any]]:
        """Create tasks from a large spec by chunking.

        Args:
            spec_content: Large specification content
            num_tasks: Total number of tasks to generate
            project_context: Optional project context
            stream: Whether to stream (not supported for chunked)

        Returns:
            List of task dictionaries
        """
        if stream:
            logger.warning(
                "Streaming not supported for chunked specs, using non-streaming"
            )

        # First, assess complexity to guide chunking
        complexity = await self.assess_complexity(
            f"Specification excerpt:\n{spec_content[:2000]}",
            include_recommendations=True,
        )

        # Determine chunk size based on complexity
        chunk_size = 4000 if complexity.get("complexity_score", 5) < 7 else 3000
        overlap = self.config.chunk_overlap_tokens * 4  # Convert to chars

        # Chunk the spec
        chunks = self._chunk_text(spec_content, chunk_size, overlap)
        logger.info(f"Processing spec in {len(chunks)} chunks")

        # Generate tasks for each chunk
        all_tasks = []
        tasks_per_chunk = max(1, num_tasks // len(chunks))

        for i, chunk in enumerate(chunks):
            chunk_context = (
                f"{project_context or ''}\n\nProcessing part {i + 1} of {len(chunks)}"
            )

            # Adjust tasks for last chunk to hit target
            if i == len(chunks) - 1:
                tasks_for_chunk = num_tasks - len(all_tasks)
            else:
                tasks_for_chunk = tasks_per_chunk

            if tasks_for_chunk <= 0:
                break

            chunk_tasks = await self.create_tasks_from_spec(
                chunk, tasks_for_chunk, chunk_context, stream=False
            )
            all_tasks.extend(chunk_tasks)

        # Deduplicate and trim to exact number
        all_tasks = self._deduplicate_tasks(all_tasks)

        if len(all_tasks) > num_tasks:
            all_tasks = all_tasks[:num_tasks]
        elif len(all_tasks) < num_tasks:
            # Generate additional tasks if needed
            remaining = num_tasks - len(all_tasks)
            logger.info(f"Generating {remaining} additional tasks")

            additional = await self.create_tasks_from_spec(
                spec_content[-chunk_size:], remaining, project_context, stream=False
            )
            all_tasks.extend(additional)

        return all_tasks[:num_tasks]

    def _chunk_text(self, text: str, chunk_size: int, overlap: int) -> List[str]:
        """Chunk text with overlap.

        Args:
            text: Text to chunk
            chunk_size: Size of each chunk in characters
            overlap: Overlap between chunks

        Returns:
            List of text chunks
        """
        chunks = []
        start = 0

        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunks.append(text[start:end])

            if end >= len(text):
                break

            start = end - overlap

        return chunks

    def _deduplicate_tasks(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Deduplicate tasks based on title similarity.

        Args:
            tasks: List of task dictionaries

        Returns:
            Deduplicated list of tasks
        """
        seen_titles = set()
        unique_tasks = []

        for task in tasks:
            title = task.get("title", "").lower().strip()

            # Simple deduplication - could be enhanced with fuzzy matching
            if title and title not in seen_titles:
                seen_titles.add(title)
                unique_tasks.append(task)

        return unique_tasks

    def _estimate_prompt_tokens(self, messages: List[Dict[str, str]]) -> int:
        """Estimate tokens in messages.

        Args:
            messages: List of message dictionaries

        Returns:
            Estimated token count
        """
        text = " ".join(msg["content"] for msg in messages)
        return self.provider.estimate_tokens(text)

    def _get_max_context_tokens(self) -> int:
        """Get maximum context tokens for current model.

        Returns:
            Maximum context size in tokens
        """
        # Model context sizes (approximate)
        model_contexts = {
            "claude-3-5-sonnet": 200000,
            "claude-3-opus": 200000,
            "claude-3-sonnet": 200000,
            "claude-3-haiku": 200000,
            "gpt-4-turbo": 128000,
            "gpt-4": 8192,
            "gpt-3.5-turbo": 16384,
            "gemini-pro": 32768,
        }

        model = self.provider.model or self.provider.default_model

        # Find matching context size
        for model_prefix, context_size in model_contexts.items():
            if model_prefix in model.lower():
                return context_size

        # Default to conservative estimate
        return 8192

    async def _stream_response(
        self, messages: List[Dict[str, str]]
    ) -> AsyncGenerator[StreamEvent, None]:
        """Stream a response from the provider.

        Args:
            messages: Messages to send

        Yields:
            StreamEvent objects
        """
        async for event in self.provider.stream_complete(messages):
            yield event

            # Track usage from final event
            if event.type == "message_end" and event.usage:
                self.total_usage += event.usage

    async def _stream_json_response(
        self, messages: List[Dict[str, str]]
    ) -> AsyncGenerator[StreamEvent, None]:
        """Stream a JSON response, accumulating text for final parsing.

        Args:
            messages: Messages to send

        Yields:
            StreamEvent objects, with final JSON result
        """
        accumulated_text = []

        async for event in self.provider.stream_complete(messages):
            yield event

            if event.type == "text" and event.data:
                accumulated_text.append(event.data)
            elif event.type == "message_end":
                # Track usage
                if event.usage:
                    self.total_usage += event.usage

                # Try to parse accumulated JSON
                full_text = "".join(accumulated_text)
                try:
                    parsed = json.loads(full_text)
                    yield StreamEvent(type="result", data=json.dumps(parsed))
                except json.JSONDecodeError:
                    # Try to extract JSON from text
                    import re

                    json_match = re.search(r"(\{.*\}|\[.*\])", full_text, re.DOTALL)
                    if json_match:
                        try:
                            parsed = json.loads(json_match.group(1))
                            yield StreamEvent(type="result", data=json.dumps(parsed))
                        except json.JSONDecodeError:
                            yield StreamEvent(
                                type="error", data="Failed to parse JSON from response"
                            )
                    else:
                        yield StreamEvent(
                            type="error", data="No JSON found in response"
                        )

    def get_usage_summary(self) -> Dict[str, Any]:
        """Get summary of token usage.

        Returns:
            Dictionary with usage statistics
        """
        return {
            "total_input_tokens": self.total_usage.input_tokens,
            "total_output_tokens": self.total_usage.output_tokens,
            "total_tokens": self.total_usage.total_tokens,
            "estimated_cost": self._estimate_cost(self.total_usage),
        }

    def _estimate_cost(self, usage: TokenUsage) -> float:
        """Estimate cost based on token usage.

        Args:
            usage: Token usage to estimate cost for

        Returns:
            Estimated cost in USD
        """
        # Rough cost estimates (per 1M tokens)
        # These should be updated based on actual pricing
        cost_per_million = {
            "claude-3-5-sonnet": {"input": 3.0, "output": 15.0},
            "claude-3-opus": {"input": 15.0, "output": 75.0},
            "claude-3-sonnet": {"input": 3.0, "output": 15.0},
            "claude-3-haiku": {"input": 0.25, "output": 1.25},
            "gpt-4-turbo": {"input": 10.0, "output": 30.0},
            "gpt-4": {"input": 30.0, "output": 60.0},
            "gpt-3.5-turbo": {"input": 0.5, "output": 1.5},
        }

        model = self.provider.model or self.provider.default_model

        # Find matching pricing
        for model_prefix, pricing in cost_per_million.items():
            if model_prefix in model.lower():
                input_cost = (usage.input_tokens / 1_000_000) * pricing["input"]
                output_cost = (usage.output_tokens / 1_000_000) * pricing["output"]
                return round(input_cost + output_cost, 4)

        # Default estimate
        return round((usage.total_tokens / 1_000_000) * 5.0, 4)
