"""Tests for adapter factory migration to ensure no regressions."""

import pytest
from unittest.mock import Mock, patch
from alfred.adapters.factory import get_adapter
from alfred.models.config import Config, Platform
from alfred.adapters.base import AuthError
from alfred.adapters.linear_adapter import LinearAdapter

# Import some core business logic functions to test they work with factory
from alfred.core.tasks.create import create_task_logic
from alfred.core.tasks.get import get_task_logic
from alfred.core.epics.create import create_epic_logic
from alfred.core.epics.list import list_epics_logic


class TestAdapterFactoryMigration:
    """Test that all refactored modules use the adapter factory correctly."""

    def test_factory_creates_linear_adapter_for_linear_platform(self):
        """Test factory creates LinearAdapter when platform is linear."""
        config = Config(
            platform=Platform.LINEAR, linear_api_key="test-key-123", team_id="team-123"
        )

        adapter = get_adapter(config)
        assert isinstance(adapter, LinearAdapter)

    def test_factory_raises_auth_error_for_missing_linear_key(self):
        """Test factory raises AuthError when linear API key is missing."""
        config = Config(
            platform=Platform.LINEAR,
            linear_api_key=None,  # Missing key
            team_id="team-123",
        )

        with pytest.raises(AuthError, match="Linear API key required"):
            get_adapter(config)

    def test_factory_raises_not_implemented_for_jira(self):
        """Test factory raises NotImplementedError for Jira platform (Phase 4)."""
        config = Config(
            platform=Platform.JIRA,
            jira_api_key="jira-key",
            jira_url="https://test.atlassian.net",
            jira_email="test@example.com",
        )

        with pytest.raises(
            NotImplementedError, match="Jira adapter not yet implemented"
        ):
            get_adapter(config)


class TestBusinessLogicUseFactory:
    """Test that business logic functions correctly use the factory."""

    @patch("alfred.core.tasks.create.get_adapter")
    def test_create_task_logic_uses_factory(self, mock_get_adapter):
        """Test create_task_logic uses factory instead of direct LinearAdapter."""
        # Setup mock
        mock_adapter = Mock()
        mock_adapter.create_task.return_value = {
            "id": "task-123",
            "title": "Test Task",
            "description": "Test Description",
            "status": "pending",
            "priority": "medium",
        }
        mock_get_adapter.return_value = mock_adapter

        # Setup config
        config = Config(
            platform=Platform.LINEAR, linear_api_key="test-key", team_id="team-123"
        )

        # Call function
        result = create_task_logic(
            config=config, title="Test Task", description="Test Description"
        )

        # Verify factory was called with config
        mock_get_adapter.assert_called_once_with(config)

        # Verify adapter method was called
        mock_adapter.create_task.assert_called_once_with(
            title="Test Task", description="Test Description", epic_id=None
        )

        # Verify result structure
        assert result["id"] == "task-123"
        assert result["title"] == "Test Task"

    @patch("alfred.core.tasks.get.get_adapter")
    def test_get_task_logic_uses_factory(self, mock_get_adapter):
        """Test get_task_logic uses factory instead of direct LinearAdapter."""
        # Setup mock
        mock_adapter = Mock()
        mock_adapter.get_task.return_value = {
            "id": "task-123",
            "title": "Existing Task",
            "description": "Task Description",
            "status": "pending",
            "priority": "high",
        }
        mock_get_adapter.return_value = mock_adapter

        # Setup config
        config = Config(
            platform=Platform.LINEAR, linear_api_key="test-key", team_id="team-123"
        )

        # Call function
        result = get_task_logic(config=config, task_id="task-123")

        # Verify factory was called
        mock_get_adapter.assert_called_once_with(config)

        # Verify adapter method was called
        mock_adapter.get_task.assert_called_once_with("task-123")

        # Verify result
        assert result["id"] == "task-123"
        assert result["title"] == "Existing Task"

    @patch("alfred.core.epics.create.get_adapter")
    @pytest.mark.asyncio
    async def test_create_epic_logic_uses_factory(self, mock_get_adapter):
        """Test create_epic_logic uses factory instead of direct LinearAdapter."""
        # Setup mock
        mock_adapter = Mock()
        mock_adapter.create_epic.return_value = {
            "id": "epic-123",
            "name": "Test Epic",
            "description": "Epic Description",
            "url": "https://linear.app/epic-123",
        }
        mock_get_adapter.return_value = mock_adapter

        # Setup config
        config = Config(
            platform=Platform.LINEAR, linear_api_key="test-key", team_id="team-123"
        )

        # Call function
        result = await create_epic_logic(
            config=config, name="Test Epic", description="Epic Description"
        )

        # Verify factory was called
        mock_get_adapter.assert_called_once_with(config)

        # Verify adapter method was called
        mock_adapter.create_epic.assert_called_once_with(
            name="Test Epic", description="Epic Description"
        )

        # Verify result structure
        assert result["status"] == "ok"
        assert result["epic"]["id"] == "epic-123"
        assert result["epic"]["name"] == "Test Epic"

    @patch("alfred.core.epics.list.get_adapter")
    @pytest.mark.asyncio
    async def test_list_epics_logic_uses_factory(self, mock_get_adapter):
        """Test list_epics_logic uses factory instead of direct LinearAdapter."""
        # Setup mock
        mock_adapter = Mock()
        mock_adapter.get_epics.return_value = [
            {
                "id": "epic-1",
                "name": "Epic 1",
                "description": "First epic",
                "url": "https://linear.app/epic-1",
            },
            {
                "id": "epic-2",
                "name": "Epic 2",
                "description": "Second epic",
                "url": "https://linear.app/epic-2",
            },
        ]
        mock_get_adapter.return_value = mock_adapter

        # Setup config
        config = Config(
            platform=Platform.LINEAR, linear_api_key="test-key", team_id="team-123"
        )

        # Call function
        result = await list_epics_logic(config=config)

        # Verify factory was called
        mock_get_adapter.assert_called_once_with(config)

        # Verify adapter method was called
        mock_adapter.get_epics.assert_called_once_with(limit=100)

        # Verify result structure
        assert result["status"] == "ok"
        assert result["count"] == 2
        assert len(result["projects"]) == 2
        assert result["projects"][0]["id"] == "epic-1"
        assert result["projects"][1]["name"] == "Epic 2"


class TestNoDirectLinearAdapterImports:
    """Verify no business logic directly imports LinearAdapter anymore."""

    def test_no_direct_imports_in_core_modules(self):
        """Test that core modules don't directly import LinearAdapter."""
        import ast
        import os
        from pathlib import Path

        core_dir = Path("src/alfred/core")
        direct_imports = []

        if core_dir.exists():
            for py_file in core_dir.rglob("*.py"):
                if py_file.name == "__init__.py":
                    continue

                try:
                    with open(py_file, "r") as f:
                        content = f.read()

                    # Parse AST to find imports
                    tree = ast.parse(content)

                    for node in ast.walk(tree):
                        if isinstance(node, ast.ImportFrom):
                            if (
                                node.module
                                and "linear_adapter" in node.module
                                and any(
                                    alias.name == "LinearAdapter"
                                    for alias in node.names
                                )
                            ):
                                direct_imports.append(str(py_file))
                        elif isinstance(node, ast.Import):
                            for alias in node.names:
                                if "linear_adapter" in alias.name:
                                    direct_imports.append(str(py_file))

                except Exception:
                    # Skip files that can't be parsed
                    continue

        assert not direct_imports, (
            f"Found direct LinearAdapter imports in: {direct_imports}"
        )
