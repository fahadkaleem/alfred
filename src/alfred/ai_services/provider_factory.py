"""AI provider factory for creating provider instances."""

import logging
from typing import Optional, Dict, Type

from .base import BaseAIProvider, AIProvider
from .anthropic_provider import AnthropicProvider
from .config import get_provider_config, get_default_provider
from .exceptions import ProviderNotFoundError

logger = logging.getLogger(__name__)

# Registry of available providers
PROVIDER_REGISTRY: Dict[AIProvider, Type[BaseAIProvider]] = {
    AIProvider.ANTHROPIC: AnthropicProvider,
    # Future providers can be added here:
    # AIProvider.OPENAI: OpenAIProvider,
    # AIProvider.GEMINI: GeminiProvider,
    # AIProvider.OLLAMA: OllamaProvider,
}


def create_provider(
    provider: Optional[AIProvider] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    **kwargs,
) -> BaseAIProvider:
    """Create an AI provider instance.

    Args:
        provider: Provider type to create (defaults to configured provider)
        api_key: Optional API key override
        model: Optional model override
        **kwargs: Additional provider-specific parameters

    Returns:
        Configured provider instance

    Raises:
        ValueError: If provider is not supported
    """
    # Use default if not specified
    provider = provider or get_default_provider()

    # Get provider class from registry
    provider_class = PROVIDER_REGISTRY.get(provider)
    if not provider_class:
        raise ValueError(
            f"Provider {provider} is not supported. Available: {list(PROVIDER_REGISTRY.keys())}"
        )

    # Get configuration
    config = get_provider_config(provider)

    # Override with provided values
    if api_key:
        config.api_key = api_key
    if model:
        config.model = model

    # Merge additional kwargs
    provider_kwargs = {
        "api_key": config.api_key,
        "model": config.model,
        "base_url": config.base_url,
        "timeout": config.timeout,
        "max_retries": config.max_retries,
        **kwargs,
    }

    logger.debug(f"Creating {provider} provider with model {config.model}")

    return provider_class(**provider_kwargs)


def get_available_providers() -> list[AIProvider]:
    """Get list of available providers.

    Returns:
        List of available provider types
    """
    return list(PROVIDER_REGISTRY.keys())


def register_provider(
    provider: AIProvider, provider_class: Type[BaseAIProvider]
) -> None:
    """Register a new provider implementation.

    Args:
        provider: Provider enum value
        provider_class: Provider implementation class
    """
    PROVIDER_REGISTRY[provider] = provider_class
    logger.info(f"Registered provider: {provider.value}")
