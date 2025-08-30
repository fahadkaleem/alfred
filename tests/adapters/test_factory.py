"""Unit tests for the adapter factory."""

import pytest
from unittest.mock import patch, MagicMock

from alfred.adapters.factory import get_adapter
from alfred.adapters.base import AuthError
from alfred.adapters.linear_adapter import LinearAdapter
from alfred.models.config import Config, Platform


class TestGetAdapter:
    """Test cases for get_adapter factory function."""

    def test_get_adapter_linear_success(self):
        """Test successful Linear adapter creation."""
        config = Config(
            platform=Platform.LINEAR,
            linear_api_key="test-linear-key",
            team_id="test-team-id",
        )

        with patch("alfred.adapters.factory.LinearAdapter") as MockLinearAdapter:
            mock_adapter = MagicMock()
            MockLinearAdapter.return_value = mock_adapter

            adapter = get_adapter(config)

            MockLinearAdapter.assert_called_once_with(
                api_token="test-linear-key", team_name="test-team-id"
            )
            assert adapter == mock_adapter

    def test_get_adapter_linear_missing_api_key(self):
        """Test Linear adapter creation fails when API key is missing."""
        config = Config(
            platform=Platform.LINEAR,
            linear_api_key=None,  # Missing API key
            team_id="test-team-id",
        )

        with pytest.raises(
            AuthError, match="Linear API key required for Linear platform"
        ):
            get_adapter(config)

    def test_get_adapter_linear_empty_api_key(self):
        """Test Linear adapter creation fails when API key is empty string (converted to None)."""
        config = Config(
            platform=Platform.LINEAR,
            linear_api_key="",  # Empty string gets converted to None by validator
            team_id="test-team-id",
        )

        with pytest.raises(
            AuthError, match="Linear API key required for Linear platform"
        ):
            get_adapter(config)

    def test_get_adapter_jira_not_implemented(self):
        """Test Jira adapter raises NotImplementedError (temporary)."""
        config = Config(
            platform=Platform.JIRA,
            jira_api_key="test-jira-key",
            jira_url="https://test.atlassian.net",
            jira_email="test@example.com",
        )

        with pytest.raises(
            NotImplementedError, match="Jira adapter not yet implemented"
        ):
            get_adapter(config)

    def test_get_adapter_unsupported_platform(self):
        """Test unsupported platform raises ValueError."""
        # Create a mock config with an invalid platform
        config = Config(platform=Platform.LINEAR)
        config.platform = "unsupported_platform"  # Bypass enum validation

        with pytest.raises(
            ValueError, match="Unsupported platform: unsupported_platform"
        ):
            get_adapter(config)

    def test_get_adapter_returns_task_adapter_interface(self):
        """Test that returned adapter implements TaskAdapter interface."""
        config = Config(
            platform=Platform.LINEAR,
            linear_api_key="test-linear-key",
            team_id="test-team-id",
        )

        with patch("alfred.adapters.factory.LinearAdapter") as MockLinearAdapter:
            mock_adapter = MagicMock()
            MockLinearAdapter.return_value = mock_adapter

            adapter = get_adapter(config)

            # Verify that the mock was properly set up to simulate TaskAdapter interface
            assert adapter == mock_adapter

    def test_get_adapter_with_minimal_linear_config(self):
        """Test Linear adapter creation with minimal required config."""
        config = Config(
            platform=Platform.LINEAR,
            linear_api_key="test-linear-key",
            # No team_id provided
        )

        with patch("alfred.adapters.factory.LinearAdapter") as MockLinearAdapter:
            mock_adapter = MagicMock()
            MockLinearAdapter.return_value = mock_adapter

            adapter = get_adapter(config)

            MockLinearAdapter.assert_called_once_with(
                api_token="test-linear-key",
                team_name=None,  # Should handle None team_name
            )
            assert adapter == mock_adapter


class TestFactoryIntegration:
    """Integration tests for factory with real config objects."""

    def test_factory_with_config_from_dict(self):
        """Test factory works with Config created from dictionary."""
        config_dict = {
            "platform": "linear",
            "linear_api_key": "test-key",
            "team_id": "test-team",
        }
        config = Config.from_dict(config_dict)

        with patch("alfred.adapters.factory.LinearAdapter") as MockLinearAdapter:
            mock_adapter = MagicMock()
            MockLinearAdapter.return_value = mock_adapter

            adapter = get_adapter(config)

            assert adapter == mock_adapter
            MockLinearAdapter.assert_called_once_with(
                api_token="test-key", team_name="test-team"
            )

    def test_factory_respects_platform_enum(self):
        """Test factory properly handles Platform enum values."""
        config = Config()
        assert config.platform == Platform.LINEAR  # Default should be LINEAR

        # Test that the factory can handle the default platform
        with patch("alfred.adapters.factory.LinearAdapter") as MockLinearAdapter:
            mock_adapter = MagicMock()
            MockLinearAdapter.return_value = mock_adapter

            # This should fail due to missing API key, not platform issue
            with pytest.raises(AuthError):
                get_adapter(config)
