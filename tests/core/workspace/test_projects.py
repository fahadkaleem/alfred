"""Unit tests for projects/epics listing logic."""

import pytest
from unittest.mock import Mock, patch
from alfred.core.workspace.projects import list_projects_logic
from alfred.adapters.base import AuthError, APIConnectionError


@pytest.mark.asyncio
async def test_list_projects_success():
    """Test successful projects listing."""
    with patch("alfred.core.workspace.projects.LinearAdapter") as MockAdapter:
        # Setup mock projects data
        mock_projects = [
            {
                "id": "epic-1",
                "name": "Q1 Features",
                "description": "Features for Q1 2024",
                "url": "https://linear.app/team/epic-1",
            },
            {
                "id": "epic-2",
                "name": "Tech Debt",
                "description": None,
                "url": "https://linear.app/team/epic-2",
            },
            {
                "id": "epic-3",
                "name": "Bug Fixes",
                # No description or URL
            },
        ]

        MockAdapter.return_value.get_epics.return_value = mock_projects

        # Call the function
        result = await list_projects_logic(api_key="test-key")

        # Assertions
        assert result["status"] == "ok"
        assert result["count"] == 3
        assert len(result["projects"]) == 3

        # Check first project with all fields
        project1 = result["projects"][0]
        assert project1["id"] == "epic-1"
        assert project1["name"] == "Q1 Features"
        assert project1["description"] == "Features for Q1 2024"
        assert project1["url"] == "https://linear.app/team/epic-1"

        # Check second project with null description
        project2 = result["projects"][1]
        assert project2["id"] == "epic-2"
        assert project2["name"] == "Tech Debt"
        assert "description" not in project2  # None should be excluded
        assert project2["url"] == "https://linear.app/team/epic-2"

        # Check third project with minimal fields
        project3 = result["projects"][2]
        assert project3["id"] == "epic-3"
        assert project3["name"] == "Bug Fixes"
        assert "description" not in project3
        assert "url" not in project3

        # Verify LinearAdapter was called correctly
        MockAdapter.assert_called_once_with(api_token="test-key")
        MockAdapter.return_value.get_epics.assert_called_once_with(limit=100)


@pytest.mark.asyncio
async def test_list_projects_missing_api_key():
    """Test error when API key is missing."""
    with pytest.raises(AuthError, match="LINEAR_API_KEY not configured"):
        await list_projects_logic(api_key="")

    with pytest.raises(AuthError, match="LINEAR_API_KEY not configured"):
        await list_projects_logic(api_key=None)


@pytest.mark.asyncio
async def test_list_projects_invalid_api_key():
    """Test handling of invalid API key."""
    with patch("alfred.core.workspace.projects.LinearAdapter") as MockAdapter:
        # Simulate 401 unauthorized error
        MockAdapter.return_value.get_epics.side_effect = Exception("401 Unauthorized")

        with pytest.raises(AuthError, match="Invalid Linear API key"):
            await list_projects_logic(api_key="invalid-key")


@pytest.mark.asyncio
async def test_list_projects_network_error():
    """Test handling of network errors."""
    with patch("alfred.core.workspace.projects.LinearAdapter") as MockAdapter:
        # Simulate network error
        MockAdapter.return_value.get_epics.side_effect = Exception("Connection timeout")

        with pytest.raises(APIConnectionError, match="Failed to list projects"):
            await list_projects_logic(api_key="test-key")


@pytest.mark.asyncio
async def test_list_projects_empty_list():
    """Test handling of empty projects list."""
    with patch("alfred.core.workspace.projects.LinearAdapter") as MockAdapter:
        # Return empty list
        MockAdapter.return_value.get_epics.return_value = []

        result = await list_projects_logic(api_key="test-key")

        assert result["status"] == "ok"
        assert result["count"] == 0
        assert result["projects"] == []


@pytest.mark.asyncio
async def test_list_projects_auth_error_propagation():
    """Test that AuthError from adapter is properly propagated."""
    with patch("alfred.core.workspace.projects.LinearAdapter") as MockAdapter:
        # Import AuthError to raise it directly
        from alfred.adapters.base import AuthError as AdapterAuthError

        # Simulate AuthError from adapter
        MockAdapter.return_value.get_epics.side_effect = AdapterAuthError(
            "API key expired"
        )

        # Should re-raise the same AuthError
        with pytest.raises(AuthError):
            await list_projects_logic(api_key="test-key")


@pytest.mark.asyncio
async def test_list_projects_with_special_characters():
    """Test handling of projects with special characters in names."""
    with patch("alfred.core.workspace.projects.LinearAdapter") as MockAdapter:
        # Setup mock projects with special characters
        mock_projects = [
            {
                "id": "epic-special",
                "name": "Project & Task / Feature",
                "description": "Description with 'quotes' and \"double quotes\"",
                "url": "https://linear.app/team/epic-special?param=value&other=test",
            }
        ]

        MockAdapter.return_value.get_epics.return_value = mock_projects

        result = await list_projects_logic(api_key="test-key")

        # Ensure special characters are preserved
        project = result["projects"][0]
        assert project["name"] == "Project & Task / Feature"
        assert (
            project["description"] == "Description with 'quotes' and \"double quotes\""
        )
        assert (
            project["url"]
            == "https://linear.app/team/epic-special?param=value&other=test"
        )
