"""Tests for create_tasks_from_spec functionality."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from alfred.core.tasks.models import TaskSuggestion, EpicSuggestion, GenerationResult
from alfred.core.tasks.utilities import (
    estimate_tokens,
    chunk_markdown,
    safe_extract_json,
    parse_ai_response,
    merge_task_candidates,
    map_priority_to_linear,
)


class TestUtilities:
    """Test utility functions."""

    def test_estimate_tokens(self):
        """Test token estimation."""
        text = "This is a test string"
        tokens = estimate_tokens(text)
        assert tokens == len(text) // 4

    def test_chunk_markdown_single_chunk(self):
        """Test chunking with content that fits in one chunk."""
        text = "Short content"
        chunks = chunk_markdown(text, target_tokens=100)
        assert len(chunks) == 1
        assert chunks[0] == text

    def test_chunk_markdown_multiple_chunks(self):
        """Test chunking with large content."""
        # Create large text that needs chunking
        text = "\n\n".join(["This is paragraph " + str(i) for i in range(100)])
        chunks = chunk_markdown(text, target_tokens=50, overlap_tokens=10)
        assert len(chunks) > 1
        # Check all content is preserved
        combined = " ".join(chunks)
        assert all(f"paragraph {i}" in combined for i in range(100))

    def test_safe_extract_json_direct(self):
        """Test extracting valid JSON."""
        json_str = '{"title": "Test Task"}'
        result = safe_extract_json(json_str)
        assert result == {"title": "Test Task"}

    def test_safe_extract_json_code_block(self):
        """Test extracting JSON from code block."""
        text = '```json\n{"title": "Test Task"}\n```'
        result = safe_extract_json(text)
        assert result == {"title": "Test Task"}

    def test_safe_extract_json_with_trailing_comma(self):
        """Test extracting JSON with trailing comma."""
        text = '{"title": "Test Task",}'
        result = safe_extract_json(text)
        assert result == {"title": "Test Task"}

    def test_parse_ai_response_list(self):
        """Test parsing AI response as list."""
        response = [
            {"title": "Task 1", "description": "Desc 1", "priority": "high"},
            {"title": "Task 2", "description": "Desc 2", "priority": "medium"},
        ]
        result = parse_ai_response(response)
        assert len(result.tasks) == 2
        assert result.tasks[0].title == "Task 1"
        assert result.tasks[0].priority == "P1"  # high -> P1
        assert result.tasks[1].priority == "P2"  # medium -> P2

    def test_parse_ai_response_dict_with_tasks(self):
        """Test parsing AI response as dict with tasks."""
        response = {
            "tasks": [{"title": "Task 1", "description": "Desc 1", "complexity": 7}],
            "epic": {
                "title": "Epic Title",
                "description": "Epic Desc",
                "create_epic": True,
            },
        }
        result = parse_ai_response(response)
        assert len(result.tasks) == 1
        assert result.epic is not None
        assert result.epic.title == "Epic Title"

    def test_merge_task_candidates(self):
        """Test merging and deduplicating tasks."""
        tasks = [
            TaskSuggestion(title="Task One", description="Desc", priority="P0"),
            TaskSuggestion(
                title="task-one", description="Desc", priority="P1"
            ),  # Duplicate
            TaskSuggestion(title="Task Two", description="Desc", priority="P1"),
            TaskSuggestion(title="Task Three", description="Desc", priority="P2"),
        ]
        merged = merge_task_candidates(tasks, limit=2)
        assert len(merged) == 2
        assert merged[0].priority == "P0"  # Highest priority first

    def test_map_priority_to_linear(self):
        """Test priority mapping."""
        assert map_priority_to_linear("P0") == 3  # Urgent
        assert map_priority_to_linear("P1") == 2  # High
        assert map_priority_to_linear("P2") == 1  # Medium
        assert map_priority_to_linear("P3") == 0  # Low


@pytest.mark.asyncio
class TestCreateFromSpec:
    """Test create_from_spec business logic."""

    @patch("alfred.core.tasks.create_from_spec.read_spec_file")
    @patch("alfred.core.tasks.create_from_spec.AIService")
    @patch("alfred.core.tasks.create_from_spec.LinearTaskCreator")
    async def test_create_tasks_from_spec_success(
        self, mock_linear_cls, mock_ai_cls, mock_read_spec
    ):
        """Test successful task creation from spec."""
        from alfred.core.tasks.create_from_spec import create_tasks_from_spec_logic
        from alfred.core.tasks.models import LinearTaskCreated, LinearEpicCreated

        # Mock file reading
        mock_read_spec.return_value = {"content": "Test specification content"}

        # Mock AI service
        mock_ai = AsyncMock()
        mock_orchestrator = AsyncMock()
        mock_orchestrator.generate_task_plan.return_value = GenerationResult(
            tasks=[
                TaskSuggestion(title="Task 1", description="Desc 1"),
                TaskSuggestion(title="Task 2", description="Desc 2"),
            ],
            epic=EpicSuggestion(title="Test Epic", description="Epic desc"),
        )
        mock_ai_cls.return_value = mock_ai

        # Mock Linear creator
        mock_linear = AsyncMock()
        mock_linear.ensure_epic_if_needed.return_value = LinearEpicCreated(
            id="epic-1", title="Test Epic", url="https://linear.app/epic/1"
        )
        mock_linear.batch_create_tasks.return_value = [
            LinearTaskCreated(
                id="task-1", title="Task 1", url="https://linear.app/task/1"
            ),
            LinearTaskCreated(
                id="task-2", title="Task 2", url="https://linear.app/task/2"
            ),
        ]
        mock_linear.create_task_dependencies.return_value = []
        mock_linear_cls.return_value = mock_linear

        # Patch orchestrator
        with patch(
            "alfred.core.tasks.create_from_spec.TaskGenerationOrchestrator"
        ) as mock_orch_cls:
            mock_orch_cls.return_value = mock_orchestrator

            result = await create_tasks_from_spec_logic(
                spec_path="/test/spec.txt",
                num_tasks=2,
                api_key="test-key",
                team_id="team-1",
                epic_name="Test Epic",
            )

        assert result["success"] is True
        assert len(result["tasks"]) == 2
        assert result["epic"]["title"] == "Test Epic"
        assert result["summary"]["created"] == 2
        assert result["summary"]["team_id"] == "team-1"

    @patch("alfred.core.tasks.create_from_spec.read_spec_file")
    @patch("alfred.core.tasks.create_from_spec.AIService")
    async def test_create_tasks_empty_spec(self, mock_ai_cls, mock_read_spec):
        """Test handling empty specification."""
        from alfred.core.tasks.create_from_spec import create_tasks_from_spec_logic

        # Mock empty file
        mock_read_spec.return_value = {
            "error": "EMPTY_FILE",
            "message": "Specification file is empty",
        }

        result = await create_tasks_from_spec_logic(
            spec_path="/test/empty.txt",
            num_tasks=5,
            api_key="test-key",
            team_id="team-1",
        )

        assert result["success"] is False
        assert result["error"]["code"] == "EMPTY_FILE"

    @patch("alfred.core.tasks.create_from_spec.read_spec_file")
    @patch("alfred.core.tasks.create_from_spec.AIService")
    async def test_create_tasks_invalid_num_tasks(self, mock_ai_cls, mock_read_spec):
        """Test handling invalid number of tasks."""
        from alfred.core.tasks.create_from_spec import create_tasks_from_spec_logic

        # Mock valid file
        mock_read_spec.return_value = {"content": "Test spec"}

        result = await create_tasks_from_spec_logic(
            spec_path="/test/spec.txt",
            num_tasks=100,  # Too many
            api_key="test-key",
            team_id="team-1",
        )

        assert result["success"] is False
        assert result["error"]["code"] == "INVALID_NUM_TASKS"

    @patch("alfred.core.tasks.create_from_spec.read_spec_file")
    @patch("alfred.core.tasks.create_from_spec.AIService")
    async def test_create_tasks_file_not_found(self, mock_ai_cls, mock_read_spec):
        """Test handling file not found."""
        from alfred.core.tasks.create_from_spec import create_tasks_from_spec_logic

        # Mock file not found
        mock_read_spec.return_value = {
            "error": "FILE_NOT_FOUND",
            "message": "Specification file does not exist",
        }

        result = await create_tasks_from_spec_logic(
            spec_path="/test/nonexistent.txt",
            num_tasks=5,
            api_key="test-key",
            team_id="team-1",
        )

        assert result["success"] is False
        assert result["error"]["code"] == "FILE_NOT_FOUND"


class TestModels:
    """Test Pydantic models."""

    def test_task_suggestion_validation(self):
        """Test TaskSuggestion model validation."""
        # Valid task
        task = TaskSuggestion(
            title="Test Task", description="Description", priority="P1", complexity=5
        )
        assert task.title == "Test Task"
        assert task.priority == "P1"

        # Test title validation
        with pytest.raises(ValueError):
            TaskSuggestion(
                title="",  # Empty title
                description="Description",
            )

    def test_epic_suggestion_validation(self):
        """Test EpicSuggestion model validation."""
        epic = EpicSuggestion(title="Test Epic", description="Epic description")
        assert epic.title == "Test Epic"
        assert epic.create_epic is True  # Default value

    def test_generation_result_validation(self):
        """Test GenerationResult model validation."""
        # Valid result
        result = GenerationResult(
            tasks=[TaskSuggestion(title="Task 1", description="Desc")]
        )
        assert len(result.tasks) == 1

        # Test empty tasks validation
        with pytest.raises(ValueError):
            GenerationResult(tasks=[])
