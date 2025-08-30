"""Configuration validation and error reporting.

Provides user-friendly configuration validation with helpful error messages.
"""

from pathlib import Path
import sys
from typing import Any

from pydantic import ValidationError

from alfred.config import Settings


def validate_configuration() -> Settings:
    """Validate configuration and provide helpful error messages.

    Returns:
        Validated Settings instance

    Raises:
        ConfigurationError: With user-friendly error messages

    """
    try:
        return Settings()
    except ValidationError as e:
        errors = []

        for error in e.errors():
            field_path = " → ".join(str(x) for x in error["loc"])
            error_type = error["type"]

            if error_type == "missing":
                errors.append(f"Missing required configuration: {field_path}")
                errors.append(
                    "  Please set the environment variable or add to .env file"
                )

            elif error_type == "value_error":
                errors.append(f"Invalid value for {field_path}: {error['msg']}")

            elif error_type == "type_error":
                errors.append(f"Wrong type for {field_path}")
                errors.append(
                    f"  Expected: {error.get('ctx', {}).get('expected_type', 'unknown')}"
                )
                errors.append(
                    f"  Got: {type(error.get('ctx', {}).get('actual_value', 'unknown')).__name__}"
                )

            else:
                errors.append(f"Configuration error in {field_path}: {error['msg']}")

        error_message = "\n".join(errors)

        # Create a custom error that follows AlfredError pattern
        from alfred.errors import AlfredError

        class ConfigValidationError(AlfredError):
            """Configuration validation error with detailed information."""

        raise ConfigValidationError(
            user_message="Configuration validation failed. See details below.",
            technical_details=error_message,
            recovery_suggestions="\n".join(
                [
                    "1. Copy .env.sample to .env and fill in your values",
                    "2. Ensure all required API keys are set",
                    "3. Check that file paths are valid",
                    "4. Verify Jira configuration if enabled",
                    "5. Run 'python src/alfred/config_validator.py' to check configuration",
                ],
            ),
        )


def check_environment() -> dict[str, Any]:
    """Check environment and provide setup guidance.

    Returns:
        Dictionary with environment status

    """
    status = {
        "env_file_exists": Path(".env").exists(),
        "sample_exists": Path(".env.sample").exists(),
        "required_vars": [],
        "optional_vars": [],
        "warnings": [],
    }

    # Check for .env file
    if not status["env_file_exists"] and status["sample_exists"]:
        status["warnings"].append(
            "No .env file found. Copy .env.sample to .env and configure it."
        )

    # Check required environment variables
    required = [
        ("GEMINI_API_KEY", "Gemini API key for AI orchestration"),
        ("GOOGLE_API_KEY", "Google API key (alternative to Gemini)"),
    ]

    has_gemini_key = False
    for var, description in required:
        import os

        if os.getenv(var):
            has_gemini_key = True
            status["required_vars"].append(f"FOUND {var}: {description}")
        else:
            status["required_vars"].append(f"MISSING {var}: {description}")

    if not has_gemini_key:
        status["warnings"].append(
            "No Gemini/Google API key found. At least one is required for orchestration."
        )

    # Check optional environment variables
    optional = [
        ("ALFRED_JIRA_API_TOKEN", "Jira API token for task integration"),
    ]

    for var, description in optional:
        import os

        if os.getenv(var):
            status["optional_vars"].append(f"FOUND {var}: {description}")
        else:
            status["optional_vars"].append(f"○ {var}: {description} (optional)")

    return status


def print_configuration_help() -> None:
    """Print configuration help and setup instructions."""
    check_environment()


if __name__ == "__main__":
    # When run directly, show configuration help
    print_configuration_help()

    try:
        settings = validate_configuration()
    except Exception:
        sys.exit(1)
