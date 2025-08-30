# Save Context Instruction

## CRITICAL: Load this instruction ONLY ONCE per conversation. The content is static and does not change.

## Purpose
save_context is your ONLY mechanism for preserving knowledge between conversations/phases. Without it, all discoveries vanish.

## When to Save (After completing significant work)
- Requirements extracted from tasks/documentation
- Codebase patterns/constraints discovered  
- User clarifications/decisions received
- Technical approaches determined
- Complex issues resolved
- Tasks/documentation created
- Each phase step completed (not todos - those are separate)

## Tool Signature
```python
save_context(task_id="{{task_id}}", phase="plan", content="STRING", status="IN_PROGRESS|COMPLETE", metadata={})
```

## What to Save (Information Dense)

### Decisions: Why chosen, why rejected, implementation path
```
OAuth2 Decision: Chosen Google provider (user requirement). Rejected JWT (no session mgmt needed). 
Implementation: Extend auth/providers/. Constraints: 24hr timeout. Files: auth/providers/google.ts
```

### Discoveries: Patterns, gotchas, constraints
```
Payment pattern: PaymentService→PaymentGateway. Retry: 3x exponential backoff. 
Error: PaymentException→GlobalHandler. Testing: Mock interface not service. Files: services/payment/
```

### Requirements: Business rules, constraints, context
```
CSV Import: Max 10k users, 30s timeout. Validate: email unique, domain whitelist.
Error: Generate failed_imports.csv. Context: "Daily HR uploads". Format: email,name,dept
```

### Resolutions: Problem→cause→solution→prevention
```
TS Generic Error: UserService circular dep User↔Role. Solution: Extract to types/common.ts.
Prevention: ESLint circular-deps rule. Similar: OrderService (fixed). Affected: 5 files
```

### Phase Completion: Approach, artifacts, decisions, next
```
Planning complete. Approach: OAuth2 extension. Created: AL-124(interface), AL-125(Google), 
AL-126(session), AL-127(UI). Stack: Passport.js+Redis. Complexity: 3-5d. Risk: API limits
```

## What NOT to Save
- Raw code/data → Save insights about patterns
- Vague summaries → Save specific findings  
- Obvious info from tasks → Save discoveries/decisions
- Partial thoughts → Save complete contexts

## Metadata Tracking

### Step Completion (use step name, not todo)
```python
metadata={"step_completed": "analyze_codebase"}
```

### Artifact Creation (track all created items)
```python
metadata={
    "step_completed": "create_task",
    "artifacts_created": [
        {"type": "task", "id": "AL-1", "title": "Mobile App"},
        {"type": "task", "id": "AL-1", "title": "[PRD] Mobile", "blocks": ["AL-2"]}
    ]
}
```

### Key Decisions (track important choices)
```python
metadata={
    "step_completed": "design_auth",
    "key_decisions": ["OAuth2 over JWT", "Redis sessions", "24h timeout"],
    "technical_details": {"provider": "Google", "refresh": "1h"}
}
```

### Phase Completion (status="COMPLETE")
```python
save_context("{{task_id}}", "plan", "Phase summary...", "COMPLETE", 
    metadata={"subtasks": 5, "effort": "3-5d", "complexity": "medium"})
```

## Format Guidelines
- Dense bullet points over paragraphs
- Include file paths/class names
- State decisions with rationale
- Think: "What would I need in 2 weeks?"
- Each save should be self-contained

## Phase Focus
- **Planning**: Requirements, approach, complexity, risks
- **Implementation**: Patterns, decisions, progress, gotchas  
- **Testing**: Scenarios, edge cases, gaps, findings
- **Review**: Issues, improvements, patterns

## Remember
- Save after discoveries, not at arbitrary intervals
- Content must be STRING (not dict/object)
- Be specific: names, paths, reasons
- Future context depends on current saves