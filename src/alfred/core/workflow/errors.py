"""Alfred Error Handling Framework.

This module implements Decision #7 (Direct, Meaningful Error Handling) from alfred.md.
Instead of multiple layers of wrapped exceptions that obscure the actual problem,
we provide clear error messages with recovery steps.

The framework includes:
- Custom exceptions with three-part messages (user, technical, recovery)
- Error handler decorator for consistent handling
- Similar task suggestions for helpful guidance
"""

import asyncio
import functools
import json
import sys
from typing import Any, TypeVar


class AlfredError(Exception):
    """Base exception with user-friendly messages.

    All Alfred exceptions inherit from this to provide:
    - User-friendly error messages
    - Technical details for debugging
    - Optional recovery suggestions
    """

    def __init__(
        self,
        user_message: str,
        technical_details: str | None = None,
        recovery_suggestions: str | None = None,
    ):
        self.user_message = user_message
        self.technical_details = technical_details or user_message
        self.recovery_suggestions = recovery_suggestions
        super().__init__(self.user_message)

    def to_tool_response_data(self) -> dict[str, Any]:
        """Convert exception to ToolResponse data."""
        data = {"error_type": self.__class__.__name__}
        if self.recovery_suggestions:
            data["recovery_suggestions"] = self.recovery_suggestions
        return data


class ConfigurationError(AlfredError):
    """Configuration-related errors."""

    def __init__(self, config_key: str, issue: str):
        super().__init__(
            user_message=f"Configuration error for '{config_key}': {issue}",
            technical_details=f"Config key '{config_key}' has issue: {issue}",
            recovery_suggestions=(
                f"Check your .alfred/config.json file or environment variables. The '{config_key}' setting needs to be fixed."
            ),
        )
        self.config_key = config_key


class WorkflowError(AlfredError):
    """Workflow execution errors."""

    def __init__(self, message: str, phase: str | None = None):
        recovery = "Check the workflow configuration and ensure all phases are properly defined."
        if phase:
            recovery = f"Check that phase '{phase}' exists in the workflow definition."

        super().__init__(
            user_message=message,
            technical_details=f"Workflow error: {message}",
            recovery_suggestions=recovery,
        )
        self.phase = phase


class ValidationError(AlfredError):
    """Input validation errors."""

    def __init__(self, message: str, field: str | None = None):
        recovery = "Check your input and try again."
        if field:
            recovery = f"Check the value provided for '{field}'."

        super().__init__(
            user_message=message,
            technical_details=f"Validation error: {message}",
            recovery_suggestions=recovery,
        )
        self.field = field


def _get_tool_response() -> type:
    """Lazy import to avoid circular dependencies."""
    from .models.core import ToolResponse

    return ToolResponse


T = TypeVar("T")


def handle_errors(func: T) -> T:
    """Decorator that converts exceptions to proper ToolResponse.

    This decorator:
    - Catches all exceptions and converts them to ToolResponse.error()
    - Converts AlfredError to helpful ToolResponse with recovery suggestions
    - Handles unexpected errors gracefully
    - Preserves async function behavior
    """

    def _handle_exception(
        e: Exception, func_name: str, args: tuple, kwargs: dict
    ) -> type:
        """Unified exception handling logic."""
        tool_response = _get_tool_response()

        if isinstance(e, AlfredError):
            return tool_response.error(
                message=e.user_message,
                next_prompt=e.recovery_suggestions,
                data=e.to_tool_response_data(),
            )

        if isinstance(e, FileNotFoundError):
            file_path = str(e.filename) if hasattr(e, "filename") else str(e)
            return tool_response.error(
                message=f"Required file not found: {file_path}",
                next_prompt="Check that the file exists and the path is correct. If this is an Alfred task, ensure it was created with create_task().",
            )

        if isinstance(e, json.JSONDecodeError | ValueError):
            return tool_response.error(
                message=f"Invalid data format: {e!s}",
                next_prompt="Check that your data is properly formatted. JSON must be valid, and all required fields must be present.",
            )

        return tool_response.error(
            message=f"An unexpected error occurred: {type(e).__name__}: {e!s}",
            data={"error_type": type(e).__name__},
        )

    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs) -> type:
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            return _handle_exception(e, func.__name__, args, kwargs)

    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs) -> type:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return _handle_exception(e, func.__name__, args, kwargs)

    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper


def format_validation_errors(errors: dict[str, list[str]]) -> str:
    """Format validation errors for display."""
    lines = ["Validation failed with the following errors:"]

    for field, field_errors in errors.items():
        lines.append(f"\n{field}:")
        for error in field_errors:
            lines.append(f"  - {error}")

    return "\n".join(lines)


def setup_error_handling() -> None:
    """Setup global error handling for the server."""

    def handle_exception(exc_type, exc_value, exc_traceback) -> None:
        """Global exception handler."""
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        # Just set the hook without logging - let the application handle errors
        sys.__excepthook__(exc_type, exc_value, exc_traceback)

    sys.excepthook = handle_exception
