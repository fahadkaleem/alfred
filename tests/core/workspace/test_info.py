"""Unit tests for workspace info logic."""

import pytest
from unittest.mock import Mock, patch
from alfred.core.workspace.info import get_workspace_info_logic


@pytest.mark.asyncio
async def test_get_workspace_info_not_configured():
    """Test workspace info when not configured."""
    with patch("alfred.core.workspace.info.current_workspace") as mock_current:
        # Simulate no workspace configured
        mock_current.return_value = {"platform": "linear"}

        result = await get_workspace_info_logic()

        assert result["status"] == "not_configured"
        assert "No workspace configured" in result["message"]
        assert result["platform"] == "linear"


@pytest.mark.asyncio
async def test_get_workspace_info_configured_not_connected():
    """Test workspace info when configured but not connected."""
    with patch("alfred.core.workspace.info.current_workspace") as mock_current:
        with patch("alfred.core.workspace.info.get_config") as mock_config:
            # Simulate configured workspace without API key
            mock_current.return_value = {
                "workspace_id": "ws-1",
                "team_id": "team-1",
                "platform": "linear",
                "has_linear_config": False,
                "has_ai_config": True,
                "active_epic_id": None,
            }

            result = await get_workspace_info_logic()

            assert result["status"] == "configured"
            assert result["connection_status"] == "not_connected"
            assert result["platform"] == "linear"
            assert result["workspace"]["id"] == "ws-1"
            assert result["team"]["id"] == "team-1"
            assert result["has_api_key"] is False
            assert result["has_ai_config"] is True
            assert result["active_epic_id"] is None


@pytest.mark.asyncio
async def test_get_workspace_info_connected():
    """Test workspace info when fully connected."""
    with patch("alfred.core.workspace.info.current_workspace") as mock_current:
        with patch("alfred.core.workspace.info.get_config") as mock_config:
            with patch("alfred.core.workspace.info.LinearAdapter") as MockAdapter:
                # Simulate configured and connected workspace
                mock_current.return_value = {
                    "workspace_id": "ws-1",
                    "team_id": "team-1",
                    "platform": "linear",
                    "has_linear_config": True,
                    "has_ai_config": True,
                    "active_epic_id": "epic-123",
                }

                # Mock config with API key
                mock_config.return_value.linear_api_key = "test-key"

                # Mock successful API call
                MockAdapter.return_value.client.teams.get_all.return_value = {
                    "team-1": Mock()
                }

                result = await get_workspace_info_logic()

                assert result["status"] == "configured"
                assert result["connection_status"] == "connected"
                assert result["platform"] == "linear"
                assert result["workspace"]["id"] == "ws-1"
                assert result["team"]["id"] == "team-1"
                assert result["has_api_key"] is True
                assert result["has_ai_config"] is True
                assert result["active_epic_id"] == "epic-123"

                # Verify LinearAdapter was called for connection test
                MockAdapter.assert_called_once_with(api_token="test-key")


@pytest.mark.asyncio
async def test_get_workspace_info_connection_failed():
    """Test workspace info when connection test fails."""
    with patch("alfred.core.workspace.info.current_workspace") as mock_current:
        with patch("alfred.core.workspace.info.get_config") as mock_config:
            with patch("alfred.core.workspace.info.LinearAdapter") as MockAdapter:
                # Simulate configured workspace with API key
                mock_current.return_value = {
                    "workspace_id": "ws-1",
                    "team_id": "team-1",
                    "platform": "linear",
                    "has_linear_config": True,
                    "has_ai_config": False,
                    "active_epic_id": None,
                }

                # Mock config with API key
                mock_config.return_value.linear_api_key = "test-key"

                # Mock failed API call
                MockAdapter.return_value.client.teams.get_all.side_effect = Exception(
                    "Connection error"
                )

                result = await get_workspace_info_logic()

                assert result["status"] == "configured"
                assert result["connection_status"] == "connection_failed"
                assert result["platform"] == "linear"
                assert result["has_api_key"] is True
                assert result["has_ai_config"] is False


@pytest.mark.asyncio
async def test_get_workspace_info_jira_platform():
    """Test workspace info for Jira platform."""
    with patch("alfred.core.workspace.info.current_workspace") as mock_current:
        # Simulate Jira workspace
        mock_current.return_value = {
            "workspace_id": "jira-ws",
            "team_id": "jira-team",
            "platform": "jira",
            "has_jira_config": True,
            "has_ai_config": True,
            "active_epic_id": None,
        }

        result = await get_workspace_info_logic()

        assert result["status"] == "configured"
        assert (
            result["connection_status"] == "not_connected"
        )  # No Jira adapter implemented yet
        assert result["platform"] == "jira"
        assert result["workspace"]["id"] == "jira-ws"
        assert result["team"]["id"] == "jira-team"
        assert result["has_api_key"] is True  # has_jira_config = True


@pytest.mark.asyncio
async def test_get_workspace_info_missing_team_id():
    """Test workspace info when team_id is missing."""
    with patch("alfred.core.workspace.info.current_workspace") as mock_current:
        # Simulate workspace with missing team_id
        mock_current.return_value = {
            "workspace_id": "ws-1",
            "team_id": None,  # Missing team_id
            "platform": "linear",
        }

        result = await get_workspace_info_logic()

        assert result["status"] == "not_configured"
        assert "No workspace configured" in result["message"]


@pytest.mark.asyncio
async def test_get_workspace_info_empty_workspace_id():
    """Test workspace info when workspace_id is empty string."""
    with patch("alfred.core.workspace.info.current_workspace") as mock_current:
        # Simulate workspace with empty workspace_id
        mock_current.return_value = {
            "workspace_id": "",  # Empty string
            "team_id": "team-1",
            "platform": "linear",
        }

        result = await get_workspace_info_logic()

        assert result["status"] == "not_configured"
        assert "No workspace configured" in result["message"]
