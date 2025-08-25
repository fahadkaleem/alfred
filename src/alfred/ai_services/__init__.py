"""AI services package for Alfred.

This package provides AI capabilities through a provider-agnostic interface,
currently supporting Anthropic Claude with a design that allows easy addition
of other providers like OpenAI and Gemini.
"""

# Base types and interfaces
from .base import AIProvider, BaseAIProvider, AIResponse, TokenUsage, StreamEvent

# Exceptions
from .exceptions import (
    AIServiceError,
    RateLimitError,
    AuthenticationError,
    InvalidRequestError,
    ProviderNotFoundError,
    ModelNotSupportedError,
    JSONParseError,
    TokenLimitError,
    StreamingError,
)

# Configuration
from .config import AIProviderConfig, get_provider_config, get_default_provider

# Provider factory
from .provider_factory import (
    create_provider,
    get_available_providers,
    register_provider,
)

# Anthropic provider
from .anthropic_provider import AnthropicProvider

# Prompt templates
from .prompts import PromptTemplates

# High-level service
from .service import AIService

__all__ = [
    # Base types
    "AIProvider",
    "BaseAIProvider",
    "AIResponse",
    "TokenUsage",
    "StreamEvent",
    # Exceptions
    "AIServiceError",
    "RateLimitError",
    "AuthenticationError",
    "InvalidRequestError",
    "ProviderNotFoundError",
    "ModelNotSupportedError",
    "JSONParseError",
    "TokenLimitError",
    "StreamingError",
    # Configuration
    "AIProviderConfig",
    "get_provider_config",
    "get_default_provider",
    # Provider factory
    "create_provider",
    "get_available_providers",
    "register_provider",
    # Providers
    "AnthropicProvider",
    # Prompts
    "PromptTemplates",
    # Service
    "AIService",
]

# Version info
__version__ = "0.1.0"
