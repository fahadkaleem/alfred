"""Constants for task operations."""

# Subtask generation defaults
MIN_SUBTASKS = 3
MAX_SUBTASKS = 5
DEFAULT_SUBTASKS = 3
TITLE_WORD_DIVISOR = 3  # Used for heuristic subtask count calculation

# Complexity thresholds
DEFAULT_COMPLEXITY_THRESHOLD = 7

# Task statuses that are eligible for operations
INELIGIBLE_STATUSES = ["done", "cancelled"]
ELIGIBLE_STATUSES = ["pending", "in_progress", "todo"]
