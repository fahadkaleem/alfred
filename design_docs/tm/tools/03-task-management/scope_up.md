# Tool: scope_up

## Purpose
Increase task complexity using AI to add more detailed requirements, edge cases, advanced features, and comprehensive testing scenarios while optionally regenerating pending subtasks to match the new complexity level.

## Business Value
- **Who uses this**: Developers and project managers adjusting task scope
- **What problem it solves**: Allows dynamic scope expansion when tasks prove more complex than initially estimated or when additional requirements emerge
- **Why it's better than manual approach**: AI intelligently adds complexity while preserving completed work, automatically regenerates subtasks to match new scope, and maintains task coherence

## Functionality Specification

### Input Requirements

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `id` | string | Yes | - | Comma-separated list of task IDs (e.g., "1,3,5") |
| `strength` | string | No | "regular" | Strength level: "light", "regular", or "heavy" |
| `prompt` | string | No | - | Custom instructions for specific adjustments |
| `file` | string | No | ".taskmaster/tasks/tasks.json" | Path to tasks file |
| `projectRoot` | string | Yes | - | Absolute path to project directory |
| `tag` | string | No | Current tag | Tag context to operate on |
| `research` | boolean | No | false | Use research capabilities for scoping |

#### Validation Rules
1. `strength` must be one of: "light", "regular", "heavy"
2. All task IDs must exist in the tasks file
3. `projectRoot` must be an existing directory
4. Tasks cannot be completed (done/cancelled status)

### Processing Logic

#### Step-by-Step Algorithm

```
1. VALIDATE_INPUTS
   - Check strength is valid
   - Verify projectRoot exists
   - Resolve tag (use current if not specified)
   - Parse task IDs from comma-separated string
   
2. LOAD_TASK_DATA
   - Read tasks.json from specified path
   - Extract tasks for target tag
   - Validate all task IDs exist
   
3. FOR EACH TASK_ID:

   3.1 GET_ORIGINAL_COMPLEXITY
      - Read complexity report if exists
      - Find task's current complexity score
      - Use for intelligent adjustment calculations
      
   3.2 ADJUST_TASK_COMPLEXITY
      - Build AI prompt for complexity increase
      - Include strength-specific instructions
      - Add custom prompt if provided
      - Call AI service with structured output
      
   3.3 REGENERATE_SUBTASKS (if has subtasks)
      - Identify subtasks by status:
         - Preserve: done, in-progress, review, cancelled, deferred, blocked
         - Regenerate: pending only
      - Calculate new subtask count based on:
         - Strength level
         - Original complexity score
         - Current pending count
         - Preserved count
      - Generate new pending subtasks via AI
      - Combine preserved + new subtasks
      
   3.4 UPDATE_TASK_DATA
      - Apply complexity changes to task
      - Replace subtasks if regenerated
      - Save to tasks.json
      
   3.5 REANALYZE_COMPLEXITY (optional)
      - If session available and original complexity known
      - Run complexity analysis on updated task
      - Compare new vs original scores
      - Log complexity change
      
4. AGGREGATE_RESULTS
   - Combine telemetry data from all tasks
   - Calculate total tokens and costs
   - Generate summary message
   
5. SAVE_AND_RETURN
   - Write updated tasks.json
   - Return updated tasks and telemetry
```

### AI Prompts Used

#### System Prompt for Task Complexity Adjustment
```
You are an expert software project manager who helps adjust task complexity while maintaining clarity and actionability.
```

#### User Prompt for Task Complexity Adjustment (Generated Dynamically)
```
You are tasked with adjusting the complexity of a task. 

CURRENT TASK:
Title: {{task.title}}
Description: {{task.description}}
Details: {{task.details}}
Test Strategy: {{task.testStrategy || 'Not specified'}}

ADJUSTMENT REQUIREMENTS:
- Direction: INCREASE complexity
- Strength: {{strength}} ({{strengthDescription}})
- Preserve the core purpose and functionality of the task
- Maintain consistency with the existing task structure
- Add more detailed requirements, edge cases, or advanced features
- Include additional implementation considerations
- Enhance error handling and validation requirements
- Expand testing strategies with more comprehensive scenarios

{{#if customPrompt}}
CUSTOM INSTRUCTIONS:
{{customPrompt}}
{{/if}}

Return a JSON object with the updated task containing these fields:
- title: Updated task title
- description: Updated task description  
- details: Updated implementation details
- testStrategy: Updated test strategy
- priority: Task priority ('low', 'medium', or 'high')

Ensure the JSON is valid and properly formatted.
```

#### System Prompt for Subtask Regeneration
```
You are an expert project manager who creates task breakdowns that match complexity levels.
```

#### User Prompt for Subtask Regeneration (Generated Dynamically)
```
Based on this updated task, generate {{newSubtasksNeeded}} NEW subtasks that reflect the increased complexity level:

**Task Title**: {{task.title}}
**Task Description**: {{task.description}}
**Implementation Details**: {{task.details}}
**Test Strategy**: {{task.testStrategy}}

**Complexity Direction**: This task was recently scoped up ({{strength}} strength) to increase complexity.
{{#if originalComplexity}}**Original Complexity**: {{originalComplexity}}/10 - consider this when determining appropriate scope level.{{/if}}

{{#if preservedCount > 0}}**Preserved Subtasks**: {{preservedCount}} existing subtasks with work already done will be kept.{{/if}}

Generate subtasks that:
{{#if strength === 'heavy'}}
- Add comprehensive implementation steps with advanced features
- Include extensive error handling, validation, and edge cases
- Cover multiple integration scenarios and advanced testing
- Provide thorough documentation and optimization approaches
{{else if strength === 'regular'}}
- Add more detailed implementation steps
- Include additional error handling and validation
- Cover more edge cases and advanced features
- Provide more comprehensive testing approaches
{{else}}
- Add some additional implementation details
- Include basic error handling considerations
- Cover a few common edge cases
- Enhance testing approaches slightly
{{/if}}

Return a JSON object with a "subtasks" array. Each subtask should have:
- id: Sequential NUMBER starting from 1 (e.g., 1, 2, 3 - NOT "1", "2", "3")
- title: Clear, specific title
- description: Detailed description
- dependencies: Array of dependency IDs as STRINGS (use format ["{{task.id}}.1", "{{task.id}}.2"] for siblings, or empty array [] for no dependencies)
- details: Implementation guidance
- status: "pending"
- testStrategy: Testing approach

IMPORTANT: 
- The 'id' field must be a NUMBER, not a string!
- Dependencies must be strings, not numbers!

Ensure the JSON is valid and properly formatted.
```

### Output Specification

#### Success Response
```javascript
{
  success: true,
  data: {
    message: "Successfully scoped up 2 task(s)",
    updatedTasks: [
      {
        id: 1,
        title: "Advanced Authentication System with Multi-Factor Support",
        description: "Implement comprehensive authentication with MFA, session management, and security auditing",
        details: "Create robust authentication system with JWT tokens, refresh token rotation, MFA via TOTP/SMS, session invalidation, security event logging, rate limiting, and account lockout policies...",
        testStrategy: "Unit tests for all auth functions, integration tests for MFA flows, security penetration testing, load testing for rate limits",
        priority: "high",
        subtasks: [/* preserved + regenerated subtasks */]
      }
    ],
    telemetryData: {
      totalTokens: 2500,
      totalCost: 0.05
    }
  }
}
```

#### Error Response
```javascript
{
  success: false,
  error: {
    code: "TASK_NOT_FOUND",
    message: "Task with ID 5 not found"
  }
}
```

#### Error Codes
- `INVALID_STRENGTH`: Invalid strength level specified
- `TASK_NOT_FOUND`: One or more task IDs don't exist
- `MISSING_ARGUMENT`: Required parameters not provided
- `AI_SERVICE_ERROR`: Failed to generate complexity adjustments

### Side Effects
1. Updates task title, description, details, and test strategy
2. Regenerates pending subtasks while preserving completed ones
3. Updates complexity report if re-analysis is performed
4. Writes changes to tasks.json
5. Multiple AI service calls (adjustment + subtask regeneration)

## Data Flow

```mermaid
graph TD
    A[Input Task IDs] --> B[Load Tasks File]
    B --> C[For Each Task]
    C --> D[Get Original Complexity]
    D --> E[Build Scope-Up Prompt]
    E --> F{Strength Level}
    F -->|Light| G[Minor Enhancements]
    F -->|Regular| H[Moderate Increases]
    F -->|Heavy| I[Significant Additions]
    G --> J[AI Adjustment Call]
    H --> J
    I --> J
    J --> K[Update Task Fields]
    K --> L{Has Subtasks?}
    L -->|No| M[Save Task]
    L -->|Yes| N[Identify Subtask Status]
    N --> O[Preserve Completed]
    N --> P[Count Pending]
    P --> Q[Calculate New Count]
    Q --> R[Generate New Subtasks]
    R --> S[Combine Preserved + New]
    S --> M
    M --> T{More Tasks?}
    T -->|Yes| C
    T -->|No| U[Re-analyze Complexity]
    U --> V[Save All & Return]
```

## Implementation Details

### Data Storage
- **Input**: `.taskmaster/tasks/tasks.json` - Task data by tag
- **Complexity Report**: `.taskmaster/reports/task-complexity-report.json` - For intelligent adjustments
- **Output**: Updates same tasks.json file

### Strength Levels
- **Light**: Minor enhancements, ~10% complexity increase
- **Regular**: Moderate complexity increase, ~30% more scope
- **Heavy**: Significant additions, ~60% more complexity

### Subtask Calculation Formula
```javascript
// For scope-up with original complexity factor
const complexityFactor = originalComplexity ? Math.max(0.5, originalComplexity / 10) : 1.0;

if (strength === 'light') {
  base = Math.max(5, preservedCount + Math.ceil(currentPendingCount * 1.1));
  targetSubtaskCount = Math.ceil(base * (0.8 + 0.4 * complexityFactor));
} else if (strength === 'regular') {
  base = Math.max(6, preservedCount + Math.ceil(currentPendingCount * 1.3));
  targetSubtaskCount = Math.ceil(base * (0.8 + 0.4 * complexityFactor));
} else { // heavy
  base = Math.max(8, preservedCount + Math.ceil(currentPendingCount * 1.6));
  targetSubtaskCount = Math.ceil(base * (0.8 + 0.6 * complexityFactor));
}
```

### Preserved Subtask Statuses
- done
- in-progress  
- review
- cancelled
- deferred
- blocked

## AI Integration Points
This tool uses AI for multiple operations:
- **Task Complexity Adjustment**: AI modifies task fields to increase scope
- **Subtask Regeneration**: AI generates new subtasks matching increased complexity
- **Complexity Re-analysis**: Optional AI analysis to score new complexity
- **Research Mode**: Enhanced adjustments using research capabilities
- **Custom Prompts**: User-provided instructions for specific adjustments

## Dependencies
- **File System Access**: Read/write tasks.json
- **AI Service**: Required for adjustments and regeneration
- **Complexity Report**: Optional but recommended for intelligent adjustments
- **Zod**: Schema validation for AI responses
- **Task Analysis**: Optional re-analysis of complexity scores

## Test Scenarios

### 1. Basic Scope Up
```javascript
// Test: Increase single task complexity
Input: {
  id: "1",
  strength: "regular",
  projectRoot: "/project"
}
Expected: Task complexity increased, subtasks regenerated
```

### 2. Multiple Tasks
```javascript
// Test: Scope up multiple tasks
Input: {
  id: "1,3,5",
  strength: "heavy",
  projectRoot: "/project"
}
Expected: All 3 tasks increased significantly
```

### 3. Light Adjustment
```javascript
// Test: Minor complexity increase
Input: {
  id: "2",
  strength: "light",
  projectRoot: "/project"
}
Expected: Small scope increase, minimal subtask changes
```

### 4. With Custom Prompt
```javascript
// Test: Specific adjustment instructions
Input: {
  id: "4",
  prompt: "Add security and compliance requirements",
  projectRoot: "/project"
}
Expected: Task focused on security/compliance additions
```

### 5. Preserve Completed Work
```javascript
// Test: Regenerate only pending subtasks
Setup: Task has 3 done, 2 pending subtasks
Input: {
  id: "6",
  strength: "regular",
  projectRoot: "/project"
}
Expected: 3 done preserved, 2+ new pending generated
```

### 6. Research Mode
```javascript
// Test: Enhanced adjustments with research
Input: {
  id: "7",
  research: true,
  projectRoot: "/project"
}
Expected: Research-informed complexity increases
```

### 7. High Complexity Task
```javascript
// Test: Scope up already complex task
Setup: Task has complexity score 9/10
Input: {
  id: "8",
  strength: "heavy",
  projectRoot: "/project"
}
Expected: Intelligent adjustment considering high baseline
```

## Implementation Notes
- **Complexity**: High (multiple AI calls, subtask regeneration logic)
- **Estimated Effort**: 10-12 hours for complete implementation
- **Critical Success Factors**:
  1. Intelligent complexity calculations based on original scores
  2. Proper preservation of completed subtasks
  3. Coherent task adjustments maintaining purpose
  4. Accurate subtask count calculations
  5. Robust AI response handling

## Performance Considerations
- Multiple AI calls per task (adjustment + regeneration)
- Complexity re-analysis adds overhead
- Token usage scales with task count and complexity
- File I/O for each task update
- Consider batching for large task lists

## Security Considerations
- Validate task IDs to prevent injection
- Sanitize custom prompts before AI calls
- Validate file paths for directory traversal
- API keys stored in environment variables
- Validate AI responses against schemas

## Code References
- Current implementation: `scripts/modules/task-manager/scope-adjustment.js`
- MCP tool: `mcp-server/src/tools/scope-up.js`
- Direct function: `mcp-server/src/core/direct-functions/scope-up.js`
- Key functions:
  - `scopeUpTask()`: Main scope-up logic
  - `adjustTaskComplexity()`: AI-based task adjustment
  - `regenerateSubtasksForComplexity()`: Subtask regeneration with preservation
  - `reanalyzeTaskComplexity()`: Optional complexity re-scoring
  - `getCurrentComplexityScore()`: Reads current complexity
- Design patterns: Strategy pattern for strength levels, preservation pattern for completed work

---

*This documentation captures the actual current implementation of the scope_up tool including exact AI prompts used.*