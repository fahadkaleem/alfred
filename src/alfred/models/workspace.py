"""Workspace-related Pydantic models."""

from typing import Optional, List
from pydantic import BaseModel, Field


class WorkspaceInfo(BaseModel):
    """Workspace information model."""

    id: str = Field(..., description="Workspace/organization ID")
    name: str = Field(..., description="Workspace name")


class TeamInfo(BaseModel):
    """Team information model."""

    id: str = Field(..., description="Team ID")
    name: str = Field(..., description="Team name")
    description: Optional[str] = Field(None, description="Team description")
    key: Optional[str] = Field(None, description="Team key/abbreviation")


class ProjectInfo(BaseModel):
    """Project/Epic information model."""

    id: str = Field(..., description="Project ID")
    name: str = Field(..., description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    url: Optional[str] = Field(None, description="Project URL")


class WorkspaceInitResponse(BaseModel):
    """Response model for workspace initialization."""

    status: str = Field("ok", description="Operation status")
    message: str = Field(..., description="Success/error message")
    platform: str = Field("linear", description="Platform name")
    workspace: WorkspaceInfo
    team: TeamInfo
    config_path: str = Field(".alfred/config.json", description="Config file path")


class WorkspaceStatusResponse(BaseModel):
    """Response model for workspace status check."""

    status: str = Field(
        ..., description="Configuration status (configured/not_configured)"
    )
    connection_status: Optional[str] = Field(None, description="Connection status")
    platform: str = Field("linear", description="Platform name")
    workspace: Optional[WorkspaceInfo] = None
    team: Optional[TeamInfo] = None
    active_epic_id: Optional[str] = None
    has_api_key: bool = False
    has_ai_config: bool = False
    message: Optional[str] = None


class TeamsListResponse(BaseModel):
    """Response model for teams listing."""

    status: str = Field("ok", description="Operation status")
    teams: List[TeamInfo] = Field(default_factory=list)
    count: int = Field(..., description="Number of teams")


class ProjectsListResponse(BaseModel):
    """Response model for projects listing."""

    status: str = Field("ok", description="Operation status")
    projects: List[ProjectInfo] = Field(default_factory=list)
    count: int = Field(..., description="Number of projects")
