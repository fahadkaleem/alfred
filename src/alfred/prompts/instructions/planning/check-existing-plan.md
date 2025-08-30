# Check Existing Plan

## Goal
Quick scan to determine if planning work already exists. This is a DECISION GATE - should we continue planning or redirect the user?

## Instructions

### 1. Get Cloud ID
To get cloud ID:
→ load_instructions("jira/get-cloud-id")

### 2. Read the Issue
To get issue details:
→ load_instructions("jira/get-issue")

### 3. Quick Scan Comments
To read all comments:
→ load_instructions("jira/read-comments")

Focus on finding:
- Plan Artifacts (search for "Plan Artifact" header)
- Existing subtasks and their status
- Labels indicating planning status

### 4. Make Quick Assessment

**Look for clear indicators:**
- ✅ Planning exists if: Subtasks created, Plan Artifact in comments, "plan-complete" label
- ❌ No planning if: No subtasks, no Plan Artifact, "needs-planning" label
- ⚠️  Partial planning if: Some subtasks but no Plan Artifact, or old/incomplete plans, labels missing

**Store for later analysis:**
- Copy of any Plan Artifacts found (you'll validate them in Step 4)
- List of existing subtasks
- Key technical decisions mentioned
- Any failure indicators or blockers

## Branching Logic

### If Planning Already Exists:

**Tell the user:**
```
I found existing planning for {{ task_id }} with [X] subtasks.

Would you like to:
1. Review and revise the current plan
2. Proceed to implementation: implement_task("{{ task_id }}")
3. View full details: inspect_task("{{ task_id }}")

Select 1-3 or describe what you'd like to do:
```

**If user chooses revision:**
- Load existing plan from comments
- Ask what needs to be changed
- Update only the affected parts
- Save updated plan as new comment

### If No Planning Found:

**Tell the user in chat:** "Starting fresh planning for {{ task_id }}..."

Then proceed to the next step.

## Important Notes
- Always check comments thoroughly - plans might be in any comment
- Look for the most recent Plan Artifact if multiple exist
- Check subtask status to understand progress
- Note any review feedback in comments for incorporation

## Next Step
Mark this task as completed in your todo list and proceed to "Read and understand the ticket context".