"""Tests for task enhancement business logic."""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from alfred.core.tasks.enhance import (
    enhance_task_scope_logic,
    simplify_task_logic,
    bulk_enhance_tasks_logic,
)


@pytest.fixture
def mock_linear_adapter():
    """Create a mock LinearAdapter."""
    adapter = Mock()
    adapter.get_task = Mock()
    adapter.update_task = Mock()
    return adapter


@pytest.fixture
def sample_task():
    """Create a sample task for testing."""
    return {
        "id": "TEST-123",
        "title": "Implement user authentication",
        "description": "Basic login functionality",
        "status": "pending",
        "priority": "medium",
        "epic_id": "epic-1",
        "labels": [],
    }


@pytest.fixture
def sample_alfred_task():
    """Create a sample Alfred task."""
    from alfred.models.tasks import AlfredTask
    from datetime import datetime

    now = datetime.now()
    return AlfredTask(
        id="TEST-123",
        title="Implement user authentication",
        description="Basic login functionality",
        status="pending",
        priority="medium",
        epic_id="epic-1",
        labels=[],
        created_at=now,
        updated_at=now,
    )


@pytest.mark.asyncio
async def test_enhance_task_scope_logic(
    mock_linear_adapter, sample_task, sample_alfred_task
):
    """Test enhancing task scope with AI."""
    with patch("alfred.core.tasks.enhance.LinearAdapter") as MockAdapter:
        with patch("alfred.core.tasks.enhance.to_alfred_task") as mock_to_alfred:
            with patch("alfred.core.tasks.enhance.AIService") as MockAIService:
                # Setup mocks
                MockAdapter.return_value = mock_linear_adapter
                mock_linear_adapter.get_task.return_value = sample_task
                mock_to_alfred.return_value = sample_alfred_task

                # Mock AI service response
                ai_service = AsyncMock()
                MockAIService.return_value = ai_service
                ai_service.enhance_scope.return_value = {
                    "description": "Enhanced description",
                    "priority": "high",
                    "additional_requirements": [
                        "Add password strength validation",
                        "Implement session management",
                    ],
                    "non_functional_requirements": [
                        "Response time < 200ms",
                        "Support 1000 concurrent users",
                    ],
                    "edge_cases": [
                        "Handle expired tokens",
                        "Deal with network timeouts",
                    ],
                    "testing_requirements": [
                        "Unit tests for all auth functions",
                        "Integration tests for login flow",
                    ],
                }

                # Updated task after enhancement
                enhanced_task = sample_task.copy()
                enhanced_task["description"] = "Enhanced full description"
                enhanced_task["priority"] = 1
                mock_linear_adapter.update_task.return_value = enhanced_task

                # Call the function
                result = await enhance_task_scope_logic(
                    api_key="test-key",
                    task_id="TEST-123",
                    enhancement_prompt="Add security requirements",
                )

                # Verify calls
                MockAdapter.assert_called_once_with(api_token="test-key")
                mock_linear_adapter.get_task.assert_called_once_with("TEST-123")
                ai_service.enhance_scope.assert_called_once()

                # Check the update data
                update_call = mock_linear_adapter.update_task.call_args
                assert update_call[0][0] == "TEST-123"
                update_data = update_call[0][1]

                # Verify description includes all sections
                assert "Additional Requirements:" in update_data["description"]
                assert "Non-Functional Requirements:" in update_data["description"]
                assert "Edge Cases to Handle:" in update_data["description"]
                assert "Testing Requirements:" in update_data["description"]
                assert update_data["priority"] == 1


@pytest.mark.asyncio
async def test_simplify_task_logic(
    mock_linear_adapter, sample_task, sample_alfred_task
):
    """Test simplifying task to core requirements."""
    with patch("alfred.core.tasks.enhance.LinearAdapter") as MockAdapter:
        with patch("alfred.core.tasks.enhance.to_alfred_task") as mock_to_alfred:
            with patch("alfred.core.tasks.enhance.AIService") as MockAIService:
                # Setup mocks
                MockAdapter.return_value = mock_linear_adapter
                mock_linear_adapter.get_task.return_value = sample_task
                mock_to_alfred.return_value = sample_alfred_task

                # Mock AI service response
                ai_service = AsyncMock()
                MockAIService.return_value = ai_service
                ai_service.simplify_task.return_value = {
                    "description": "Simple login only",
                    "priority": "medium",
                    "core_requirements": [
                        "Basic email/password login",
                        "Simple session token",
                    ],
                    "simplified_approach": "Use basic JWT with no refresh tokens",
                    "future_enhancements": [
                        "OAuth integration",
                        "Two-factor authentication",
                        "Password reset flow",
                    ],
                }

                # Updated task after simplification
                simplified_task = sample_task.copy()
                simplified_task["description"] = "Simplified description"
                simplified_task["priority"] = 2
                mock_linear_adapter.update_task.return_value = simplified_task

                # Call the function
                result = await simplify_task_logic(
                    api_key="test-key",
                    task_id="TEST-123",
                    simplification_prompt="Focus on MVP",
                )

                # Verify calls
                MockAdapter.assert_called_once_with(api_token="test-key")
                mock_linear_adapter.get_task.assert_called_once_with("TEST-123")
                ai_service.simplify_task.assert_called_once()

                # Check the update data
                update_call = mock_linear_adapter.update_task.call_args
                assert update_call[0][0] == "TEST-123"
                update_data = update_call[0][1]

                # Verify description includes all sections
                assert "Core Requirements:" in update_data["description"]
                assert "Implementation Approach:" in update_data["description"]
                assert "Future Enhancements (Deferred):" in update_data["description"]
                assert update_data["priority"] == 2


@pytest.mark.asyncio
async def test_bulk_enhance_tasks_logic():
    """Test bulk enhancement of multiple tasks."""
    with patch("alfred.core.tasks.enhance.enhance_task_scope_logic") as mock_enhance:
        with patch("alfred.core.tasks.enhance.simplify_task_logic") as mock_simplify:
            # Mock successful enhancements
            mock_enhance.return_value = {"id": "TEST-1", "enhanced": True}
            mock_simplify.return_value = {"id": "TEST-2", "simplified": True}

            # Test scope enhancement
            result = await bulk_enhance_tasks_logic(
                api_key="test-key",
                task_ids=["TEST-1", "TEST-2", "TEST-3"],
                enhancement_prompt="Add more requirements",
                enhancement_type="scope",
            )

            assert result["total"] == 3
            assert result["success"] == 3
            assert result["errors"] == 0
            assert len(result["results"]) == 3
            assert mock_enhance.call_count == 3

            # Reset mocks
            mock_enhance.reset_mock()
            mock_simplify.reset_mock()

            # Test simplification
            result = await bulk_enhance_tasks_logic(
                api_key="test-key",
                task_ids=["TEST-1", "TEST-2"],
                enhancement_prompt="Simplify to MVP",
                enhancement_type="simplify",
            )

            assert result["total"] == 2
            assert result["success"] == 2
            assert result["errors"] == 0
            assert mock_simplify.call_count == 2


@pytest.mark.asyncio
async def test_bulk_enhance_with_errors():
    """Test bulk enhancement with some failures."""
    with patch("alfred.core.tasks.enhance.enhance_task_scope_logic") as mock_enhance:
        # Mock mixed results
        mock_enhance.side_effect = [
            {"id": "TEST-1", "enhanced": True},
            Exception("Task not found"),
            {"id": "TEST-3", "enhanced": True},
        ]

        result = await bulk_enhance_tasks_logic(
            api_key="test-key",
            task_ids=["TEST-1", "TEST-2", "TEST-3"],
            enhancement_prompt="Add requirements",
            enhancement_type="scope",
        )

        assert result["total"] == 3
        assert result["success"] == 2
        assert result["errors"] == 1

        # Check individual results
        assert result["results"][0]["status"] == "success"
        assert result["results"][1]["status"] == "error"
        assert "Task not found" in result["results"][1]["error"]
        assert result["results"][2]["status"] == "success"


@pytest.mark.asyncio
async def test_enhance_with_no_changes(
    mock_linear_adapter, sample_task, sample_alfred_task
):
    """Test enhancement when AI returns no changes."""
    with patch("alfred.core.tasks.enhance.LinearAdapter") as MockAdapter:
        with patch("alfred.core.tasks.enhance.to_alfred_task") as mock_to_alfred:
            with patch("alfred.core.tasks.enhance.AIService") as MockAIService:
                # Setup mocks
                MockAdapter.return_value = mock_linear_adapter
                mock_linear_adapter.get_task.return_value = sample_task
                mock_to_alfred.return_value = sample_alfred_task

                # Mock AI service response with no significant changes
                ai_service = AsyncMock()
                MockAIService.return_value = ai_service
                ai_service.enhance_scope.return_value = {
                    "description": sample_alfred_task.description,
                    "priority": "medium",
                }

                # Call the function
                result = await enhance_task_scope_logic(
                    api_key="test-key", task_id="TEST-123"
                )

                # Should not call update_task when no changes
                mock_linear_adapter.update_task.assert_not_called()
