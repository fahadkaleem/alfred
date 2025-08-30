# Check Current Progress

## Purpose
Determine exact implementation state through systematic validation. Make no assumptions about previous work.

## What to tell the user
"Checking implementation state of {{ task_id }}..."

## Critical Validations

### 1. Git State Check
**CRITICAL**: Verify current branch matches pattern `feature/{{ task_id }}`

If branch doesn't match → **HALT IMMEDIATELY**
```
Current branch: [actual branch name]
Expected branch: feature/{{ task_id }}

This mismatch needs to be resolved. Options:

1. Switch to correct branch (if it exists)
   → git checkout feature/{{ task_id }}
   
2. Create new branch (if planning was skipped)
   → git checkout -b feature/{{ task_id }}
   
3. Stay on current branch (if there's a reason)
   → Explain why you're on [current branch]

Please select 1-3:
```

If on correct branch:
- Check for uncommitted changes: `git status`
- Review commit history: `git log --oneline -10`
- Note any work already done

### 2. Workflow Gate Check
To get cloud ID and issue details:
→ load_instructions("jira/get-cloud-id")
→ load_instructions("jira/get-issue")

**CRITICAL**: Verify JIRA status is "In Development"
- If status is "Planning Review" → **HALT IMMEDIATELY**
  - Tell user: "The ticket is in Planning Review. The plan needs to be approved and moved to 'In Development' before I can start implementation."
  - Cannot proceed until status changes

### 3. Progress Investigation
To read comments and artifacts:
→ load_instructions("jira/read-comments")

Look for:
- Plan Artifact (helpful if exists but NOT required)
- Implementation Artifact (indicates completion)
- Any implementation notes or decisions
- Subtask statuses (To Do/In Progress/Done)
- Raw requirements and discussions in comments

## Scenario Detection & User Questions

Ask clarifying questions based on what you find:

**If subtasks are marked Done but no artifacts exist:**
- "I see subtasks marked complete but no planning/implementation artifacts. Did you or the team work on these directly?"
- "Should I analyze the git history to understand what's been implemented?"

**If git has uncommitted changes:**
- "There are uncommitted changes on this branch. Can you tell me what these changes are for?"
- "Should I review these changes before proceeding?"

**If commits exist but no JIRA documentation:**
- "I found [X] commits but no implementation notes in JIRA. Were these changes made outside the normal workflow?"
- "Would you like me to analyze these commits and document what's been done?"

**If mixed AI/human work detected:**
- "I see a planning artifact from [date] but implementation appears to be done manually. Is this correct?"
- "Should I incorporate the existing work into my implementation approach?"

**If implementation artifact exists:**
- "I found a complete Implementation Artifact. It looks like implementation is done. Should we move to testing/review?"

**If no planning artifact found:**
"I don't see a Planning Artifact in the comments. We have two options:

**Option 1: Plan First (Recommended)**
- I can help create a comprehensive plan using Alfred's planning system
- You'll need to change the JIRA status back to 'In Planning'
- Once changed, use: `plan_task('{{ task_id }}')`
- This ensures we have complete context before implementation

**Option 2: Extract and Implement**
- I'll extract requirements directly from JIRA 
- I'll analyze ticket description, acceptance criteria, and comments
- We'll proceed with implementation using available information
- Higher risk of missing hidden requirements

Which would you prefer? (1 or 2)"

## Decision Matrix

| Scenario | Git State | JIRA Status | Artifacts | Action |
|----------|-----------|-------------|-----------|---------|
| Wrong branch | Not feature/{{ task_id }} | Any | Any | HALT - offer branch options |
| Fresh start | Correct branch, clean | In Development | Any | Load context, begin implementation |
| Continuing | Correct branch, commits | In Development | Partial work | Load context, continue from last point |
| Status blocked | Any | Planning Review | Any | HALT - need approval |
| Complete | Correct branch, commits | In Development | Implementation exists | Suggest moving to review |
| Human work | Correct branch, commits | In Development | No artifacts | Ask about work done, document it |
| No plan artifact | Any | In Development | No Plan Artifact | Offer choice: Plan first or Extract from JIRA |
| Unclear | Mixed signals | Any | Mixed | ASK USER for clarification |

## What to Document

Based on your investigation and user answers:
- Current git branch and state
- JIRA ticket status (must be "In Development" to proceed)
- Existing artifacts found (Planning/Implementation)
- Subtask statuses and any notes
- Git commit history summary
- Any anomalies or gaps detected
- User's clarifications about the work history
- Decision on how to proceed

## Validation Checklist

Before proceeding, verify:
- [ ] Current git branch matches expected pattern
- [ ] JIRA status is "In Development" (not blocked)
- [ ] Identified what work has been done (if any)
- [ ] Documented any anomalies found
- [ ] Clear on next action to take

## Self-Check Questions

Ask yourself:
1. Do I know the EXACT state of this implementation?
2. Are there any blockers preventing progress?
3. Is the work history clear (AI vs human)?

If ANY answer is "no", investigate further with user.

## Next Step

Based on findings:
- If wrong branch → HALT until resolved
- If blocked (Planning Review) → HALT until approved
- If implementation complete → Suggest review phase
- If user chooses "Plan First" → Wait for status change, then guide to use plan_task
- If user chooses "Extract and Implement" → Proceed to "Get subtasks"
- Otherwise → Proceed to "Get subtasks"