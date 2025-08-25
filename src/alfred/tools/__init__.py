"""Tool discovery and registration for Alfred MCP server."""

import pkgutil
import importlib
import inspect
from typing import Callable, Any, List
from fastmcp import FastMCP

from alfred.utils import get_logger

logger = get_logger("alfred.tools")


def register_tools(server: FastMCP) -> int:
    """
    Discover and register tools with the FastMCP server.

    This function walks through the tools package, discovers tool modules,
    and registers them with the server following FastMCP conventions.

    Args:
        server: FastMCP server instance

    Returns:
        Number of tools successfully registered
    """
    tool_count = 0
    discovered_modules = list_discovered_modules()

    logger.info(f"Discovering tools in {len(discovered_modules)} modules")

    for module_name in discovered_modules:
        try:
            # Import the module
            full_module_name = f"alfred.tools.{module_name}"
            logger.debug(f"Importing module: {full_module_name}")
            module = importlib.import_module(full_module_name)

            # Convention 1: Module has a register(server) function
            if hasattr(module, "register") and callable(module.register):
                logger.debug(f"Registering tools from {module_name} using register()")
                count = module.register(server)
                if isinstance(count, int):
                    tool_count += count
                else:
                    # If register doesn't return a count, assume at least 1 tool
                    tool_count += 1

            # Convention 2: Module has MCP_TOOLS list
            elif hasattr(module, "MCP_TOOLS"):
                logger.debug(f"Registering tools from {module_name} using MCP_TOOLS")
                tools = module.MCP_TOOLS
                if isinstance(tools, (list, tuple)):
                    for tool in tools:
                        if callable(tool):
                            # Register the tool with the server
                            # FastMCP decorators might auto-register, so check first
                            try:
                                server.tool(tool)
                                tool_count += 1
                                logger.debug(f"Registered tool: {tool.__name__}")
                            except Exception as e:
                                logger.warning(
                                    f"Failed to register tool {tool.__name__}: {e}"
                                )

            # Convention 3: Look for functions decorated with @tool
            else:
                logger.debug(f"Scanning {module_name} for decorated tools")
                for name, obj in inspect.getmembers(module):
                    if callable(obj) and hasattr(obj, "__mcp_tool__"):
                        # This is a tool decorated with @mcp.tool
                        tool_count += 1
                        logger.debug(f"Found pre-registered tool: {name}")
                    elif name.startswith("tool_") and callable(obj):
                        # Convention: functions starting with tool_ are tools
                        try:
                            server.tool(obj)
                            tool_count += 1
                            logger.debug(f"Registered tool: {name}")
                        except Exception as e:
                            logger.warning(f"Failed to register tool {name}: {e}")

        except ImportError as e:
            logger.error(f"Failed to import module {module_name}: {e}")
            continue
        except Exception as e:
            logger.error(f"Error processing module {module_name}: {e}", exc_info=True)
            continue

    logger.info(f"Successfully registered {tool_count} tools")
    return tool_count


def list_discovered_modules() -> List[str]:
    """
    List all Python modules in the tools package.

    Returns:
        List of module names (without package prefix)
    """
    modules = []

    # Get the tools package path
    package = importlib.import_module("alfred.tools")

    # Walk through the package to find modules
    for importer, modname, ispkg in pkgutil.walk_packages(package.__path__, prefix=""):
        # Skip __init__ and private modules
        if modname and not modname.startswith("_"):
            modules.append(modname)
            logger.debug(f"Discovered module: {modname}")

    return modules


def create_tool_wrapper(func: Callable) -> Callable:
    """
    Create a wrapper for tool functions to add error handling and logging.

    Args:
        func: The tool function to wrap

    Returns:
        Wrapped function with error handling
    """

    async def wrapper(*args, **kwargs):
        """Wrapped tool function with error handling."""
        try:
            logger.debug(f"Executing tool: {func.__name__}")
            result = (
                await func(*args, **kwargs)
                if inspect.iscoroutinefunction(func)
                else func(*args, **kwargs)
            )
            logger.debug(f"Tool {func.__name__} completed successfully")
            return result
        except Exception as e:
            logger.error(f"Tool {func.__name__} failed: {e}", exc_info=True)
            raise

    # Preserve function metadata
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    wrapper.__annotations__ = func.__annotations__

    return wrapper


# Export for convenience
__all__ = ["register_tools", "list_discovered_modules", "create_tool_wrapper"]
