"""Alfred data models using Pydantic v2."""

from .workspace import (
    WorkspaceInfo,
    TeamInfo,
    ProjectInfo,
    WorkspaceInitResponse,
    WorkspaceStatusResponse,
    TeamsListResponse,
    ProjectsListResponse,
)

from .config import Config, Platform, AIProvider
from .tasks import (
    AlfredTask,
    AlfredTaskStatus,
    TaskListResult,
    WorkspaceConfig,
    map_status_linear_to_alfred,
    map_status_alfred_to_linear,
    to_alfred_task,
)

__all__ = [
    # Workspace models
    "WorkspaceInfo",
    "TeamInfo",
    "ProjectInfo",
    "WorkspaceInitResponse",
    "WorkspaceStatusResponse",
    "TeamsListResponse",
    "ProjectsListResponse",
    # Config models
    "Config",
    "Platform",
    "AIProvider",
    # Task models
    "AlfredTask",
    "AlfredTaskStatus", 
    "TaskListResult",
    "WorkspaceConfig",
    "map_status_linear_to_alfred",
    "map_status_alfred_to_linear",
    "to_alfred_task",
]
