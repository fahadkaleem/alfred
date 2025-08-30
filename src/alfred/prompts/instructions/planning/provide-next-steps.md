# Provide Next Steps

## Purpose
Guide the user on what happens after planning is complete, ensuring smooth workflow continuation.

## What to tell the user

### Standard Next Steps Message
```
Planning Complete for {{ task_id }}

Created: [X] subtasks
Total estimate: [Y] hours

Your plan is ready for review! The Plan Artifact contains all implementation context.

Next steps:
1. Review the plan (subtasks and Plan Artifact context)
2. Once approved:
   - Update task status to "in_progress" using update_task
   - Run: execute_phase("{{ task_id }}", "implement")

If changes needed:
- Add feedback as task context
- Run: plan_task("{{ task_id }}") to revise the plan
```

## Optional Quality Review

**Only mention if user asks about review:**
```
If you'd like an automated quality review:
review_task("{{ task_id }}", type="planning")

This will provide structured feedback on the plan quality.
```

## Additional Guidance

Based on the task type, you might add:

### For Complex Features
"Given the complexity, consider reviewing with a technical lead before implementation."

### For Bug Fixes
"The plan includes root cause analysis. Implementation can begin immediately if urgent."

### For Technical Debt
"This plan addresses the debt while maintaining backward compatibility as discussed."

### For Time-Sensitive Tasks
"With [Y] hours estimated, this can be completed in [Z] days with focused effort."

## Workflow Continuity

Explain the workflow:
1. **Planning** (current) → Creates subtasks and artifact
2. **Review** (optional) → Validates plan quality
3. **Implementation** → Developer uses plan artifact
4. **Testing** → Validates implementation
5. **Completion** → Final review and merge

## Common Questions to Address

Proactively answer:
- "The Plan Artifact in the comments contains everything the developer needs"
- "Subtasks can be assigned to different developers if needed"
- "Dependencies are documented in the subtask descriptions"
- "Time estimates are based on the codebase analysis"

## Handling User Questions

Be ready to:
- Explain any part of the plan
- Adjust subtasks if needed
- Clarify dependencies
- Provide more context on estimates

## Sign-off

End with:
"Is there anything specific about the plan you'd like me to explain or adjust?"

## Important Notes
- Keep the tone helpful and forward-looking
- Make next actions crystal clear
- Remind about the implement_task command
- Stay available for questions

## Task Complete
Mark this final task as completed in your todo list. Planning is now complete!