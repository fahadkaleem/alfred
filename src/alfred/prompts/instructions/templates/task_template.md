# Task: [TASK_ID] - [Brief Task Title]

## Overview
[1-2 sentences describing what this task accomplishes and why it's important for Alfred]

## Context
[Provide background information that helps the engineer understand:]
- Where this fits in the Alfred architecture
- What components it interacts with
- Any decisions from alfred.md that apply
- Links to relevant documentation or code examples

## Prerequisites
- [ ] Alfred project structure is set up
- [ ] Dependencies installed (`uv sync`)
- [ ] Familiar with [relevant concepts/tools]
- [ ] Read alfred.md sections: [list relevant decisions]

## Implementation Details

### Files to Create/Modify
```
src/alfred/
├── [file1.py]     # Description of what goes here
├── [file2.py]     # Description of what goes here
└── tests/
    └── [test_file.py]  # Tests for this component
```

### Step-by-Step Implementation

1. **[First Major Step]**
   ```python
   # Example code structure or interface
   ```
   - Key considerations
   - Potential gotchas

2. **[Second Major Step]**
   - Detailed instructions
   - Code patterns to follow

3. **[Continue for all steps...]**

### Code Standards
- Use type hints for all functions
- Follow the error handling pattern from Decision #7
- Keep functions small and focused
- Document complex logic with comments

### Example Implementation
```python
# Show a small but complete example of the expected pattern
# This helps junior engineers understand the style
```

## Testing Strategy

### Unit Tests Required
- [ ] Test happy path scenarios
- [ ] Test error conditions
- [ ] Test edge cases
- [ ] Test with missing/invalid inputs

### Test Structure
```python
# tests/test_[component].py
import pytest
from alfred.[module] import [function]

class Test[ComponentName]:
    def test_[scenario]_success(self):
        """Test that [scenario] works correctly."""
        # Arrange
        
        # Act
        
        # Assert
    
    def test_[scenario]_handles_error(self):
        """Test that [error condition] is handled properly."""
        # Test implementation
```

### Specific Test Cases
1. **[Test Case 1]**: Description and expected behavior
2. **[Test Case 2]**: Description and expected behavior
3. **[Continue for all critical cases...]**

### Testing Commands
```bash
# Run tests for this component
pytest tests/test_[component].py -v

# Run with coverage
pytest tests/test_[component].py --cov=alfred.[module] --cov-report=term-missing
```

## Acceptance Criteria

### Functional Requirements
- [ ] [Component] can [do primary function]
- [ ] Error messages are helpful and actionable
- [ ] Handles missing/invalid inputs gracefully
- [ ] Integrates with [other components] correctly
- [ ] No hardcoded values (use config or constants)

### Code Quality
- [ ] All functions have type hints
- [ ] All public functions have docstrings
- [ ] No functions longer than 50 lines
- [ ] Passes linting (`ruff check src/alfred/[module].py`)
- [ ] No commented-out code
- [ ] Meaningful variable names

### Testing
- [ ] Unit tests achieve >90% code coverage
- [ ] All test cases from Testing Strategy are implemented
- [ ] Tests are independent (no shared state)
- [ ] Tests run in <1 second
- [ ] No tests are skipped without explanation

### Documentation
- [ ] Module docstring explains purpose
- [ ] Complex logic has inline comments
- [ ] Any deviations from alfred.md are documented
- [ ] README updated if adding new concepts

## Dependencies
- External packages: [list any new pip packages needed]
- Internal modules: [list alfred modules this depends on]
- Templates: [list any template files needed]

## Potential Challenges
- [Known difficulty 1 and suggested approach]
- [Known difficulty 2 and suggested approach]

## Definition of Done
- [ ] All acceptance criteria met
- [ ] Code reviewed by senior engineer
- [ ] Tests passing in CI
- [ ] No merge conflicts with main branch
- [ ] Task marked complete in tracking system

## Resources
- [Link to relevant documentation]
- [Link to similar implementations]
- [Link to design decisions]

## Notes for Reviewer
[Any specific areas where you'd like feedback or weren't sure about approach]

---

**Time Estimate**: [X hours]
**Complexity**: [Low/Medium/High]
**Priority**: [P0/P1/P2]