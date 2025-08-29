"""Constants for task operations."""

from alfred.models.tasks import TaskStatus, TaskStatusGroups

# Subtask generation defaults
MIN_SUBTASKS = 3
MAX_SUBTASKS = 5
DEFAULT_SUBTASKS = 3
TITLE_WORD_DIVISOR = 3  # Used for heuristic subtask count calculation


# Task statuses that are eligible for operations
# Convert enum sets to lists for backward compatibility
INELIGIBLE_STATUSES = [status.value for status in TaskStatusGroups.COMPLETED]
ELIGIBLE_STATUSES = [status.value for status in TaskStatusGroups.ELIGIBLE]
