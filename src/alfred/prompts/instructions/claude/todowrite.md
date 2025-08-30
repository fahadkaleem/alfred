# TodoWrite Hierarchical Task Pattern

When using TodoWrite, you can create parent tasks and subtasks using decimal notation for better organization.

## How to Create Subtasks

1. Create main tasks with integer IDs (1, 2, 3, etc.)
2. When a main task needs breaking down, mark it as `in_progress`
3. Add subtasks using decimal notation (1.1, 1.2, 1.3, etc.)
4. Complete all subtasks before marking the parent task as `completed`

## Example

<example>
# Initial state - main tasks only
[
  {"id": "1", "content": "Analyze codebase", "status": "pending", "priority": "medium"},
  {"id": "2", "content": "Create implementation plan", "status": "pending", "priority": "high"}
]

# When starting task 1, discover it needs subtasks
[
  {"id": "1", "content": "Analyze codebase", "status": "in_progress", "priority": "medium"},
  {"id": "1.1", "content": "Search for authentication patterns", "status": "pending", "priority": "medium"},
  {"id": "1.2", "content": "Review database schema", "status": "pending", "priority": "medium"},
  {"id": "1.3", "content": "Check API structure", "status": "pending", "priority": "medium"},
  {"id": "2", "content": "Create implementation plan", "status": "pending", "priority": "high"}
]

# Work through subtasks sequentially
# Only mark parent task 1 as completed after all subtasks (1.1, 1.2, 1.3) are completed
</example>

## Key Rules

- Only ONE task should be `in_progress` at any time
- Complete subtasks before marking parent as completed
- Use this pattern when you discover a task is more complex than initially thought