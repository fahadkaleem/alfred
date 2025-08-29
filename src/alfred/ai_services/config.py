"""AI service configuration utilities."""

from typing import Optional
from pydantic import BaseModel, Field
from alfred.config import get_config, Config
from .base import AIProvider


class AIProviderConfig(BaseModel):
    """Configuration for a specific AI provider."""

    provider: AIProvider
    api_key: Optional[str] = None
    model: Optional[str] = None
    base_url: Optional[str] = None
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=4096, ge=1)
    timeout: int = Field(default=60, ge=1)
    max_retries: int = Field(default=3, ge=0)


def get_provider_config(provider: AIProvider) -> AIProviderConfig:
    """Get configuration for a specific AI provider.

    Args:
        provider: Provider to get config for

    Returns:
        AIProviderConfig for the provider
    """
    config = get_config()

    provider_configs = {
        AIProvider.ANTHROPIC: AIProviderConfig(
            provider=provider,
            api_key=config.anthropic_api_key,
            model=config.claude_model,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            timeout=config.request_timeout,
            max_retries=config.max_retries,
        ),
        AIProvider.PERPLEXITY: AIProviderConfig(
            provider=provider,
            api_key=config.perplexity_api_key,
            model=config.perplexity_model,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            timeout=config.request_timeout,
            max_retries=config.max_retries,
        ),
    }

    return provider_configs.get(provider, provider_configs[AIProvider.ANTHROPIC])


def get_default_provider() -> AIProvider:
    """Get default provider based on configuration."""
    config = get_config()
    provider_map = {
        "anthropic": AIProvider.ANTHROPIC,
        "perplexity": AIProvider.PERPLEXITY,
    }
    return provider_map.get(config.ai_provider, AIProvider.ANTHROPIC)
