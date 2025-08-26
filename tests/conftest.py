"""Global test configuration for Alfred Task Manager.

This file provides centralized configuration for all tests including:
- Python path setup for importing from src/
- Environment variable loading from .env
- API key fixtures for graceful test skipping
"""

import os
import sys
import pytest
from pathlib import Path
from dotenv import load_dotenv

# Add src/ to Python path for all tests
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Load environment variables from .env file
env_path = project_root / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path, override=True)


@pytest.fixture(scope="session")
def linear_api_key():
    """Provide Linear API key for tests that need it."""
    return os.getenv("LINEAR_API_KEY")


@pytest.fixture(scope="session")
def anthropic_api_key():
    """Provide Anthropic API key for tests that need it."""
    return os.getenv("ANTHROPIC_API_KEY")


@pytest.fixture(scope="session")
def has_linear_api_key():
    """Check if Linear API key is available (bool)."""
    return bool(os.getenv("LINEAR_API_KEY"))


@pytest.fixture(scope="session")
def has_anthropic_api_key():
    """Check if Anthropic API key is available (bool)."""
    return bool(os.getenv("ANTHROPIC_API_KEY"))


@pytest.fixture(scope="session")
def test_team_name():
    """Provide Linear team name for integration tests."""
    return os.getenv("LINEAR_TEAM_NAME", "Alfred")


def pytest_collection_modifyitems(config, items):
    """Add markers to tests based on their location and requirements."""
    for item in items:
        # Mark tests in integration/ directory as integration tests
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)

        # Mark Linear client tests that make actual API calls as integration tests
        # These should be moved to integration/ directory, but for now mark them
        if "clients/linear" in str(item.fspath):
            # Check if test makes real API calls (not mocked unit tests)
            test_file_content = item.fspath.read_text("utf-8")
            if any(
                pattern in test_file_content
                for pattern in [
                    "LINEAR_API_KEY",
                    "@pytest.mark.skip",
                    "api_key",
                    "real",
                    "live",
                ]
            ) and not any(
                mock_pattern in test_file_content
                for mock_pattern in ["Mock(", "MagicMock(", "@patch", "mock_"]
            ):
                item.add_marker(pytest.mark.integration)
                item.add_marker(pytest.mark.requires_linear_api)


# Define custom markers
def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "integration: integration tests that make real API calls"
    )
    config.addinivalue_line(
        "markers", "requires_linear_api: tests that require LINEAR_API_KEY"
    )
    config.addinivalue_line("markers", "unit: unit tests with mocked dependencies")
