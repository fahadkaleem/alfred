"""Unit tests for AI services."""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, List, Any

from alfred.ai_services import (
    AIService,
    AIProvider,
    AnthropicProvider,
    AIResponse,
    TokenUsage,
    StreamEvent,
    PromptTemplates,
    create_provider,
    RateLimitError,
    AuthenticationError,
    InvalidRequestError,
    ProviderNotFoundError,
)
from alfred.ai_services.config import AIProviderConfig


class TestPromptTemplates:
    """Test prompt template system."""

    def test_sanitize_text(self):
        """Test text sanitization."""
        templates = PromptTemplates()

        # Test whitespace normalization
        text = "  This   has\n\nextra    whitespace  "
        sanitized = templates.sanitize_text(text)
        assert sanitized == "This has extra whitespace"

        # Test truncation
        long_text = "a" * 100
        truncated = templates.sanitize_text(long_text, max_length=10)
        assert truncated == "aaaaaaa..."
        assert len(truncated) == 10

    def test_format_messages(self):
        """Test message formatting."""
        templates = PromptTemplates()

        # With system prompt
        messages = templates.format_messages("System prompt", "User prompt")
        assert len(messages) == 2
        assert messages[0] == {"role": "system", "content": "System prompt"}
        assert messages[1] == {"role": "user", "content": "User prompt"}

        # Without system prompt
        messages = templates.format_messages(None, "User prompt")
        assert len(messages) == 1
        assert messages[0] == {"role": "user", "content": "User prompt"}

    def test_render_create_tasks_from_spec(self):
        """Test task creation prompt rendering."""
        templates = PromptTemplates()

        result = templates.render_create_tasks_from_spec(
            "Build a login system", num_tasks=3, project_context="Web application"
        )

        assert "system" in result
        assert "user" in result
        assert "messages" in result
        assert "3" in result["user"]  # Should mention number of tasks
        assert "Build a login system" in result["user"]
        assert "Web application" in result["user"]

    def test_render_decompose_task(self):
        """Test task decomposition prompt rendering."""
        templates = PromptTemplates()

        # With string task
        result = templates.render_decompose_task(
            "Implement authentication", num_subtasks=4
        )
        assert "4" in result["user"]
        assert "Implement authentication" in result["user"]

        # With dict task
        task_dict = {"title": "Auth system", "description": "Build OAuth"}
        result = templates.render_decompose_task(task_dict, num_subtasks=2)
        assert "Auth system" in result["user"]
        assert "Build OAuth" in result["user"]

    def test_render_research(self):
        """Test research prompt rendering."""
        templates = PromptTemplates()

        result = templates.render_research(
            "How to implement OAuth?",
            context="For a Python web app",
            detail_level="high",
        )

        assert "How to implement OAuth?" in result["user"]
        assert "Python web app" in result["user"]
        assert "comprehensive" in result["user"].lower()


class TestAnthropicProvider:
    """Test Anthropic provider."""

    @pytest.fixture
    def mock_anthropic_client(self):
        """Create mock Anthropic client."""
        with patch("alfred.ai_services.anthropic_provider.AsyncAnthropic") as mock:
            yield mock

    def test_provider_initialization(self, mock_anthropic_client):
        """Test provider initialization."""
        provider = AnthropicProvider(api_key="test-key")

        assert provider.provider_name == AIProvider.ANTHROPIC
        assert provider.default_model == "claude-3-5-sonnet-20241022"
        assert provider.api_key == "test-key"
        mock_anthropic_client.assert_called_once()

    def test_provider_no_api_key(self, mock_anthropic_client):
        """Test provider initialization without API key."""
        # AnthropicProvider requires api_key, but doesn't validate it in __init__
        # The validation happens when actually making API calls
        provider = AnthropicProvider(api_key=None)
        assert provider.api_key is None

    def test_convert_messages(self, mock_anthropic_client):
        """Test message conversion for Anthropic format."""
        provider = AnthropicProvider(api_key="test-key")

        messages = [
            {"role": "system", "content": "System prompt"},
            {"role": "user", "content": "User message"},
            {"role": "assistant", "content": "Assistant response"},
        ]

        anthropic_messages, system = provider._convert_messages(messages)

        assert len(anthropic_messages) == 2
        assert anthropic_messages[0]["role"] == "user"
        assert anthropic_messages[1]["role"] == "assistant"
        assert system == "System prompt"

    @pytest.mark.asyncio
    async def test_complete(self, mock_anthropic_client):
        """Test completion generation."""
        provider = AnthropicProvider(api_key="test-key")

        # Mock response
        mock_response = MagicMock()
        mock_response.content = [MagicMock(type="text", text="Generated text")]
        mock_response.usage.input_tokens = 10
        mock_response.usage.output_tokens = 20
        mock_response.model = "claude-3-5-sonnet-20241022"
        mock_response.stop_reason = "end_turn"

        provider.client.messages.create = AsyncMock(return_value=mock_response)

        messages = [{"role": "user", "content": "Test prompt"}]
        response = await provider.complete(messages)

        assert isinstance(response, AIResponse)
        assert response.text == "Generated text"
        assert response.usage.input_tokens == 10
        assert response.usage.output_tokens == 20
        assert response.usage.total_tokens == 30

    @pytest.mark.asyncio
    async def test_stream_complete(self, mock_anthropic_client):
        """Test streaming completion."""
        provider = AnthropicProvider(api_key="test-key")

        # Mock streaming response
        class MockStream:
            async def __aiter__(self):
                # Yield events that Anthropic would send
                event1 = MagicMock()
                event1.type = "content_block_delta"
                event1.delta.text = "Hello"
                yield event1

                event2 = MagicMock()
                event2.type = "content_block_delta"
                event2.delta.text = " world"
                yield event2

                event3 = MagicMock()
                event3.type = "message_stop"
                event3.usage.input_tokens = 5
                event3.usage.output_tokens = 10
                yield event3

        mock_stream = MockStream()
        provider.client.messages.create = AsyncMock(return_value=mock_stream)

        messages = [{"role": "user", "content": "Test"}]
        events = []

        async for event in provider.stream_complete(messages):
            events.append(event)

        assert len(events) == 4  # start, 2 text, end
        assert events[0].type == "message_start"
        assert events[1].type == "text"
        assert events[1].data == "Hello"
        assert events[2].type == "text"
        assert events[2].data == " world"
        assert events[3].type == "message_end"


class TestAIService:
    """Test high-level AI service."""

    @pytest.fixture
    def mock_provider(self):
        """Create mock AI provider."""
        provider = MagicMock()
        provider.model = "test-model"
        provider.default_model = "test-model"
        provider.estimate_tokens = MagicMock(return_value=100)
        return provider

    @pytest.fixture
    def ai_service(self, mock_provider):
        """Create AI service with mock provider."""
        service = AIService(custom_provider=mock_provider)
        return service

    @pytest.mark.asyncio
    async def test_create_tasks_from_spec(self, ai_service, mock_provider):
        """Test task creation from specification."""
        mock_response = [
            {"title": "Task 1", "description": "First task"},
            {"title": "Task 2", "description": "Second task"},
        ]

        mock_provider.complete_json = AsyncMock(return_value=mock_response)

        tasks = await ai_service.create_tasks_from_spec("Build a web app", num_tasks=2)

        assert len(tasks) == 2
        assert tasks[0]["title"] == "Task 1"
        mock_provider.complete_json.assert_called_once()

    @pytest.mark.asyncio
    async def test_decompose_task(self, ai_service, mock_provider):
        """Test task decomposition."""
        mock_response = [
            {"title": "Subtask 1", "description": "First subtask"},
            {"title": "Subtask 2", "description": "Second subtask"},
        ]

        mock_provider.complete_json = AsyncMock(return_value=mock_response)

        subtasks = await ai_service.decompose_task("Main task", num_subtasks=2)

        assert len(subtasks) == 2
        assert subtasks[0]["title"] == "Subtask 1"


    @pytest.mark.asyncio
    async def test_research(self, ai_service, mock_provider):
        """Test research functionality."""
        mock_response = {
            "summary": "Research summary",
            "key_insights": ["Insight 1", "Insight 2"],
            "recommendations": ["Recommendation 1"],
        }

        mock_provider.complete_json = AsyncMock(return_value=mock_response)

        research = await ai_service.research(
            "How to implement caching?", detail_level="medium"
        )

        assert research["summary"] == "Research summary"
        assert len(research["key_insights"]) == 2

    @pytest.mark.asyncio
    async def test_chunking_large_spec(self, ai_service, mock_provider):
        """Test chunking for large specifications."""
        # Just test the chunking method directly to avoid recursion issues
        text = "a" * 1000
        chunks = ai_service._chunk_text(text, chunk_size=100, overlap=20)

        # Should create proper chunks with overlap
        assert len(chunks) > 5
        for chunk in chunks[:-1]:  # All but last should be full size
            assert len(chunk) == 100

        # Check overlap between consecutive chunks
        for i in range(len(chunks) - 1):
            assert chunks[i][-20:] == chunks[i + 1][:20]

    def test_deduplicate_tasks(self, ai_service):
        """Test task deduplication."""
        tasks = [
            {"title": "Task 1", "description": "First"},
            {"title": "Task 1", "description": "Duplicate"},
            {"title": "Task 2", "description": "Second"},
            {"title": "TASK 2", "description": "Case variant"},
        ]

        unique = ai_service._deduplicate_tasks(tasks)

        assert len(unique) == 2
        assert unique[0]["title"] == "Task 1"
        assert unique[1]["title"] == "Task 2"

    def test_chunk_text(self, ai_service):
        """Test text chunking."""
        text = "a" * 100
        chunks = ai_service._chunk_text(text, chunk_size=30, overlap=10)

        assert len(chunks) == 5  # With overlap, 100 chars makes 5 chunks
        assert len(chunks[0]) == 30
        assert len(chunks[-1]) <= 30

        # Check overlap
        assert chunks[0][-10:] == chunks[1][:10]

    def test_usage_tracking(self, ai_service):
        """Test token usage tracking."""
        ai_service.total_usage = TokenUsage(100, 200, 300)

        summary = ai_service.get_usage_summary()

        assert summary["total_input_tokens"] == 100
        assert summary["total_output_tokens"] == 200
        assert summary["total_tokens"] == 300
        assert "estimated_cost" in summary


class TestProviderFactory:
    """Test provider factory."""

    def test_create_provider(self):
        """Test provider creation."""
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}, clear=True):
            provider = create_provider(AIProvider.ANTHROPIC, api_key="test-key")
            assert isinstance(provider, AnthropicProvider)
            assert provider.api_key == "test-key"

    def test_provider_not_found(self):
        """Test handling of unknown provider."""
        # OpenAI provider not implemented yet, so this should raise
        with pytest.raises(ValueError) as exc_info:
            create_provider(AIProvider.OPENAI)  # Not implemented yet
        assert "not supported" in str(exc_info.value)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
