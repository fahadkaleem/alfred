# Understand the Context

## Goal
Extract EVERY requirement, constraint, and piece of context from the task. Document everything - assumptions kill projects.

## Prerequisites
You've already fetched the task details in the previous step. This step is pure ANALYSIS of that data.

## Instructions

### Requirement Extraction Protocol

Using the task details you ALREADY retrieved in the previous step, analyze and document EXACTLY what the task asks for:

**Core Requirements:**
- The EXACT acceptance criteria from the task (this is the CONTRACT)
- What must NOT change (backwards compatibility constraints)
- NO additions, NO nice-to-haves, NO scope creep
- Success = ALL acceptance criteria met, NOTHING MORE

**Constraints & Context:**
- Technical constraints mentioned (performance, scale, compatibility)
- Business constraints (deadlines, dependencies, stakeholders)
- Security/compliance requirements
- Integration requirements (APIs, services, databases)

**Missing Information (for questions phase):**
- Ambiguous requirements (note EACH one)
- Undefined terms or acronyms
- Missing acceptance criteria
- Unclear scope boundaries

### 4. Complexity Analysis

Assess the task complexity:
- **Simple** (< 1 day): Clear requirements, known patterns, minimal integration
- **Medium** (1-3 days): Some unknowns, moderate integration, standard patterns
- **Complex** (3-5 days): Multiple integrations, new patterns, performance concerns
- **Very Complex** (5+ days): Architectural changes, high risk, many unknowns

Document WHY you chose this complexity level.

### 5. Risk Identification

List ALL potential risks:
- Technical risks (performance, scalability, compatibility)
- Implementation risks (unclear requirements, dependencies)
- Timeline risks (external dependencies, complexity)
- Quality risks (testing challenges, edge cases)

### 6. Dependency Mapping

Document ALL dependencies:
- Other tasks that must be completed first
- External services or APIs needed
- Team members who must be consulted
- Resources or access required

## Validation Checklist

Before proceeding, verify:
- [ ] I can explain what success looks like in one sentence
- [ ] I have EXTRACTED all acceptance criteria from the task
- [ ] I have identified MISSING or UNCLEAR criteria that need clarification
- [ ] I have identified all technical constraints
- [ ] I have assessed complexity with justification

## Output Format

Structure your findings:
```
### Task Summary
[One sentence: What is being asked]

### Acceptance Criteria Analysis
From task:
- [Criterion 1 - EXACT from task]
- [Criterion 2 - EXACT from task]

Missing/Unclear:
- [What criteria should exist but doesn't]
- [Which criteria are ambiguous]

### Implementation Constraints
Technical:
- [Performance requirements, compatibility, etc.]

Systems:
- [What existing systems must be used/not touched]

### Questions for Clarification
[Numbered list of specific questions about unclear requirements]

### Complexity Assessment: [Level]
[Why this complexity - based on unknowns, integrations, risks]

### Dependencies
- Blocks: [What this prevents from starting]
- Needs: [What must be done first]
```

## Next Step
ONLY after documenting ALL findings, mark this task as completed and proceed to "Analyze the codebase".