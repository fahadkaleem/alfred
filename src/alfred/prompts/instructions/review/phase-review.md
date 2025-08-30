# Phase Review Instruction

## Goal
Conduct a thorough review of completed phase work to ensure quality, completeness, and requirements adherence.

## Review Process

### 1. Load Phase Context
First, load the context from the phase being reviewed:
```
load_context("TASK-ID", "PHASE-NAME")
```

### 2. Review Checklist

**Quality Standards:**
- [ ] All deliverables meet the defined acceptance criteria
- [ ] Work follows established patterns and conventions
- [ ] Documentation is clear and complete
- [ ] Code (if applicable) follows best practices

**Completeness Check:**
- [ ] All required steps were completed
- [ ] No obvious gaps or missing components
- [ ] Edge cases were considered and addressed
- [ ] Integration points were properly handled

**Requirements Adherence:**
- [ ] Original requirements were fully addressed
- [ ] No scope creep beyond defined boundaries
- [ ] Success criteria can be verified
- [ ] Stakeholder needs were met

### 3. Issue Classification

**Critical Issues** (must fix before proceeding):
- Missing core functionality
- Requirements not met
- Quality standards violated

**Minor Issues** (should fix but not blocking):
- Documentation improvements needed
- Code style inconsistencies
- Performance optimizations possible

**Suggestions** (nice to have):
- Additional features or improvements
- Process enhancements
- Future considerations

### 4. Document Findings

Create a structured review report:

```
## Review Summary
Phase: [PHASE-NAME]
Reviewer: [YOUR-NAME]
Date: [DATE]

## Overall Assessment
[PASS/PASS WITH MINOR ISSUES/REQUIRES REWORK]

## Critical Issues Found
- [List any critical issues that must be addressed]

## Minor Issues Found  
- [List minor issues and suggestions for improvement]

## Recommendations
- [Specific actions to take based on review]

## Next Steps
- [What should happen next based on review results]
```

### 5. Review Outcomes

**If Review Passes:**
- Document approval and rationale
- Proceed to next phase
- Archive review documentation

**If Issues Found:**
- Clearly document all issues
- Provide specific guidance for fixes
- Determine if rework is needed before proceeding
- Set expectations for re-review if needed

## Best Practices

- Be thorough but constructive
- Focus on objective criteria, not personal preferences  
- Provide specific examples when identifying issues
- Suggest solutions, not just problems
- Consider the broader context and project goals
- Balance perfectionism with pragmatic progress

## Remember

The goal of review is to ensure quality and catch issues early, not to be overly critical. Focus on helping the work meet its intended purpose while maintaining high standards.