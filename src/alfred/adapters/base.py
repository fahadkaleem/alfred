"""Base adapter interface and shared types for task management platforms."""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union, TypedDict


class TaskDict(TypedDict, total=False):
    """Normalized task structure shared across all adapters."""

    id: str
    title: str
    description: Optional[str]
    status: Optional[str]
    epic_id: Optional[str]
    parent_id: Optional[str]
    url: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]


class EpicDict(TypedDict, total=False):
    """Normalized epic structure shared across all adapters."""

    id: str
    name: str
    description: Optional[str]
    url: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]


class AdapterError(Exception):
    """Base exception for all adapter errors."""

    pass


class AuthError(AdapterError):
    """Authentication or authorization failure."""

    pass


class NotFoundError(AdapterError):
    """Resource not found."""

    pass


class ValidationError(AdapterError):
    """Invalid input or validation failure."""

    pass


class RateLimitError(AdapterError):
    """API rate limit exceeded."""

    def __init__(
        self, message: str = "Rate limit exceeded", retry_after: Optional[int] = None
    ):
        super().__init__(message)
        self.retry_after = retry_after


class APIConnectionError(AdapterError):
    """Network or connection failure."""

    pass


class APIResponseError(AdapterError):
    """API returned an error response."""

    pass


class MappingError(AdapterError):
    """Failed to map data between systems."""

    pass


class TaskAdapter(ABC):
    """Abstract base class for task management adapters.

    All adapters must implement these methods to ensure consistent behavior
    across different backends (Linear, Jira, etc.).
    """

    @abstractmethod
    def create_task(
        self,
        title: str,
        description: Optional[str] = None,
        epic_id: Optional[str] = None,
    ) -> TaskDict:
        """Create a new task.

        Args:
            title: Task title (required)
            description: Task description
            epic_id: ID of the epic/project to add the task to

        Returns:
            TaskDict with created task information

        Raises:
            ValidationError: If title is empty or invalid
            AuthError: If not authenticated
            APIConnectionError: If network fails
            APIResponseError: If API returns error
        """
        pass

    @abstractmethod
    def get_tasks(
        self,
        epic_id: Optional[str] = None,
        status: Optional[Union[str, List[str]]] = None,
        limit: int = 50,
    ) -> List[TaskDict]:
        """Get tasks with optional filtering.

        Args:
            epic_id: Filter by epic/project ID
            status: Filter by status (single or multiple)
            limit: Maximum number of tasks to return

        Returns:
            List of TaskDict objects

        Raises:
            AuthError: If not authenticated
            APIConnectionError: If network fails
            APIResponseError: If API returns error
        """
        pass

    @abstractmethod
    def get_task(self, task_id: str) -> TaskDict:
        """Get a specific task by ID.

        Args:
            task_id: Task identifier

        Returns:
            TaskDict with task information

        Raises:
            NotFoundError: If task doesn't exist
            AuthError: If not authenticated
            APIConnectionError: If network fails
        """
        pass

    @abstractmethod
    def update_task(self, task_id: str, updates: Dict[str, Any]) -> TaskDict:
        """Update a task with new values.

        Args:
            task_id: Task identifier
            updates: Dictionary of fields to update (title, description, status)

        Returns:
            Updated TaskDict

        Raises:
            NotFoundError: If task doesn't exist
            ValidationError: If updates are invalid
            AuthError: If not authenticated
            APIConnectionError: If network fails
        """
        pass

    @abstractmethod
    def create_subtask(
        self, parent_id: str, title: str, description: Optional[str] = None
    ) -> TaskDict:
        """Create a subtask under a parent task.

        Args:
            parent_id: Parent task ID
            title: Subtask title
            description: Subtask description

        Returns:
            Created subtask as TaskDict

        Raises:
            NotFoundError: If parent task doesn't exist
            ValidationError: If title is empty
            AuthError: If not authenticated
            APIConnectionError: If network fails
        """
        pass

    @abstractmethod
    def delete_task(self, task_id: str) -> bool:
        """Delete a task.

        Args:
            task_id: Task identifier

        Returns:
            True if deletion was successful

        Raises:
            NotFoundError: If task doesn't exist
            AuthError: If not authenticated
            APIConnectionError: If network fails
        """
        pass

    @abstractmethod
    def create_epic(self, name: str, description: Optional[str] = None) -> EpicDict:
        """Create a new epic/project.

        Args:
            name: Epic name
            description: Epic description

        Returns:
            Created epic as EpicDict

        Raises:
            ValidationError: If name is empty
            AuthError: If not authenticated
            APIConnectionError: If network fails
        """
        pass

    @abstractmethod
    def get_epics(self, limit: int = 50) -> List[EpicDict]:
        """Get list of epics/projects.

        Args:
            limit: Maximum number of epics to return

        Returns:
            List of EpicDict objects

        Raises:
            AuthError: If not authenticated
            APIConnectionError: If network fails
        """
        pass

    @abstractmethod
    def link_tasks(self, task_id: str, depends_on_id: str) -> bool:
        """Create a dependency relationship between tasks.

        Args:
            task_id: Task that depends on another
            depends_on_id: Task that blocks the first one

        Returns:
            True if link was created successfully

        Raises:
            NotFoundError: If either task doesn't exist
            ValidationError: If circular dependency would be created
            AuthError: If not authenticated
            APIConnectionError: If network fails
        """
        pass

    @abstractmethod
    def get_task_children(self, parent_id: str) -> List[TaskDict]:
        """Get all subtasks of a parent task.

        Args:
            parent_id: Parent task ID

        Returns:
            List of child tasks as TaskDict objects

        Raises:
            NotFoundError: If parent task doesn't exist
            AuthError: If not authenticated
        """
        pass

    @abstractmethod
    def rename_epic(self, epic_id: str, new_name: str) -> EpicDict:
        """Rename an epic/project.

        Args:
            epic_id: Epic/project ID
            new_name: New name for the epic

        Returns:
            Updated epic as EpicDict

        Raises:
            NotFoundError: If epic doesn't exist
            ValidationError: If new name is invalid or already exists
            AuthError: If not authenticated
        """
        pass

    @abstractmethod
    def delete_epic(self, epic_id: str) -> bool:
        """Delete/archive an epic.

        Args:
            epic_id: Epic/project ID to delete

        Returns:
            True if deletion was successful

        Raises:
            NotFoundError: If epic doesn't exist
            AuthError: If not authenticated
        """
        pass

    @abstractmethod
    def get_epic_tasks(self, epic_id: str) -> List[TaskDict]:
        """Get all tasks in an epic/project.

        Args:
            epic_id: Epic/project ID

        Returns:
            List of tasks in the epic

        Raises:
            NotFoundError: If epic doesn't exist
            AuthError: If not authenticated
        """
        pass

    @abstractmethod
    def get_workflow_states(self, team_id: Optional[str] = None) -> Dict[str, Any]:
        """Get workflow states for a team.

        Args:
            team_id: Optional team ID. If not provided, uses default team

        Returns:
            Dictionary with workflow states and metadata

        Raises:
            NotFoundError: If team doesn't exist
            AuthError: If not authenticated
        """
        pass
