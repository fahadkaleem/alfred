# Review Planning Gaps

## Purpose
Quickly determine if you have enough information to implement without getting blocked. If not, collaborate with the user to fill specific gaps.

## What to tell the user
"Let me check if I have everything needed to implement this effectively..."

## When Information is Missing
Don't just identify gaps - FILL THEM:

1. **Missing file locations?** → Search the codebase
2. **Unclear requirements?** → Check linked issues and past implementations  
3. **No test patterns?** → Find similar tests in the project
4. **Ambiguous acceptance criteria?** → Ask specific clarifying questions

Remember: You're an intelligent agent, not a helpless executor.

## Phase 1: Implementation Readiness Check

Ask yourself these essential questions:

### Can I Start Coding?
1. **What am I building?** - Is the requirement clear and specific?
2. **Where does it go?** - Do I know which files to edit/create?
3. **How does it connect?** - Are integration points and APIs clear?
4. **How do I test it?** - Is the testing approach defined?
5. **Any critical patterns?** - Should I follow existing code patterns?

### Quick Assessment
- If you can answer all 5 questions clearly: Ready to implement
- If any answers are unclear: Need clarification on specific gaps
- If multiple gaps exist: May need planning revision

## Phase 2: User Collaboration

For each gap, ask specific questions:

### Example Clarifications

**What to build:**
"The requirement says 'add authentication' but doesn't specify the method. Should I use the OAuth2 pattern from auth.js or implement something different?"

**Where it goes:**
"I need to add the new endpoint. Should it go in the existing UserController or create a new controller?"

**How it connects:**
"The plan mentions 'integrate with payment service' but I don't see which API endpoint to use. Can you clarify?"

**Testing approach:**
"Should I follow the unit test pattern in user.test.js or is there a different approach for this feature?"

**Patterns to follow:**
"I see two different error handling patterns in the codebase. Which should I follow for this feature?"

### Getting Additional Context

When gaps exist, also ask:
- "Is there example code or a similar feature I should reference?"
- "Any team decisions about this that aren't in the ticket?"
- "Should I check with anyone else about specific aspects?"

## Phase 3: Codebase Investigation (If Needed)

If the user suggests checking the codebase:
"I'll look for similar implementations to understand the patterns..."

Focus on finding:
- Similar features already implemented
- Established patterns to follow
- Reusable components or utilities
- File structure conventions

## Phase 4: Document Planning Gaps

After clarifications, document gaps for process improvement:

To add comment documenting gaps:
→ load_instructions("jira/add-comment")

### Planning Gap template

```markdown
## Planning Gaps Identified

### Gap: [What was unclear]
**Found:** [What was missing]
**Clarified:** [Resolution from user]
**For planner:** [How to catch this next time]

### Gap: [What was unclear]
**Found:** [What was missing]
**Clarified:** [Resolution from user]
**For planner:** [How to catch this next time]

### Implementation Approach Confirmed
Based on clarifications:
- [Approach for requirement 1]
- [Approach for requirement 2]
- [File locations confirmed]
- [Testing strategy confirmed]
```

## Key Principles

1. **Focus on Implementation** - Can I code this now?
2. **Be Specific** - "Authentication method unclear" not "missing details"
3. **Get Confirmation** - "So I'll implement X using Y pattern, correct?"
4. **Document Decisions** - Write down what was clarified

## Next Step

With all gaps identified and filled, proceed to "Extract implementation context" to build your implementation strategy based on the complete picture.