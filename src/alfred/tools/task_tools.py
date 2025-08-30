"""MCP tools for local task management.
Exposes TaskManager operations as tools for Claude Code.
"""

from pathlib import Path
from alfred.core.workflow.task_manager import TaskManager

# Global task manager instance
_task_manager: TaskManager | None = None


def get_task_manager() -> TaskManager:
    """Get or create global task manager instance."""
    global _task_manager
    if _task_manager is None:
        data_dir = Path.cwd() / ".alfred"  # Use current working directory
        _task_manager = TaskManager(data_dir)
    return _task_manager
