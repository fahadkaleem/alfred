"""
Tests for the WorkflowStateManager class.

This module tests the functionality of the WorkflowStateManager class,
including workflow state discovery, caching, and status mapping.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime

from alfred.clients.linear import LinearClient
from alfred.clients.linear.domain import LinearState
from alfred.clients.linear.managers.workflow_manager import WorkflowStateManager
from alfred.models.workflow import (
    WorkflowState,
    TeamWorkflowStates,
    WorkspaceWorkflowStates,
)


class TestWorkflowStateManager:
    """Test suite for WorkflowStateManager with mocked dependencies."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock LinearClient instance."""
        client = Mock(spec=LinearClient)
        client.teams = Mock()
        client.cache = Mock()
        return client

    @pytest.fixture
    def manager(self, mock_client):
        """Create a WorkflowStateManager instance with mocked client."""
        return WorkflowStateManager(mock_client)

    @pytest.fixture
    def mock_workflow_states_response(self):
        """Create mock workflow states GraphQL response."""
        return {
            "workflowStates": {
                "nodes": [
                    {
                        "id": "state-1",
                        "name": "Backlog",
                        "type": "backlog",
                        "position": 0,
                        "color": "#bec2c8",
                        "description": None,
                        "team": {"id": "team-1", "name": "Test Team"},
                    },
                    {
                        "id": "state-2",
                        "name": "Todo",
                        "type": "unstarted",
                        "position": 1,
                        "color": "#e2e2e2",
                        "description": "Ready to start",
                        "team": {"id": "team-1", "name": "Test Team"},
                    },
                    {
                        "id": "state-3",
                        "name": "In Progress",
                        "type": "started",
                        "position": 2,
                        "color": "#f2c94c",
                        "description": None,
                        "team": {"id": "team-1", "name": "Test Team"},
                    },
                    {
                        "id": "state-4",
                        "name": "Done",
                        "type": "completed",
                        "position": 3,
                        "color": "#5e6ad2",
                        "description": None,
                        "team": {"id": "team-1", "name": "Test Team"},
                    },
                    {
                        "id": "state-5",
                        "name": "Canceled",
                        "type": "canceled",
                        "position": 4,
                        "color": "#95a2b3",
                        "description": None,
                        "team": {"id": "team-1", "name": "Test Team"},
                    },
                    # State from different team (should be filtered out)
                    {
                        "id": "state-other",
                        "name": "Other Team State",
                        "type": "backlog",
                        "position": 0,
                        "color": "#000000",
                        "description": None,
                        "team": {"id": "team-2", "name": "Other Team"},
                    },
                ]
            }
        }

    def test_discover_team_states_success(self, manager, mock_workflow_states_response):
        """Test successful discovery of team workflow states."""
        # Setup mocks
        manager._cache_get = Mock(return_value=None)  # No cache hit
        manager._cache_set = Mock()
        manager._execute_query = Mock(return_value=mock_workflow_states_response)

        # Execute
        result = manager.discover_team_states("team-1")

        # Verify
        assert isinstance(result, TeamWorkflowStates)
        assert result.team_id == "team-1"
        assert result.team_name == "Test Team"
        assert len(result.states) == 5  # Only states from team-1
        
        # Check state details
        assert result.states[0].name == "Backlog"
        assert result.states[0].type == "backlog"
        assert result.states[0].position == 0
        assert result.states[0].alfred_status == "pending"
        
        assert result.states[2].name == "In Progress"
        assert result.states[2].type == "started"
        assert result.states[2].alfred_status == "in_progress"
        
        # Check state names list
        assert result.state_names == ["Backlog", "Todo", "In Progress", "Done", "Canceled"]
        
        # Check alfred mappings
        assert "Backlog" in result.alfred_mappings["pending"]
        assert "Todo" in result.alfred_mappings["pending"]
        assert "In Progress" in result.alfred_mappings["in_progress"]
        assert "Done" in result.alfred_mappings["done"]
        assert "Canceled" in result.alfred_mappings["cancelled"]
        
        # Verify cache was set
        manager._cache_set.assert_called_once()

    def test_discover_team_states_with_cache(self, manager):
        """Test that cached results are returned when available."""
        # Setup cached data
        cached_data = {
            "team_id": "team-1",
            "team_name": "Cached Team",
            "states": [
                {
                    "id": "cached-1",
                    "name": "Cached State",
                    "type": "backlog",
                    "position": 0,
                    "color": "#000000",
                    "description": None,
                    "team_id": "team-1",
                    "team_name": "Cached Team",
                }
            ],
            "discovered_at": datetime.now().isoformat(),
        }
        
        manager._cache_get = Mock(return_value=cached_data)
        manager._execute_query = Mock()  # Should not be called
        
        # Execute
        result = manager.discover_team_states("team-1")
        
        # Verify
        assert result.team_name == "Cached Team"
        assert len(result.states) == 1
        assert result.states[0].name == "Cached State"
        
        # Verify API was not called
        manager._execute_query.assert_not_called()

    def test_discover_team_states_force_refresh(self, manager, mock_workflow_states_response):
        """Test that force_refresh bypasses cache."""
        # Setup cached data
        cached_data = {"team_id": "team-1", "team_name": "Cached Team"}
        manager._cache_get = Mock(return_value=cached_data)
        manager._cache_set = Mock()
        manager._execute_query = Mock(return_value=mock_workflow_states_response)
        
        # Execute with force_refresh
        result = manager.discover_team_states("team-1", force_refresh=True)
        
        # Verify API was called despite cache
        manager._execute_query.assert_called_once()
        assert result.team_name == "Test Team"  # From API, not cache

    def test_discover_team_states_no_states_found(self, manager):
        """Test error handling when no states are found for team."""
        response = {"workflowStates": {"nodes": []}}
        manager._cache_get = Mock(return_value=None)
        manager._execute_query = Mock(return_value=response)
        
        with pytest.raises(ValueError, match="No workflow states found for team"):
            manager.discover_team_states("team-1")

    def test_discover_team_states_api_error(self, manager):
        """Test error handling when API returns invalid response."""
        manager._cache_get = Mock(return_value=None)
        manager._execute_query = Mock(return_value={})  # Invalid response
        
        with pytest.raises(ValueError, match="Failed to fetch workflow states"):
            manager.discover_team_states("team-1")

    def test_discover_all_teams_states_success(self, manager, mock_workflow_states_response):
        """Test successful discovery of all teams' workflow states."""
        # Mock teams
        mock_teams = {
            "team-1": Mock(name="Test Team", id="team-1"),
            "team-2": Mock(name="Other Team", id="team-2"),
        }
        manager.client.teams.get_all = Mock(return_value=mock_teams)
        
        # Mock discover_team_states to return different states for each team
        def mock_discover(team_id, force_refresh=False):
            if team_id == "team-1":
                return TeamWorkflowStates(
                    team_id="team-1",
                    team_name="Test Team",
                    states=[
                        WorkflowState(
                            id="state-1",
                            name="Backlog",
                            type="backlog",
                            position=0,
                            color="#000",
                            team_id="team-1",
                            team_name="Test Team",
                        )
                    ],
                )
            else:
                return TeamWorkflowStates(
                    team_id="team-2",
                    team_name="Other Team",
                    states=[
                        WorkflowState(
                            id="state-2",
                            name="Todo",
                            type="unstarted",
                            position=0,
                            color="#fff",
                            team_id="team-2",
                            team_name="Other Team",
                        )
                    ],
                )
        
        manager.discover_team_states = Mock(side_effect=mock_discover)
        manager._cache_get = Mock(return_value=None)
        manager._cache_set = Mock()
        
        # Execute
        result = manager.discover_all_teams_states()
        
        # Verify
        assert isinstance(result, WorkspaceWorkflowStates)
        assert len(result.teams) == 2
        assert "team-1" in result.teams
        assert "team-2" in result.teams
        assert result.teams["team-1"].team_name == "Test Team"
        assert result.teams["team-2"].team_name == "Other Team"
        
        # Check all state names
        assert "Backlog" in result.all_state_names
        assert "Todo" in result.all_state_names

    def test_discover_all_teams_states_handles_team_errors(self, manager):
        """Test that errors for individual teams don't break the whole operation."""
        # Mock teams
        mock_teams = {
            "team-1": Mock(name="Good Team", id="team-1"),
            "team-2": Mock(name="Bad Team", id="team-2"),
        }
        manager.client.teams.get_all = Mock(return_value=mock_teams)
        
        # Mock discover_team_states to fail for team-2
        def mock_discover(team_id, force_refresh=False):
            if team_id == "team-1":
                return TeamWorkflowStates(
                    team_id="team-1",
                    team_name="Good Team",
                    states=[
                        WorkflowState(
                            id="state-1",
                            name="Backlog",
                            type="backlog",
                            position=0,
                            color="#000",
                            team_id="team-1",
                            team_name="Good Team",
                        )
                    ],
                )
            else:
                raise Exception("Access denied to team-2")
        
        manager.discover_team_states = Mock(side_effect=mock_discover)
        manager._cache_get = Mock(return_value=None)
        manager._cache_set = Mock()
        
        # Execute (should not raise)
        with patch("builtins.print"):  # Suppress warning prints
            result = manager.discover_all_teams_states()
        
        # Verify only successful team is included
        assert len(result.teams) == 1
        assert "team-1" in result.teams
        assert "team-2" not in result.teams

    def test_get_status_mapper(self, manager, mock_workflow_states_response):
        """Test get_status_mapper convenience method."""
        # Mock discover_team_states
        mock_states = TeamWorkflowStates(
            team_id="team-1",
            team_name="Test Team",
            states=[
                WorkflowState(
                    id="state-1",
                    name="Backlog",
                    type="backlog",
                    position=0,
                    color="#000",
                    team_id="team-1",
                    team_name="Test Team",
                )
            ],
        )
        manager.discover_team_states = Mock(return_value=mock_states)
        
        # Execute
        result = manager.get_status_mapper("team-1")
        
        # Verify
        assert result == mock_states
        manager.discover_team_states.assert_called_once_with("team-1")

    def test_refresh_workflow_cache(self, manager):
        """Test refresh_workflow_cache forces refresh."""
        mock_workspace_states = WorkspaceWorkflowStates(teams={})
        manager.discover_all_teams_states = Mock(return_value=mock_workspace_states)
        
        # Execute
        result = manager.refresh_workflow_cache()
        
        # Verify
        assert result == mock_workspace_states
        manager.discover_all_teams_states.assert_called_once_with(force_refresh=True)


# Integration tests that make real API calls
@pytest.mark.integration
@pytest.mark.requires_linear_api
class TestWorkflowStateManagerIntegration:
    """Integration tests for WorkflowStateManager with real API calls."""

    @pytest.fixture
    def client(self, linear_api_key):
        """Create a real LinearClient instance for testing."""
        if not linear_api_key:
            pytest.skip("LINEAR_API_KEY environment variable not set")
        return LinearClient(api_key=linear_api_key)

    @pytest.fixture
    def manager(self, client):
        """Create a WorkflowStateManager instance with real client."""
        return client.workflow_states

    def test_discover_team_states_real_api(self, manager, test_team_name):
        """Test discovering workflow states with real Linear API."""
        # Get team ID
        team_id = manager.client.teams.get_id_by_name(test_team_name)
        
        # Discover states
        result = manager.discover_team_states(team_id)
        
        # Verify
        assert isinstance(result, TeamWorkflowStates)
        assert result.team_id == team_id
        assert result.team_name == test_team_name
        assert len(result.states) > 0
        
        # Check that we have standard workflow state types
        state_types = {state.type for state in result.states}
        assert "backlog" in state_types or "unstarted" in state_types
        assert "started" in state_types
        assert "completed" in state_types
        assert "canceled" in state_types
        
        # Test status mapping
        assert result.get_linear_state_for_alfred("pending") is not None
        assert result.get_linear_state_for_alfred("in_progress") is not None
        assert result.get_linear_state_for_alfred("done") is not None
        assert result.get_linear_state_for_alfred("cancelled") is not None

    def test_discover_all_teams_states_real_api(self, manager):
        """Test discovering all teams' workflow states with real API."""
        # Discover all states
        result = manager.discover_all_teams_states()
        
        # Verify
        assert isinstance(result, WorkspaceWorkflowStates)
        assert len(result.teams) > 0
        assert len(result.all_state_names) > 0
        
        # Check that each team has states
        for team_id, team_states in result.teams.items():
            assert isinstance(team_states, TeamWorkflowStates)
            assert len(team_states.states) > 0
            assert team_states.team_id == team_id

    def test_caching_real_api(self, manager, test_team_name):
        """Test that caching works with real API calls."""
        import time
        
        # Get team ID
        team_id = manager.client.teams.get_id_by_name(test_team_name)
        
        # First call - should hit API
        start = time.time()
        result1 = manager.discover_team_states(team_id)
        time1 = time.time() - start
        
        # Second call - should use cache
        start = time.time()
        result2 = manager.discover_team_states(team_id)
        time2 = time.time() - start
        
        # Verify results are the same
        assert result1.team_id == result2.team_id
        assert result1.state_names == result2.state_names
        
        # Cache should be significantly faster (at least 2x)
        assert time2 < time1 / 2
        
        # Force refresh should take similar time to first call
        start = time.time()
        result3 = manager.discover_team_states(team_id, force_refresh=True)
        time3 = time.time() - start
        
        # Should be slower than cached call
        assert time3 > time2