# Alfred Task Manager - Data Models

## Overview
Alfred operates as a stateless bridge between AI agents and professional task management platforms (Linear/Jira). All task data is stored in Linear/Jira, with Alfred maintaining only minimal configuration locally.

## Platform Data Structures

### 1. Linear Data Model

#### Linear Issue Object
```python
{
  "id": "uuid",                        # Linear's unique ID
  "identifier": "ENG-123",              # Human-readable ID
  "title": "Implement authentication",
  "description": "Set up JWT-based auth with OAuth2 support",
  "state": {
    "id": "state-id",
    "name": "In Progress",              # Backlog, Todo, In Progress, Done, Canceled
    "type": "started"
  },
  "priority": 2,                        # 0=None, 1=Urgent, 2=High, 3=Medium, 4=Low
  "project": {                          # Linear Project (Epic equivalent)
    "id": "project-id",
    "name": "Authentication System"
  },
  "team": {                             # Linear Team (Project equivalent)
    "id": "team-id",
    "key": "ENG",
    "name": "Engineering"
  },
  "assignee": {
    "id": "user-id",
    "name": "John Doe"
  },
  "labels": [                           # Used for complexity, categories
    {"id": "label-id", "name": "backend"},
    {"id": "label-id2", "name": "complex"}
  ],
  "parent": {                           # Parent issue for sub-issues
    "id": "parent-id",
    "identifier": "ENG-122"
  },
  "children": [],                       # Sub-issues
  "relations": [                        # Dependencies/blocks
    {
      "id": "relation-id",
      "type": "blocks",
      "relatedIssue": {"id": "issue-id", "identifier": "ENG-124"}
    }
  ],
  "createdAt": "2024-01-20T10:00:00Z",
  "updatedAt": "2024-01-20T15:30:00Z",
  "completedAt": null,
  "cycle": {                            # Sprint/Iteration
    "id": "cycle-id",
    "number": 23,
    "startsAt": "2024-01-15T00:00:00Z",
    "endsAt": "2024-01-29T00:00:00Z"
  },
  "estimate": 5,                        # Story points
  "customFields": {                     # Alfred-specific data
    "complexity_score": 7.5,
    "ai_generated": true,
    "test_strategy": "Unit tests for auth flow"
  }
}
```

### 2. Jira Data Model (Future)

#### Jira Issue Object
```python
{
  "id": "10001",
  "key": "PROJ-123",
  "fields": {
    "summary": "Implement authentication",
    "description": "Set up JWT-based auth with OAuth2 support",
    "issuetype": {
      "id": "10001",
      "name": "Story"                  # Epic, Story, Task, Sub-task, Bug
    },
    "status": {
      "id": "3",
      "name": "In Progress"             # To Do, In Progress, Done, Blocked
    },
    "priority": {
      "id": "2",
      "name": "High"                    # Critical, High, Medium, Low
    },
    "project": {
      "id": "10000",
      "key": "PROJ",
      "name": "Project Name"
    },
    "epic": {                           # Parent Epic
      "id": "10100",
      "key": "PROJ-100",
      "name": "Authentication Epic"
    },
    "assignee": {
      "accountId": "user-id",
      "displayName": "John Doe"
    },
    "labels": ["backend", "complex"],
    "parent": {                         # For sub-tasks
      "id": "10000",
      "key": "PROJ-122"
    },
    "subtasks": [],                     # Child sub-tasks
    "issuelinks": [                     # Dependencies
      {
        "id": "10001",
        "type": {
          "name": "Blocks"
        },
        "outwardIssue": {
          "id": "10002",
          "key": "PROJ-124"
        }
      }
    ],
    "created": "2024-01-20T10:00:00Z",
    "updated": "2024-01-20T15:30:00Z",
    "resolutiondate": null,
    "customfield_10001": 7.5,          # Complexity score
    "customfield_10002": true,         # AI generated
    "customfield_10003": "Unit tests"  # Test strategy
  }
}
```

## Alfred Data Models

### 3. Alfred Task Model (Unified)

Alfred's unified task representation that maps to both Linear and Jira:

```python
@dataclass
class AlfredTask:
    # Core fields
    id: str                             # Platform ID (Linear UUID or Jira key)
    title: str
    description: str
    status: TaskStatus                  # Enum: TODO, IN_PROGRESS, DONE, BLOCKED
    priority: Priority                  # Enum: LOW, MEDIUM, HIGH, CRITICAL
    
    # Hierarchy
    epic_id: Optional[str]              # Linear Project ID or Jira Epic ID
    parent_id: Optional[str]            # Parent task for subtasks
    subtask_ids: List[str]              # Child tasks
    
    # Relationships
    blocks: List[str]                   # Tasks this blocks
    blocked_by: List[str]               # Tasks blocking this
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    
    # AI Enhancement
    complexity_score: Optional[float]   # 1-10 scale
    ai_generated: bool = False
    test_strategy: Optional[str]
    implementation_notes: Optional[str]
    
    # Platform-specific
    platform: Platform                  # Enum: LINEAR, JIRA
    raw_data: Dict                      # Original platform data
```

### 4. Configuration Model

```python
@dataclass
class AlfredConfig:
    # Platform settings
    platform: str                       # "linear" or "jira"
    workspace_id: str                   # Linear workspace or Jira site
    team_id: str                        # Linear team or Jira project
    active_epic_id: Optional[str]       # Current epic/project context
    
    # AI settings
    anthropic_api_key: str              # From environment
    ai_model: str = "claude-3-5-sonnet-20241022"
    
    # Preferences
    default_priority: str = "medium"
    auto_decompose: bool = True
    complexity_threshold: float = 7.0
    
    # Session
    last_sync: datetime
    cache_ttl: int = 300                # 5 minutes
```

### 5. Epic Model

```python
@dataclass
class AlfredEpic:
    id: str                             # Linear Project ID or Jira Epic ID
    name: str
    description: Optional[str]
    status: str                         # Active, Completed, Archived
    
    # Statistics
    total_tasks: int
    completed_tasks: int
    in_progress_tasks: int
    blocked_tasks: int
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    target_date: Optional[datetime]
    
    # Platform-specific
    platform: Platform
    raw_data: Dict
```

### 6. Complexity Analysis Model

```python
@dataclass
class ComplexityAnalysis:
    task_id: str
    title: str
    
    # Scoring
    complexity_score: float             # 1-10 scale
    factors: ComplexityFactors
    
    # Recommendations
    should_decompose: bool
    suggested_subtasks: int
    estimated_hours: float
    reasoning: str
    
    # Risk assessment
    risk_level: RiskLevel               # LOW, MEDIUM, HIGH
    risk_factors: List[str]

@dataclass
class ComplexityFactors:
    technical: float                    # Technical difficulty
    dependencies: float                  # Dependency complexity
    scope: float                        # Scope size
    uncertainty: float                  # Requirements clarity
```

### 7. Research Result Model

```python
@dataclass
class ResearchResult:
    query: str
    task_id: Optional[str]              # Associated task
    
    # Results
    findings: str                       # Main research output
    sources: List[str]                  # Referenced sources
    confidence: float                   # 0-1 confidence score
    
    # Metadata
    timestamp: datetime
    tokens_used: int
    cost: float
    
    # Storage
    saved_to_task: bool
    saved_as_comment: bool              # Linear comment or Jira comment
```

## Adapter Interface Models

### 8. Base Adapter Interface

```python
class BaseAdapter(ABC):
    """Abstract interface for platform adapters"""
    
    @abstractmethod
    async def create_task(
        self,
        title: str,
        description: str,
        epic_id: Optional[str] = None,
        parent_id: Optional[str] = None,
        priority: Priority = Priority.MEDIUM,
        labels: List[str] = None
    ) -> AlfredTask:
        pass
    
    @abstractmethod
    async def get_task(self, task_id: str) -> AlfredTask:
        pass
    
    @abstractmethod
    async def update_task(
        self,
        task_id: str,
        updates: Dict[str, Any]
    ) -> AlfredTask:
        pass
    
    @abstractmethod
    async def list_tasks(
        self,
        epic_id: Optional[str] = None,
        status: Optional[TaskStatus] = None
    ) -> List[AlfredTask]:
        pass
    
    @abstractmethod
    async def create_epic(
        self,
        name: str,
        description: Optional[str] = None
    ) -> AlfredEpic:
        pass
    
    @abstractmethod
    async def link_tasks(
        self,
        from_id: str,
        to_id: str,
        link_type: LinkType
    ) -> bool:
        pass
```

## Enumerations

### Task Status
```python
class TaskStatus(Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    BLOCKED = "blocked"
    CANCELED = "canceled"
```

### Priority
```python
class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
```

### Platform
```python
class Platform(Enum):
    LINEAR = "linear"
    JIRA = "jira"
```

### Link Type
```python
class LinkType(Enum):
    BLOCKS = "blocks"
    RELATES_TO = "relates_to"
    DUPLICATES = "duplicates"
```

### Risk Level
```python
class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
```

## Hierarchy Mapping

### Alfred to Platform Mapping
```
Alfred          →    Linear              →    Jira
-------------------------------------------------------
Project         →    Team                →    Project
Epic            →    Project             →    Epic
Task            →    Issue               →    Story/Task
Subtask         →    Sub-issue           →    Sub-task
```

### Status Mapping
```python
STATUS_MAP = {
    Platform.LINEAR: {
        "Backlog": TaskStatus.TODO,
        "Todo": TaskStatus.TODO,
        "In Progress": TaskStatus.IN_PROGRESS,
        "Done": TaskStatus.DONE,
        "Canceled": TaskStatus.CANCELED
    },
    Platform.JIRA: {
        "To Do": TaskStatus.TODO,
        "In Progress": TaskStatus.IN_PROGRESS,
        "Done": TaskStatus.DONE,
        "Blocked": TaskStatus.BLOCKED
    }
}
```

### Priority Mapping
```python
PRIORITY_MAP = {
    Platform.LINEAR: {
        0: Priority.LOW,      # No priority
        1: Priority.CRITICAL, # Urgent
        2: Priority.HIGH,
        3: Priority.MEDIUM,
        4: Priority.LOW
    },
    Platform.JIRA: {
        "Critical": Priority.CRITICAL,
        "High": Priority.HIGH,
        "Medium": Priority.MEDIUM,
        "Low": Priority.LOW
    }
}
```

## Data Flow

### Task Creation Flow
1. AI generates task data from spec
2. Alfred maps to platform-specific format
3. Platform adapter creates task via API
4. Platform returns created task with ID
5. Alfred maps back to unified model
6. Returns to MCP client

### Task Query Flow
1. MCP client requests tasks
2. Alfred queries platform API
3. Platform returns native format
4. Alfred maps to unified model
5. Applies any filtering/sorting
6. Returns to MCP client

## Performance Considerations

### Caching Strategy
- **No task caching**: Always fetch fresh data
- **Epic list caching**: 5-minute TTL
- **Config caching**: Session lifetime
- **Workspace metadata**: 15-minute TTL

### API Rate Limits
- **Linear**: 1500 requests/hour
- **Jira**: 50 requests/second
- **Anthropic**: Based on tier

### Batch Operations
- Use Linear's batch mutation API
- Use Jira's bulk operations
- Group AI requests when possible

---

*This document defines all data structures and models used in Alfred Task Manager.*