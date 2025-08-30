# Create Implementation Plan

## Goal
Collaborate with the user to create a clear, executable implementation plan using natural LOST-style structure. This plan will guide the implementation phase with specific, testable tasks.

## Process

### 1. Present Your Understanding
Based on your analysis so far, present a draft implementation plan:

```
Based on my analysis, here's how I would approach implementing {{ task_id }}:

## Implementation Plan

### 1. [First logical task name]
CREATE/UPDATE path/to/file.py
- [Specific requirement or change]
- [Another requirement]
- [Integration point or pattern to follow]
Unit Tests:
- [Test case to verify functionality]
- [Edge case to test]

### 2. [Second logical task name]
UPDATE path/to/another_file.py
- [Specific changes needed]
- [Methods to add/modify]
- [Patterns to follow from existing code]
Unit Tests:
- [Test scenarios]
- [Error cases]

### 3. [Third logical task name]
CREATE path/to/new_file.py
- [Components to create]
- [Interfaces to implement]
- [Dependencies to inject]
Unit Tests:
- [Test coverage needed]
- [Integration tests]

[Continue with all identified tasks...]

Does this approach make sense? Any concerns or changes you'd like me to make?
```

### 2. Iterate Based on Feedback
Listen carefully to user feedback:
- **If they suggest changes**: "Good point about [X]. Let me update task 2 to include [Y]..."
- **If they add requirements**: "I'll add a new task to handle [requirement]..."
- **If they question approach**: "Let me explain why I chose [approach] - [reasoning]. Would you prefer [alternative]?"

### 3. Common Patterns to Include

#### For API Endpoints
```
### Create [endpoint name] endpoint
CREATE/UPDATE routes/[resource].py
- POST/GET/PUT/DELETE /[path] endpoint
- Accept [request format]
- Validate [fields]
- Call [service method]
- Return [response format]
Unit Tests:
- Successful [operation] returns [status]
- Invalid [field] returns 400
- [Edge case] handled properly
```

#### For Service Methods
```
### Implement [service method]
UPDATE services/[service_name].py
- Add [method_name]([parameters]) method
- [Business logic description]
- Handle [error cases]
- Return [return type]
Unit Tests:
- [Happy path test]
- [Error condition test]
- [Edge case test]
```

#### For Data Models
```
### Create [model name] model
CREATE models/[model].py
- Fields: [field1, field2, field3]
- Methods: [method1(), method2()]
- Validations: [validation rules]
Unit Tests:
- Model creation with valid data
- Validation failures for invalid data
- Method behavior tests
```

### 4. Key Principles
- **One logical unit per task** - Each task should be implementable and testable independently
- **Clear file locations** - Always specify CREATE or UPDATE with exact paths
- **Specific requirements** - No vague statements like "implement feature"
- **Testable outcomes** - Every task must have clear test cases
- **Follow existing patterns** - Reference patterns you found during analysis

### 5. Final Confirmation
After iterations, get explicit approval:

```
Here's the final implementation plan:

[Final plan with all tasks]

This plan includes [X] implementation tasks that cover all requirements we discussed. 
The approach follows the existing patterns in your codebase and includes comprehensive tests.

Shall I save this plan and proceed with planning completion?
```

### 6. What NOT to Do
- Don't create overly granular tasks (e.g., "Add import statement")
- Don't create tasks without test cases
- Don't assume implementation details - be specific
- Don't skip user collaboration - this is a dialogue, not a monologue

## Next Step
After user approves the plan, mark this task as completed and proceed to "Save Plan Artifact".