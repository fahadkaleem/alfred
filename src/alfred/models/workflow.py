"""Workflow state models for dynamic status mapping."""

from datetime import datetime
from typing import Dict, List, Optional, Set
from pydantic import BaseModel, Field


class WorkflowState(BaseModel):
    """Represents a single workflow state from Linear."""

    id: str
    name: str
    type: str  # 'backlog', 'unstarted', 'started', 'completed', 'canceled'
    position: float
    color: str
    description: Optional[str] = None
    team_id: str
    team_name: str

    @property
    def alfred_status(self) -> Optional[str]:
        """Map this workflow state to an Alfred status based on type."""
        type_mapping = {
            "backlog": "pending",
            "unstarted": "pending",
            "started": "in_progress",
            "completed": "done",
            "canceled": "cancelled",
        }
        return type_mapping.get(self.type)


class TeamWorkflowStates(BaseModel):
    """Workflow states for a specific team."""

    team_id: str
    team_name: str
    states: List[WorkflowState]
    discovered_at: datetime = Field(default_factory=datetime.now)

    @property
    def state_names(self) -> List[str]:
        """Get list of state names."""
        return [state.name for state in self.states]

    @property
    def states_by_type(self) -> Dict[str, List[WorkflowState]]:
        """Group states by their type."""
        result = {}
        for state in self.states:
            if state.type not in result:
                result[state.type] = []
            result[state.type].append(state)
        return result

    @property
    def alfred_mappings(self) -> Dict[str, List[str]]:
        """Get Alfred status to Linear state name mappings."""
        mappings = {"pending": [], "in_progress": [], "done": [], "cancelled": []}

        for state in self.states:
            alfred_status = state.alfred_status
            if alfred_status:
                mappings[alfred_status].append(state.name)

        return mappings

    def get_linear_state_for_alfred(self, alfred_status: str) -> Optional[str]:
        """Get the first Linear state name for an Alfred status."""
        mappings = self.alfred_mappings
        states = mappings.get(alfred_status, [])
        return states[0] if states else None

    def get_alfred_status_for_linear(self, linear_state_name: str) -> Optional[str]:
        """Get Alfred status for a Linear state name."""
        for state in self.states:
            if state.name.lower() == linear_state_name.lower():
                return state.alfred_status
        return None


class WorkspaceWorkflowStates(BaseModel):
    """All workflow states across a workspace."""

    teams: Dict[str, TeamWorkflowStates]
    discovered_at: datetime = Field(default_factory=datetime.now)

    @property
    def all_state_names(self) -> Set[str]:
        """Get all unique state names across teams."""
        names = set()
        for team_states in self.teams.values():
            names.update(team_states.state_names)
        return names

    def get_team_states(self, team_id: str) -> Optional[TeamWorkflowStates]:
        """Get workflow states for a specific team."""
        return self.teams.get(team_id)


class WorkflowStateCache(BaseModel):
    """Cached workflow state configuration."""

    workspace_states: WorkspaceWorkflowStates
    cached_at: datetime = Field(default_factory=datetime.now)
    ttl_seconds: int = 3600  # 1 hour default TTL

    @property
    def is_expired(self) -> bool:
        """Check if cache has expired."""
        age = (datetime.now() - self.cached_at).total_seconds()
        return age > self.ttl_seconds
