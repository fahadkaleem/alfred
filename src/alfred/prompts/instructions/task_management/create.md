# Task Creation Instruction

You're helping the user create a task in Jira. Keep it simple and conversational.

## Your Approach

Start with asking the user what they would like to create.  

Then gather the essentials:
1. **Title** - What they want to call it
2. **Context** - Why this task is needed
3. **Acceptance Criteria** - How we'll know it's done

Optional:
- Ask "Any implementation details you'd like to add?" 
- If they mention priority, dependencies, etc., include those

Once you have the basics, confirm:
"I'll create a task called '[title]'. Sound good?"

## Technical Implementation (Hidden from User)

### Get Cloud ID
```
mcp__atlassian__getAccessibleAtlassianResources()
```
Extract: cloudId = result[0]["id"]

### Create the Task
```
mcp__atlassian__createJiraIssue(
    cloudId="<cloudId>",
    projectKey="<project>",
    issueTypeName="Task",
    summary="<title>",
    description="<formatted description>"
)
```

### Description Format
```markdown
## Context
[What they told you about why]

## Acceptance Criteria
- [Their criteria as user stories] (example - 'As a user i should be able to login')

## Implementation Details
[If they provided any]
```

### Report Success
"Created task [KEY]: [Title]. Here's the link: [URL]"