"""Perplexity AI provider implementation."""

import asyncio
import json
import logging
from typing import Any, AsyncGenerator, Dict, List, Optional

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from .base import AIProvider, AIResponse, BaseAIProvider, StreamEvent, TokenUsage
from .exceptions import RateLimitError, AuthenticationError, InvalidRequestError

logger = logging.getLogger(__name__)


class PerplexityProvider(BaseAIProvider):
    """Perplexity AI provider implementation."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 60,
        max_retries: int = 3,
    ):
        super().__init__(api_key, model, base_url, timeout, max_retries)
        self.base_url = base_url or "https://api.perplexity.ai"
        self.client = httpx.AsyncClient(timeout=timeout)

    @property
    def provider_name(self) -> AIProvider:
        return AIProvider.PERPLEXITY

    @property
    def default_model(self) -> str:
        return "sonar-pro"

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True,
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
        """Generate a completion from Perplexity AI."""
        model = model or self.model or self.default_model

        formatted_messages = self._format_messages(messages, system)

        payload = {
            "model": model,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=headers,
            )
            response.raise_for_status()

            data = response.json()
            choice = data["choices"][0]
            usage = data.get("usage", {})

            return AIResponse(
                text=choice["message"]["content"],
                usage=TokenUsage(
                    input_tokens=usage.get("prompt_tokens", 0),
                    output_tokens=usage.get("completion_tokens", 0),
                    total_tokens=usage.get("total_tokens", 0),
                ),
                model=model,
                provider=self.provider_name,
                stop_reason=choice.get("finish_reason"),
                raw_response=data,
            )

        except httpx.HTTPStatusError as e:
            self._handle_http_error(e)
        except Exception as e:
            logger.error(f"Perplexity API error: {e}")
            raise

    async def stream_complete(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        system: Optional[str] = None,
        **kwargs,
    ) -> AsyncGenerator[StreamEvent, None]:
        """Stream a completion from Perplexity AI."""
        model = model or self.model or self.default_model

        formatted_messages = self._format_messages(messages, system)

        payload = {
            "model": model,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
            **kwargs,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with self.client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=headers,
            ) as response:
                response.raise_for_status()

                yield StreamEvent(type="message_start", model=model)

                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str == "[DONE]":
                            break

                        try:
                            data = json.loads(data_str)
                            choice = data["choices"][0]

                            if "content" in choice.get("delta", {}):
                                content = choice["delta"]["content"]
                                yield StreamEvent(type="text", data=content)

                            if choice.get("finish_reason"):
                                usage = data.get("usage", {})
                                yield StreamEvent(
                                    type="message_end",
                                    usage=TokenUsage(
                                        input_tokens=usage.get("prompt_tokens", 0),
                                        output_tokens=usage.get("completion_tokens", 0),
                                        total_tokens=usage.get("total_tokens", 0),
                                    ),
                                    stop_reason=choice["finish_reason"],
                                )

                        except json.JSONDecodeError:
                            continue

        except httpx.HTTPStatusError as e:
            self._handle_http_error(e)

    def count_tokens(self, text: str, model: Optional[str] = None) -> int:
        """Count tokens using estimation."""
        return self.estimate_tokens(text)

    def _format_messages(
        self, messages: List[Dict[str, str]], system: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """Format messages for Perplexity API."""
        formatted = []

        if system:
            formatted.append({"role": "system", "content": system})

        for msg in messages:
            if msg["role"] == "system" and not system:
                formatted.append(msg)
            elif msg["role"] in ["user", "assistant"]:
                formatted.append(msg)

        return formatted

    def _handle_http_error(self, error: httpx.HTTPStatusError) -> None:
        """Handle HTTP errors from Perplexity API."""
        status_code = error.response.status_code

        try:
            error_data = error.response.json()
            error_msg = error_data.get("error", {}).get("message", str(error))
        except:
            error_msg = str(error)

        if status_code == 401:
            raise AuthenticationError(f"Perplexity authentication failed: {error_msg}")
        elif status_code == 429:
            raise RateLimitError(f"Perplexity rate limit exceeded: {error_msg}")
        elif status_code >= 400:
            raise InvalidRequestError(f"Perplexity API error: {error_msg}")
        else:
            raise Exception(f"Perplexity API error: {error_msg}")

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.client.aclose()
