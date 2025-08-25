"""Anthropic Claude AI provider implementation."""

import os
import asyncio
import logging
from typing import Any, AsyncGenerator, Dict, List, Optional
from datetime import datetime, timedelta

import anthropic
from anthropic import AsyncAnthropic, RateLimitError as AnthropicRateLimitError
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)

from .base import BaseAIProvider, AIProvider, AIResponse, TokenUsage, StreamEvent
from .exceptions import (
    AIServiceError,
    RateLimitError,
    AuthenticationError,
    InvalidRequestError,
    StreamingError,
)

logger = logging.getLogger(__name__)


class AnthropicProvider(BaseAIProvider):
    """Anthropic Claude AI provider implementation.

    Supports Claude 3.5 Sonnet and other Claude models with streaming,
    token counting, and retry logic.
    """

    def __init__(
        self,
        api_key: str,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 60,
        max_retries: int = 3,
    ):
        """Initialize Anthropic provider.

        Args:
            api_key: Anthropic API key
            model: Model to use (default: claude-3-5-sonnet-20241022)
            base_url: Optional base URL for API
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
        """
        super().__init__(
            api_key=api_key,
            model=model or self.default_model,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
        )

        # Initialize Anthropic client
        self.client = AsyncAnthropic(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.timeout,
            max_retries=0,  # We handle retries ourselves
        )

        # Rate limiting tracking
        self._last_request_time: Optional[datetime] = None
        self._request_count = 0
        self._rate_limit_reset = datetime.now()

    @property
    def provider_name(self) -> AIProvider:
        """Return the provider name."""
        return AIProvider.ANTHROPIC

    @property
    def default_model(self) -> str:
        """Return the default model for Anthropic."""
        return "claude-3-5-sonnet-20241022"

    def _convert_messages(
        self, messages: List[Dict[str, str]], system: Optional[str] = None
    ) -> tuple[List[Dict[str, str]], Optional[str]]:
        """Convert messages to Anthropic format.

        Args:
            messages: List of message dicts
            system: Optional system prompt

        Returns:
            Tuple of (converted messages, system prompt)
        """
        converted = []
        extracted_system = system

        for message in messages:
            role = message["role"]
            content = message["content"]

            # Extract system message if present
            if role == "system":
                extracted_system = content
                continue

            # Convert to Anthropic format
            converted.append(
                {"role": "user" if role == "user" else "assistant", "content": content}
            )

        return converted, extracted_system

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=60),
        retry=retry_if_exception_type(AnthropicRateLimitError),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    async def _make_request(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        max_tokens: int,
        system: Optional[str] = None,
        **kwargs,
    ) -> Any:
        """Make a request to the Anthropic API with retry logic.

        Args:
            messages: Conversation messages
            model: Model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            system: System prompt
            **kwargs: Additional parameters

        Returns:
            API response

        Raises:
            RateLimitError: If rate limited
            AuthenticationError: If authentication fails
            InvalidRequestError: If request is invalid
        """
        try:
            response = await self.client.messages.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system,
                **kwargs,
            )
            return response

        except anthropic.RateLimitError as e:
            logger.warning(f"Rate limit hit: {e}")
            raise RateLimitError(
                f"Anthropic rate limit exceeded: {e}",
                provider=self.provider_name.value,
                retry_after=getattr(e, "retry_after", 60),
            )
        except anthropic.AuthenticationError as e:
            raise AuthenticationError(
                f"Anthropic authentication failed: {e}",
                provider=self.provider_name.value,
            )
        except anthropic.BadRequestError as e:
            raise InvalidRequestError(
                f"Invalid request to Anthropic: {e}",
                provider=self.provider_name.value,
                details={"error": str(e)},
            )
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise AIServiceError(
                f"Anthropic API error: {e}", provider=self.provider_name.value
            )

    async def complete(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        system: Optional[str] = None,
        **kwargs,
    ) -> AIResponse:
        """Generate a completion from Anthropic.

        Args:
            messages: Conversation messages
            model: Model to use (overrides default)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            system: System prompt
            **kwargs: Additional Anthropic-specific parameters

        Returns:
            AIResponse with generated text and metadata
        """
        model = model or self.model

        # Convert messages to Anthropic format
        anthropic_messages, extracted_system = self._convert_messages(messages, system)

        # Make the request
        response = await self._make_request(
            messages=anthropic_messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            system=extracted_system,
            **kwargs,
        )

        # Extract response data
        text = response.content[0].text if response.content else ""

        usage = TokenUsage(
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            total_tokens=response.usage.input_tokens + response.usage.output_tokens,
        )

        return AIResponse(
            text=text,
            usage=usage,
            model=model,
            provider=self.provider_name,
            stop_reason=response.stop_reason,
            raw_response=response,
        )

    async def stream_complete(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        system: Optional[str] = None,
        **kwargs,
    ) -> AsyncGenerator[StreamEvent, None]:
        """Stream a completion from Anthropic.

        Args:
            messages: Conversation messages
            model: Model to use (overrides default)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            system: System prompt
            **kwargs: Additional Anthropic-specific parameters

        Yields:
            StreamEvent objects with text deltas and metadata
        """
        model = model or self.model

        # Convert messages to Anthropic format
        anthropic_messages, extracted_system = self._convert_messages(messages, system)

        try:
            # Create stream
            stream = await self.client.messages.create(
                model=model,
                messages=anthropic_messages,
                max_tokens=max_tokens,
                temperature=temperature,
                system=extracted_system,
                stream=True,
                **kwargs,
            )

            # Track usage
            total_usage = TokenUsage(0, 0, 0)

            # Yield message start event
            yield StreamEvent(type="message_start", model=model)

            # Process stream events
            async for event in stream:
                if event.type == "content_block_delta":
                    # Text delta
                    if hasattr(event.delta, "text"):
                        yield StreamEvent(type="text", data=event.delta.text)

                elif event.type == "message_delta":
                    # Usage update
                    if hasattr(event, "usage"):
                        total_usage.output_tokens = event.usage.output_tokens

                elif event.type == "message_stop":
                    # Final usage
                    if hasattr(event, "usage"):
                        total_usage.input_tokens = event.usage.input_tokens
                        total_usage.output_tokens = event.usage.output_tokens
                        total_usage.total_tokens = (
                            total_usage.input_tokens + total_usage.output_tokens
                        )

            # Yield message end event
            yield StreamEvent(type="message_end", usage=total_usage, model=model)

        except Exception as e:
            logger.error(f"Streaming error: {e}")
            raise StreamingError(
                f"Failed to stream from Anthropic: {e}",
                provider=self.provider_name.value,
            )

    async def count_tokens(self, text: str, model: Optional[str] = None) -> int:
        """Count tokens in text.

        Args:
            text: Text to count tokens for
            model: Model to use for counting

        Returns:
            Number of tokens
        """
        # Anthropic doesn't provide a direct token counting API
        # Use approximation: ~4 characters per token for Claude
        return len(text) // 4

    async def validate_connection(self) -> bool:
        """Validate the connection to Anthropic.

        Returns:
            True if connection is valid
        """
        try:
            # Try a minimal request
            await self.complete(
                messages=[{"role": "user", "content": "Hi"}], max_tokens=10
            )
            return True
        except Exception as e:
            logger.error(f"Connection validation failed: {e}")
            return False
