# Create Subtasks

## Goal
Break down the main task into self-contained implementation packages. Each subtask should provide EVERYTHING a developer needs to implement that piece without looking elsewhere.

## When to Create Subtasks

### Create subtasks when:
- Total work exceeds 8 hours (1 day)
- Multiple independent pieces exist that can be worked on in parallel
- Different skill sets are required (e.g., backend API vs frontend UI)
- Natural testing boundaries exist between components
- Logical phases make sense (e.g., data layer → API → UI)

### DON'T create subtasks when:
- Task is < 4 hours of cohesive work
- Changes are tightly coupled and must be done together
- Single file or component change
- One developer will implement everything sequentially anyway

### Examples:
- **"Fix login error message"** → NO subtasks (single change)
- **"Add dark mode to application"** → YES subtasks:
  - Implement theme state management
  - Create theme toggle component
  - Add theme persistence layer
  - Apply theme styles across components

## Subtask Design Principles

Each subtask must be:
- **Independent**: Can be started without waiting for other subtasks
- **Complete**: Has clear definition of done
- **Testable**: Can be verified in isolation
- **Sized right**: 2-8 hours of focused work
- **Self-contained**: ALL implementation details included

## Subtask Description Template

Every subtask MUST follow this structure:

```markdown
# Context
[Plain English explanation of WHAT this subtask does and WHY it's needed]
- How this piece fits into the overall feature
- Business/technical reason for this work
- Dependencies on or from other subtasks (if any)

# Acceptance Criteria
[Specific, testable requirements - these define "done"]
- [ ] User can perform X action
- [ ] System responds with Y when Z occurs
- [ ] Performance remains under Nms
- [ ] All tests pass
- [ ] No regressions in existing functionality

# Implementation Details
[Everything needed to code this without searching the codebase]

## Files to Modify
- `path/to/file1.ts` - Add new method after line 123
- `path/to/file2.tsx` - Update component to use new prop

## Code Patterns to Follow
- Authentication: Follow pattern in `src/auth/middleware.ts:45-89`
- Error handling: Use approach from `src/utils/errors.ts:23-45`
- State management: See `src/store/user.ts` for similar pattern

## Integration Points
- Call UserService.getProfile() from `src/services/user.ts:34`
- Emit 'user-updated' event via `src/events/emitter.ts`
- Update cache using `src/cache/redis.ts:invalidate()`

## Configuration Required
- Add `FEATURE_FLAG_DARK_MODE` to `.env`
- Update `config/features.json` with new flag

## Testing Approach
- Unit tests: Add to `tests/unit/theme.test.ts`
- Integration: Update `tests/e2e/settings.test.ts`
- Use existing mocks from `tests/mocks/localStorage.ts`

## Important Notes
- Performance: Theme switch must be instant (<50ms)
- Accessibility: Respect prefers-color-scheme
- Storage: Use localStorage with fallback to cookies
```

## Example: Real Subtask

```markdown
Title: "Implement theme context and state management"

## Context
This subtask creates the foundational theme system that other components will use. It manages the current theme state (light/dark), provides theme switching functionality, and integrates with system preferences. This is the first subtask because all UI components will depend on this theme context.

## Acceptance Criteria
- ThemeProvider component wraps the application
- useTheme hook returns current theme and toggle function
- System preference (prefers-color-scheme) is detected on load
- Theme changes are instant with no flash
- Theme state persists across page reloads
- Tests cover all theme switching scenarios

## Implementation Details

### Files to Modify
- Create `src/contexts/ThemeContext.tsx` - New theme context
- Update `src/App.tsx` - Wrap with ThemeProvider at line 15
- Create `src/hooks/useTheme.ts` - Custom hook for components

### Code Patterns to Follow
- Context pattern: Similar to `src/contexts/AuthContext.tsx:12-45`
- Hook pattern: Follow `src/hooks/useAuth.ts` structure
- Local storage: Use utility from `src/utils/storage.ts:setItem()`

### Integration Points
- Read system preference via `window.matchMedia('(prefers-color-scheme: dark)')`
- Store preference using `StorageUtil.setItem('theme', value)`
- Emit theme-changed event for analytics: `analytics.track('theme-changed', { theme })`

### Configuration Required
- None - this is purely client-side

### Testing Approach
- Unit tests: Create `tests/contexts/ThemeContext.test.tsx`
  - Test provider renders
  - Test hook returns correct values
  - Test theme persistence
  - Test system preference detection
- Mock localStorage using `tests/mocks/localStorage.ts`
- Mock matchMedia using pattern from `tests/mocks/window.ts:23`

### Important Notes
- Avoid flash of wrong theme by reading localStorage synchronously before first render
- Add 'color-scheme' CSS property to html element for native form controls
- Consider users with 'prefers-reduced-motion' for theme transitions
```

## Before Creating Subtasks

Present your breakdown to the user:
```
"Based on our discussion and my analysis, I'll create [X] subtasks:

1. **[Title]** - [One line summary] (Est: X hours)
2. **[Title]** - [One line summary] (Est: X hours)

This breakdown allows parallel development and clear testing boundaries. Each subtask contains all implementation details needed.

Does this look good, or would you like adjustments?"
```

Wait for confirmation before creating!

## Handling Dependencies

**What to tell the user:** "I'll note the dependencies between tasks..."

### Create Dependencies
To manage subtask dependencies:
Use add_dependency(task_id, depends_on_task_id) to create task dependencies

### Dependency Guidelines
- Only create dependencies when truly needed
- Prefer parallel work when possible
- Document why dependency exists
- Consider "soft" dependencies in descriptions

## Progress Updates

As you create each subtask:
- Show the user what was created
- Include the issue key (e.g., "Created AL-101: [Title]")
- Confirm successful creation
- Handle any errors gracefully

## Important Notes
- Keep subtasks focused and atomic
- Include context from codebase analysis
- Make acceptance criteria specific
- Ensure estimates are realistic
- Create subtasks in logical order

## Next Step
Mark this task as completed and proceed to "Save comprehensive Plan Artifact".