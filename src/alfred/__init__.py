"""Alfred Task Manager - AI-powered task management MCP server."""

from alfred.server import main
from alfred.config import Config, get_config
from alfred.mcp import mcp

__version__ = "0.1.0"
__all__ = ["main", "Config", "get_config", "mcp"]
