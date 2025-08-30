"""Tests for task subtask creation business logic."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from alfred.core.tasks.create_subtasks import (
    create_subtasks_logic,
    create_all_subtasks_logic,
)
from alfred.adapters.base import NotFoundError
from alfred.models.config import Config, Platform


@pytest.fixture
def mock_config():
    """Create a mock config object for testing."""
    config = Mock(spec=Config)
    config.platform = Platform.LINEAR
    config.linear_api_key = "test-key"
    config.linear_team_id = "team-123"
    return config


@pytest.mark.asyncio
async def test_create_subtasks_success(mock_config):
    """Test successful subtask creation."""
    with patch("alfred.core.tasks.create_subtasks.get_adapter") as mock_get_adapter:
        # Setup mock adapter
        mock_adapter = Mock()
        mock_get_adapter.return_value = mock_adapter

        # Mock task retrieval
        mock_task = {
            "id": "TASK-123",
            "title": "Implement authentication",
            "description": "Add user authentication",
            "status": "todo",
            "epic_id": "EPIC-1",
            "subtasks": [],
        }
        mock_adapter.get_task.return_value = mock_task

        # Mock get_task_children (returns empty list for new task)
        mock_adapter.get_task_children.return_value = []

        # Mock subtask creation
        mock_adapter.create_subtask.side_effect = [
            {
                "id": "TASK-124",
                "title": "Subtask 1",
                "description": "Details 1",
                "status": "todo",
            },
            {
                "id": "TASK-125",
                "title": "Subtask 2",
                "description": "Details 2",
                "status": "todo",
            },
            {
                "id": "TASK-126",
                "title": "Subtask 3",
                "description": "Details 3",
                "status": "todo",
            },
        ]

        # Mock AI service
        with patch("alfred.core.tasks.create_subtasks.AIService") as MockAIService:
            mock_ai_service = Mock()
            MockAIService.return_value = mock_ai_service
            mock_ai_service.decompose_task = AsyncMock(
                return_value=[
                    {
                        "title": "Subtask 1",
                        "description": "Details 1",
                        "technical_details": "Implementation approach",
                        "acceptance_criteria": ["Criterion 1"],
                    },
                    {
                        "title": "Subtask 2",
                        "description": "Details 2",
                        "technical_details": "Implementation approach",
                        "acceptance_criteria": ["Criterion 2"],
                    },
                    {
                        "title": "Subtask 3",
                        "description": "Details 3",
                        "technical_details": "Implementation approach",
                        "acceptance_criteria": ["Criterion 3"],
                    },
                ]
            )

            # Execute
            result = await create_subtasks_logic(
                config=mock_config, task_id="TASK-123", num_subtasks=3
            )

            # Verify
            assert result.task_id == "TASK-123"
            assert result.task_title == "Implement authentication"
            assert len(result.subtasks_created) == 3
            assert mock_adapter.create_subtask.call_count == 3


@pytest.mark.asyncio
async def test_create_subtasks_already_has_subtasks(mock_config):
    """Test subtask creation fails when task has subtasks and force is False."""
    with patch("alfred.core.tasks.create_subtasks.get_adapter") as mock_get_adapter:
        # Setup mock adapter
        mock_adapter = Mock()
        mock_get_adapter.return_value = mock_adapter

        # Mock task (without subtasks field since we use get_task_children now)
        mock_task = {
            "id": "TASK-123",
            "title": "Implement authentication",
            "description": "Add user authentication",
            "status": "todo",
            "epic_id": "EPIC-1",
        }
        mock_adapter.get_task.return_value = mock_task

        # Mock get_task_children to return existing subtasks
        mock_adapter.get_task_children.return_value = [
            {"id": "TASK-124", "title": "Existing subtask", "status": "todo"}
        ]

        # Execute and expect ValueError
        with pytest.raises(ValueError) as exc_info:
            await create_subtasks_logic(
                config=mock_config, task_id="TASK-123", num_subtasks=3, force=False
            )

        # Verify
        assert "already has" in str(exc_info.value)
        assert "subtasks" in str(exc_info.value)


@pytest.mark.asyncio
async def test_create_subtasks_force_override(mock_config):
    """Test forced subtask creation deletes existing subtasks."""
    with patch("alfred.core.tasks.create_subtasks.get_adapter") as mock_get_adapter:
        # Setup mock adapter
        mock_adapter = Mock()
        mock_get_adapter.return_value = mock_adapter

        # Mock task (without subtasks field since we use get_task_children now)
        mock_task = {
            "id": "TASK-123",
            "title": "Implement authentication",
            "description": "Add user authentication",
            "status": "todo",
            "epic_id": "EPIC-1",
        }
        mock_adapter.get_task.return_value = mock_task

        # Mock get_task_children to return existing subtasks
        mock_adapter.get_task_children.return_value = [
            {"id": "TASK-124", "title": "Existing subtask", "status": "todo"}
        ]

        mock_adapter.delete_task.return_value = True

        # Mock subtask creation
        mock_adapter.create_subtask.return_value = {
            "id": "TASK-125",
            "title": "New subtask",
            "description": "New details",
            "status": "todo",
        }

        # Mock AI service
        with patch("alfred.core.tasks.create_subtasks.AIService") as MockAIService:
            mock_ai_service = Mock()
            MockAIService.return_value = mock_ai_service
            mock_ai_service.decompose_task = AsyncMock(
                return_value=[{"title": "New subtask", "description": "New details"}]
            )

            # Execute
            result = await create_subtasks_logic(
                config=mock_config, task_id="TASK-123", num_subtasks=1, force=True
            )

            # Verify
            assert result.task_id == "TASK-123"
            assert len(result.subtasks_created) == 1
            assert mock_adapter.delete_task.called
            assert mock_adapter.create_subtask.called


@pytest.mark.asyncio
async def test_create_subtasks_not_eligible(mock_config):
    """Test subtask creation fails for completed/cancelled tasks."""
    with patch("alfred.core.tasks.create_subtasks.get_adapter") as mock_get_adapter:
        # Setup mock adapter
        mock_adapter = Mock()
        mock_get_adapter.return_value = mock_adapter

        # Mock completed task
        mock_task = {
            "id": "TASK-123",
            "title": "Completed task",
            "description": "Already done",
            "status": "done",
            "epic_id": "EPIC-1",
        }
        mock_adapter.get_task.return_value = mock_task

        # Mock get_task_children (shouldn't be called for completed tasks)
        mock_adapter.get_task_children.return_value = []

        # Execute and expect ValueError
        with pytest.raises(ValueError) as exc_info:
            await create_subtasks_logic(config=mock_config, task_id="TASK-123")

        # Verify
        assert "Cannot create subtasks for task with status" in str(exc_info.value)


@pytest.mark.asyncio
async def test_create_all_subtasks_success(mock_config):
    """Test successful batch subtask creation."""
    with patch("alfred.core.tasks.create_subtasks.get_adapter") as mock_get_adapter:
        # Setup mock adapter
        mock_adapter = Mock()
        mock_get_adapter.return_value = mock_adapter

        # Mock task list
        mock_tasks = [
            {"id": "TASK-1", "title": "Task 1", "status": "todo"},
            {"id": "TASK-2", "title": "Task 2", "status": "in progress"},
            {
                "id": "TASK-3",
                "title": "Task 3",
                "status": "done",  # Should be skipped
            },
        ]
        mock_adapter.get_tasks.return_value = mock_tasks
        mock_adapter.get_task.side_effect = mock_tasks

        # Mock get_task_children for each task (all empty)
        mock_adapter.get_task_children.return_value = []

        # Mock subtask creation
        mock_adapter.create_subtask.return_value = {
            "id": "SUB-1",
            "title": "Subtask",
            "description": "Details",
            "status": "todo",
        }

        # Mock AI service
        with patch("alfred.core.tasks.create_subtasks.AIService") as MockAIService:
            mock_ai_service = Mock()
            MockAIService.return_value = mock_ai_service
            mock_ai_service.decompose_task = AsyncMock(
                return_value=[{"title": "Subtask", "description": "Details"}]
            )

            # Execute
            result = await create_all_subtasks_logic(config=mock_config, num_subtasks=1)

            # Verify
            assert result.expanded_count == 2  # Task 1 and 2
            assert result.skipped_count == 1  # Task 3 (done)
            assert result.failed_count == 0


@pytest.mark.asyncio
async def test_create_all_subtasks_with_epic_filter(mock_config):
    """Test batch subtask creation with epic filtering."""
    with patch("alfred.core.tasks.create_subtasks.get_adapter") as mock_get_adapter:
        # Setup mock adapter
        mock_adapter = Mock()
        mock_get_adapter.return_value = mock_adapter

        # Mock filtered task list
        mock_tasks = [
            {
                "id": "TASK-1",
                "title": "Epic task",
                "status": "todo",
                "epic_id": "EPIC-1",
            }
        ]
        mock_adapter.get_tasks.return_value = mock_tasks
        mock_adapter.get_task.return_value = mock_tasks[0]

        # Mock get_task_children (empty for new task)
        mock_adapter.get_task_children.return_value = []

        # Mock subtask creation
        mock_adapter.create_subtask.return_value = {
            "id": "SUB-1",
            "title": "Subtask",
            "description": "Details",
            "status": "todo",
        }

        # Mock AI service
        with patch("alfred.core.tasks.create_subtasks.AIService") as MockAIService:
            mock_ai_service = Mock()
            MockAIService.return_value = mock_ai_service
            mock_ai_service.decompose_task = AsyncMock(
                return_value=[{"title": "Subtask", "description": "Details"}]
            )

            # Execute
            result = await create_all_subtasks_logic(
                config=mock_config, epic_id="EPIC-1", num_subtasks=1
            )

            # Verify
            assert result.expanded_count == 1
            assert result.failed_count == 0
            mock_adapter.get_tasks.assert_called_with(epic_id="EPIC-1")
