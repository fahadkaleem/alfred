# Document Implementation

## Purpose
Create comprehensive Implementation Artifact for persistent memory and handoff readiness.

## What to tell the user
"Documenting complete implementation..."

## Phase 1: Gather Information

Collect from all sources:
1. **Each subtask's implementation artifact** (from JIRA comments)
2. **Git commits** made during this session
3. **Test results** from the full suite run
4. **Planning gaps** identified and resolved
5. **User clarifications** received during implementation

## Phase 2: Create Implementation Artifact

To add implementation artifact as comment:
→ load_instructions("jira/add-comment")

### Implementation Artifact Template

```markdown
## Implementation Artifact: {{ task_id }}

### Executive Summary
[2-3 sentences on what was accomplished overall]

### Subtasks Completed
- **[Subtask ID]**: [What was done]
- **[Subtask ID]**: [What was done]
- **[Subtask ID]**: [What was done]

### Technical Implementation

#### Architecture Decisions
- Chose [pattern/approach] for [reason]
- Used [library/tool] because [justification]
- Structured [component] to follow [existing pattern]

#### Files Modified
- `src/auth/controller.js` - Added login endpoint
- `src/auth/middleware.js` - Created JWT validation
- `tests/auth.test.js` - Added 15 test cases
- `config/routes.js` - Registered new routes

#### Key Integration Points
- Integrated with existing auth service at [location]
- Connected to database using [pattern]
- Added middleware to [pipeline]

### Test Coverage
- **Total tests added**: X across Y files
- **Test scenarios covered**:
  - Authentication flow (happy path + errors)
  - Authorization checks
  - Edge cases (empty inputs, SQL injection)
- **Full suite results**: All XXX tests passing

### Planning Gaps Addressed
- **Gap**: Auth method wasn't specified
  - **Resolution**: Used JWT pattern from existing services
- **Gap**: Error handling approach unclear
  - **Resolution**: Followed pattern from user service

### Implementation Notes
- All code follows existing patterns found in [reference]
- Maintained backward compatibility with [feature]
- Performance considerations: [if any]

### Commit History
- `[hash]` AL-101: Add authentication endpoint
- `[hash]` AL-102: Add JWT generation
- `[hash]` AL-103: Add authorization middleware
- `[hash]` Fix failing tests after auth changes

### Next Steps
- Ready for code review
- All acceptance criteria met
- Consider [future enhancement] in next iteration

### Session Metadata
- **Implementation Date**: [Date]
- **Developer**: AI Assistant
- **Total Duration**: [Estimate]
- **Model Used**: Claude

---
*This artifact enables seamless handoff to any developer or AI for future work*
```

## Phase 3: Update Task Status

Update any relevant fields:
- Add label "implementation-complete"
- Ensure all subtasks marked as "Done"
- Note any follow-up items

## Phase 4: Final Git Commit

If there are uncommitted changes:
```bash
git add .
git commit -m "{{ task_id }}: Complete implementation

- All subtasks implemented
- Full test coverage added
- Implementation artifact created
- Ready for review"
```

## Validation Before Saving

Verify artifact includes:
- [ ] All subtasks with completion status
- [ ] Key technical decisions and rationale
- [ ] Complete file modification list
- [ ] Test coverage summary
- [ ] Planning gaps that were addressed
- [ ] Clear next steps

## Self-Validation Questions

Ask yourself:
1. Could a new AI/developer continue from this?
2. Are all decisions documented with rationale?
3. Is this reviewable in <10 minutes?

If ANY answer is "no", add missing information.

## Documentation Principles

- **Navigate, Don't Duplicate**: Reference file:line not code blocks
- **Decisions Over Details**: WHY matters more than WHAT
- **Gaps Are Gold**: Document what planning missed for improvement

## Next Step
Only after validation complete → Proceed to "Prepare for review"