from typing import Any
from pydantic import BaseModel
from fastmcp import FastMCP
from alfred.config import Config, get_config
from alfred.utils import get_logger, SessionManager
import logging


class MCPState(BaseModel):
    """Type-safe state container for MCP server."""

    model_config = {"arbitrary_types_allowed": True}

    config: Config
    logger: logging.Logger
    session_manager: SessionManager


# Single global MCP instance
mcp = FastMCP(
    name="Alfred Task Manager",
    instructions="""
    Alfred is an AI-powered task management system that interfaces with Linear and Jira.
    It provides intelligent task creation, analysis, and management capabilities.
    
    Key features:
    - Parse PRDs and specifications to generate tasks
    - Analyze task complexity and provide recommendations
    - Manage task dependencies and hierarchies
    - AI-powered task enhancement and simplification
    
    Use 'initialize_project' to connect to your Linear/Jira workspace.
    """,
)

# Attach typed state for tools to access
mcp.state = MCPState(
    config=get_config(),
    logger=get_logger("alfred.mcp"),
    session_manager=SessionManager(),
)
