# Task Master AI - Data Models

## Core Data Structures

### 1. Task Object

The fundamental unit of work in Task Master.

```javascript
{
  "id": "1",                          // Unique identifier (string)
  "title": "Implement user authentication", // Task name
  "description": "Set up JWT-based auth",   // Detailed description
  "status": "pending",                // Status enum (see below)
  "priority": "high",                 // Priority level
  "category": "backend",              // Optional category
  "dependencies": ["2", "3"],         // Array of task IDs
  "created": "2024-01-20T10:00:00Z", // ISO timestamp
  "updated": "2024-01-20T15:30:00Z", // ISO timestamp
  "details": "Additional implementation notes...", // Extended notes
  "testStrategy": "Unit tests for auth flow",     // Testing approach
  "subtasks": [                       // Array of subtask objects
    {
      "id": "1.1",
      "title": "Create user model",
      "description": "Database schema for users",
      "status": "done",
      "priority": "high",
      "dependencies": [],
      "created": "2024-01-20T10:30:00Z",
      "updated": "2024-01-20T14:00:00Z",
      "details": "",
      "testStrategy": "",
      "subtasks": []                  // Can have sub-subtasks
    }
  ]
}
```

### 2. Tasks Database Structure

The main tasks.json file structure with tag support.

```javascript
{
  "master": {                         // Default tag
    "tasks": [                        // Array of task objects
      { /* task object */ },
      { /* task object */ }
    ],
    "metadata": {
      "created": "2024-01-01T00:00:00Z",
      "lastModified": "2024-01-20T15:30:00Z",
      "taskCount": 25,
      "completedCount": 10
    }
  },
  "feature-auth": {                   // Feature branch tag
    "tasks": [
      { /* task object */ }
    ],
    "metadata": { /* ... */ }
  },
  "_currentTag": "master",            // Active tag indicator
  "_migrationHappened": true          // Migration flag
}
```

### 3. Configuration Model

AI model and project configuration.

```javascript
{
  "project": {
    "name": "My Project",
    "description": "Project description",
    "created": "2024-01-01T00:00:00Z",
    "defaultNumTasks": 5,
    "defaultSubtasks": 3
  },
  "models": {
    "main": {
      "id": "claude-3-5-sonnet-20241022",
      "provider": "anthropic",
      "apiKeyVar": "ANTHROPIC_API_KEY"
    },
    "research": {
      "id": "perplexity-llama-3.1-sonar-large-128k-online",
      "provider": "perplexity",
      "apiKeyVar": "PERPLEXITY_API_KEY"
    },
    "fallback": {
      "id": "gpt-4o-mini",
      "provider": "openai",
      "apiKeyVar": "OPENAI_API_KEY"
    }
  },
  "rules": {
    "profiles": ["nextjs", "typescript", "react"],
    "customRules": []
  },
  "preferences": {
    "responseLanguage": "en",
    "outputFormat": "markdown",
    "verbosity": "normal"
  }
}
```

### 4. Complexity Report Model

Task complexity analysis results.

```javascript
{
  "timestamp": "2024-01-20T10:00:00Z",
  "totalTasks": 25,
  "tasksAnalyzed": 20,
  "summary": {
    "simple": 5,
    "moderate": 10,
    "complex": 3,
    "veryComplex": 2
  },
  "tasks": [
    {
      "id": "1",
      "title": "Implement authentication",
      "complexity": "complex",
      "score": 7.5,
      "factors": {
        "technical": 8,
        "dependencies": 6,
        "scope": 7,
        "risk": 8
      },
      "suggestedSubtasks": 5,
      "estimatedHours": 16,
      "reasoning": "High security requirements..."
    }
  ],
  "recommendations": [
    "Break down complex tasks first",
    "Start with simple tasks to build momentum"
  ]
}
```

### 5. Dependency Model

Task dependency relationships.

```javascript
{
  "taskId": "5",
  "dependencies": [
    {
      "id": "2",
      "type": "hard",          // hard or soft dependency
      "status": "satisfied",   // satisfied, pending, broken
      "reason": "Requires database schema"
    }
  ],
  "dependents": [              // Tasks that depend on this
    {
      "id": "8",
      "type": "hard"
    }
  ],
  "validationResults": {
    "hasCircular": false,
    "brokenDependencies": [],
    "crossTagDependencies": []
  }
}
```

### 6. AI Prompt Template Model

Structure for AI prompt templates.

```javascript
{
  "id": "task-generation",
  "version": "1.0.0",
  "description": "Generate tasks from description",
  "metadata": {
    "author": "system",
    "created": "2024-01-01T00:00:00Z",
    "tags": ["task", "generation", "planning"]
  },
  "parameters": {
    "description": {
      "type": "string",
      "required": true,
      "description": "Task description"
    },
    "numTasks": {
      "type": "number",
      "default": 5,
      "minimum": 1,
      "maximum": 20
    }
  },
  "prompts": {
    "default": {
      "system": "You are a task planning assistant...",
      "user": "Generate {{numTasks}} tasks for: {{description}}"
    },
    "detailed": {
      "condition": "detailLevel === 'high'",
      "system": "You are an expert project planner...",
      "user": "Create detailed tasks with subtasks..."
    }
  }
}
```

### 7. Provider Model

AI provider configuration.

```javascript
{
  "name": "anthropic",
  "displayName": "Anthropic",
  "models": [
    {
      "id": "claude-3-5-sonnet-20241022",
      "name": "Claude 3.5 Sonnet",
      "contextWindow": 200000,
      "outputLimit": 8192,
      "capabilities": ["text", "vision", "analysis"],
      "pricing": {
        "input": 0.003,       // per 1K tokens
        "output": 0.015       // per 1K tokens
      }
    }
  ],
  "apiKeyVar": "ANTHROPIC_API_KEY",
  "baseUrl": "https://api.anthropic.com/v1",
  "headers": {
    "anthropic-version": "2023-06-01"
  }
}
```

### 8. Rule Profile Model

Coding rules and best practices.

```javascript
{
  "id": "nextjs",
  "name": "Next.js Best Practices",
  "version": "1.0.0",
  "rules": [
    {
      "id": "use-app-router",
      "type": "convention",
      "severity": "error",
      "description": "Use App Router for new projects",
      "example": "app/page.tsx instead of pages/index.tsx"
    },
    {
      "id": "server-components-default",
      "type": "performance",
      "severity": "warning",
      "description": "Use Server Components by default",
      "example": "Mark with 'use client' only when needed"
    }
  ],
  "compatibility": ["react", "typescript"],
  "metadata": {
    "author": "system",
    "created": "2024-01-01T00:00:00Z"
  }
}
```

### 9. Tag Model

Tag/branch context structure.

```javascript
{
  "name": "feature-auth",
  "type": "feature",           // master, feature, bugfix, etc.
  "created": "2024-01-15T10:00:00Z",
  "lastModified": "2024-01-20T15:30:00Z",
  "gitBranch": "feature/auth-system",  // Optional git integration
  "parentTag": "master",       // Source tag for copying
  "metadata": {
    "taskCount": 15,
    "completedCount": 5,
    "inProgressCount": 3,
    "description": "Authentication implementation"
  }
}
```

### 10. Research Context Model

Research query context structure.

```javascript
{
  "query": "How to implement OAuth2?",
  "timestamp": "2024-01-20T10:00:00Z",
  "context": {
    "tasks": [                 // Related task IDs
      "1", "1.1", "1.2"
    ],
    "files": [                 // Related file paths
      "src/auth/oauth.js",
      "src/auth/config.js"
    ],
    "customContext": "Using NextAuth.js",
    "projectTree": false
  },
  "response": {
    "result": "OAuth2 implementation guide...",
    "tokens": {
      "context": 1200,
      "system": 450,
      "user": 1650,
      "total": 3300
    },
    "detailLevel": "medium",
    "savedTo": "1.2",          // Optional task ID
    "savedFile": ".taskmaster/docs/research/oauth2-guide.md"
  }
}
```

## Enumerations

### Task Status
```javascript
const TASK_STATUS = {
  PENDING: "pending",          // Not started
  IN_PROGRESS: "in-progress",  // Currently working
  DONE: "done",                // Completed
  BLOCKED: "blocked",          // Waiting on dependency
  DEFERRED: "deferred",        // Postponed
  CANCELLED: "cancelled"       // No longer needed
}
```

### Task Priority
```javascript
const TASK_PRIORITY = {
  LOW: "low",
  MEDIUM: "medium",
  HIGH: "high",
  CRITICAL: "critical"
}
```

### Task Complexity
```javascript
const TASK_COMPLEXITY = {
  SIMPLE: "simple",            // 1-2 hours
  MODERATE: "moderate",        // 2-4 hours
  COMPLEX: "complex",          // 4-8 hours
  VERY_COMPLEX: "very-complex" // 8+ hours
}
```

### Dependency Type
```javascript
const DEPENDENCY_TYPE = {
  HARD: "hard",                // Must complete before
  SOFT: "soft"                 // Should complete before
}
```

### Rule Severity
```javascript
const RULE_SEVERITY = {
  ERROR: "error",              // Must fix
  WARNING: "warning",          // Should fix
  INFO: "info",                // Suggestion
  HINT: "hint"                 // Optional
}
```

## Validation Schemas

### Task ID Format
```regex
^(\d+)(\.(\d+))*$

Examples:
- "1"       // Main task
- "1.1"     // Subtask
- "1.1.1"   // Sub-subtask
```

### Tag Name Format
```regex
^[a-z0-9-]+$

Examples:
- "master"
- "feature-auth"
- "bugfix-123"
```

### Model ID Format
```regex
^[a-z0-9-]+(\/[a-z0-9-]+)?$

Examples:
- "claude-3-5-sonnet"
- "gpt-4o-mini"
- "google/gemini-pro"
```

## Data Relationships

### Task Hierarchy
```
tasks.json
└── Tag (master)
    └── Task (1)
        ├── Subtask (1.1)
        │   └── Sub-subtask (1.1.1)
        └── Subtask (1.2)
```

### Dependency Graph
```
Task 1 ──depends-on──> Task 2
  ↑                      ↓
  │                   depends-on
  │                      ↓
Task 4 <──depends-on── Task 3
```

### Tag Relationships
```
master (default)
  ├── feature-auth (copied from master)
  ├── feature-api (copied from master)
  └── bugfix-123 (copied from feature-auth)
```

## Data Persistence

### File Locations
```
.taskmaster/
├── tasks/
│   └── tasks.json          # Main database
├── config.json             # Configuration
├── reports/
│   └── task-complexity-report.json
├── docs/
│   ├── research/           # Research outputs
│   └── prd.txt            # Product requirements
└── templates/
    └── example_prd.txt     # Template files
```

### Backup Strategy
- Auto-backup before destructive operations
- JSON format for portability
- Git-friendly for version control

### Migration Support
- Version tracking in data files
- Backward compatibility for 1 major version
- Automatic structure upgrades

## Performance Considerations

### Indexing Strategy
- Task IDs are strings for fast lookup
- Tags stored as object keys for O(1) access
- Dependencies tracked bidirectionally

### Memory Limits
- Maximum 10,000 tasks per tag
- Maximum 100 tags per project
- Maximum 10 levels of subtask nesting

### Optimization Techniques
- Lazy loading of subtask details
- Cached complexity calculations
- Incremental dependency validation

---

*This document defines all data structures, models, and schemas used in Task Master AI.*