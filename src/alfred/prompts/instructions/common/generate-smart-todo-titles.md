# Generate Smart Todo Titles

When creating todos for workflow phases and subtasks, generate concise, descriptive titles that clearly communicate the work to be done.

## Format Guidelines

### For Phase-Level Todos
Format: `[Phase] - Brief description of objective`

Examples:
- "Plan - Design authentication system"
- "Implement - Add OAuth2 integration"
- "Test - Validate security requirements"
- "Review - Check code quality"
- "Finalize - Deploy and document"

### For Subtasks Within a Phase
Format: `[Phase] - Specific action`

Examples:
- "[Plan] - Analyze existing codebase"
- "[Plan] - Extract requirements from ticket"
- "[Implement] - Create authentication service"
- "[Implement] - Add login endpoint"
- "[Test] - Write unit tests for auth"

## Best Practices

1. **Be Specific**: Focus on what will actually be done
   -  "Execute Planning Phase for AV-5"
   -  "Plan - Design error boundary system"

2. **Keep It Concise**: Aim for under 50 characters
   -  "Implement the complete authentication and authorization system with OAuth2"
   -  "Implement - OAuth2 authentication"

3. **Action-Oriented**: Start with the action verb
   -  "The system needs error handling"
   -  "Add error handling middleware"

4. **Context-Aware**: Use JIRA ticket information
   - Read the ticket title and description
   - Extract the main objective
   - Create titles that reflect the actual work

5. **Avoid Redundancy**: Don't repeat information
   -  "AV-5: Plan authentication for AV-5"
   -  "Plan - Authentication system"

## When You Can't Determine Specifics

If the JIRA ticket doesn't provide enough context, use simple phase names:
- "Plan"
- "Implement"
- "Test"
- "Review"
- "Finalize"

This is better than generic, verbose titles.

## Examples by Phase

### Planning Phase
- "Plan - API architecture"
- "Plan - Database schema design"
- "Plan - Security requirements"

### Implementation Phase
- "Implement - User model"
- "Implement - API endpoints"
- "Implement - Frontend components"

### Testing Phase
- "Test - Unit tests"
- "Test - Integration tests"
- "Test - Security validation"

### Review Phase
- "Review - Code quality"
- "Review - Performance metrics"
- "Review - Documentation"

### Finalize Phase
- "Finalize - Deploy to staging"
- "Finalize - Update documentation"
- "Finalize - Close ticket"