# Prepare for Review

## Purpose
Prepare the user for the quality review process by explaining what to expect and why it matters.

## Review Recommendation

**Tell the user**:
```
Implementation complete! Before proceeding to QA, let's ensure code quality.

Run quality review:
review_task("{{ task_id }}", scope="targeted", focus_areas=["code_quality", "test_coverage", "acceptance_criteria"])

This will verify:
- ✓ All acceptance criteria implemented correctly
- ✓ Code follows project standards  
- ✓ Test coverage is adequate
- ✓ No security vulnerabilities
- ✓ Documentation is complete
```

## Review Outcomes

### IF Review APPROVED:
```
Excellent! Review passed all quality checks.

Next steps:
1. Transition ticket to "Ready for QA"
2. QA team can run: test_task("{{ task_id }}")
3. Monitor for any QA findings
```

### IF Review NEEDS_REVISION:
```
Review identified issues to address:

[Review feedback will appear here]

To fix:
1. Address each issue raised
2. Re-run affected tests
3. Run review again: review_task("{{ task_id }}")

Do NOT proceed to QA until review passes.
```

### IF Review FINDS MAJOR ISSUES:
```
Review found blocking issues:

[Critical issues listed]

Required actions:
1. Fix all blocking issues
2. May need to revise approach
3. Update Implementation Artifact
4. Full re-review required

This is normal - better to catch now than in QA!
```

## Why Review Matters

Emphasize to user:
- Catches issues early (cheaper to fix)
- Ensures code quality standards
- Validates acceptance criteria
- Reduces QA cycle time
- Builds confidence in implementation

## Workflow Integration

```
Current workflow position:
Planning → Implementation → [Review] → QA → Done
                            ↑
                        YOU ARE HERE

Review is your quality gate before QA.
```

## Common Review Findings

Prepare user for typical feedback:
- Missing edge case handling
- Insufficient test coverage
- Code style violations
- Performance concerns
- Security considerations
- Documentation gaps

## Next Actions

Based on review outcome:

1. **Pass**: Update ticket status, proceed to QA
2. **Minor Issues**: Quick fixes, re-review
3. **Major Issues**: Significant rework needed
4. **Clarification**: Add questions to ticket

## Final Message

```
Remember: A thorough review now saves time later.

Ready to run the review? 
review_task("{{ task_id }}", scope="targeted", focus_areas=["code_quality", "test_coverage", "acceptance_criteria"])
```

## DO NOT
- Skip review to "save time"
- Proceed to QA without review passing
- Ignore review feedback
- Treat review as optional