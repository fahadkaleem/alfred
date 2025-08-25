"""Tests for the configuration management system."""

import os
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest
from pydantic import ValidationError

from alfred.config import Config, get_config, set_config
from alfred.config.settings import load_env, ENV_VAR_MAPPING
from alfred.config.storage import (
    get_config_dir,
    ensure_config_dir,
    get_config_file_path,
    read_config_file,
    write_config_file,
    merge_env_overrides,
)


class TestConfig:
    """Test the Config dataclass."""

    def test_config_defaults(self):
        """Test Config creation with default values."""
        config = Config()
        assert config.platform == "linear"
        assert config.linear_api_key is None
        assert config.anthropic_api_key is None
        assert config.workspace_id is None
        assert config.team_id is None
        assert config.claude_model == "claude-3-5-sonnet-20241022"
        assert config.max_tokens == 4096
        assert config.temperature == 0.7

    def test_config_to_dict(self):
        """Test converting Config to dictionary."""
        config = Config(linear_api_key="test_key", workspace_id="workspace123")
        data = config.to_dict()
        assert data["linear_api_key"] == "test_key"
        assert data["workspace_id"] == "workspace123"
        assert "anthropic_api_key" not in data  # None values excluded

    def test_config_from_dict(self):
        """Test creating Config from dictionary."""
        data = {
            "linear_api_key": "test_key",
            "workspace_id": "workspace123",
            "unknown_field": "ignored",  # Should be ignored
        }
        config = Config.from_dict(data)
        assert config.linear_api_key == "test_key"
        assert config.workspace_id == "workspace123"
        assert not hasattr(config, "unknown_field")

    def test_config_empty_string_to_none(self):
        """Test that empty strings are converted to None."""
        data = {"linear_api_key": "", "workspace_id": "valid"}
        config = Config.from_dict(data)
        assert config.linear_api_key is None
        assert config.workspace_id == "valid"


class TestConfigStorage:
    """Test configuration storage and persistence."""

    def test_config_dir_default(self):
        """Test default config directory resolution."""
        with patch.dict(os.environ, {}, clear=True):
            config_dir = get_config_dir()
            assert config_dir == Path.home() / ".alfred"

    def test_config_dir_override(self):
        """Test config directory override via environment."""
        with patch.dict(os.environ, {"ALFRED_CONFIG_DIR": "/tmp/test_alfred"}):
            config_dir = get_config_dir()
            # Use resolve() to handle symlinks (e.g., /tmp -> /private/tmp on macOS)
            assert config_dir == Path("/tmp/test_alfred").resolve()

    def test_config_dir_xdg(self):
        """Test XDG_CONFIG_HOME support on Linux."""
        with patch.dict(os.environ, {"XDG_CONFIG_HOME": "/home/user/.config"}):
            with patch("os.name", "posix"):
                config_dir = get_config_dir()
                assert config_dir == Path("/home/user/.config/alfred")

    def test_ensure_config_dir(self, tmp_path):
        """Test config directory creation."""
        test_dir = tmp_path / "test_alfred"
        with patch.dict(os.environ, {"ALFRED_CONFIG_DIR": str(test_dir)}):
            config_dir = ensure_config_dir()
            assert config_dir.exists()
            assert config_dir.is_dir()

            # Check permissions on POSIX
            if os.name != "nt":
                assert oct(config_dir.stat().st_mode)[-3:] == "700"

    def test_read_write_config_file(self, tmp_path):
        """Test reading and writing config.json."""
        with patch.dict(os.environ, {"ALFRED_CONFIG_DIR": str(tmp_path)}):
            # Write config
            config_data = {"linear_api_key": "test_key", "workspace_id": "workspace123"}
            write_config_file(config_data)

            # Read it back
            read_data = read_config_file()
            assert read_data["linear_api_key"] == "test_key"
            assert read_data["workspace_id"] == "workspace123"

            # Check file permissions on POSIX
            config_file = get_config_file_path()
            if os.name != "nt":
                assert oct(config_file.stat().st_mode)[-3:] == "600"

    def test_read_missing_config_file(self, tmp_path):
        """Test reading non-existent config file returns empty dict."""
        with patch.dict(os.environ, {"ALFRED_CONFIG_DIR": str(tmp_path)}):
            data = read_config_file()
            assert data == {}

    def test_malformed_config_backup(self, tmp_path):
        """Test that malformed config.json is backed up."""
        with patch.dict(os.environ, {"ALFRED_CONFIG_DIR": str(tmp_path)}):
            config_file = get_config_file_path()
            config_file.parent.mkdir(parents=True, exist_ok=True)

            # Write malformed JSON
            config_file.write_text("{ invalid json }")

            # Reading should return empty dict and create backup
            data = read_config_file()
            assert data == {}

            # Check backup was created
            backups = list(config_file.parent.glob("config.json.bak.*"))
            assert len(backups) == 1
            assert backups[0].read_text() == "{ invalid json }"

    def test_atomic_write(self, tmp_path):
        """Test atomic write behavior."""
        with patch.dict(os.environ, {"ALFRED_CONFIG_DIR": str(tmp_path)}):
            # Write initial config
            write_config_file({"key1": "value1"})

            # Simulate partial write failure
            with patch("tempfile.NamedTemporaryFile") as mock_temp:
                mock_temp.side_effect = Exception("Write failed")

                # Should raise but not corrupt existing file
                with pytest.raises(Exception):
                    write_config_file({"key2": "value2"})

                # Original file should still be intact
                data = read_config_file()
                assert data == {"key1": "value1"}

    def test_merge_env_overrides(self):
        """Test merging environment variable overrides."""
        base_config = {
            "linear_api_key": "base_key",
            "workspace_id": "base_workspace",
            "max_tokens": 1024,
        }

        with patch.dict(
            os.environ,
            {"LINEAR_API_KEY": "env_key", "MAX_TOKENS": "2048", "TEMPERATURE": "0.9"},
        ):
            merged = merge_env_overrides(base_config)
            assert merged["linear_api_key"] == "env_key"  # Overridden
            assert merged["workspace_id"] == "base_workspace"  # Not overridden
            assert merged["max_tokens"] == 2048  # Overridden and converted to int
            assert merged["temperature"] == 0.9  # Added from env


class TestConfigManagement:
    """Test the main configuration management functions."""

    def test_get_config_caching(self, tmp_path):
        """Test that get_config caches the configuration."""
        with patch.dict(os.environ, {"ALFRED_CONFIG_DIR": str(tmp_path)}):
            # First call should build config
            config1 = get_config()
            # Second call should return cached
            config2 = get_config()
            assert config1 is config2  # Same instance

            # Refresh should rebuild
            config3 = get_config(refresh=True)
            assert config3 is not config1  # New instance

    def test_set_config(self, tmp_path):
        """Test setting and persisting configuration."""
        with patch.dict(os.environ, {"ALFRED_CONFIG_DIR": str(tmp_path)}):
            config = Config(linear_api_key="new_key", workspace_id="new_workspace")
            set_config(config)

            # Should be persisted to file
            file_data = read_config_file()
            assert file_data["linear_api_key"] == "new_key"
            assert file_data["workspace_id"] == "new_workspace"

            # Should update cache
            cached = get_config()
            assert cached.linear_api_key == "new_key"
            assert cached.workspace_id == "new_workspace"

    def test_workspace_management(self, tmp_path):
        """Test workspace switching and persistence."""
        with patch.dict(os.environ, {"ALFRED_CONFIG_DIR": str(tmp_path)}):
            # Set config with workspace info
            config = Config(
                workspace_id="workspace123", team_id="team456", active_epic_id="epic789"
            )
            set_config(config)

            # Should be persisted
            file_data = read_config_file()
            assert file_data["workspace_id"] == "workspace123"
            assert file_data["team_id"] == "team456"
            assert file_data["active_epic_id"] == "epic789"

            # Read it back
            loaded_config = get_config(refresh=True)
            assert loaded_config.workspace_id == "workspace123"
            assert loaded_config.team_id == "team456"
            assert loaded_config.active_epic_id == "epic789"

    def test_load_env_search_paths(self, tmp_path):
        """Test .env file search paths."""
        # Create .env in temp directory
        env_file = tmp_path / ".env"
        env_file.write_text("TEST_VAR=from_env_file")

        # Clear any existing TEST_VAR
        os.environ.pop("TEST_VAR", None)

        # Load from specific path
        load_env(env_file)
        assert os.environ.get("TEST_VAR") == "from_env_file"

        # Clean up
        os.environ.pop("TEST_VAR", None)

    def test_layered_configuration(self, tmp_path):
        """Test the complete layered configuration precedence."""
        with patch.dict(os.environ, {"ALFRED_CONFIG_DIR": str(tmp_path)}):
            # 1. Write config.json (base layer)
            write_config_file(
                {
                    "linear_api_key": "from_file",
                    "workspace_id": "file_workspace",
                    "max_tokens": 1024,
                }
            )

            # 2. Set environment variables (override layer)
            with patch.dict(
                os.environ, {"LINEAR_API_KEY": "from_env", "TEMPERATURE": "0.8"}
            ):
                # 3. Build config
                config = get_config(refresh=True)

                # Environment should override file
                assert config.linear_api_key == "from_env"
                # File value preserved when no env override
                assert config.workspace_id == "file_workspace"
                # Env adds new value
                assert config.temperature == 0.8
                # File value for max_tokens preserved
                assert config.max_tokens == 1024


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
