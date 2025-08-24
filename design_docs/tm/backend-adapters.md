# Task Master AI - Backend Adapters Documentation

## Overview
Task Master AI currently uses a local JSON file storage system as its backend. This document describes the current implementation and provides a design for future backend adapters that would enable integration with external task management systems like Linear, Jira, GitHub Issues, and others.

## Current Implementation: Local JSON Adapter

### Architecture

```
Task Master Storage Layer
├── Local JSON Adapter (Current)
│   ├── File System Operations
│   ├── JSON Serialization/Deserialization
│   ├── Tag-Based Structure
│   └── Atomic Write Operations
└── Future Adapters (Planned)
    ├── Linear GraphQL Adapter
    ├── Jira REST Adapter
    ├── GitHub Issues Adapter
    └── Custom Backend Adapters
```

### Local JSON Storage Implementation

#### Core Storage Functions

```javascript
// Read tasks from JSON file
function readJSON(filepath, projectRoot = null, tag = null) {
  const data = JSON.parse(fs.readFileSync(filepath, 'utf8'));
  
  // Handle tag-based structure
  if (hasTaggedStructure(data)) {
    const resolvedTag = tag || getCurrentTag(projectRoot);
    return data[resolvedTag] || data.master;
  }
  
  return data;
}

// Write tasks to JSON file
function writeJSON(filepath, data, projectRoot = null, tag = null) {
  // Merge resolved data back into tagged structure
  if (data._rawTaggedData && projectRoot) {
    const resolvedTag = tag || getCurrentTag(projectRoot);
    const finalData = {
      ...data._rawTaggedData,
      [resolvedTag]: data
    };
    fs.writeFileSync(filepath, JSON.stringify(finalData, null, 2));
  }
}
```

#### File Structure

```
.taskmaster/
├── tasks/
│   └── tasks.json          # Main task database
├── config.json             # Configuration
├── state.json              # Current state (active tag)
└── reports/                # Analysis reports
```

#### Tagged Data Structure

```json
{
  "master": {
    "tasks": [...],
    "metadata": {
      "created": "2024-01-01T00:00:00Z",
      "lastModified": "2024-01-20T15:30:00Z"
    }
  },
  "feature-auth": {
    "tasks": [...],
    "metadata": {...}
  },
  "_currentTag": "master",
  "_migrationHappened": true
}
```

### Local Adapter Operations

#### 1. Task CRUD Operations

```javascript
// Create
function addTask(task) {
  const tasks = readJSON(tasksPath);
  tasks.push(task);
  writeJSON(tasksPath, tasks);
}

// Read
function getTask(taskId) {
  const tasks = readJSON(tasksPath);
  return findTaskById(tasks, taskId);
}

// Update
function updateTask(taskId, updates) {
  const tasks = readJSON(tasksPath);
  const task = findTaskById(tasks, taskId);
  Object.assign(task, updates);
  writeJSON(tasksPath, tasks);
}

// Delete
function removeTask(taskId) {
  const tasks = readJSON(tasksPath);
  const index = tasks.findIndex(t => t.id === taskId);
  tasks.splice(index, 1);
  writeJSON(tasksPath, tasks);
}
```

#### 2. Tag Management

```javascript
// Switch active tag
function useTag(tagName) {
  const state = { currentTag: tagName };
  fs.writeFileSync(statePath, JSON.stringify(state));
}

// Create new tag
function addTag(tagName, copyFrom = 'master') {
  const data = readJSON(tasksPath);
  data[tagName] = {
    tasks: [...data[copyFrom].tasks],
    metadata: { created: new Date().toISOString() }
  };
  writeJSON(tasksPath, data);
}
```

#### 3. File Generation

```javascript
// Generate markdown files for each task
function generateTaskFiles(tasks) {
  tasks.forEach(task => {
    const content = formatTaskAsMarkdown(task);
    fs.writeFileSync(`task-${task.id}.md`, content);
  });
}
```

## Future Backend Adapter Design

### Adapter Interface

```typescript
interface TaskAdapter {
  // Core CRUD operations
  createTask(task: Task): Promise<Task>;
  getTask(taskId: string): Promise<Task | null>;
  updateTask(taskId: string, updates: Partial<Task>): Promise<Task>;
  deleteTask(taskId: string): Promise<boolean>;
  listTasks(filter?: TaskFilter): Promise<Task[]>;
  
  // Bulk operations
  createTasks(tasks: Task[]): Promise<Task[]>;
  updateTasks(updates: TaskUpdate[]): Promise<Task[]>;
  
  // Subtask operations
  addSubtask(parentId: string, subtask: Subtask): Promise<Subtask>;
  updateSubtask(parentId: string, subtaskId: string, updates: Partial<Subtask>): Promise<Subtask>;
  removeSubtask(parentId: string, subtaskId: string): Promise<boolean>;
  
  // Dependency management
  addDependency(taskId: string, dependsOn: string): Promise<boolean>;
  removeDependency(taskId: string, dependsOn: string): Promise<boolean>;
  validateDependencies(): Promise<DependencyValidation>;
  
  // Tag/Branch management (if supported)
  listTags?(): Promise<string[]>;
  createTag?(name: string, copyFrom?: string): Promise<boolean>;
  switchTag?(name: string): Promise<boolean>;
  deleteTag?(name: string): Promise<boolean>;
  
  // Search and query
  searchTasks(query: string): Promise<Task[]>;
  getNextTask(): Promise<Task | null>;
  
  // Metadata
  getMetadata(): Promise<AdapterMetadata>;
  isHealthy(): Promise<boolean>;
}
```

### Adapter Factory Pattern

```typescript
class AdapterFactory {
  private static adapters: Map<string, TaskAdapter> = new Map();
  
  static registerAdapter(type: string, adapter: TaskAdapter) {
    this.adapters.set(type, adapter);
  }
  
  static getAdapter(type: string = 'local'): TaskAdapter {
    const adapter = this.adapters.get(type);
    if (!adapter) {
      throw new Error(`Unknown adapter type: ${type}`);
    }
    return adapter;
  }
}
```

## Planned Backend Adapters

### 1. Linear GraphQL Adapter

#### Mapping Strategy

| Task Master | Linear |
|------------|--------|
| Task | Issue |
| Subtask | Sub-issue |
| Tag | Project/Cycle |
| Priority | Priority |
| Status | State |
| Dependencies | Blocked by/Blocks |

#### Implementation Sketch

```typescript
class LinearAdapter implements TaskAdapter {
  private client: LinearClient;
  
  constructor(apiKey: string) {
    this.client = new LinearClient({ apiKey });
  }
  
  async createTask(task: Task): Promise<Task> {
    const issue = await this.client.createIssue({
      title: task.title,
      description: task.description,
      priority: this.mapPriority(task.priority),
      stateId: this.mapStatus(task.status)
    });
    
    return this.mapIssueToTask(issue);
  }
  
  private mapTaskToIssue(task: Task): LinearIssue {
    return {
      title: task.title,
      description: `${task.description}\n\n${task.details}`,
      priority: PRIORITY_MAP[task.priority],
      labels: task.category ? [task.category] : []
    };
  }
  
  private mapIssueToTask(issue: LinearIssue): Task {
    return {
      id: issue.identifier,
      title: issue.title,
      description: issue.description,
      status: STATUS_MAP[issue.state.type],
      priority: PRIORITY_REVERSE_MAP[issue.priority]
    };
  }
}
```

### 2. Jira REST Adapter

#### Mapping Strategy

| Task Master | Jira |
|------------|------|
| Task | Issue |
| Subtask | Sub-task |
| Tag | Epic/Sprint |
| Priority | Priority |
| Status | Status |
| Dependencies | Issue Links |

#### Implementation Sketch

```typescript
class JiraAdapter implements TaskAdapter {
  private client: JiraClient;
  
  constructor(config: JiraConfig) {
    this.client = new JiraClient(config);
  }
  
  async createTask(task: Task): Promise<Task> {
    const issue = await this.client.post('/rest/api/3/issue', {
      fields: {
        project: { key: this.projectKey },
        summary: task.title,
        description: this.formatDescription(task),
        issuetype: { name: 'Task' },
        priority: { name: task.priority }
      }
    });
    
    return this.mapIssueToTask(issue);
  }
  
  private formatDescription(task: Task): object {
    // Convert to Atlassian Document Format
    return {
      type: 'doc',
      version: 1,
      content: [
        {
          type: 'paragraph',
          content: [
            { type: 'text', text: task.description }
          ]
        }
      ]
    };
  }
}
```

### 3. GitHub Issues Adapter

#### Mapping Strategy

| Task Master | GitHub |
|------------|--------|
| Task | Issue |
| Subtask | Task list item |
| Tag | Milestone/Project |
| Priority | Label |
| Status | State + Labels |
| Dependencies | Issue references |

#### Implementation Sketch

```typescript
class GitHubAdapter implements TaskAdapter {
  private octokit: Octokit;
  
  constructor(token: string, owner: string, repo: string) {
    this.octokit = new Octokit({ auth: token });
    this.owner = owner;
    this.repo = repo;
  }
  
  async createTask(task: Task): Promise<Task> {
    const issue = await this.octokit.rest.issues.create({
      owner: this.owner,
      repo: this.repo,
      title: task.title,
      body: this.formatBody(task),
      labels: [task.priority, task.category].filter(Boolean)
    });
    
    return this.mapIssueToTask(issue.data);
  }
  
  private formatBody(task: Task): string {
    return `
${task.description}

## Details
${task.details || 'N/A'}

## Test Strategy
${task.testStrategy || 'N/A'}

## Subtasks
${task.subtasks?.map(s => `- [ ] ${s.title}`).join('\n') || 'None'}
    `.trim();
  }
}
```

## Migration Strategies

### 1. Export/Import Migration

```typescript
class MigrationService {
  async migrate(from: TaskAdapter, to: TaskAdapter) {
    // Export all data from source
    const tasks = await from.listTasks();
    const metadata = await from.getMetadata();
    
    // Transform data if needed
    const transformed = this.transformTasks(tasks, from.type, to.type);
    
    // Import to destination
    await to.createTasks(transformed);
    
    // Verify migration
    return this.verifyMigration(from, to);
  }
  
  private transformTasks(tasks: Task[], fromType: string, toType: string): Task[] {
    const transformer = this.getTransformer(fromType, toType);
    return tasks.map(task => transformer.transform(task));
  }
}
```

### 2. Sync Strategy

```typescript
class SyncService {
  private syncInterval: number = 5 * 60 * 1000; // 5 minutes
  
  async startSync(local: TaskAdapter, remote: TaskAdapter) {
    setInterval(async () => {
      await this.syncTasks(local, remote);
    }, this.syncInterval);
  }
  
  private async syncTasks(local: TaskAdapter, remote: TaskAdapter) {
    const localTasks = await local.listTasks();
    const remoteTasks = await remote.listTasks();
    
    // Detect changes
    const changes = this.detectChanges(localTasks, remoteTasks);
    
    // Apply changes bidirectionally
    await this.applyChanges(changes, local, remote);
  }
}
```

## Configuration Management

### Adapter Configuration Schema

```json
{
  "backend": {
    "type": "linear",
    "config": {
      "apiKey": "${LINEAR_API_KEY}",
      "teamId": "TEAM_ID",
      "projectId": "PROJECT_ID",
      "syncEnabled": true,
      "syncInterval": 300000
    },
    "mapping": {
      "priority": {
        "low": 0,
        "medium": 1,
        "high": 2,
        "critical": 3
      },
      "status": {
        "pending": "backlog",
        "in-progress": "in_progress",
        "done": "done"
      }
    }
  }
}
```

### Multi-Backend Support

```typescript
class MultiBackendManager {
  private adapters: Map<string, TaskAdapter> = new Map();
  private primary: string = 'local';
  
  async executeOnAll<T>(operation: (adapter: TaskAdapter) => Promise<T>): Promise<T[]> {
    const results = [];
    for (const adapter of this.adapters.values()) {
      results.push(await operation(adapter));
    }
    return results;
  }
  
  async syncAll() {
    const primary = this.adapters.get(this.primary);
    const tasks = await primary.listTasks();
    
    for (const [name, adapter] of this.adapters) {
      if (name !== this.primary) {
        await this.syncToAdapter(tasks, adapter);
      }
    }
  }
}
```

## Error Handling and Recovery

### Adapter Error Handling

```typescript
class AdapterErrorHandler {
  async executeWithRetry<T>(
    operation: () => Promise<T>,
    maxRetries: number = 3
  ): Promise<T> {
    let lastError: Error;
    
    for (let i = 0; i < maxRetries; i++) {
      try {
        return await operation();
      } catch (error) {
        lastError = error;
        await this.handleError(error, i);
      }
    }
    
    throw new AdapterError('Operation failed after retries', lastError);
  }
  
  private async handleError(error: Error, attempt: number) {
    if (error instanceof RateLimitError) {
      await this.wait(error.retryAfter);
    } else if (error instanceof NetworkError) {
      await this.wait(Math.pow(2, attempt) * 1000);
    }
  }
}
```

### Offline Mode Support

```typescript
class OfflineQueue {
  private queue: Operation[] = [];
  
  async addOperation(operation: Operation) {
    this.queue.push(operation);
    await this.persistQueue();
  }
  
  async flush(adapter: TaskAdapter) {
    while (this.queue.length > 0) {
      const operation = this.queue.shift();
      try {
        await this.executeOperation(operation, adapter);
      } catch (error) {
        // Re-queue on failure
        this.queue.unshift(operation);
        throw error;
      }
    }
  }
}
```

## Performance Optimization

### Caching Layer

```typescript
class AdapterCache {
  private cache: Map<string, CacheEntry> = new Map();
  private ttl: number = 60000; // 1 minute
  
  async get<T>(key: string, fetcher: () => Promise<T>): Promise<T> {
    const entry = this.cache.get(key);
    
    if (entry && !this.isExpired(entry)) {
      return entry.data as T;
    }
    
    const data = await fetcher();
    this.cache.set(key, {
      data,
      timestamp: Date.now()
    });
    
    return data;
  }
}
```

### Batch Operations

```typescript
class BatchProcessor {
  private batchSize: number = 50;
  
  async processBatch<T>(
    items: T[],
    processor: (batch: T[]) => Promise<void>
  ) {
    for (let i = 0; i < items.length; i += this.batchSize) {
      const batch = items.slice(i, i + this.batchSize);
      await processor(batch);
    }
  }
}
```

## Testing Strategy

### Adapter Testing Interface

```typescript
abstract class AdapterTest {
  abstract getAdapter(): TaskAdapter;
  
  @test
  async testCreateTask() {
    const adapter = this.getAdapter();
    const task = await adapter.createTask({
      title: 'Test Task',
      description: 'Test Description'
    });
    
    expect(task.id).toBeDefined();
    expect(task.title).toBe('Test Task');
  }
  
  @test
  async testUpdateTask() {
    // Common test implementation
  }
  
  @test
  async testDeleteTask() {
    // Common test implementation
  }
}
```

### Mock Adapter for Testing

```typescript
class MockAdapter implements TaskAdapter {
  private tasks: Map<string, Task> = new Map();
  
  async createTask(task: Task): Promise<Task> {
    const id = `mock-${Date.now()}`;
    const newTask = { ...task, id };
    this.tasks.set(id, newTask);
    return newTask;
  }
  
  async getTask(taskId: string): Promise<Task | null> {
    return this.tasks.get(taskId) || null;
  }
}
```

## Security Considerations

### API Key Management

```typescript
class SecureConfig {
  private keyring: Keyring;
  
  async getApiKey(service: string): Promise<string> {
    // Try environment variable first
    const envKey = process.env[`${service.toUpperCase()}_API_KEY`];
    if (envKey) return envKey;
    
    // Try system keyring
    return await this.keyring.getPassword('task-master', service);
  }
  
  async setApiKey(service: string, key: string): Promise<void> {
    await this.keyring.setPassword('task-master', service, key);
  }
}
```

### Data Encryption

```typescript
class EncryptedAdapter implements TaskAdapter {
  private adapter: TaskAdapter;
  private crypto: CryptoService;
  
  async createTask(task: Task): Promise<Task> {
    const encrypted = this.crypto.encrypt(task);
    const result = await this.adapter.createTask(encrypted);
    return this.crypto.decrypt(result);
  }
}
```

## Future Enhancements

### 1. Webhook Support
- Real-time updates from external systems
- Event-driven synchronization
- Conflict resolution strategies

### 2. Plugin System
```typescript
interface AdapterPlugin {
  name: string;
  version: string;
  initialize(adapter: TaskAdapter): void;
  beforeCreate?(task: Task): Task;
  afterCreate?(task: Task): void;
  beforeUpdate?(task: Task, updates: Partial<Task>): Partial<Task>;
  afterUpdate?(task: Task): void;
}
```

### 3. GraphQL Universal Adapter
```typescript
class GraphQLAdapter implements TaskAdapter {
  private schema: GraphQLSchema;
  
  constructor(endpoint: string, schema: GraphQLSchema) {
    this.schema = schema;
    // Auto-generate queries/mutations from schema
    this.generateOperations();
  }
}
```

### 4. AI-Powered Mapping
```typescript
class SmartMapper {
  async generateMapping(
    sourceSchema: Schema,
    targetSchema: Schema
  ): Promise<FieldMapping> {
    // Use AI to intelligently map fields
    return await this.ai.mapSchemas(sourceSchema, targetSchema);
  }
}
```

---

*This document provides comprehensive documentation of Task Master's backend adapter system, including current implementation and future extensibility.*