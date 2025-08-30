"""Adapter factory for platform abstraction."""

from typing import Optional
from alfred.models.config import Config, Platform
from alfred.adapters.base import TaskAdapter, AuthError
from alfred.adapters.linear_adapter import LinearAdapter
# from alfred.adapters.jira_adapter import JiraAdapter  # Phase 4


def get_adapter(config: Config) -> TaskAdapter:
    """
    Factory function to get the appropriate adapter based on platform config.

    Args:
        config: Alfred configuration object with platform and API keys

    Returns:
        TaskAdapter implementation for the configured platform

    Raises:
        ValueError: If platform is not supported
        AuthError: If required API keys are missing
    """
    if config.platform == Platform.LINEAR:
        if not config.linear_api_key:
            raise AuthError("Linear API key required for Linear platform")
        return LinearAdapter(
            api_token=config.linear_api_key,
            team_name=config.team_name,
        )
    elif config.platform == Platform.JIRA:
        # Phase 4: Implement JiraAdapter
        raise NotImplementedError("Jira adapter not yet implemented")
        # if not config.jira_api_key:
        #     raise AuthError("Jira API key required for Jira platform")
        # return JiraAdapter(
        #     api_key=config.jira_api_key,
        #     url=config.jira_url,
        #     email=config.jira_email
        # )
    else:
        raise ValueError(f"Unsupported platform: {config.platform}")
