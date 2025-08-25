"""Alfred Task Manager - AI-powered task management MCP server."""

from alfred.server import create_server, main
from alfred.config import Config, get_config

__version__ = "0.1.0"
__all__ = ["create_server", "main", "Config", "get_config"]
