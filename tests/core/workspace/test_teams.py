"""Unit tests for teams listing logic."""

import pytest
from unittest.mock import Mock, patch
from alfred.core.workspace.teams import list_teams_logic
from alfred.adapters.base import AuthError, APIConnectionError


@pytest.mark.asyncio
async def test_list_teams_success():
    """Test successful teams listing."""
    with patch("alfred.core.workspace.teams.LinearAdapter") as MockAdapter:
        # Setup mock teams
        mock_team1 = Mock()
        mock_team1.id = "team-1"
        mock_team1.name = "Engineering"
        mock_team1.description = "Engineering team"
        mock_team1.key = "ENG"

        mock_team2 = Mock()
        mock_team2.id = "team-2"
        mock_team2.name = "Product"
        mock_team2.description = None
        mock_team2.key = "PROD"

        mock_teams = {"team-1": mock_team1, "team-2": mock_team2}

        MockAdapter.return_value.client.teams.get_all.return_value = mock_teams

        # Call the function
        result = await list_teams_logic(api_key="test-key")

        # Assertions
        assert result["status"] == "ok"
        assert result["count"] == 2
        assert len(result["teams"]) == 2

        # Check first team
        team1 = next(t for t in result["teams"] if t["id"] == "team-1")
        assert team1["name"] == "Engineering"
        assert team1["description"] == "Engineering team"
        assert team1["key"] == "ENG"

        # Check second team
        team2 = next(t for t in result["teams"] if t["id"] == "team-2")
        assert team2["name"] == "Product"
        assert team2["description"] is None  # None value is included
        assert team2["key"] == "PROD"

        # Verify LinearAdapter was called correctly
        MockAdapter.assert_called_once_with(api_token="test-key")


@pytest.mark.asyncio
async def test_list_teams_missing_api_key():
    """Test error when API key is missing."""
    with pytest.raises(AuthError, match="LINEAR_API_KEY not configured"):
        await list_teams_logic(api_key="")

    with pytest.raises(AuthError, match="LINEAR_API_KEY not configured"):
        await list_teams_logic(api_key=None)


@pytest.mark.asyncio
async def test_list_teams_invalid_api_key():
    """Test handling of invalid API key."""
    with patch("alfred.core.workspace.teams.LinearAdapter") as MockAdapter:
        # Simulate 401 unauthorized error
        MockAdapter.return_value.client.teams.get_all.side_effect = Exception(
            "401 Unauthorized"
        )

        with pytest.raises(AuthError, match="Invalid Linear API key"):
            await list_teams_logic(api_key="invalid-key")


@pytest.mark.asyncio
async def test_list_teams_network_error():
    """Test handling of network errors."""
    with patch("alfred.core.workspace.teams.LinearAdapter") as MockAdapter:
        # Simulate network error
        MockAdapter.return_value.client.teams.get_all.side_effect = Exception(
            "Connection timeout"
        )

        with pytest.raises(APIConnectionError, match="Failed to list teams"):
            await list_teams_logic(api_key="test-key")


@pytest.mark.asyncio
async def test_list_teams_empty_list():
    """Test handling of empty teams list."""
    with patch("alfred.core.workspace.teams.LinearAdapter") as MockAdapter:
        # Return empty teams dict
        MockAdapter.return_value.client.teams.get_all.return_value = {}

        result = await list_teams_logic(api_key="test-key")

        assert result["status"] == "ok"
        assert result["count"] == 0
        assert result["teams"] == []


@pytest.mark.asyncio
async def test_list_teams_with_minimal_fields():
    """Test handling teams with minimal fields."""
    with patch("alfred.core.workspace.teams.LinearAdapter") as MockAdapter:
        # Setup mock team with only required fields
        mock_team = Mock()
        mock_team.id = "team-min"
        mock_team.name = "Minimal Team"
        # No description or key attributes
        del mock_team.description
        del mock_team.key

        mock_teams = {"team-min": mock_team}
        MockAdapter.return_value.client.teams.get_all.return_value = mock_teams

        result = await list_teams_logic(api_key="test-key")

        assert result["status"] == "ok"
        assert result["count"] == 1
        team = result["teams"][0]
        assert team["id"] == "team-min"
        assert team["name"] == "Minimal Team"
        assert "description" not in team
        assert "key" not in team
