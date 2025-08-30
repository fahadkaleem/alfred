# Save Plan Artifact

## Goal
Create an adaptive Plan Artifact that serves as either a strategic overview (when subtasks exist) or a complete implementation guide (when no subtasks needed).

## Adaptive Structure

### Determine Content Level
**If subtasks were created**: Focus on WHY and high-level WHAT
**If NO subtasks**: Include WHY, WHAT, and detailed HOW

## Plan Artifact Template

```markdown
## Plan Artifact: {{ task_id }}

### Executive Summary
[One paragraph: What we're building, why it matters, and the approach we're taking]

### Requirements & Success Criteria
#### From Discussion
- [Clarifications and additions from user conversation]
- [Any scope changes or constraints identified]

#### Definition of Done
- [Specific, measurable success criteria]
- [Performance targets if applicable]
- [User experience goals]

### Technical Approach

#### Architecture Overview
[High-level diagram or description of components and data flow]

#### Key Technical Decisions
[ALWAYS INCLUDE - This is the WHY that subtasks don't capture]

| Decision | Rationale | Trade-offs |
|----------|-----------|------------|
| Use WebSockets instead of polling | Real-time updates, better UX | More complex error handling |
| Implement optimistic updates | Instant feedback | Need rollback mechanism |
| Choose Redux over Context | Complex state, time-travel debugging | Additional boilerplate |

#### Assumptions & Risks
- Assuming: [List assumptions made during planning]
- Risk: [Potential issues and mitigation strategies]

[CONDITIONAL SECTION - Include if NO subtasks]
### Implementation Guide

#### Files to Modify
[Detailed list with specific changes needed]

#### Code Patterns to Follow
[Specific examples from codebase analysis]

#### Integration Points
[How to connect with existing systems]

#### Testing Approach
[Detailed test scenarios and patterns]

[CONDITIONAL SECTION - Include if subtasks exist]
### Work Breakdown
Implementation details are in the following subtasks:
1. {{ subtask_1_key }}: {{ subtask_1_title }}
2. {{ subtask_2_key }}: {{ subtask_2_title }}
3. {{ subtask_3_key }}: {{ subtask_3_title }}

Each subtask contains complete implementation details including file locations, code patterns, and testing approach.

### Important Notes
- [Any gotchas or special considerations]
- [Performance or security requirements]
- [Dependencies or blockers to watch for]

### Next Steps
[What happens after this planning - who picks up the work, when, etc.]
```

## What Goes Where

### ALWAYS in Plan Artifact:
- Executive summary
- Requirements clarification
- Technical decisions and rationale
- Architecture overview
- Assumptions and risks
- Important notes/warnings

### In Subtasks (if they exist):
- Detailed file locations
- Specific code patterns
- Line-by-line implementation
- Test implementation details
- Configuration changes

### In Plan Artifact (if NO subtasks):
- Everything above PLUS
- All implementation details
- Complete file modification list
- All code patterns and examples
- Full testing approach

## Saving the Artifact

**What to tell the user:** "Saving the Plan Artifact as task context..."

### Save the Context
To save plan artifact as context:
→ Use save_context(task_id, "plan_artifact", "artifact content")

Format your artifact according to the template above, adapting based on whether subtasks exist.

## Quality Checklist

Before saving, ensure:
- [ ] Executive summary clearly explains the approach
- [ ] All user clarifications are captured
- [ ] Technical decisions include rationale
- [ ] Implementation plan is ready to save
- [ ] Risks and assumptions are documented

## Save Planning Context

Save the comprehensive planning context including both the implementation plan and summary:

```python
save_context("{{ task_id }}", "plan", """
Planning Summary for {{ task_id }}:

WHAT WE'RE BUILDING:
[One paragraph executive summary from Plan Artifact]

KEY DECISIONS MADE:
- [Technical decision 1]: [Rationale]
- [Technical decision 2]: [Rationale]
- [Architecture choice]: [Why chosen over alternatives]

USER CLARIFICATIONS:
- [What user originally asked vs what they actually want]
- [Any constraints or requirements they added]
- [Preferences they expressed during conversation]

APPROACH:
- Overall strategy: [High-level approach]
- Complexity: [Simple/Medium/Complex with justification]

CRITICAL CONSTRAINTS:
- Technical: [Performance, compatibility, existing patterns]
- Business: [Deadlines, dependencies, stakeholders]
- Integration: [APIs, services, systems to work with]

DISCOVERIES:
- Existing code patterns: [What we found and will follow]
- Potential gotchas: [Things to watch out for]
- Reusable components: [What we can leverage]

NEXT STEPS:
- Immediate: [What happens after planning]
- Implementation: [Who picks up the work, when]
- Success metrics: [How we know it's done right]

CONTEXT FOR FUTURE:
[Any additional context that would help someone picking this up later]

## IMPLEMENTATION PLAN

### 1. [First logical task]
CREATE/UPDATE path/to/file.py
- [Specific requirement 1]
- [Specific requirement 2]
- [Method/function details]
Unit Tests:
- [Test case 1]
- [Test case 2]

### 2. [Second logical task]
UPDATE path/to/another_file.py
- [Specific changes needed]
- [Integration points]
Unit Tests:
- [Test scenarios]

### 3. [Third logical task]
CREATE path/to/new_file.py
- [Components to create]
- [Patterns to follow]
Unit Tests:
- [Test coverage needed]

[Continue with all tasks...]
""")
```

Note: Be comprehensive but concise. This memory will be searched and used when working on this task. Include enough detail to understand decisions but not so much that it becomes noise.

## Next Step
After saving to memory, mark this task as completed and proceed to "Provide next steps guidance".