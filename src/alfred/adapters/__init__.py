"""Alfred Task Manager - Backend Adapters.

This module provides a unified interface for integrating with task management platforms
like Linear and Jira.
"""

from .base import (
    TaskAdapter,
    TaskDict,
    EpicDict,
    AdapterError,
    AuthError,
    NotFoundError,
    ValidationError,
    RateLimitError,
    APIConnectionError,
    APIResponseError,
    MappingError,
)
from .linear_adapter import LinearAdapter

__all__ = [
    "TaskAdapter",
    "TaskDict",
    "EpicDict",
    "AdapterError",
    "AuthError",
    "NotFoundError",
    "ValidationError",
    "RateLimitError",
    "APIConnectionError",
    "APIResponseError",
    "MappingError",
    "LinearAdapter",
]
