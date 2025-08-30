# Planning Review

## Your Mission
Verify the Plan Artifact contains EVERYTHING needed for a developer to implement without exploring the codebase.

## Phase 1: Load Context

### 1. Get Task Details
To get task details:
→ Use get_task(task_id) to retrieve task information

Extract:
- ALL acceptance criteria
- Technical requirements  
- Constraints or dependencies

### 2. Load Plan Artifact
To read all task context:
→ Use load_context(task_id, "planning") to retrieve planning context

Find the Plan Artifact context and extract:
- Executive summary
- Requirements analysis
- Technical approach
- Work breakdown (subtasks)

## Phase 2: Acceptance Criteria Coverage

For EACH acceptance criterion from the task:

```markdown
### Criterion: "[Exact text from task]"
Plan Coverage:
- Where addressed: [Section in plan]
- How addressed: [Approach described]
- Subtask assignment: [Which subtask handles this]
- Status: ✓ COVERED or ✗ MISSING
```

## Phase 3: Developer Readiness Check

### Can a Developer Implement Without Codebase Exploration?

For each planned implementation area:
- [ ] Specific files to modify/create identified
- [ ] Integration points with line numbers provided
- [ ] Code patterns to follow referenced
- [ ] Test approach defined
- [ ] Error handling strategy clear

### Critical Information Presence
- [ ] WHERE to put code (file paths)
- [ ] HOW to integrate (specific patterns)
- [ ] WHAT to test (scenarios listed)
- [ ] WHY decisions made (rationale provided)

## Phase 4: Subtask Quality Verification

For EACH subtask:
```markdown
### Subtask: [ID - Title]
- Self-contained: YES/NO
- Clear boundaries: YES/NO
- Testable independently: YES/NO
- Has acceptance criteria: YES/NO
```

## Phase 5: Forensic Extraction Validation

### Code Analysis Evidence
Check the plan shows evidence of actual codebase investigation:
- [ ] Specific file:line references found
- [ ] Actual code patterns identified
- [ ] Real integration points discovered
- [ ] Existing test patterns noted

**Generic statements = FAIL**
Examples of failures:
- "Follow existing patterns" (WHICH patterns?)
- "Integrate with auth service" (HOW? WHERE?)
- "Add appropriate tests" (WHAT tests?)

## Self-Validation Questions

Before approving:
1. Could I implement this without opening the codebase?
2. Are all acceptance criteria mapped to subtasks?
3. Does every technical decision have a rationale?
4. Is there evidence of forensic code extraction?

If ANY answer is "no", the plan needs revision.

## Review Decision Matrix

| Criteria Coverage | Implementation Details | Forensic Evidence | Subtasks Quality | Decision |
|------------------|----------------------|-------------------|------------------|----------|
| 100% | Complete | Present | Good | APPROVED |
| 100% | Minor gaps | Present | Good | CONDITIONAL - add details |
| <100% | - | - | - | NEEDS REVISION |
| Any | Generic/Vague | Missing | Any | **FAIL - INSUFFICIENT DETAIL** |

## Review Comment Format

To add review result as context:
→ Use save_context(task_id, "planning_review", "review content")

```markdown
## Planning Review Result: [APPROVED/NEEDS REVISION]

### Acceptance Criteria Coverage
✓ [Criterion 1] - Covered in subtasks X, Y
✓ [Criterion 2] - Covered in subtask Z
✗ [Criterion 3] - NOT ADDRESSED

### Implementation Readiness
- File locations: [Specific/Generic/Missing]
- Integration details: [Clear/Vague/Missing]
- Test approach: [Defined/Generic/Missing]
- Forensic evidence: [Present/Missing]

### Subtask Assessment
- Total subtasks: X
- Self-contained: Y/X
- Clear boundaries: Y/X
- Quality: [Good/Needs work]

### Required Improvements (if any)
1. [Specific gap to fill]
2. [Missing detail needed]

### Notable Strengths (if any)
- [What was done well]

---
*Review completed by {{ reviewer }} on {{ timestamp }}*
```