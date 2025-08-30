# Conversational Understanding

## Goal
Extract ALL hidden requirements, constraints, and context the user knows but hasn't written. Use progressive questioning based on task complexity.

## First: Assess Complexity

After analyzing the ticket and codebase, determine:

### Simple/Clear Tasks
If the task is straightforward (e.g., "Add loading spinner to submit button", "Fix typo in error message"):

```
"I analyzed {{ task_id }} and the codebase. This looks straightforward:
[One sentence summary of what needs to be done]

I have everything I need to plan this. The implementation is clear:
[Brief outline of approach]

Does this match your expectations, or are there any specific requirements I should consider?"
```

**If user confirms → Proceed to planning**

### Complex/Ambiguous Tasks
If ANYTHING is unclear, missing, or could be interpreted multiple ways → Use full gap analysis:

## Instructions for Complex Tasks

### Phase 1: Gap Analysis (Internal Thinking)
Before asking questions, analyze:

```
WHAT I KNOW:
- From ticket: [List all requirements explicitly stated]
- From codebase: [List all technical findings]
- From existing plans: [List all decisions/feedback]

WHAT I NEED TO KNOW:
- Missing acceptance criteria: [What success looks like]
- Technical constraints: [Performance, security, compatibility]
- Integration details: [How it connects to existing systems]
- Edge cases: [What could go wrong]
- Non-functional requirements: [Scale, maintenance, monitoring]

GAPS TO FILL:
[List specific unknowns that would block implementation]
```

### Phase 2: Progressive Questioning

Structure questions from broad to specific:

```
ROUND 1 - Foundational Understanding:
"I analyzed {{ task_id }} and found [key findings].

To create a comprehensive plan, I need to clarify:
1. [Scope question - what's included/excluded]
2. [Constraint question - any limitations]
3. [Success criteria - how do we know it's done]"

WAIT FOR RESPONSE

ROUND 2 - Technical Deep Dive:
Based on answers, probe deeper:
- [Implementation specifics]
- [Edge case handling]
- [Integration requirements]
```

### Phase 3: Trust But Verify
When user statements conflict with code:
"You mentioned [X], but the codebase shows [Y]. Should I [option A] or [option B]?"

### Phase 4: Edge Case Exploration
For each major functionality:
- "What should happen when [edge case]?"
- "How should we handle [error scenario]?"
- "Is [assumption] correct?"

## Question Generation Framework

For EACH gap, create questions that:
1. **Reference context**: "I see in the code that..."
2. **Target the gap**: "But I need to know..."
3. **Seek specifics**: "For example, should it..."
4. **Enable decision**: "So I can plan..."

## Acceptance Criteria

For SIMPLE tasks:
- [ ] User confirms understanding is correct
- [ ] No ambiguities exist

For COMPLEX tasks:
- [ ] All implementation ambiguities resolved
- [ ] All edge cases explored
- [ ] All constraints identified
- [ ] Success criteria crystal clear
- [ ] No assumptions remain

## Examples

### Simple Task Example:
"This is a straightforward bug fix - the validation regex for email is rejecting valid addresses with '+' symbols. I'll update the regex pattern and add test cases. Any other email formats we should support?"

### Complex Task Example:
"This authentication overhaul touches multiple systems. I found OAuth2 partially implemented but the ticket mentions 'standard auth'. Let me understand:
1. Should we complete the OAuth2 implementation or replace it?
2. What about existing user sessions during migration?
3. Any compliance requirements (SOC2, GDPR)?"

## Next Step
Mark this task as completed ONLY after the user responds. Then proceed to "Create subtasks".