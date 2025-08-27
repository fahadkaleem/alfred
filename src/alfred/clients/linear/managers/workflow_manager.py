"""
Workflow state manager for Linear API.

This module provides the WorkflowStateManager class for discovering and managing
workflow states across teams.
"""

from typing import Dict, List, Optional
from datetime import datetime

from .base_manager import BaseManager
from ..domain import LinearState
from alfred.models.workflow import (
    WorkflowState,
    TeamWorkflowStates, 
    WorkspaceWorkflowStates,
    WorkflowStateCache
)


class WorkflowStateManager(BaseManager[LinearState]):
    """
    Manager for workflow state discovery and mapping.
    
    This class provides methods for discovering workflow states across teams
    and managing the mapping between Linear and Alfred statuses.
    """
    
    def discover_team_states(self, team_id: str, force_refresh: bool = False) -> TeamWorkflowStates:
        """
        Discover all workflow states for a specific team.
        
        This method fetches all workflow states configured for a team,
        providing the foundation for dynamic status mapping.
        
        Args:
            team_id: The ID of the team to fetch states for
            force_refresh: Force refreshing the cache
            
        Returns:
            TeamWorkflowStates object with all states for the team
            
        Raises:
            ValueError: If the team doesn't exist or has no states
        """
        # Check cache first if not forcing refresh
        cache_key = f"workflow_states_{team_id}"
        if not force_refresh:
            cached = self._cache_get("workflow_discovery", cache_key)
            if cached:
                return TeamWorkflowStates(**cached)
        
        # Query to get all workflow states
        query = """
        query GetWorkflowStates {
            workflowStates {
                nodes {
                    id
                    name
                    type
                    position
                    color
                    description
                    team {
                        id
                        name
                    }
                }
            }
        }
        """
        
        result = self._execute_query(query, {})
        
        if not result or "workflowStates" not in result:
            raise ValueError("Failed to fetch workflow states from Linear API")
        
        all_states = result["workflowStates"].get("nodes", [])
        
        # Filter states for the specific team
        team_states = [
            state for state in all_states 
            if state.get("team", {}).get("id") == team_id
        ]
        
        if not team_states:
            raise ValueError(f"No workflow states found for team {team_id}")
        
        # Get team name from first state
        team_name = team_states[0]["team"]["name"] if team_states else "Unknown"
        
        # Sort states by position for consistent ordering
        team_states.sort(key=lambda s: s.get("position", 0))
        
        # Convert to WorkflowState models
        workflow_states = []
        for state in team_states:
            workflow_states.append(WorkflowState(
                id=state["id"],
                name=state["name"],
                type=state["type"],
                position=state.get("position", 0),
                color=state.get("color", ""),
                description=state.get("description"),
                team_id=team_id,
                team_name=team_name
            ))
        
        result = TeamWorkflowStates(
            team_id=team_id,
            team_name=team_name,
            states=workflow_states
        )
        
        # Cache the result
        self._cache_set("workflow_discovery", cache_key, result.model_dump())
        
        return result
    
    def discover_all_teams_states(self, force_refresh: bool = False) -> WorkspaceWorkflowStates:
        """
        Discover workflow states across all accessible teams.
        
        This method fetches workflow states for all teams in the workspace,
        providing a complete picture of available states.
        
        Args:
            force_refresh: Force refreshing the cache
            
        Returns:
            WorkspaceWorkflowStates object with states for all teams
        """
        # Check cache first
        cache_key = "all_workflow_states"
        if not force_refresh:
            cached = self._cache_get("workflow_discovery", cache_key)
            if cached:
                # Reconstruct the models from cached data
                teams = {}
                for team_id, team_data in cached.get("teams", {}).items():
                    teams[team_id] = TeamWorkflowStates(**team_data)
                return WorkspaceWorkflowStates(
                    teams=teams,
                    discovered_at=datetime.fromisoformat(cached["discovered_at"])
                )
        
        # Get all teams
        teams = self.client.teams.get_all()
        workspace_teams = {}
        
        for team_id, team in teams.items():
            try:
                team_states = self.discover_team_states(team_id, force_refresh)
                workspace_teams[team_id] = team_states
            except Exception as e:
                # Log but continue for teams we can't access
                print(f"Warning: Could not fetch workflow states for team {team.name}: {e}")
                continue
        
        result = WorkspaceWorkflowStates(teams=workspace_teams)
        
        # Cache the result
        cache_data = {
            "teams": {tid: ts.model_dump() for tid, ts in workspace_teams.items()},
            "discovered_at": result.discovered_at.isoformat()
        }
        self._cache_set("workflow_discovery", cache_key, cache_data)
        
        return result
    
    def get_status_mapper(self, team_id: str) -> TeamWorkflowStates:
        """
        Get a status mapper for a specific team.
        
        This is a convenience method that returns the team's workflow states
        which can be used for status mapping.
        
        Args:
            team_id: The team ID to get the mapper for
            
        Returns:
            TeamWorkflowStates object that provides mapping methods
        """
        return self.discover_team_states(team_id)
    
    def refresh_workflow_cache(self) -> WorkspaceWorkflowStates:
        """
        Force refresh the workflow state cache.
        
        This method forces a refresh of all workflow states,
        useful when workflow configurations change.
        
        Returns:
            Updated WorkspaceWorkflowStates
        """
        return self.discover_all_teams_states(force_refresh=True)