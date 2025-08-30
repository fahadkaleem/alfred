# Implementation Review

## Your Mission
Verify the implementation fulfills ALL acceptance criteria from the ticket by examining actual code against documented plans and artifacts.

## Phase 1: Load Context

### 1. Get Ticket Details
To get issue details:
→ load_instructions("jira/get-issue")

Extract:
- Actual acceptance criteria (not summaries)
- Technical requirements
- Dependencies

### 2. Load Planning & Implementation Artifacts
To read all comments:
→ load_instructions("jira/read-comments")

Find and load:
- Plan Artifact (comprehensive implementation guide)
- Implementation Artifacts from each subtask
- Any revision decisions documented

### 3. Identify Code Changes
Review git commits for this branch:
```bash
git log --oneline main..HEAD
git diff --name-status main..HEAD
```

## Phase 2: Acceptance Criteria Verification

For EACH acceptance criterion from the ticket:

```markdown
### Criterion: "[Exact text from JIRA]"
- Implementation location: [file:lines]
- How it works: [Brief explanation]
- Test coverage: [test file:lines]
- Status: ✓ VERIFIED or ✗ NOT FOUND
```

Example:
```markdown
### Criterion: "Users can authenticate with email/password"
- Implementation location: auth.controller.js:45-67 (login endpoint)
- How it works: Validates credentials against database, returns JWT
- Test coverage: auth.test.js:23-89 (happy path + error cases)
- Status: ✓ VERIFIED
```

## Phase 3: Scope Verification (CRITICAL GUARDRAIL)

### Check for Unauthorized Additions
Review ALL changes to ensure NOTHING beyond acceptance criteria was added:

```markdown
### Authorized Changes (from acceptance criteria):
- [ ] Feature A at location X
- [ ] Feature B at location Y

### Actual Changes Found:
- [ ] Change 1: [file:lines] - ✓ AUTHORIZED / ✗ UNAUTHORIZED
- [ ] Change 2: [file:lines] - ✓ AUTHORIZED / ✗ UNAUTHORIZED
- [ ] Change 3: [file:lines] - ✓ AUTHORIZED / ✗ UNAUTHORIZED

### Unauthorized Additions:
- [Extra feature/enhancement not in requirements]
- [Refactoring not requested]
- ["Helpful" additions not approved]
```

**ANY unauthorized changes = AUTOMATIC FAIL**

## Phase 4: Implementation Quality Checks

### 1. Pattern Compliance
Compare implementation against existing codebase patterns:

```markdown
### Pattern: [What you're checking]
Expected (from [reference file]): [Pattern description]
Actual (in [implementation file]): [What was implemented]
Status:  MATCHES or  DEVIATES
```

### 2. Test Verification
- [ ] Test scenarios match what was approved by user
- [ ] All approved scenarios have test coverage
- [ ] Tests follow existing patterns in codebase

### 3. Documentation Accuracy
- [ ] Implementation matches Plan Artifact approach
- [ ] Technical decisions from planning were followed
- [ ] Any deviations are documented and justified

## Phase 5: Code Navigation (NOT Duplication)

For significant implementations, provide navigation:
```markdown
### Feature: [Feature name]
Entry point: [file:line]
Key components:
- Data model: [file:lines] 
- Business logic: [file:lines]
- API endpoint: [file:lines]
- Tests: [file:lines]
```

## Phase 6: Gap Analysis

```markdown
WHAT WAS PLANNED:
- [From Plan Artifact]

WHAT WAS IMPLEMENTED:
- [From code review]

GAPS OR DEVIATIONS:
- [Any differences found]
```

## Self-Validation Questions

Before finalizing review:
1. Did I verify EACH acceptance criterion against actual code?
2. Can I trace every requirement to specific implementation?
3. Did I check tests match approved scenarios?
4. Is implementation consistent with documented decisions?

If ANY answer is "no", continue reviewing.

## Review Decision Matrix

| Scope Check | All Criteria Met | Patterns Followed | Tests Complete | Decision |
|-------------|-----------------|-------------------|----------------|----------|
| ✓ No extras | Yes | Yes | Yes | APPROVED |
| ✓ No extras | Yes | Minor deviations | Yes | APPROVED with notes |
| ✓ No extras | Yes | Yes | Missing some | CONDITIONAL - add tests |
| ✓ No extras | No | - | - | NEEDS REVISION |
| ✗ EXTRAS FOUND | - | - | - | **FAIL - UNAUTHORIZED CHANGES** |

## Review Comment Format

To add review result as comment:
→ load_instructions("jira/add-comment")

```markdown
## Implementation Review Result: [APPROVED/NEEDS REVISION]

### Acceptance Criteria Verification
✓ [Criterion 1] - Implemented in [file:lines]
✓ [Criterion 2] - Implemented in [file:lines]
✗ [Criterion 3] - NOT FOUND

### Implementation Quality
- Pattern compliance: [X/Y patterns match]
- Test coverage: [All approved scenarios covered/Missing X]
- Matches planned approach: [Yes/No with specifics]

### Required Actions (if any)
1. [Specific action needed]
2. [File:lines to fix]

### Navigation Map
[Key files and line numbers for future reference]

---
*Review completed by {{ reviewer }} on {{ timestamp }}*
```