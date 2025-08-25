"""Custom exceptions for AI services."""

from typing import Optional, Dict, Any


class AIServiceError(Exception):
    """Base exception for AI service errors."""

    def __init__(
        self,
        message: str,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.provider = provider
        self.model = model
        self.details = details or {}


class RateLimitError(AIServiceError):
    """Raised when rate limit is exceeded."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[float] = None,
        **kwargs,
    ):
        super().__init__(message, **kwargs)
        self.retry_after = retry_after


class AuthenticationError(AIServiceError):
    """Raised when authentication fails."""

    pass


class InvalidRequestError(AIServiceError):
    """Raised when request is invalid."""

    pass


class ProviderNotFoundError(AIServiceError):
    """Raised when requested provider is not available."""

    pass


class ModelNotSupportedError(AIServiceError):
    """Raised when requested model is not supported by provider."""

    pass


class JSONParseError(AIServiceError):
    """Raised when JSON response cannot be parsed."""

    def __init__(
        self,
        message: str = "Failed to parse JSON response",
        raw_text: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(message, **kwargs)
        self.raw_text = raw_text


class TokenLimitError(AIServiceError):
    """Raised when token limit is exceeded."""

    def __init__(
        self,
        message: str = "Token limit exceeded",
        token_count: Optional[int] = None,
        limit: Optional[int] = None,
        **kwargs,
    ):
        super().__init__(message, **kwargs)
        self.token_count = token_count
        self.limit = limit


class StreamingError(AIServiceError):
    """Raised when streaming response fails."""

    pass
