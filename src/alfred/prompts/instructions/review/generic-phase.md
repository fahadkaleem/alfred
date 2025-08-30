# Generic Phase Review

## Purpose
Conduct comprehensive review of the completed phase work to ensure quality, completeness, and readiness for next phase.

## When to Use
This instruction is automatically loaded when a phase has `requires_review: true` but no custom review instruction specified.

## Review Process

### 1. Load Phase Context
```python
load_context("{{ task_id }}", "{{ reviewed_phase }}")
```
Review all context from the completed phase to understand what was accomplished.

### 2. Quality Assessment

**Completeness Check:**
- Were all phase objectives met?
- Are there any gaps in the deliverables?
- Were all acceptance criteria satisfied?

**Quality Standards:**
- Is the work up to professional standards?
- Are best practices followed?
- Is documentation adequate?

**Technical Review:**
- Are technical decisions sound?
- Are there any security or performance concerns?
- Is the approach scalable and maintainable?

### 3. Deliverable Validation

**Review Key Outputs:**
- Check all files, documents, or artifacts created
- Validate against requirements and acceptance criteria
- Ensure consistency with project standards

**Integration Check:**
- Does work integrate properly with existing systems?
- Are interfaces and dependencies handled correctly?
- Are there any conflicts or breaking changes?

### 4. Risk Assessment

**Identify Risks:**
- Technical risks in the implementation
- Dependencies that could cause delays
- Areas that need additional attention

**Mitigation Planning:**
- What steps can reduce identified risks?
- Are there alternative approaches to consider?
- What monitoring or validation is needed?

### 5. Next Phase Readiness

**Prerequisites Check:**
- Are all prerequisites for next phase met?
- Is documentation sufficient for handoff?
- Are any additional approvals needed?

**Recommendations:**
- Specific guidance for next phase team
- Areas requiring extra attention
- Lessons learned to apply going forward

## Review Outcomes

### Approval Decision
Choose one outcome:

** Approved - Ready for Next Phase**
- All criteria met, no blocking issues
- Minor recommendations noted for improvement

** Approved with Conditions**  
- Most criteria met, some improvements needed
- Specific actions required before next phase

** Needs Revision**
- Significant gaps or quality issues
- Must address critical items before proceeding

### Document Review Results
```python
save_context(
    task_id="{{ task_id }}",
    phase="{{ reviewed_phase }}_review", 
    content="[Review findings and decision]",
    status="COMPLETE",
    metadata={
        "review_outcome": "approved|conditional|revision_needed",
        "critical_issues": ["list of blocking issues"],
        "recommendations": ["improvement suggestions"],
        "next_phase_ready": true/false
    }
)
```

## Example Review Summary

```
{{ reviewed_phase|title }} Phase Review Complete: Approved with minor recommendations.

Quality Assessment:
 All phase objectives met
 Technical approach is sound  
 Documentation is adequate
️  Consider adding error handling in auth flow

Deliverable Validation:
 Plan Artifact complete and detailed
 All subtasks created in JIRA
 Architecture decisions documented
️  Database migration scripts need review

Risk Assessment:
- Low risk: Well-established patterns used
- Medium risk: Third-party API dependency (mitigation: fallback plan)
- Timeline: On track for next phase

Next Phase Readiness:  Ready to proceed
Recommendations: Add comprehensive error handling, review DB migrations

Review Outcome: APPROVED with conditions
```

## Completion
After documenting review results, mark this review step as completed and proceed to next phase or revision as determined.