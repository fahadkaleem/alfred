"""Utility functions and types for Alfred MCP server."""

import os
import logging
from typing import TypeAlias, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

# Type aliases
SessionId: TypeAlias = str
WorkspacePath: TypeAlias = str
TaskId: TypeAlias = str


# Configure logging
def get_logger(name: str) -> logging.Logger:
    """
    Get a configured logger for the given name.

    Args:
        name: Logger name (typically module name)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Only configure if not already configured
    if not logger.handlers:
        # Get log level from environment or default to INFO
        log_level = os.environ.get("ALFRED_LOG_LEVEL", "INFO").upper()
        logger.setLevel(getattr(logging, log_level, logging.INFO))

        # Create console handler with formatting
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s %(levelname)s %(name)s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        # Prevent propagation to avoid duplicate logs
        logger.propagate = False

    return logger


# Session management types
@dataclass
class SessionContext:
    """Context for a session in the Alfred MCP server."""

    session_id: SessionId
    workspace_path: WorkspacePath
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    def update_metadata(self, key: str, value: Any) -> None:
        """Update metadata for the session."""
        self.metadata[key] = value


# Error types for Alfred
class AlfredError(Exception):
    """Base exception for Alfred-specific errors."""

    def __init__(
        self, message: str, code: int = -32000, data: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.data = data or {}


class BadRequestError(AlfredError):
    """Error for bad/invalid requests."""

    def __init__(self, message: str, data: Optional[Dict[str, Any]] = None):
        super().__init__(message, code=-32602, data=data)


class NotFoundError(AlfredError):
    """Error for resources not found."""

    def __init__(self, message: str, data: Optional[Dict[str, Any]] = None):
        super().__init__(message, code=-32004, data=data)


class ExternalServiceError(AlfredError):
    """Error for external service failures (Linear/Jira/AI)."""

    def __init__(self, message: str, data: Optional[Dict[str, Any]] = None):
        super().__init__(message, code=-32011, data=data)


def to_mcp_error(exc: Exception) -> Dict[str, Any]:
    """
    Convert an exception to an MCP-compliant error dictionary.

    Args:
        exc: The exception to convert

    Returns:
        MCP error dictionary with code, message, and data
    """
    if isinstance(exc, AlfredError):
        return {"code": exc.code, "message": exc.message, "data": exc.data}

    # Unknown exceptions map to internal error
    return {"code": -32603, "message": str(exc), "data": {"type": type(exc).__name__}}


class SessionManager:
    """Manages session contexts for the Alfred MCP server."""

    def __init__(self):
        """Initialize the session manager."""
        self._contexts: Dict[SessionId, SessionContext] = {}
        self._logger = get_logger("alfred.utils.session")

    def start_session(
        self, session_id: SessionId, workspace_path: Optional[WorkspacePath] = None
    ) -> SessionContext:
        """
        Start a new session with the given ID and workspace.

        Args:
            session_id: Unique session identifier
            workspace_path: Optional workspace path (defaults to cwd or env)

        Returns:
            Created session context

        Raises:
            BadRequestError: If workspace path doesn't exist
        """
        # Determine workspace path
        if workspace_path is None:
            workspace_path = os.environ.get("ALFRED_WORKSPACE", os.getcwd())

        # Normalize and validate path
        workspace_path = os.path.abspath(workspace_path)
        if not os.path.exists(workspace_path):
            raise BadRequestError(
                f"Workspace path does not exist: {workspace_path}",
                data={"path": workspace_path},
            )

        # Create and store context
        context = SessionContext(session_id=session_id, workspace_path=workspace_path)
        self._contexts[session_id] = context

        self._logger.info(
            f"Started session {session_id} with workspace {workspace_path}"
        )

        return context

    def get(self, session_id: SessionId) -> SessionContext:
        """
        Get session context by ID.

        Args:
            session_id: Session identifier

        Returns:
            Session context

        Raises:
            NotFoundError: If session doesn't exist
        """
        if session_id not in self._contexts:
            raise NotFoundError(
                f"Session not found: {session_id}", data={"session_id": session_id}
            )

        return self._contexts[session_id]

    def update_workspace(self, session_id: SessionId, new_path: WorkspacePath) -> None:
        """
        Update the workspace path for a session.

        Args:
            session_id: Session identifier
            new_path: New workspace path

        Raises:
            NotFoundError: If session doesn't exist
            BadRequestError: If new path doesn't exist
        """
        context = self.get(session_id)

        # Validate new path
        new_path = os.path.abspath(new_path)
        if not os.path.exists(new_path):
            raise BadRequestError(
                f"Workspace path does not exist: {new_path}", data={"path": new_path}
            )

        old_path = context.workspace_path
        context.workspace_path = new_path

        self._logger.info(
            f"Updated session {session_id} workspace from {old_path} to {new_path}"
        )

    def end_session(self, session_id: SessionId) -> None:
        """
        End a session and remove its context.

        Args:
            session_id: Session identifier
        """
        if session_id in self._contexts:
            del self._contexts[session_id]
            self._logger.info(f"Ended session {session_id}")
        else:
            self._logger.warning(f"Attempted to end non-existent session {session_id}")

    def list_sessions(self) -> Dict[SessionId, SessionContext]:
        """
        Get all active sessions.

        Returns:
            Dictionary of session IDs to contexts
        """
        return self._contexts.copy()
