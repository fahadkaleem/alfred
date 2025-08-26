"""Unit tests for Linear adapter."""

import os
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
import pytest

from alfred.adapters import (
    LinearAdapter,
    TaskDict,
    EpicDict,
    AuthError,
    NotFoundError,
    ValidationError,
    APIResponseError,
    APIConnectionError,
    MappingError,
)


class TestLinearAdapter:
    """Test suite for LinearAdapter."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock Linear client."""
        with patch("alfred.adapters.linear_adapter.LinearClient") as mock:
            yield mock

    @pytest.fixture
    def adapter(self, mock_client):
        """Create a LinearAdapter instance with mocked client."""
        # Mock the LinearClient constructor
        mock_instance = Mock()
        mock_client.return_value = mock_instance

        # Create adapter with test token
        os.environ["LINEAR_API_KEY"] = "test-token"
        adapter = LinearAdapter(
            team_name="test-team", default_project_name="test-project"
        )

        return adapter

    def test_init_without_token(self, mock_client):
        """Test initialization without API token raises AuthError."""
        # Clear environment variable
        os.environ.pop("LINEAR_API_KEY", None)

        with pytest.raises(AuthError, match="Linear API key is required"):
            LinearAdapter()

    def test_init_with_token(self, mock_client):
        """Test successful initialization with API token."""
        adapter = LinearAdapter(api_token="test-token")
        assert adapter.client is not None
        mock_client.assert_called_once_with(api_key="test-token")

    def test_init_with_env_token(self, mock_client):
        """Test initialization with environment variable token."""
        os.environ["LINEAR_API_KEY"] = "env-token"
        adapter = LinearAdapter()
        assert adapter.client is not None
        mock_client.assert_called_once_with(api_key="env-token")

    def test_create_task_success(self, adapter):
        """Test successful task creation."""
        # Mock the Linear API response
        mock_issue = Mock()
        mock_issue.id = "issue-id"
        mock_issue.identifier = "TASK-123"
        mock_issue.title = "Test Task"
        mock_issue.description = "Test Description"
        mock_issue.state = Mock()
        mock_issue.state.name = "Todo"
        mock_issue.project = Mock(id="project-id")
        mock_issue.parent = None
        mock_issue.url = "https://linear.app/team/issue/TASK-123"
        mock_issue.created_at = datetime.now()
        mock_issue.updated_at = datetime.now()

        adapter.client.issues.create = Mock(return_value=mock_issue)

        # Create task
        task = adapter.create_task(
            title="Test Task", description="Test Description", epic_id="project-id"
        )

        # Verify result
        assert task["id"] == "TASK-123"
        assert task["title"] == "Test Task"
        assert task["description"] == "Test Description"
        assert task["status"] == "Todo"
        assert task["epic_id"] == "project-id"
        assert task["url"] == "https://linear.app/team/issue/TASK-123"

    def test_create_task_empty_title(self, adapter):
        """Test task creation with empty title raises ValidationError."""
        with pytest.raises(ValidationError, match="Task title cannot be empty"):
            adapter.create_task(title="")

    def test_create_task_api_failure(self, adapter):
        """Test task creation with API failure."""
        adapter.client.issues.create = Mock(side_effect=Exception("API Error"))

        with pytest.raises(APIResponseError, match="Linear API error"):
            adapter.create_task(title="Test Task")

    def test_get_tasks_success(self, adapter):
        """Test successful task retrieval."""
        # Mock issues
        mock_issue1 = Mock()
        mock_issue1.identifier = "TASK-1"
        mock_issue1.title = "Task 1"
        mock_issue1.description = "Description 1"
        mock_issue1.state = Mock()
        mock_issue1.state.name = "Todo"
        mock_issue1.project = None
        mock_issue1.parent = None
        mock_issue1.url = "https://linear.app/team/issue/TASK-1"
        mock_issue1.created_at = datetime.now()
        mock_issue1.updated_at = datetime.now()

        mock_issue2 = Mock()
        mock_issue2.identifier = "TASK-2"
        mock_issue2.title = "Task 2"
        mock_issue2.description = "Description 2"
        mock_issue2.state = Mock()
        mock_issue2.state.name = "In Progress"
        mock_issue2.project = None
        mock_issue2.parent = None
        mock_issue2.url = "https://linear.app/team/issue/TASK-2"
        mock_issue2.created_at = datetime.now()
        mock_issue2.updated_at = datetime.now()

        mock_issues_dict = {"issue-1-id": mock_issue1, "issue-2-id": mock_issue2}

        adapter.client.issues.get_by_team = Mock(return_value=mock_issues_dict)

        # Get tasks
        tasks = adapter.get_tasks(limit=10)

        # Verify results
        assert len(tasks) == 2
        assert tasks[0]["id"] == "TASK-1"
        assert tasks[0]["title"] == "Task 1"
        assert tasks[0]["status"] == "Todo"
        assert tasks[1]["id"] == "TASK-2"
        assert tasks[1]["title"] == "Task 2"
        assert tasks[1]["status"] == "In Progress"

    def test_get_tasks_with_filters(self, adapter):
        """Test task retrieval with filters."""
        mock_issues_dict = {}

        adapter.client.issues.get_by_team = Mock(return_value=mock_issues_dict)

        # Get tasks with filters
        tasks = adapter.get_tasks(
            epic_id="project-123", status=["Todo", "In Progress"], limit=25
        )

        # Verify the call was made
        adapter.client.issues.get_by_team.assert_called_once()
        # Note: Filtering is done in Python, not in the GraphQL call

    def test_get_task_success(self, adapter):
        """Test successful single task retrieval."""
        mock_issue = Mock()
        mock_issue.identifier = "TASK-123"
        mock_issue.title = "Test Task"
        mock_issue.description = "Test Description"
        mock_issue.state = Mock()
        mock_issue.state.name = "Todo"
        mock_issue.project = None
        mock_issue.parent = None
        mock_issue.url = "https://linear.app/team/issue/TASK-123"
        mock_issue.created_at = datetime.now()
        mock_issue.updated_at = datetime.now()

        mock_issues_dict = {"issue-123-id": mock_issue}
        adapter.client.issues.get_all = Mock(return_value=mock_issues_dict)

        # Get task
        task = adapter.get_task("TASK-123")

        # Verify result
        assert task["id"] == "TASK-123"
        assert task["title"] == "Test Task"
        assert task["description"] == "Test Description"

    def test_get_task_not_found(self, adapter):
        """Test task retrieval when task doesn't exist."""
        mock_issues_dict = {}  # Empty dict means no issues found
        adapter.client.issues.get_all = Mock(return_value=mock_issues_dict)

        with pytest.raises(NotFoundError, match="Task INVALID-ID not found"):
            adapter.get_task("INVALID-ID")

    def test_update_task_success(self, adapter):
        """Test successful task update."""
        # Mock existing issue
        mock_issue = Mock()
        mock_issue.id = "issue-id"
        mock_issue.identifier = "TASK-123"

        # Mock updated issue
        mock_updated = Mock()
        mock_updated.identifier = "TASK-123"
        mock_updated.title = "Updated Title"
        mock_updated.description = "Updated Description"
        mock_updated.state = Mock()
        mock_updated.state.name = "In Progress"
        mock_updated.project = None
        mock_updated.parent = None
        mock_updated.url = "https://linear.app/team/issue/TASK-123"
        mock_updated.created_at = datetime.now()
        mock_updated.updated_at = datetime.now()

        mock_issues_dict = {"issue-id": mock_issue}
        adapter.client.issues.get_all = Mock(return_value=mock_issues_dict)
        adapter.client.issues.update = Mock(return_value=mock_updated)

        # Update task
        task = adapter.update_task(
            "TASK-123", {"title": "Updated Title", "description": "Updated Description"}
        )

        # Verify result
        assert task["title"] == "Updated Title"
        assert task["description"] == "Updated Description"

    def test_update_task_not_found(self, adapter):
        """Test task update when task doesn't exist."""
        mock_issues_dict = {}  # Empty dict means no issues found
        adapter.client.issues.get_all = Mock(return_value=mock_issues_dict)

        with pytest.raises(NotFoundError, match="Task INVALID-ID not found"):
            adapter.update_task("INVALID-ID", {"title": "New Title"})

    def test_create_subtask_success(self, adapter):
        """Test successful subtask creation."""
        # Mock parent issue
        mock_parent = Mock()
        mock_parent.id = "parent-id"
        mock_parent.identifier = "TASK-100"
        mock_parent.project = Mock(id="project-id")

        # Mock subtask
        mock_subtask = Mock()
        mock_subtask.id = "subtask-id"
        mock_subtask.identifier = "TASK-101"
        mock_subtask.title = "Subtask"
        mock_subtask.description = "Subtask Description"
        mock_subtask.state = Mock()
        mock_subtask.state.name = "Todo"
        mock_subtask.project = Mock(id="project-id")
        mock_subtask.parent = Mock(id="parent-id")
        mock_subtask.url = "https://linear.app/team/issue/TASK-101"
        mock_subtask.created_at = datetime.now()
        mock_subtask.updated_at = datetime.now()

        mock_issues_dict = {"parent-id": mock_parent}
        adapter.client.issues.get_all = Mock(return_value=mock_issues_dict)
        adapter.client.issues.create = Mock(return_value=mock_subtask)

        # Create subtask
        task = adapter.create_subtask(
            parent_id="TASK-100", title="Subtask", description="Subtask Description"
        )

        # Verify result
        assert task["id"] == "TASK-101"
        assert task["title"] == "Subtask"
        assert task["parent_id"] == "parent-id"

    def test_create_subtask_parent_not_found(self, adapter):
        """Test subtask creation when parent doesn't exist."""
        mock_issues_dict = {}  # Empty dict means no issues found
        adapter.client.issues.get_all = Mock(return_value=mock_issues_dict)

        with pytest.raises(NotFoundError, match="Parent task INVALID-ID not found"):
            adapter.create_subtask("INVALID-ID", "Subtask")

    def test_delete_task_success(self, adapter):
        """Test successful task deletion."""
        mock_issue = Mock()
        mock_issue.id = "issue-id"
        mock_issue.identifier = "TASK-123"

        mock_issues_dict = {"issue-id": mock_issue}
        adapter.client.issues.get_all = Mock(return_value=mock_issues_dict)
        adapter.client.issues.delete = Mock(return_value=True)

        # Delete task
        result = adapter.delete_task("TASK-123")

        # Verify result
        assert result is True
        adapter.client.issues.delete.assert_called_once_with("issue-id")

    def test_delete_task_not_found(self, adapter):
        """Test task deletion when task doesn't exist."""
        mock_issues_dict = {}  # Empty dict means no issues found
        adapter.client.issues.get_all = Mock(return_value=mock_issues_dict)

        with pytest.raises(NotFoundError, match="Task INVALID-ID not found"):
            adapter.delete_task("INVALID-ID")

    def test_create_epic_success(self, adapter):
        """Test successful epic (project) creation."""
        mock_project = Mock()
        mock_project.id = "project-id"
        mock_project.name = "Test Epic"
        mock_project.description = "Epic Description"
        mock_project.url = "https://linear.app/team/project/project-id"
        mock_project.created_at = datetime.now()
        mock_project.updated_at = datetime.now()

        # Mock teams for team lookup
        mock_team = Mock()
        mock_team.name = "test-team"
        mock_teams_dict = {"team-id": mock_team}
        adapter.client.teams.get_all = Mock(return_value=mock_teams_dict)

        # Mock GraphQL response
        graphql_response = {
            "projectCreate": {
                "project": {
                    "id": "project-id",
                    "name": "Test Epic",
                    "description": "Epic Description",
                    "url": "https://linear.app/team/project/project-id",
                    "createdAt": mock_project.created_at.isoformat(),
                    "updatedAt": mock_project.updated_at.isoformat(),
                },
                "success": True,
            }
        }
        adapter.client.execute_graphql = Mock(return_value=graphql_response)

        # Create epic
        epic = adapter.create_epic(name="Test Epic", description="Epic Description")

        # Verify result
        assert epic["id"] == "project-id"
        assert epic["name"] == "Test Epic"
        assert epic["description"] == "Epic Description"

    def test_create_epic_empty_name(self, adapter):
        """Test epic creation with empty name raises ValidationError."""
        with pytest.raises(ValidationError, match="Epic name cannot be empty"):
            adapter.create_epic(name="")

    def test_get_epics_success(self, adapter):
        """Test successful epic retrieval."""
        mock_project1 = Mock()
        mock_project1.id = "project-1"
        mock_project1.name = "Epic 1"
        mock_project1.description = "Description 1"
        mock_project1.url = "https://linear.app/team/project/project-1"
        mock_project1.created_at = datetime.now()
        mock_project1.updated_at = datetime.now()

        mock_project2 = Mock()
        mock_project2.id = "project-2"
        mock_project2.name = "Epic 2"
        mock_project2.description = "Description 2"
        mock_project2.url = "https://linear.app/team/project/project-2"
        mock_project2.created_at = datetime.now()
        mock_project2.updated_at = datetime.now()

        mock_projects_dict = {"project-1": mock_project1, "project-2": mock_project2}

        adapter.client.projects.get_all = Mock(return_value=mock_projects_dict)

        # Get epics
        epics = adapter.get_epics(limit=10)

        # Verify results
        assert len(epics) == 2
        assert epics[0]["id"] == "project-1"
        assert epics[0]["name"] == "Epic 1"
        assert epics[1]["id"] == "project-2"
        assert epics[1]["name"] == "Epic 2"

    def test_link_tasks_success(self, adapter):
        """Test successful task linking (dependency creation)."""
        mock_task = Mock()
        mock_task.id = "task-id"

        mock_depends_on = Mock()
        mock_depends_on.id = "depends-on-id"

        mock_task.identifier = "TASK-123"
        mock_depends_on.identifier = "TASK-100"

        mock_issues_dict = {"task-id": mock_task, "depends-on-id": mock_depends_on}

        adapter.client.issues.get_all = Mock(return_value=mock_issues_dict)

        # Mock GraphQL response
        graphql_response = {"issueRelationCreate": {"success": True}}
        adapter.client.execute_graphql = Mock(return_value=graphql_response)

        # Link tasks
        result = adapter.link_tasks("TASK-123", "TASK-100")

        # Verify result
        assert result is True
        adapter.client.execute_graphql.assert_called_once()

    def test_link_tasks_not_found(self, adapter):
        """Test task linking when one task doesn't exist."""
        mock_issues_dict = {}  # Empty dict means no issues found
        adapter.client.issues.get_all = Mock(return_value=mock_issues_dict)

        with pytest.raises(NotFoundError, match="Task TASK-123 not found"):
            adapter.link_tasks("TASK-123", "TASK-100")

    def test_mapping_error_handling(self, adapter):
        """Test error handling in mapping functions."""
        # Create an issue with missing attributes
        mock_issue = Mock()
        mock_issue.identifier = "TASK-123"
        mock_issue.title = "Test"
        # Simulate attribute error
        del mock_issue.description

        with pytest.raises(MappingError, match="Failed to map Linear issue"):
            adapter._map_linear_issue_to_task(mock_issue)

    def test_auth_error_handling(self, adapter):
        """Test authentication error handling."""
        adapter.client.issues.create = Mock(side_effect=Exception("401 Unauthorized"))

        with pytest.raises(AuthError, match="Authentication failed"):
            adapter.create_task(title="Test")

    def test_connection_error_handling(self, adapter):
        """Test network error handling."""
        adapter.client.issues.create = Mock(
            side_effect=Exception("Network connection failed")
        )

        with pytest.raises(APIConnectionError, match="Network error"):
            adapter.create_task(title="Test")
