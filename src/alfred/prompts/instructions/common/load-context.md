# Load Context Instruction

## Purpose
Load all relevant context for a task including implementation plans, past decisions, and discovered patterns. This enables continuity across sessions and phases.

## When to Load Context

### Always Load At Phase Start
Before beginning any phase, load context to understand:
- Previous work on this task
- Implementation plans created during planning
- Related decisions and constraints
- Discovered patterns and approaches
- Open questions or blockers

### Load During Work When You Need
- The implementation plan details
- Context about a previous decision
- Understanding of discovered patterns  
- Clarification on requirements
- Technical approaches used before

## The load_context Tool

```python
# Load all context for a task
context = load_context(
    task_id="{{ task_id }}"  # Task ID to load context for
)

# Load specific context type
context = load_context(
    task_id="{{ task_id }}",
    context_type="plan"  # Optional: specific context type
)

# Returns:
# - contexts: List of all saved contexts with content and metadata
# - plan: Implementation plan if available
# - summary: Latest planning summary if available
```

## Common Context Types to Load

```python
# Load planning context
context = load_context("{{ task_id }}", "plan")

# Load implementation progress
context = load_context("{{ task_id }}", "implementation")

# Load all contexts (default)
context = load_context("{{ task_id }}")
```

## Context Types You'll Find

- `plan` - Comprehensive planning context with implementation tasks
- `implementation` - Progress during implementation
- `test` - Testing results and findings
- `review` - Review findings and feedback
- `brainstorm` - Results from brainstorming sessions
- `research` - Research and analysis results
- `decision` - Important technical/business decisions
- `progress` - General progress updates
- `milestone` - Significant achievements

## Using the Loaded Context

### 1. At Implementation Start
```python
# Load everything to understand the task
context = load_context("{{ task_id }}")

# Extract the implementation plan
if context.data.get("plan"):
    # Use the plan to create implementation todos
    plan = context.data["plan"]
```

### 2. During Implementation
```python
# Load specific context when needed
context = load_context("{{ task_id }}", "plan")

# Use the planning decisions to guide implementation
planning_context = context.data["contexts"][0]["content"]
```

### 3. For Understanding Decisions
```python
# Load all context and look for specific decisions
context = load_context("{{ task_id }}")

for ctx in context.data["contexts"]:
    if ctx["context_type"] == "decision":
        # Found a decision context
        print(ctx["content"])
```

## Best Practices

### DO:
- Load context at the start of every phase
- Use specific context_type when you know what you need
- Check for plan context when starting implementation
- Review plan context for implementation tasks and decisions

### DON'T:
- Don't assume context exists - check the response
- Don't ignore context from previous phases
- Don't skip loading context to save time

## Next Step
After loading context, proceed with your work informed by previous decisions and plans.