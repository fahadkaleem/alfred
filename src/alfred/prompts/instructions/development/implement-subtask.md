# Implement Subtask

## Purpose
Execute implementation matching existing patterns exactly, with test-driven development and user collaboration.

## What to tell the user
"Implementing [subtask ID]: [subtask summary]..."

## Complexity Assessment

First, assess task complexity:
- **Simple** (add button, fix typo): Minimal analysis needed
- **Medium** (new endpoint, component): Standard pattern matching
- **Complex** (auth system, integration): Deep extraction required

Route effort based on complexity - don't over-engineer simple tasks.

## Phase 1: Gap Analysis (Just-in-Time)

### What I Need vs What I Have

WHAT I NEED TO KNOW:
1. Exact requirements for this subtask
2. Where code goes (files/functions)
3. Patterns to follow
4. Test approach
5. Integration points

WHAT I'LL EXTRACT:
- Subtask details → load_instructions("jira/get-issue")
- All comments and context → load_instructions("jira/read-comments")
- Previous work → Load subtasks 1 to N-1 artifacts
- Plan Artifact (if exists) → Extract from comments

GAPS TO FILL:
[Identify after extraction]

## Phase 2: Code Analysis & Pattern Matching

Before writing any code, study the existing codebase:

### 1. Find Target Files
Based on the subtask, identify:
- Which files to modify
- Which files to create
- Related test files

### 2. Dynamic Pattern Extraction

Generate search patterns by decomposing the feature:
1. Break feature into components
2. Think of synonyms/variations
3. Search for each pattern

Document findings as navigation, not duplication:
```
auth.service.ts:
- Line 45-67: JWT validation pattern
- Line 89-95: Error handling approach
- Key: Uses AuthError class for all auth errors
```

### 3. Progressive Pattern Learning

ROUND 1: Find similar features
ROUND 2: Study implementation details
ROUND 3: Extract test patterns

Document patterns to follow:
- Code style: [specific observations]
- Error handling: [exact pattern used]
- Test structure: [naming, mocking approach]

## Phase 3: Implementation

### 1. Write Code
- Match EXACTLY the patterns you found
- Use existing utilities/helpers
- Follow file organization
- Maintain consistent style

### 2. Ask User About Edge Cases
If requirements are ambiguous:
"The requirement says 'handle errors' - should I:
1. Return error codes?
2. Throw exceptions?
3. Log and continue?
I see the codebase uses pattern X in similar cases."

## Phase 4: Test Development (WITH APPROVAL)

### 1. Present Test Scenarios
Before writing ANY tests, present scenarios in plain English:

```
For the authentication endpoint, I plan to test:

1. **Happy Path**
   - Valid credentials return JWT token
   - Token contains correct user claims

2. **Error Cases**
   - Invalid username returns 401
   - Invalid password returns 401
   - Missing credentials returns 400

3. **Edge Cases**
   - Empty username/password
   - SQL injection attempts
   - Very long inputs

4. **Integration**
   - Token works with protected endpoints
   - Refresh token flow

Does this cover all scenarios? Any additional cases to test?
```

### 2. Get User Approval
Wait for user to:
- Approve test cases
- Suggest additional scenarios
- Clarify edge cases

### 3. Write Tests
After approval:
- Match existing test file patterns EXACTLY
- Use same assertion style
- Follow naming conventions
- Include all approved scenarios

### 4. Update Existing Tests
If modifying existing code:
- Check which tests might break
- Update test expectations
- Add new test cases for new functionality
- Maintain backward compatibility

## Phase 5: Validation

### 1. Run Tests for Modified Files
```bash
# Run specific test file
npm test [test_file]
# or
pytest [test_file]
# or appropriate command for the project
```

If tests fail:
- Fix implementation or tests
- Ensure all scenarios pass

### 2. Verify Acceptance Criteria
Go through each acceptance criterion:
- "✓ API returns JSON" - Verified in test case X
- "✓ Handles errors gracefully" - Covered by error tests
- "✓ Performance < 200ms" - May need performance test

## Phase 6: Document Implementation

Create implementation artifact as JIRA comment:

To add comment with implementation details:
→ load_instructions("jira/add-comment")

```markdown
## Implementation: [Subtask ID]

### What was implemented
- [Feature/change description]
- [Files modified/created]

### Technical decisions
- Chose pattern X because...
- Used library Y for...

### Test coverage
- [Number] test cases added
- All scenarios approved by user
- Tests passing

### Next steps
- [Any follow-up needed]
```

## Phase 7: Commit Changes

```bash
# Stage changes
git add [files]

# Commit with subtask reference
git commit -m "[Subtask ID]: [Description]

- Implementation details
- Test coverage added
- Meets acceptance criteria"
```

## Acceptance Criteria Validation

Before marking complete, verify:
- [ ] All subtask acceptance criteria met
- [ ] Code matches existing patterns exactly
- [ ] Test scenarios approved by user
- [ ] All tests written and passing
- [ ] Implementation documented in JIRA
- [ ] Changes committed with subtask ID

## Self-Validation Questions

Ask yourself:
1. Could another developer continue from my artifact?
2. Did I match patterns EXACTLY?
3. Are all edge cases tested?
4. Is the implementation complete?

If ANY answer is "no", continue working.

## Next Step
Only after ALL criteria checked → Mark complete in TodoWrite → Next subtask or "Run test suite"