# Alfred Task Manager - Backend Adapters Documentation

## Overview
Alfred Task Manager integrates with professional task management platforms (Linear and Jira) through a unified adapter interface. This document describes the adapter pattern that enables seamless switching between Linear and Jira backends while maintaining consistent behavior for the MCP layer.

## Architecture

```
Alfred MCP Server
├── Adapter Interface (Abstract Base)
│   ├── Task Operations
│   ├── Epic Management  
│   ├── Search & Filter
│   └── Comments & Research
├── Linear Adapter (GraphQL)
│   ├── linear-api SDK
│   ├── GraphQL Operations
│   └── Linear-specific mappings
└── Jira Adapter (REST)
    ├── jira-python SDK
    ├── REST API Operations
    └── Jira-specific mappings
```

## Unified Adapter Interface

### Base Adapter Class

```python
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum

class TaskStatus(Enum):
    BACKLOG = "backlog"
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"
    DONE = "done"
    CANCELLED = "cancelled"

class TaskPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

@dataclass
class Task:
    """Unified task representation"""
    id: str
    title: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    epic_id: Optional[str] = None
    assignee_id: Optional[str] = None
    parent_id: Optional[str] = None  # For subtasks
    labels: List[str] = None
    custom_fields: Dict[str, Any] = None
    created_at: str = None
    updated_at: str = None
    
@dataclass
class Epic:
    """Unified epic representation"""
    id: str
    name: str
    description: str
    team_id: str  # Team in Linear, Project in Jira
    status: str
    tasks: List[Task] = None

class TaskAdapter(ABC):
    """Abstract base class for task management adapters"""
    
    @abstractmethod
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize connection to the backend"""
        pass
    
    # Task Operations
    @abstractmethod
    async def create_task(self, task: Task) -> Task:
        """Create a new task"""
        pass
    
    @abstractmethod
    async def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID"""
        pass
    
    @abstractmethod
    async def update_task(self, task_id: str, updates: Dict[str, Any]) -> Task:
        """Update task fields"""
        pass
    
    @abstractmethod
    async def delete_task(self, task_id: str) -> bool:
        """Delete a task"""
        pass
    
    @abstractmethod
    async def list_tasks(self, epic_id: Optional[str] = None, 
                        status: Optional[TaskStatus] = None) -> List[Task]:
        """List tasks with optional filters"""
        pass
    
    # Subtask Operations
    @abstractmethod
    async def create_subtask(self, parent_id: str, subtask: Task) -> Task:
        """Create a subtask under a parent task"""
        pass
    
    @abstractmethod
    async def decompose_task(self, task_id: str, subtasks: List[Task]) -> List[Task]:
        """Break a task into multiple subtasks"""
        pass
    
    # Epic Management
    @abstractmethod
    async def create_epic(self, epic: Epic) -> Epic:
        """Create a new epic/project"""
        pass
    
    @abstractmethod
    async def get_epic(self, epic_id: str) -> Optional[Epic]:
        """Get epic by ID"""
        pass
    
    @abstractmethod
    async def list_epics(self, team_id: str) -> List[Epic]:
        """List all epics for a team"""
        pass
    
    # Status Operations
    @abstractmethod
    async def update_task_status(self, task_id: str, status: TaskStatus) -> Task:
        """Update task status with proper transition"""
        pass
    
    @abstractmethod
    async def get_next_task(self, team_id: str) -> Optional[Task]:
        """Get the next recommended task to work on"""
        pass
    
    # Search and Query
    @abstractmethod
    async def search_tasks(self, query: str) -> List[Task]:
        """Search tasks using platform-specific query language"""
        pass
    
    # Comments and Research
    @abstractmethod
    async def add_comment(self, task_id: str, comment: str) -> bool:
        """Add a comment to a task"""
        pass
    
    @abstractmethod
    async def add_research(self, task_id: str, research: str) -> bool:
        """Add research findings to a task"""
        pass
    
    # Complexity Assessment
    @abstractmethod
    async def assess_complexity(self, task_id: str, complexity: Dict[str, Any]) -> bool:
        """Add complexity assessment as custom field"""
        pass
```

## Linear Adapter Implementation

### GraphQL Operations and Mapping

```python
from linear_api import LinearClient
from linear_api.models import Issue, IssueCreateInput, Project, Team
import asyncio

class LinearAdapter(TaskAdapter):
    """Linear GraphQL API adapter"""
    
    def __init__(self):
        self.client: Optional[LinearClient] = None
        self.team_id: Optional[str] = None
        
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize Linear client with API key"""
        try:
            self.client = LinearClient(api_key=config['api_key'])
            self.team_id = config.get('team_id')
            
            # Verify connection
            teams = await self.client.teams()
            if self.team_id and not any(t.id == self.team_id for t in teams):
                raise ValueError(f"Team {self.team_id} not found")
            
            return True
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Linear: {e}")
    
    # Mapping Functions
    def _map_linear_to_task(self, issue: Issue) -> Task:
        """Convert Linear Issue to unified Task"""
        return Task(
            id=issue.identifier,
            title=issue.title,
            description=issue.description or "",
            status=self._map_linear_status(issue.state.type),
            priority=self._map_linear_priority(issue.priority),
            epic_id=issue.project.id if issue.project else None,
            assignee_id=issue.assignee.id if issue.assignee else None,
            parent_id=issue.parent.id if issue.parent else None,
            labels=[label.name for label in issue.labels],
            custom_fields={
                'linear_id': issue.id,
                'linear_url': issue.url,
                'cycle_id': issue.cycle.id if issue.cycle else None
            },
            created_at=issue.created_at.isoformat(),
            updated_at=issue.updated_at.isoformat()
        )
    
    def _map_linear_status(self, state_type: str) -> TaskStatus:
        """Map Linear state types to unified status"""
        mapping = {
            'backlog': TaskStatus.BACKLOG,
            'unstarted': TaskStatus.TODO,
            'started': TaskStatus.IN_PROGRESS,
            'completed': TaskStatus.DONE,
            'canceled': TaskStatus.CANCELLED
        }
        return mapping.get(state_type, TaskStatus.BACKLOG)
    
    def _map_linear_priority(self, priority: int) -> TaskPriority:
        """Map Linear priority (0-4) to unified priority"""
        mapping = {
            0: TaskPriority.LOW,
            1: TaskPriority.LOW,
            2: TaskPriority.MEDIUM,
            3: TaskPriority.HIGH,
            4: TaskPriority.URGENT
        }
        return mapping.get(priority, TaskPriority.MEDIUM)
    
    # Task Operations
    async def create_task(self, task: Task) -> Task:
        """Create a Linear issue"""
        input_data = IssueCreateInput(
            title=task.title,
            description=task.description,
            team_id=self.team_id,
            priority=self._priority_to_linear(task.priority),
            project_id=task.epic_id,
            parent_id=task.parent_id
        )
        
        issue = await self.client.create_issue(input_data)
        return self._map_linear_to_task(issue)
    
    async def decompose_task(self, task_id: str, subtasks: List[Task]) -> List[Task]:
        """Create multiple sub-issues under a parent"""
        parent = await self.client.issue(task_id)
        created_subtasks = []
        
        for subtask in subtasks:
            subtask.parent_id = parent.id
            created = await self.create_task(subtask)
            created_subtasks.append(created)
            
        return created_subtasks
    
    async def get_next_task(self, team_id: str) -> Optional[Task]:
        """Get next task based on priority and dependencies"""
        # Query for unassigned high-priority tasks
        query = """
        query {
            issues(
                filter: {
                    team: { id: { eq: "%s" } }
                    assignee: { null: true }
                    state: { type: { in: ["backlog", "unstarted"] } }
                }
                orderBy: priority
            ) {
                nodes {
                    id
                    identifier
                    title
                    description
                    priority
                    state { type }
                    project { id }
                }
            }
        }
        """ % team_id
        
        result = await self.client.query(query)
        if result['issues']['nodes']:
            return self._map_linear_to_task(result['issues']['nodes'][0])
        return None
    
    async def add_research(self, task_id: str, research: str) -> bool:
        """Add research as a comment with special formatting"""
        comment = f"## Research Findings\n\n{research}\n\n*Generated by Alfred AI*"
        return await self.add_comment(task_id, comment)
    
    async def assess_complexity(self, task_id: str, complexity: Dict[str, Any]) -> bool:
        """Add complexity as labels and description update"""
        issue = await self.client.issue(task_id)
        
        # Add complexity label
        complexity_label = f"complexity:{complexity['score']}"
        await self.client.add_label(task_id, complexity_label)
        
        # Update description with complexity analysis
        updated_desc = f"{issue.description}\n\n---\n## Complexity Analysis\n"
        updated_desc += f"- Score: {complexity['score']}/10\n"
        updated_desc += f"- Factors: {complexity.get('factors', 'N/A')}\n"
        updated_desc += f"- Suggested Subtasks: {complexity.get('suggested_subtasks', 0)}\n"
        
        await self.client.update_issue(task_id, description=updated_desc)
        return True
```

## Jira Adapter Implementation

### REST API Operations and Mapping

```python
from jira import JIRA
from jira.resources import Issue, Project
from typing import List, Optional, Dict, Any

class JiraAdapter(TaskAdapter):
    """Jira REST API adapter"""
    
    def __init__(self):
        self.client: Optional[JIRA] = None
        self.project_key: Optional[str] = None
        
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize Jira client"""
        try:
            self.client = JIRA(
                server=config['server'],
                basic_auth=(config['email'], config['api_token'])
            )
            self.project_key = config.get('project_key')
            
            # Verify project exists
            if self.project_key:
                project = self.client.project(self.project_key)
                
            return True
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Jira: {e}")
    
    # Mapping Functions
    def _map_jira_to_task(self, issue: Issue) -> Task:
        """Convert Jira Issue to unified Task"""
        return Task(
            id=issue.key,
            title=issue.fields.summary,
            description=issue.fields.description or "",
            status=self._map_jira_status(issue.fields.status.name),
            priority=self._map_jira_priority(issue.fields.priority.name),
            epic_id=self._get_epic_link(issue),
            assignee_id=issue.fields.assignee.accountId if issue.fields.assignee else None,
            parent_id=issue.fields.parent.key if hasattr(issue.fields, 'parent') else None,
            labels=issue.fields.labels,
            custom_fields={
                'jira_id': issue.id,
                'jira_url': f"{self.client.server_url}/browse/{issue.key}",
                'issue_type': issue.fields.issuetype.name
            },
            created_at=issue.fields.created,
            updated_at=issue.fields.updated
        )
    
    def _map_jira_status(self, status_name: str) -> TaskStatus:
        """Map Jira status to unified status"""
        status_lower = status_name.lower()
        if 'backlog' in status_lower:
            return TaskStatus.BACKLOG
        elif 'to do' in status_lower or 'open' in status_lower:
            return TaskStatus.TODO
        elif 'progress' in status_lower:
            return TaskStatus.IN_PROGRESS
        elif 'review' in status_lower:
            return TaskStatus.IN_REVIEW
        elif 'done' in status_lower or 'closed' in status_lower:
            return TaskStatus.DONE
        elif 'cancelled' in status_lower:
            return TaskStatus.CANCELLED
        return TaskStatus.BACKLOG
    
    def _map_jira_priority(self, priority_name: str) -> TaskPriority:
        """Map Jira priority to unified priority"""
        priority_lower = priority_name.lower()
        if 'low' in priority_lower:
            return TaskPriority.LOW
        elif 'medium' in priority_lower:
            return TaskPriority.MEDIUM
        elif 'high' in priority_lower:
            return TaskPriority.HIGH
        elif 'highest' in priority_lower or 'urgent' in priority_lower:
            return TaskPriority.URGENT
        return TaskPriority.MEDIUM
    
    def _get_epic_link(self, issue: Issue) -> Optional[str]:
        """Extract epic link from Jira issue"""
        # Epic link field ID may vary by instance
        epic_field = 'customfield_10014'  # Common epic link field
        if hasattr(issue.fields, epic_field):
            return getattr(issue.fields, epic_field)
        return None
    
    # Task Operations
    async def create_task(self, task: Task) -> Task:
        """Create a Jira issue"""
        issue_dict = {
            'project': {'key': self.project_key},
            'summary': task.title,
            'description': task.description,
            'issuetype': {'name': 'Task'},
            'priority': {'name': self._priority_to_jira(task.priority)}
        }
        
        if task.epic_id:
            issue_dict['customfield_10014'] = task.epic_id
            
        if task.parent_id:
            issue_dict['parent'] = {'key': task.parent_id}
            issue_dict['issuetype'] = {'name': 'Sub-task'}
        
        issue = self.client.create_issue(fields=issue_dict)
        return self._map_jira_to_task(issue)
    
    async def decompose_task(self, task_id: str, subtasks: List[Task]) -> List[Task]:
        """Create multiple subtasks under a parent"""
        created_subtasks = []
        
        for subtask in subtasks:
            subtask_dict = {
                'project': {'key': self.project_key},
                'parent': {'key': task_id},
                'summary': subtask.title,
                'description': subtask.description,
                'issuetype': {'name': 'Sub-task'},
                'priority': {'name': self._priority_to_jira(subtask.priority)}
            }
            
            issue = self.client.create_issue(fields=subtask_dict)
            created_subtasks.append(self._map_jira_to_task(issue))
            
        return created_subtasks
    
    async def get_next_task(self, team_id: str) -> Optional[Task]:
        """Get next task using JQL query"""
        jql = f"""
            project = {self.project_key} 
            AND assignee is EMPTY 
            AND status in ("To Do", "Backlog")
            ORDER BY priority DESC, created ASC
        """
        
        issues = self.client.search_issues(jql, maxResults=1)
        if issues:
            return self._map_jira_to_task(issues[0])
        return None
    
    async def search_tasks(self, query: str) -> List[Task]:
        """Search using JQL"""
        issues = self.client.search_issues(query, maxResults=50)
        return [self._map_jira_to_task(issue) for issue in issues]
    
    async def add_research(self, task_id: str, research: str) -> bool:
        """Add research as a formatted comment"""
        comment = f"h2. Research Findings\n\n{research}\n\n_Generated by Alfred AI_"
        self.client.add_comment(task_id, comment)
        return True
    
    async def assess_complexity(self, task_id: str, complexity: Dict[str, Any]) -> bool:
        """Add complexity assessment to Jira issue"""
        issue = self.client.issue(task_id)
        
        # Add complexity label
        complexity_label = f"complexity-{complexity['score']}"
        issue.update(fields={'labels': issue.fields.labels + [complexity_label]})
        
        # Add complexity analysis as comment
        comment = f"""h2. Complexity Analysis
        
||Metric||Value||
|Score|{complexity['score']}/10|
|Technical Complexity|{complexity.get('technical', 'N/A')}|
|Dependencies|{complexity.get('dependencies', 'N/A')}|
|Suggested Subtasks|{complexity.get('suggested_subtasks', 0)}|
|Estimation|{complexity.get('estimation', 'N/A')}|

*Reasoning:* {complexity.get('reasoning', 'N/A')}
        
_Generated by Alfred AI_"""
        
        self.client.add_comment(task_id, comment)
        return True
```

## Adapter Factory and Configuration

### Factory Pattern for Adapter Selection

```python
from typing import Type
import os
from dotenv import load_dotenv

class AdapterFactory:
    """Factory for creating appropriate adapter based on configuration"""
    
    _adapters: Dict[str, Type[TaskAdapter]] = {
        'linear': LinearAdapter,
        'jira': JiraAdapter
    }
    
    @classmethod
    def create_adapter(cls, platform: str = None) -> TaskAdapter:
        """Create adapter instance based on platform"""
        if not platform:
            platform = os.getenv('ALFRED_PLATFORM', 'linear').lower()
        
        if platform not in cls._adapters:
            raise ValueError(f"Unsupported platform: {platform}")
        
        adapter_class = cls._adapters[platform]
        return adapter_class()
    
    @classmethod
    async def create_configured_adapter(cls) -> TaskAdapter:
        """Create and initialize adapter from environment configuration"""
        load_dotenv()
        
        platform = os.getenv('ALFRED_PLATFORM', 'linear').lower()
        adapter = cls.create_adapter(platform)
        
        # Load platform-specific configuration
        if platform == 'linear':
            config = {
                'api_key': os.getenv('LINEAR_API_KEY'),
                'team_id': os.getenv('LINEAR_TEAM_ID')
            }
        elif platform == 'jira':
            config = {
                'server': os.getenv('JIRA_SERVER'),
                'email': os.getenv('JIRA_EMAIL'),
                'api_token': os.getenv('JIRA_API_TOKEN'),
                'project_key': os.getenv('JIRA_PROJECT_KEY')
            }
        else:
            raise ValueError(f"No configuration for platform: {platform}")
        
        await adapter.initialize(config)
        return adapter
```

### Configuration Schema

```python
# .alfred/config.json
{
    "platform": "linear",  # or "jira"
    "linear": {
        "team_id": "TEAM_xxx",
        "default_project_id": "PROJECT_xxx",
        "default_cycle_id": null,
        "custom_field_mappings": {
            "complexity": "customField1",
            "ai_notes": "customField2"
        }
    },
    "jira": {
        "project_key": "PROJ",
        "default_epic_id": null,
        "issue_type_mappings": {
            "task": "Task",
            "subtask": "Sub-task",
            "epic": "Epic"
        },
        "custom_field_ids": {
            "epic_link": "customfield_10014",
            "complexity": "customfield_10020"
        }
    },
    "ai": {
        "model": "claude-3-5-sonnet",
        "temperature": 0.7
    }
}
```

### Environment Variables

```bash
# .env.example

# Platform selection
ALFRED_PLATFORM=linear  # or jira

# Linear configuration
LINEAR_API_KEY=lin_api_xxx
LINEAR_TEAM_ID=xxx
LINEAR_WORKSPACE_ID=xxx

# Jira configuration  
JIRA_SERVER=https://yourcompany.atlassian.net
JIRA_EMAIL=user@company.com
JIRA_API_TOKEN=xxx
JIRA_PROJECT_KEY=PROJ

# AI configuration
ANTHROPIC_API_KEY=sk-ant-xxx
```

## Error Handling and Resilience

### Unified Error Handling

```python
class AdapterError(Exception):
    """Base exception for adapter errors"""
    pass

class ConnectionError(AdapterError):
    """Failed to connect to backend"""
    pass

class RateLimitError(AdapterError):
    """API rate limit exceeded"""
    def __init__(self, retry_after: int = 60):
        self.retry_after = retry_after

class NotFoundError(AdapterError):
    """Resource not found"""
    pass

class PermissionError(AdapterError):
    """Insufficient permissions"""
    pass

class RetryableAdapter:
    """Wrapper for automatic retry logic"""
    
    def __init__(self, adapter: TaskAdapter, max_retries: int = 3):
        self.adapter = adapter
        self.max_retries = max_retries
    
    async def _retry_operation(self, operation, *args, **kwargs):
        """Execute operation with exponential backoff"""
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                return await operation(*args, **kwargs)
            except RateLimitError as e:
                await asyncio.sleep(e.retry_after)
                last_error = e
            except (ConnectionError, TimeoutError) as e:
                wait_time = 2 ** attempt  # Exponential backoff
                await asyncio.sleep(wait_time)
                last_error = e
            except Exception as e:
                raise e  # Non-retryable error
        
        raise last_error
```

## Performance Optimization

### Caching Layer

```python
from functools import lru_cache
import hashlib
import json
from datetime import datetime, timedelta

class CachedAdapter:
    """Caching wrapper for adapters"""
    
    def __init__(self, adapter: TaskAdapter, cache_ttl: int = 300):
        self.adapter = adapter
        self.cache_ttl = cache_ttl  # seconds
        self._cache = {}
    
    def _cache_key(self, method: str, *args, **kwargs) -> str:
        """Generate cache key from method and arguments"""
        key_data = {
            'method': method,
            'args': args,
            'kwargs': kwargs
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _is_expired(self, timestamp: datetime) -> bool:
        """Check if cache entry is expired"""
        return datetime.now() - timestamp > timedelta(seconds=self.cache_ttl)
    
    async def get_task(self, task_id: str) -> Optional[Task]:
        """Cached get_task operation"""
        cache_key = self._cache_key('get_task', task_id)
        
        if cache_key in self._cache:
            entry = self._cache[cache_key]
            if not self._is_expired(entry['timestamp']):
                return entry['data']
        
        # Fetch from adapter
        task = await self.adapter.get_task(task_id)
        
        # Update cache
        self._cache[cache_key] = {
            'data': task,
            'timestamp': datetime.now()
        }
        
        return task
```

### Batch Operations

```python
class BatchAdapter:
    """Batch operations for efficiency"""
    
    def __init__(self, adapter: TaskAdapter):
        self.adapter = adapter
        self.batch_size = 50
    
    async def create_tasks_from_spec(self, spec: str, epic_id: str = None) -> List[Task]:
        """Create multiple tasks from specification"""
        # Parse spec into tasks (using AI)
        tasks = await self._parse_spec_to_tasks(spec)
        
        # Batch create tasks
        created_tasks = []
        for i in range(0, len(tasks), self.batch_size):
            batch = tasks[i:i + self.batch_size]
            
            # Create tasks in parallel
            batch_results = await asyncio.gather(
                *[self.adapter.create_task(task) for task in batch],
                return_exceptions=True
            )
            
            # Filter out errors
            for result in batch_results:
                if not isinstance(result, Exception):
                    created_tasks.append(result)
                    
        return created_tasks
```

## Testing Strategy

### Mock Adapter for Testing

```python
class MockAdapter(TaskAdapter):
    """Mock adapter for testing"""
    
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.epics: Dict[str, Epic] = {}
        self.comments: Dict[str, List[str]] = {}
        
    async def initialize(self, config: Dict[str, Any]) -> bool:
        return True
    
    async def create_task(self, task: Task) -> Task:
        task.id = f"MOCK-{len(self.tasks) + 1}"
        self.tasks[task.id] = task
        return task
    
    async def get_task(self, task_id: str) -> Optional[Task]:
        return self.tasks.get(task_id)
    
    async def update_task(self, task_id: str, updates: Dict[str, Any]) -> Task:
        if task_id not in self.tasks:
            raise NotFoundError(f"Task {task_id} not found")
        
        task = self.tasks[task_id]
        for key, value in updates.items():
            if hasattr(task, key):
                setattr(task, key, value)
        
        return task
```

### Integration Tests

```python
import pytest
from unittest.mock import Mock, AsyncMock

@pytest.mark.asyncio
async def test_adapter_interface():
    """Test that adapters implement the interface correctly"""
    for adapter_class in [LinearAdapter, JiraAdapter, MockAdapter]:
        adapter = adapter_class()
        
        # Verify all required methods exist
        assert hasattr(adapter, 'initialize')
        assert hasattr(adapter, 'create_task')
        assert hasattr(adapter, 'get_task')
        assert hasattr(adapter, 'update_task')
        # ... test all interface methods

@pytest.mark.asyncio
async def test_linear_adapter_mapping():
    """Test Linear adapter field mapping"""
    adapter = LinearAdapter()
    
    # Mock Linear issue
    mock_issue = Mock()
    mock_issue.identifier = "TASK-123"
    mock_issue.title = "Test Task"
    mock_issue.description = "Test Description"
    mock_issue.state.type = "started"
    mock_issue.priority = 3
    
    # Test mapping
    task = adapter._map_linear_to_task(mock_issue)
    assert task.id == "TASK-123"
    assert task.status == TaskStatus.IN_PROGRESS
    assert task.priority == TaskPriority.HIGH
```

## Migration Guide

### Migrating from Local TaskMaster to Alfred

```python
class TaskMasterMigrator:
    """Migrate from TaskMaster local storage to Linear/Jira"""
    
    def __init__(self, adapter: TaskAdapter):
        self.adapter = adapter
    
    async def migrate_from_json(self, json_path: str, epic_name: str = "Migrated Tasks"):
        """Migrate tasks from TaskMaster JSON to backend"""
        
        # Load TaskMaster data
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        # Create epic for migrated tasks
        epic = await self.adapter.create_epic(Epic(
            name=epic_name,
            description="Tasks migrated from TaskMaster",
            team_id=self.adapter.team_id
        ))
        
        # Migrate tasks
        task_mapping = {}  # Old ID -> New ID
        
        for old_task in data.get('tasks', []):
            new_task = Task(
                title=old_task['title'],
                description=old_task.get('description', ''),
                status=self._map_status(old_task['status']),
                priority=self._map_priority(old_task.get('priority', 'medium')),
                epic_id=epic.id
            )
            
            created = await self.adapter.create_task(new_task)
            task_mapping[old_task['id']] = created.id
            
            # Migrate subtasks
            for subtask in old_task.get('subtasks', []):
                await self._migrate_subtask(subtask, created.id)
        
        return task_mapping
```

## Future Enhancements

### 1. Multi-Platform Support
- Simultaneous Linear and Jira connections
- Cross-platform synchronization
- Platform-agnostic task URLs

### 2. Advanced Features
- Webhook support for real-time updates
- Custom field mapping configuration
- Template-based task creation
- Bulk operations optimization

### 3. AI Enhancements
- Smart task assignment based on team capacity
- Automatic epic creation from specs
- Intelligent task prioritization
- Predictive complexity assessment

---

*This document describes Alfred's backend adapter system that enables seamless integration with Linear and Jira while maintaining a consistent interface for the MCP layer.*