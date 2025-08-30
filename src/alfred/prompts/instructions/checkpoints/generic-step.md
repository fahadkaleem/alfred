# Generic Step Checkpoint

## Purpose
Save focused context for this critical step milestone to capture key progress and decisions.

## When to Use
This instruction is automatically loaded when a step has `checkpoint: true` but no custom checkpoint instruction specified.

## Save Context Instructions

### Step Context Format
Save focused context that captures:

**Step Accomplishment:**
- What specific work was completed
- Key findings or insights from this step
- Any problems solved or decisions made

**Important Details:**
- Technical discoveries or patterns
- Data gathered or analyzed
- Files or artifacts created

**Impact on Phase:**
- How this affects the overall phase progress
- Dependencies resolved or new ones discovered
- Any changes to approach or timeline

### Save Context Call
```python
save_context(
    task_id="{{ task_id }}",
    phase="{{ phase_name }}",
    content="[Focused step summary]",
    status="IN_PROGRESS",
    metadata={
        "step_completed": "{{ step_name }}",
        "artifacts": ["files created/modified"],
        "key_insights": ["important discoveries"]
    }
)
```

## Example Step Context Save

**Step: Analyze Codebase**
```
Codebase Analysis Complete: Found authentication patterns, identified integration points.

Key Findings:
- Auth handled by middleware/auth.js (JWT validation)
- User data in models/User.js (Mongoose schema)
- Sessions stored in Redis (config/redis.js)
- Password hashing uses bcrypt with 12 rounds

Integration Points:
- POST /api/auth/login - returns JWT token
- GET /api/user/profile - requires auth header
- Middleware checks auth on protected routes

Files Analyzed:
- middleware/auth.js: JWT validation logic
- models/User.js: User schema with auth fields
- routes/auth.js: Login/logout endpoints
- config/redis.js: Session configuration

Impact: Implementation approach confirmed, no changes needed to existing auth flow.
```

## Completion
After saving context, mark this checkpoint step as completed in your todos and continue with the next step.