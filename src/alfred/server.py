"""Main FastMCP server implementation for Alfred Task Manager."""

from alfred.mcp import mcp
import importlib
from pathlib import Path


def auto_import_tools():
    """Import all tool modules to trigger decorator registration."""
    tools_dir = Path(__file__).parent / "tools"

    for module_file in tools_dir.rglob("*.py"):
        if module_file.name.startswith("_") or module_file.name == "__init__.py":
            continue

        # Build module path (e.g., alfred.tools.tasks.create_task)
        relative_path = module_file.relative_to(tools_dir.parent.parent)
        module_path = str(relative_path).replace("/", ".").replace(".py", "")

        try:
            importlib.import_module(module_path)
        except ImportError as e:
            print(f"Failed to import {module_path}: {e}")


# Import all tools (decorators will auto-register)
auto_import_tools()


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
