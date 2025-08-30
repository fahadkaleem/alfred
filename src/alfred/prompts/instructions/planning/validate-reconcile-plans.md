# Validate and Reconcile Plans

## Goal
You've already found existing plans in Step 1. Now you have context (Step 2) and codebase knowledge (Step 3). Time to VALIDATE if those plans are still accurate and IDENTIFY what they missed.

## Instructions

### Phase 1: Validation Against Current Codebase
For EVERY technical decision or file reference in the existing plan:

1. **Verify file existence**:
   - "Plan says modify auth.js" → Does auth.js exist? Or is it now auth.ts?
   - "Plan references UserService" → Does this class still exist? Same location?

2. **Check implementation status**:
   - "Plan says implement OAuth" → Is OAuth already partially implemented?
   - "Plan says add caching" → Does caching already exist elsewhere?

3. **Validate assumptions**:
   - "Plan assumes REST API" → Is it still REST or did it move to GraphQL?
   - "Plan uses Redis" → Is Redis still the caching solution?

### Phase 2: Gap Analysis
Compare your codebase analysis (Step 3) with the existing plan:

1. **What did the previous planner miss?**
   - Files they didn't find
   - Integration points they overlooked
   - Dependencies they didn't consider
   - Test patterns they ignored

2. **What has changed since the plan?**
   - New code added
   - Architecture changes
   - Different libraries/frameworks
   - Updated requirements in comments

3. **What failures can we learn from?**
   - If subtasks were attempted, why did they fail?
   - What questions did implementers ask? (reveals plan gaps)
   - What got blocked? Why?

### Phase 3: Reconciliation Strategy

Based on validation and gaps, decide:

1. **Keep and enhance**: Plan is 80%+ valid
   - Use existing structure
   - Add missing pieces you found
   - Update outdated references
   - Address feedback points

2. **Major revision**: Plan is 50-80% valid
   - Keep valid architectural decisions
   - Rebuild implementation details
   - Incorporate new findings
   - Address all past feedback

3. **Start fresh**: Plan is <50% valid or fundamentally flawed
   - Document why the old plan won't work
   - Note any valuable insights to keep
   - Build new plan with lessons learned

## Acceptance Criteria

- [ ] Validated EVERY file reference and technical decision against current code
- [ ] Identified ALL gaps between old plan and your codebase analysis
- [ ] Extracted lessons from any failed implementation attempts
- [ ] Made clear decision: keep/revise/restart with justification
- [ ] Documented what to preserve and what to change

## Output Format

```
### Validation Results
Files that moved/changed:
- auth.js → auth.ts (plan needs update)
- UserService → Now split into UserService + AuthService

Already implemented:
- OAuth2 flow exists in auth.ts (plan said to create from scratch)

### Gap Analysis
Previous plan missed:
- WebSocket authentication requirements
- Rate limiting considerations
- Database migration needs

### Reconciliation Decision: [Keep/Revise/Restart]
Reasoning: [Why this decision]

What to keep:
- [Valid decisions/insights]

What to change:
- [Outdated/incorrect parts]

Lessons learned:
- [Why previous attempts failed]
```

## Next Step
With validated knowledge of what exists and what's needed, proceed to "Ask clarifying questions".