"""Unit tests for workspace initialization logic."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from alfred.core.workspace.initialize import initialize_workspace_logic
from alfred.adapters.base import AuthError, ValidationError


@pytest.mark.asyncio
async def test_initialize_workspace_success():
    """Test successful workspace initialization."""
    with patch("alfred.core.workspace.initialize.LinearAdapter") as MockAdapter:
        # Setup mock
        mock_team = Mock()
        mock_team.id = "team-1"
        mock_team.name = "Test Team"

        mock_teams = {"team-1": mock_team}
        MockAdapter.return_value.client.teams.get_all.return_value = mock_teams

        # Mock set_active_workspace
        with patch("alfred.core.workspace.initialize.set_active_workspace") as mock_set:
            mock_set.return_value = {"workspace_id": "ws-1", "team_id": "team-1"}

            # Call the function
            result = await initialize_workspace_logic(
                workspace_id="ws-1", team_id="team-1", api_key="test-key"
            )

            # Assertions
            assert result["status"] == "ok"
            assert result["workspace"]["id"] == "ws-1"
            assert result["team"]["id"] == "team-1"
            assert result["team"]["name"] == "Test Team"

            # Verify LinearAdapter was called with correct API key
            MockAdapter.assert_called_once_with(api_token="test-key")

            # Verify set_active_workspace was called
            mock_set.assert_called_once_with(workspace_id="ws-1", team_id="team-1")


@pytest.mark.asyncio
async def test_initialize_workspace_missing_inputs():
    """Test validation error for missing inputs."""
    with pytest.raises(
        ValidationError, match="Both workspace_id and team_id are required"
    ):
        await initialize_workspace_logic(
            workspace_id="", team_id="team-1", api_key="test-key"
        )

    with pytest.raises(
        ValidationError, match="Both workspace_id and team_id are required"
    ):
        await initialize_workspace_logic(
            workspace_id="ws-1", team_id="", api_key="test-key"
        )


@pytest.mark.asyncio
async def test_initialize_workspace_missing_api_key():
    """Test auth error for missing API key."""
    with pytest.raises(AuthError, match="LINEAR_API_KEY not configured"):
        await initialize_workspace_logic(
            workspace_id="ws-1", team_id="team-1", api_key=""
        )


@pytest.mark.asyncio
async def test_initialize_workspace_team_not_found():
    """Test validation error when team is not found."""
    with patch("alfred.core.workspace.initialize.LinearAdapter") as MockAdapter:
        # Setup mock with no matching team
        mock_team = Mock()
        mock_team.id = "other-team"
        mock_team.name = "Other Team"

        mock_teams = {"other-team": mock_team}
        MockAdapter.return_value.client.teams.get_all.return_value = mock_teams

        # Call the function and expect ValidationError
        with pytest.raises(ValidationError, match="Team 'team-1' not found"):
            await initialize_workspace_logic(
                workspace_id="ws-1", team_id="team-1", api_key="test-key"
            )


@pytest.mark.asyncio
async def test_initialize_workspace_invalid_api_key():
    """Test auth error for invalid API key."""
    with patch("alfred.core.workspace.initialize.LinearAdapter") as MockAdapter:
        # Make LinearAdapter raise an exception indicating auth failure
        MockAdapter.return_value.client.teams.get_all.side_effect = Exception(
            "401 Unauthorized"
        )

        # Call the function and expect AuthError
        with pytest.raises(AuthError, match="Invalid Linear API key"):
            await initialize_workspace_logic(
                workspace_id="ws-1", team_id="team-1", api_key="invalid-key"
            )
