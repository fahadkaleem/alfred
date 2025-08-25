"""Main FastMCP server implementation for Alfred Task Manager."""

import os
import sys
from typing import Optional, Any, Dict
from fastmcp import FastMCP

from alfred.config import get_config
from alfred.utils import (
    get_logger,
    SessionManager,
    to_mcp_error,
    AlfredError,
    BadRequestError,
)
from alfred import tools


def create_server() -> FastMCP:
    """
    Create and configure the Alfred FastMCP server.

    Returns:
        Configured FastMCP server instance
    """
    # Load configuration
    config = get_config()
    logger = get_logger("alfred.server")

    # Create FastMCP server with metadata
    server = FastMCP(
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

    # Initialize session manager and attach to server state
    server.state = {}
    server.state["session_manager"] = SessionManager()
    server.state["config"] = config
    server.state["logger"] = logger

    logger.info("Created Alfred FastMCP server")

    return server


def register_tools(server: FastMCP) -> int:
    """
    Register all tools with the server.

    This function discovers and registers tools from the tools package.

    Args:
        server: FastMCP server instance

    Returns:
        Number of tools registered
    """
    logger = server.state["logger"]

    # Import tools package for discovery
    try:
        tool_count = tools.register_tools(server)
        logger.info(f"Registered {tool_count} tools")
        return tool_count
    except ImportError as e:
        logger.warning(f"Tools package not available: {e}")
        return 0
    except Exception as e:
        logger.error(f"Error registering tools: {e}", exc_info=True)
        return 0


def run_stdio(server: FastMCP) -> None:
    """
    Run the server on stdio transport.

    Args:
        server: FastMCP server instance
    """
    logger = server.state["logger"]

    try:
        logger.info("Starting Alfred MCP server on stdio transport")
        server.run(transport="stdio")
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        raise


def main() -> None:
    """Main entry point for the Alfred MCP server."""
    # Setup logging
    logger = get_logger("alfred.server")

    try:
        # Create server
        server = create_server()

        # Register tools
        tool_count = register_tools(server)
        logger.info(f"Server ready with {tool_count} tools")

        # Run server on stdio
        run_stdio(server)

    except Exception as e:
        logger.error(f"Failed to start server: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
