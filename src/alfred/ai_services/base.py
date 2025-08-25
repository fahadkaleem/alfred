"""Base AI provider interface for Alfred.

This module defines the abstract base class that all AI providers must implement,
enabling future support for OpenAI, Gemini, and other providers.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, AsyncGenerator, Dict, List, Optional, Union
from enum import Enum


class AIProvider(str, Enum):
    """Supported AI providers."""

    ANTHROPIC = "anthropic"
    OPENAI = "openai"  # Future
    GEMINI = "gemini"  # Future
    OLLAMA = "ollama"  # Future


@dataclass
class TokenUsage:
    """Token usage information for a request."""

    input_tokens: int
    output_tokens: int
    total_tokens: int

    def __add__(self, other: "TokenUsage") -> "TokenUsage":
        """Add two TokenUsage instances together."""
        return TokenUsage(
            input_tokens=self.input_tokens + other.input_tokens,
            output_tokens=self.output_tokens + other.output_tokens,
            total_tokens=self.total_tokens + other.total_tokens,
        )


@dataclass
class AIResponse:
    """Standard response from any AI provider."""

    text: str
    usage: TokenUsage
    model: str
    provider: AIProvider
    stop_reason: Optional[str] = None
    raw_response: Optional[Any] = None


@dataclass
class StreamEvent:
    """Event emitted during streaming responses."""

    type: str  # "message_start", "text", "message_end"
    data: Optional[str] = None  # Text delta for "text" events
    usage: Optional[TokenUsage] = None  # Usage for "message_end" events
    model: Optional[str] = None
    stop_reason: Optional[str] = None


class BaseAIProvider(ABC):
    """Abstract base class for AI providers.

    All AI providers (Anthropic, OpenAI, Gemini, etc.) must implement this interface.
    This ensures consistent behavior across different providers and enables easy switching.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 60,
        max_retries: int = 3,
    ):
        """Initialize the AI provider.

        Args:
            api_key: API key for the provider
            model: Default model to use
            base_url: Optional base URL for API calls
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries

    @property
    @abstractmethod
    def provider_name(self) -> AIProvider:
        """Return the provider name."""
        pass

    @property
    @abstractmethod
    def default_model(self) -> str:
        """Return the default model for this provider."""
        pass

    @abstractmethod
    async def complete(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        system: Optional[str] = None,
        **kwargs,
    ) -> AIResponse:
        """Generate a completion from the AI provider.

        Args:
            messages: List of message dicts with 'role' and 'content' keys
            model: Model to use (overrides default)
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
            system: System prompt (if supported by provider)
            **kwargs: Provider-specific parameters

        Returns:
            AIResponse with generated text and metadata
        """
        pass

    @abstractmethod
    async def stream_complete(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        system: Optional[str] = None,
        **kwargs,
    ) -> AsyncGenerator[StreamEvent, None]:
        """Stream a completion from the AI provider.

        Args:
            messages: List of message dicts with 'role' and 'content' keys
            model: Model to use (overrides default)
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
            system: System prompt (if supported by provider)
            **kwargs: Provider-specific parameters

        Yields:
            StreamEvent objects with text deltas and metadata
        """
        pass

    @abstractmethod
    def count_tokens(self, text: str, model: Optional[str] = None) -> int:
        """Count tokens in the given text.

        Args:
            text: Text to count tokens for
            model: Model to use for counting (affects tokenization)

        Returns:
            Number of tokens
        """
        pass

    async def complete_json(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        system: Optional[str] = None,
        response_schema: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Generate a JSON completion from the AI provider.

        This is a convenience method that ensures JSON output.
        Providers can override this for native JSON mode support.

        Args:
            messages: List of message dicts
            model: Model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens
            system: System prompt
            response_schema: Expected JSON schema (for validation/prompting)
            **kwargs: Provider-specific parameters

        Returns:
            Parsed JSON response
        """
        import json
        import re

        # Add JSON instruction to the last user message
        if messages and response_schema:
            json_instruction = f"\n\nReturn your response as valid JSON matching this structure:\n{json.dumps(response_schema, indent=2)}"
        else:
            json_instruction = "\n\nReturn your response as valid JSON."

        # Clone messages to avoid modifying original
        json_messages = messages.copy()
        if json_messages and json_messages[-1]["role"] == "user":
            json_messages[-1] = {
                "role": "user",
                "content": json_messages[-1]["content"] + json_instruction,
            }

        response = await self.complete(
            messages=json_messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            system=system,
            **kwargs,
        )

        # Try to parse JSON from response
        text = response.text.strip()

        # Try direct parsing first
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Try to extract JSON from markdown code blocks
        json_match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        # Try to find JSON object or array in the text
        json_match = re.search(r"(\{.*\}|\[.*\])", text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        # If all else fails, wrap in a simple object
        return {"response": text}

    def estimate_tokens(self, text: str) -> int:
        """Estimate token count using a simple heuristic.

        This is a fallback for providers that don't have token counting.
        Roughly 1 token ≈ 4 characters or 0.75 words.

        Args:
            text: Text to estimate tokens for

        Returns:
            Estimated token count
        """
        # Simple heuristic: ~4 characters per token
        return len(text) // 4
