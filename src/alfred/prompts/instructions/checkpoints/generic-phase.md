# Generic Phase Checkpoint

## Purpose
Save comprehensive context for this completed phase to enable workflow continuity and knowledge preservation.

## When to Use
This instruction is automatically loaded when a phase completes with `auto_checkpoint: true` but no custom checkpoint instruction specified.

## Save Context Instructions

### Context Content Format
Save dense, information-rich context that captures:

**Phase Summary:**
- What was accomplished in this phase
- Key decisions made and rationale
- Important discoveries or insights

**Deliverables Created:**
- Files modified or created
- Documentation updated
- JIRA tickets created or updated

**Technical Details:**
- Patterns identified or established  
- Constraints discovered
- Integration points identified

**Next Phase Handoff:**
- Critical information for next phase
- Dependencies resolved or identified
- Risks or blockers discovered

### Save Context Call
```python
save_context(
    task_id="{{ task_id }}",
    phase="{{ phase_name }}",
    content="[Dense bullet-point summary]",
    status="COMPLETE",
    metadata={
        "deliverables": ["file1.py", "docs/spec.md"],
        "decisions": ["Use Redis for sessions", "OAuth2 over JWT"],
        "next_phase_notes": "Architecture approved, ready for implementation"
    }
)
```

## Example Context Save

**Phase: Planning**
```
Planning Complete: Requirements extracted, implementation approach defined, subtasks created.

Decisions:
- PostgreSQL over MongoDB (better ACID guarantees)
- React Query for state management (team familiarity)  
- Microservice architecture (scalability requirements)

Deliverables:
- Plan Artifact in .claude/tasks/{{ task_id }}/plan.md
- 8 implementation subtasks in JIRA
- Database schema defined

Technical Details:
- Auth service handles JWT validation
- User service manages profile data
- Rate limiting: 100 req/min per user
- Files: services/auth/, services/user/, db/schema.sql

Next Phase: Implementation team has clear subtasks, architecture approved, ready to code.
```

## Completion
After saving context, mark this checkpoint step as completed in your todos.