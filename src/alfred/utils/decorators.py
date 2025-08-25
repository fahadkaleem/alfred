"""Decorators for error handling and context management."""

import functools
import inspect
from typing import Callable, Any, Optional, TypeVar, ParamSpec
from fastmcp import Context

from alfred.utils import (
    get_logger,
    AlfredError,
    BadRequestError,
    NotFoundError,
    SessionManager,
    SessionContext,
)

P = ParamSpec("P")
T = TypeVar("T")

logger = get_logger("alfred.utils.decorators")


def error_guard(func: Callable[P, T]) -> Callable[P, T]:
    """
    Decorator to wrap functions with error handling.

    Catches exceptions and converts them to MCP-compliant errors.
    Logs errors with full context.

    Args:
        func: Function to wrap

    Returns:
        Wrapped function with error handling
    """

    @functools.wraps(func)
    async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        """Async wrapper with error handling."""
        try:
            logger.debug(f"Executing {func.__name__}")
            result = await func(*args, **kwargs)
            logger.debug(f"{func.__name__} completed successfully")
            return result
        except AlfredError as e:
            # Alfred-specific errors - log and re-raise
            logger.error(f"{func.__name__} failed with {type(e).__name__}: {e.message}")
            raise
        except Exception as e:
            # Unexpected errors - log with stack trace and convert
            logger.error(f"{func.__name__} failed with unexpected error", exc_info=True)
            # Convert to Alfred error for consistent handling
            raise AlfredError(
                message=f"Internal error in {func.__name__}: {str(e)}",
                code=-32603,
                data={"function": func.__name__, "error_type": type(e).__name__},
            )

    @functools.wraps(func)
    def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        """Sync wrapper with error handling."""
        try:
            logger.debug(f"Executing {func.__name__}")
            result = func(*args, **kwargs)
            logger.debug(f"{func.__name__} completed successfully")
            return result
        except AlfredError as e:
            # Alfred-specific errors - log and re-raise
            logger.error(f"{func.__name__} failed with {type(e).__name__}: {e.message}")
            raise
        except Exception as e:
            # Unexpected errors - log with stack trace and convert
            logger.error(f"{func.__name__} failed with unexpected error", exc_info=True)
            # Convert to Alfred error for consistent handling
            raise AlfredError(
                message=f"Internal error in {func.__name__}: {str(e)}",
                code=-32603,
                data={"function": func.__name__, "error_type": type(e).__name__},
            )

    # Return appropriate wrapper based on function type
    if inspect.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper


def with_session_context(func: Callable[P, T]) -> Callable[P, T]:
    """
    Decorator to inject session context into tool functions.

    Extracts session ID from the FastMCP context and provides
    the SessionContext as a keyword argument.

    The decorated function should accept a 'session_context' keyword argument.

    Args:
        func: Function to wrap

    Returns:
        Wrapped function with session context injection
    """

    @functools.wraps(func)
    async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        """Async wrapper with session context injection."""
        # Look for Context in arguments
        context = None
        for arg in args:
            if isinstance(arg, Context):
                context = arg
                break

        # Also check kwargs
        if context is None:
            context = kwargs.get("ctx") or kwargs.get("context")

        if context is None:
            raise BadRequestError(
                "No MCP context available for session management",
                data={"function": func.__name__},
            )

        # Get session manager from server state
        server = context.server
        if not hasattr(server, "state") or "session_manager" not in server.state:
            raise BadRequestError(
                "Session manager not initialized", data={"function": func.__name__}
            )

        session_manager: SessionManager = server.state["session_manager"]

        # Extract session ID from context
        # This depends on FastMCP's context structure
        session_id = getattr(context, "session_id", None)
        if session_id is None:
            # Try to get from request metadata
            if hasattr(context, "request"):
                session_id = context.request.get("session_id")

        if session_id is None:
            raise BadRequestError(
                "No session ID in context", data={"function": func.__name__}
            )

        # Get session context
        try:
            session_context = session_manager.get(session_id)
        except NotFoundError:
            # Auto-create session if it doesn't exist
            logger.warning(f"Auto-creating session for {session_id}")
            session_context = session_manager.start_session(session_id)

        # Inject session context as kwarg
        kwargs["session_context"] = session_context

        # Call the wrapped function
        if inspect.iscoroutinefunction(func):
            return await func(*args, **kwargs)
        else:
            return func(*args, **kwargs)

    @functools.wraps(func)
    def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        """Sync wrapper with session context injection."""
        # Look for Context in arguments
        context = None
        for arg in args:
            if isinstance(arg, Context):
                context = arg
                break

        # Also check kwargs
        if context is None:
            context = kwargs.get("ctx") or kwargs.get("context")

        if context is None:
            raise BadRequestError(
                "No MCP context available for session management",
                data={"function": func.__name__},
            )

        # Get session manager from server state
        server = context.server
        if not hasattr(server, "state") or "session_manager" not in server.state:
            raise BadRequestError(
                "Session manager not initialized", data={"function": func.__name__}
            )

        session_manager: SessionManager = server.state["session_manager"]

        # Extract session ID from context
        session_id = getattr(context, "session_id", None)
        if session_id is None:
            # Try to get from request metadata
            if hasattr(context, "request"):
                session_id = context.request.get("session_id")

        if session_id is None:
            raise BadRequestError(
                "No session ID in context", data={"function": func.__name__}
            )

        # Get session context
        try:
            session_context = session_manager.get(session_id)
        except NotFoundError:
            # Auto-create session if it doesn't exist
            logger.warning(f"Auto-creating session for {session_id}")
            session_context = session_manager.start_session(session_id)

        # Inject session context as kwarg
        kwargs["session_context"] = session_context

        # Call the wrapped function
        return func(*args, **kwargs)

    # Return appropriate wrapper based on function type
    if inspect.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper


def require_linear_config(func: Callable[P, T]) -> Callable[P, T]:
    """
    Decorator to ensure Linear configuration is available.

    Args:
        func: Function to wrap

    Returns:
        Wrapped function that checks Linear config
    """

    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        """Wrapper that checks Linear configuration."""
        from alfred.config import get_config

        config = get_config()

        if not config.linear_api_key:
            raise BadRequestError(
                "Linear API key not configured",
                data={"function": func.__name__, "required": "LINEAR_API_KEY"},
            )

        return func(*args, **kwargs)

    return wrapper


def require_jira_config(func: Callable[P, T]) -> Callable[P, T]:
    """
    Decorator to ensure Jira configuration is available.

    Args:
        func: Function to wrap

    Returns:
        Wrapped function that checks Jira config
    """

    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        """Wrapper that checks Jira configuration."""
        from alfred.config import get_config

        config = get_config()

        if not (config.jira_api_key and config.jira_url):
            raise BadRequestError(
                "Jira configuration not available",
                data={
                    "function": func.__name__,
                    "required": ["JIRA_API_KEY", "JIRA_URL"],
                },
            )

        return func(*args, **kwargs)

    return wrapper


def require_ai_config(func: Callable[P, T]) -> Callable[P, T]:
    """
    Decorator to ensure AI configuration is available.

    Args:
        func: Function to wrap

    Returns:
        Wrapped function that checks AI config
    """

    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        """Wrapper that checks AI configuration."""
        from alfred.config import get_config

        config = get_config()

        if not config.anthropic_api_key:
            raise BadRequestError(
                "AI provider not configured",
                data={"function": func.__name__, "required": "ANTHROPIC_API_KEY"},
            )

        return func(*args, **kwargs)

    return wrapper


# Export decorators
__all__ = [
    "error_guard",
    "with_session_context",
    "require_linear_config",
    "require_jira_config",
    "require_ai_config",
]
