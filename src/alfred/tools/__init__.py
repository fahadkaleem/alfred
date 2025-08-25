"""Tool discovery and registration for Alfred MCP server."""

import importlib
from pathlib import Path
from fastmcp import FastMCP

from alfred.utils import get_logger

logger = get_logger("alfred.tools")


def register_tools(server: FastMCP) -> int:
    """
    Discover and register tools with the FastMCP server.

    This function discovers tool modules in the tools package and subdirectories,
    and registers them with the server using the register(server) convention.

    Args:
        server: FastMCP server instance

    Returns:
        Number of tools successfully registered
    """
    tool_count = 0
    tools_dir = Path(__file__).parent

    # Discover all .py files in tools directory and subdirectories
    module_files = [
        f
        for f in tools_dir.rglob("*.py")
        if f.is_file() and not f.name.startswith("_") and f.name != "__init__.py"
    ]

    logger.info(f"Discovering tools in {len(module_files)} modules")

    for module_file in module_files:
        # Build module path relative to tools directory
        # e.g., workspace/initialize_workspace.py -> alfred.tools.workspace.initialize_workspace
        relative_path = module_file.relative_to(tools_dir)
        module_path = (
            f"alfred.tools.{str(relative_path).replace('/', '.').replace('.py', '')}"
        )

        try:
            # Import the module
            logger.debug(f"Importing module: {module_path}")
            module = importlib.import_module(module_path)

            # Only support register(server) pattern
            if hasattr(module, "register") and callable(module.register):
                logger.debug(f"Registering tools from {module_path}")
                count = module.register(server)

                if isinstance(count, int):
                    tool_count += count
                    logger.info(f"Registered {count} tools from {module_path}")
                else:
                    logger.warning(
                        f"Module {module_path} register() did not return a count"
                    )
            else:
                logger.debug(
                    f"Module {module_path} has no register() function, skipping"
                )

        except ImportError as e:
            logger.error(f"Failed to import module {module_path}: {e}")
            continue
        except Exception as e:
            logger.error(
                f"Error registering tools from {module_path}: {e}", exc_info=True
            )
            continue

    logger.info(f"Successfully registered {tool_count} tools total")
    return tool_count


# Export for convenience
__all__ = ["register_tools"]
