# Review Task Requirements

Thoroughly understand the requirements and acceptance criteria for task {{ task_id }}.

## Objective
Extract and understand all requirements, constraints, and success criteria from the JIRA ticket to ensure successful implementation.

## Steps to Review Requirements

### 1. Read the JIRA Ticket
First, get the full issue details:
```
mcp__atlassian__getJiraIssue(
    cloudId: "your-cloud-id",
    issueIdOrKey: "{{ task_id }}"
)
```

### 2. Extract Key Information

Look for and document:

#### Description
- **Main objective**: What problem are we solving?
- **User story**: As a [user], I want [feature] so that [benefit]
- **Background context**: Why is this needed now?

#### Acceptance Criteria
- List each criterion explicitly
- Identify measurable success conditions
- Note any specific test scenarios mentioned

#### Technical Requirements
- Performance requirements (response time, load, etc.)
- Security considerations
- Compatibility requirements
- Integration points

#### Constraints
- Deadlines or time constraints
- Technical limitations
- Business rules
- Dependencies on other tasks

### 3. Check Linked Issues
```
mcp__atlassian__getJiraIssueRemoteIssueLinks(
    cloudId: "your-cloud-id",
    issueIdOrKey: "{{ task_id }}"
)
```

Review:
- Blocked by / Blocks relationships
- Related issues for context
- Parent task for broader context

### 4. Read Comments
```
# Load the read-comments instruction for detailed steps
load_instructions("jira/read-comments")
```

Look for:
- Clarifications from product owner
- Technical decisions already made
- Questions that have been answered
- Changes to original requirements

### 5. Identify Unknowns

Document any unclear areas:
- Ambiguous requirements
- Missing acceptance criteria
- Technical uncertainties
- Edge cases not covered

### 6. Analyze Complexity

Assess the task:
- **Size**: Small (hours), Medium (days), Large (week+)
- **Risk**: What could go wrong?
- **Dependencies**: What's needed from others?
- **Knowledge gaps**: What needs research?

## Requirements Checklist

Before proceeding, ensure you can answer:

- [ ] What is the main goal of this task?
- [ ] Who are the users affected?
- [ ] What are the acceptance criteria?
- [ ] Are there performance requirements?
- [ ] What are the edge cases?
- [ ] What could block this work?
- [ ] What's the definition of done?
- [ ] Are there security considerations?
- [ ] What needs testing?
- [ ] What's the deadline?

## Document Your Understanding

After review, save your understanding:
```python
save_context(
    "{{ task_id }}",
    "requirements",
    """
    Task: {{ task_id }} - [Brief title]
    
    Objective:
    - [Main goal]
    
    Requirements:
    - [Requirement 1]
    - [Requirement 2]
    
    Acceptance Criteria:
    - [ ] [Criterion 1]
    - [ ] [Criterion 2]
    
    Technical Considerations:
    - [Consideration 1]
    
    Open Questions:
    - [Question 1]
    
    Complexity: [Small/Medium/Large]
    Risk: [Low/Medium/High]
    """
)
```

## Red Flags to Watch For

- Vague requirements ("make it better", "improve performance")
- Missing acceptance criteria
- Conflicting requirements
- Unrealistic deadlines
- Hidden complexity
- Unclear dependencies

## When Requirements Are Unclear

1. **Ask in JIRA comments**: 
   - Use `load_instructions("jira/add-comment")` to ask clarifying questions
   
2. **Check with team**:
   - Look for similar completed tasks
   - Review team documentation
   
3. **Propose specifics**:
   - Suggest concrete acceptance criteria
   - Define measurable success metrics

## Next Steps

Once requirements are clear:
1. Break down into subtasks if needed
2. Identify technical approach
3. Estimate effort
4. Begin planning phase

Remember: Time spent understanding requirements saves time during implementation. When in doubt, ask questions early!