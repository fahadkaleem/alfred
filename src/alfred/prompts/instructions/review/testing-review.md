# Testing Review Checklist

## Review Criteria

### Test Coverage (Critical)
- [ ] All acceptance criteria have corresponding tests
- [ ] Happy path scenarios are thoroughly tested
- [ ] Edge cases and error conditions are tested
- [ ] Integration points are verified
- [ ] Performance tests exist for critical paths

### Test Quality (Critical)
- [ ] Tests are independent and can run in any order
- [ ] Tests are deterministic (no flaky tests)
- [ ] Test data is properly isolated
- [ ] Tests follow AAA pattern (Arrange, Act, Assert)
- [ ] Test names clearly describe what is being tested

### Validation Completeness (Critical)
- [ ] All user inputs are validated
- [ ] Boundary conditions are tested
- [ ] Error messages are helpful and accurate
- [ ] System behaves correctly under failure conditions
- [ ] Rollback scenarios are tested

### Documentation (Important)
- [ ] Test plan documents all scenarios
- [ ] Complex test setups are documented
- [ ] Known limitations are documented
- [ ] Test results are reproducible

### User Experience (Important)
- [ ] Feature works as users would expect
- [ ] Performance meets user expectations
- [ ] Error handling is user-friendly
- [ ] Accessibility requirements are met

## Scoring Instructions

Calculate percentage: (passed items / total items) * 100

- **100%**: All criteria met - Approved
- **90-99%**: Minor issues - Conditional approval with notes
- **<90%**: Major issues - Needs revision

## Status Transition

If score < 90%:
- Recommend updating task status back to "in_progress"
- Use these instructions:
  ```
  I need to update this task back to "in_progress" due to review findings.
  
  Use update_task(task_id, status="in_progress") to change status
  ```

## Review Comment Format

Use the format specified in the task requirements:

```markdown
## Review Result: Testing Review - [Status]

**Score:** [X]%
**Status:** [Approved/Needs Revision]

### Critical Issues (Must Fix)
- [ ] [Test gap or failure description]

### Important Issues 
- [ ] [Test improvement suggestion]

### Summary
[Brief summary of test coverage and quality]

---
*Review performed by review_task on [timestamp]*
```