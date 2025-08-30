from fastmcp import FastMCP
from alfred.config import get_config
from alfred.utils import get_logger, SessionManager

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

# Attach config and utilities to state for tools to access
mcp.state = {
    "config": get_config(),
    "logger": get_logger("alfred.mcp"),
    "session_manager": SessionManager(),
}
