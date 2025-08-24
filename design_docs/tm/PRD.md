# Task Master AI - Comprehensive Product Requirements Document

## Executive Summary

Task Master AI is a sophisticated task management system designed for AI-driven development workflows. It provides both a CLI interface and an MCP (Model Context Protocol) server for seamless integration with AI assistants like Claude. The system specializes in transforming Product Requirements Documents (PRDs) into hierarchical, actionable tasks with AI-powered expansion, complexity analysis, and intelligent task prioritization.

## 1. Purpose and Scope

### Purpose
- Provide a complete, tool-by-tool specification of the Task Master MCP server that exposes Task Master's task management functionality via the Model Context Protocol (MCP)
- Document every registered tool, its parameters, behavior, data flow, and system-wide patterns so future agents and developers can reason about and extend the server reliably
- Enable AI-driven development workflows with seamless integration between CLI and MCP interfaces

### Out of Scope
- Changing core business logic in `scripts/modules/*`. This PRD describes current behaviors; it does not introduce new runtime features

## 2. System Overview

### Core Architecture

Task Master is a Node.js application built with a **modular architecture** that provides both CLI and MCP (Model Context Protocol) interfaces for AI-driven task management.

### System Components

1. **CLI Application** (`bin/task-master.js`)
   - Main entry point for command-line interactions
   - Delegates commands to the dev script with argument transformation
   - Handles kebab-case to camelCase conversions for flags
   - Provides interactive setup workflows

2. **MCP Server** (`mcp-server/`)
   - FastMCP-based server implementation over stdio
   - Exposes Task Master functionality as MCP tools
   - Enables integration with Claude Code and other MCP clients
   - Manages session-based AI provider registration
   - FastMCP server timeout: 120s

3. **Core Task Management Engine** (`scripts/modules/task-manager/`)
   - Central task processing logic
   - Hierarchical task structure management
   - Dependency tracking and validation
   - Task status workflow management

4. **AI Provider System** (`src/ai-providers/` & `src/provider-registry/`)
   - Unified interface for multiple AI providers
   - Dynamic provider registration via singleton registry
   - Support for 13+ AI providers including Anthropic, OpenAI, Google, Perplexity
   - Fallback mechanisms and retry logic

### Startup Process
- Loads name and version from `package.json`
- Calls `registerTaskMasterTools(server)` to attach all MCP tools
- On connect, validates client sampling capability
- Registers the MCP provider in the shared `ProviderRegistry` so AI calls can route via the MCP host when available

### Tool Registration
- `mcp-server/src/tools/index.js` is the single registry of all tools
- If a tool is not registered here, it is not exposed

## 3. Data Architecture

### Data Stores and Configuration

#### Primary Data Files
- **Primary data file**: `.taskmaster/tasks/tasks.json` (tagged task lists format with tag keys at top-level)
- **State, tags, migration**: `.taskmaster/state.json`, managed by core utilities
- **Model configuration**: `.taskmaster/config.json`, managed by tools and CLI
- **Complexity report**: Default path under `.taskmaster/reports/` (tag-aware)

#### Tagged Task Lists System
The system uses a **tagged task lists architecture** where tasks are organized by context (tags):

```json
{
  "master": {
    "tasks": [/* standard task objects */]
  },
  "feature-branch": {
    "tasks": [/* separate task context */]
  }
}
```

**Key Features:**
- **Silent Migration**: Automatically converts legacy format to tagged format
- **Backward Compatibility**: 100% compatibility with existing commands via tag resolution layer
- **Context Separation**: Different task contexts for branches, environments, or project phases
- **State Management**: `.taskmaster/state.json` tracks current tag and migration status

### Task Structure

```json
{
  "id": "1.2.3",           // Hierarchical ID
  "title": "string",       // Task title
  "description": "string", // Detailed description
  "status": "pending|in-progress|done|blocked|deferred|cancelled",
  "priority": "low|medium|high|critical",
  "dependencies": ["1.2.1", "1.2.2"], // Task IDs
  "details": "string",     // Implementation details
  "testStrategy": "string", // Testing approach
  "acceptanceCriteria": "string", // Completion criteria
  "subtasks": [],          // Nested subtask array
  "tags": [],              // Associated tags
  "complexity": "XS|S|M|L|XL", // T-shirt sizing
  "estimatedTime": "string" // Time estimate
}
```

### Configuration Structure

```json
{
  "activeModels": {
    "main": "model-id",
    "research": "model-id",
    "fallback": "model-id"
  },
  "providers": {
    "anthropic": { "apiKey": "..." },
    "openai": { "apiKey": "..." },
    // ... other providers
  },
  "settings": {
    "responseLanguage": "en",
    "defaultPriority": "medium",
    "defaultNumTasks": 10,
    "defaultSubtasks": 3,
    "streamingEnabled": true
  }
}
```

### File System Structure

```
.taskmaster/
├── tasks/
│   ├── tasks.json         # Main task database
│   ├── task-1.md          # Individual task files
│   └── ...
├── reports/
│   └── task-complexity-report.json
├── docs/
│   ├── prd.txt           # Product requirements
│   └── templates/
├── config.json           # AI configuration
└── .current-tag          # Active tag marker
```

## 4. Cross-Cutting Patterns Used by All Tools

### Core Patterns

- **Project Root Normalization**: The `withNormalizedProjectRoot` wrapper ensures `args.projectRoot` is present and normalized, honoring `TASK_MASTER_PROJECT_ROOT` env or session roots
- **Path Resolution**: `mcp-server/src/core/utils/path-utils.js` augments core path resolvers, supports absolute/relative paths and tag-aware complexity report lookup
- **Tag Resolution**: `resolveTag()` derives the effective tag (current or provided) so commands operate within a specific tag context
- **Response Shaping**: `handleApiResult()` unifies success/error responses, adds `{ version: {name,version}, tag: {currentTag,availableTags} }`, and may strip verbose fields (e.g., `details`, `testStrategy`) from task payloads
- **Logging**: `mcp-server/src/logger.js` respects silent mode and configured log level; the MCP context logger is used during tool execution
- **Progress Reporting**: Long-running tools may use `checkProgressCapability(reportProgress)` to emit progress if the host supports it

### Silent Mode in MCP Functions
MCP direct functions must implement silent mode to prevent console interference:

```javascript
import { enableSilentMode, disableSilentMode, isSilentMode } from '../../../../scripts/modules/utils.js';

export async function someDirectFunction(args, log) {
  try {
    const tasksPath = findTasksJsonPath(args, log);
    
    enableSilentMode();
    try {
      const result = await someCoreFunction(tasksPath, arg);
      return { success: true, data: result, fromCache: false };
    } finally {
      disableSilentMode(); // Always restore in finally block
    }
  } catch (error) {
    // Standard error handling
  }
}
```

## 5. High-Level Architecture and Data Flow

### MCP Integration Architecture
```
External Tool → mcp-server/server.js → Tool (mcp-server/src/tools/*) → 
Direct Function (mcp-server/src/core/direct-functions/*) → 
Core Logic (scripts/modules/*) → AI Services
```

### Typical End-to-End Flow

1. The FastMCP server receives a tool request (tool name + JSON parameters)
2. `withNormalizedProjectRoot(args, context)` computes `args.projectRoot` (env > args > session roots > cwd)
3. Tool-specific code resolves paths (`tasks.json`, complexity report, PRD file) and the effective tag
4. The tool invokes the corresponding Direct Function (`mcp-server/src/core/direct-functions/*`) via `task-master-core.js`
5. The Direct Function enables silent mode and calls core logic in `scripts/modules/task-manager/*` or related modules; some use the unified AI layer for LLM calls
6. The Direct Function returns a structured result: `{ success, data|error }`
7. The tool wraps the result with `handleApiResult()`, returning MCP-safe content (JSON text) including version/tag metadata

## 6. Feature Catalog & Tool Registry

### Tool Catalog (42 Registered Tools)

*Note: Tool names below are the canonical names exposed via MCP (`server.addTool` name). For each tool, we include a summary, parameters, behavior, and data flow.*

### 6.1. Initialization & Configuration

#### A) `initialize_project` / CLI: `task-master init`
- **Summary**: Creates Task Master scaffolding (folders, configs), optionally adds rule profiles, initializes git, etc.
- **Parameters**:
  - `projectRoot` (string, required): Absolute path to the project root
  - `skipInstall` (boolean, default: `false`): Skips package installation
  - `addAliases` (boolean, default: `true`): Adds shell aliases
  - `initGit` (boolean, default: `true`): Initializes a git repository
  - `storeTasksInGit` (boolean, default: `true`): Includes tasks in VCS
  - `yes` (boolean, default: `true`): Non-interactive initialization
  - `rules` (array<enum RULE_PROFILES>, optional): Rule profile set to add
- **Behavior**: Sets up `.taskmaster/*`, configs, templates; non-interactive by default under MCP
- **Flow**: Tool → `initializeProjectDirect` → Core init logic
- **To-dos**:
  - Validate projectRoot exists and is writable
  - Confirm idempotency when re-running in an already-initialized project

#### B) `models` / CLI: `task-master models`
- **Summary**: Reads/sets AI models (main/research/fallback); optionally lists available models; supports custom provider flags
- **Parameters**:
  - `setMain`, `setResearch`, `setFallback` (string, optional): Model IDs
  - `listAvailableModels` (boolean, optional)
  - `projectRoot` (string, required)
  - Provider flags: `openrouter`, `ollama`, `bedrock`, `azure`, `vertex` (booleans, optional)
- **Behavior**: Reads/writes `.taskmaster/config.json`, checks for API key presence
- **Flow**: Tool → `modelsDirect` → Config manager + provider registry
- **To-dos**:
  - Validate model ID format and provider compatibility
  - Emit warnings if required API key is missing

#### C) `rules` / CLI: `task-master rules`
- **Summary**: Adds or removes curated rule profiles (e.g., Cursor, VS Code, Windsurf) to the project
- **Parameters**:
  - `action` (enum: `add`|`remove`)
  - `profiles` (array<RULE_PROFILES>, min 1)
  - `projectRoot` (string, required)
  - `force` (boolean, default: `false`) for removals
- **Behavior**: Updates rule files under the project (e.g., `.cursor/rules/`, `assets/rules/...`)
- **Flow**: Tool → `rulesDirect` → Rules manager utilities
- **To-dos**:
  - Validate nonexistent profiles and error gracefully
  - Ensure atomic updates (avoid partial rules on failure)

### 6.2. PRD and Complexity Analysis

#### D) `parse_prd` / CLI: `task-master parse-prd`
- **Summary**: Parses a PRD text/markdown file to generate tasks; supports append and research modes; emits progress events if supported
- **Parameters**:
  - `input` (string, default: `.taskmaster/docs/prd.txt`), `projectRoot` (string), `tag` (string, optional)
  - `output` (string, optional override for `tasks.json`)
  - `numTasks` (string numeric; `0` lets the system determine the number)
  - `force`, `research`, `append` (booleans)
- **Behavior**: Reads the PRD, calls an AI (via the unified service) to produce a task set, and writes to a tagged tasks file
- **Flow**: Tool (checkProgressCapability) → `parsePRDDirect` → `task-manager/parse-prd` (streaming or non-streaming) → AI providers
- **To-dos**:
  - Validate PRD file existence and encoding
  - Cap numTasks; document large PRDs behavior and streaming mode

#### E) `analyze_project_complexity` / CLI: `task-master analyze-complexity`
- **Summary**: Analyzes tasks and produces a tagged complexity report; supports optional research and filtering by IDs
- **Parameters**: `threshold` (1-10, default: 5), `research` (bool), `output` (relative path), `file` (tasks path), `ids` (csv), `from` (int), `to` (int), `projectRoot`, `tag`
- **Behavior**: Generates a JSON report in `.taskmaster/reports/...`; creates the directory if needed
- **Flow**: Tool → `analyzeTaskComplexityDirect` → `task-manager/analyze-task-complexity` + AI
- **To-dos**:
  - Validate id ranges vs existing tasks
  - Confirm output path for tag context

#### F) `complexity_report` / CLI: `task-master complexity-report`
- **Summary**: Loads and presents the latest complexity report for the current tag
- **Parameters**: `file` (override), `projectRoot`
- **Behavior**: Reads the report path computed via tag and defaults; returns the report content
- **Flow**: Tool → `complexityReportDirect`
- **To-dos**:
  - Provide clear error when report missing; suggest running analyze_project_complexity

### 6.3. Task Listing and Viewing

#### G) `get_tasks` / CLI: `task-master list`
- **Summary**: Lists tasks, with optional filtering by status and inclusion of subtasks; includes complexity report context if available
- **Parameters**: `status` (csv), `withSubtasks` (bool), `file`, `complexityReport`, `projectRoot`, `tag`
- **Behavior**: Resolves `tasks.json` and report paths; returns a structured list of tasks
- **Flow**: Tool → `listTasksDirect`
- **To-dos**:
  - Validate status values; accept multiple statuses
  - Consider pagination for very large task sets

#### H) `get_task` / CLI: `task-master show <id>`
- **Summary**: Shows details for one or multiple task IDs; can filter subtasks by status; supports an optional complexity report
- **Parameters**: `id` (string or csv), `status` (optional), `file`, `complexityReport`, `projectRoot`, `tag`
- **Behavior**: Returns task object(s); the tool strips wrapper fields if present
- **Flow**: Tool → `showTaskDirect`
- **To-dos**:
  - Validate all IDs exist; partial success messaging for multiple IDs

#### I) `next_task` / CLI: `task-master next`
- **Summary**: Determines the next actionable task based on status, dependencies, and context; optional report context
- **Parameters**: `file`, `complexityReport`, `projectRoot`, `tag`
- **Behavior**: Uses a dependency graph and statuses to select the next task
- **Flow**: Tool → `nextTaskDirect`
- **To-dos**:
  - Clarify selection criteria; include tie-breaker behavior in output

### 6.4. Task Status and File Generation

#### J) `set_task_status` / CLI: `task-master set-status`
- **Summary**: Updates the status for one or more tasks/subtasks
- **Parameters**: `id` (csv of IDs), `status` (enum from `TASK_STATUS_OPTIONS`), `file`, `complexityReport` (optional), `projectRoot`, `tag`
- **Behavior**: Updates `tasks.json` and returns a summary; honors the tag
- **Flow**: Tool → `setTaskStatusDirect`
- **To-dos**:
  - Enforce allowed transitions? Document no-op transitions

#### K) `generate` / CLI: `task-master generate`
- **Summary**: Generates per-task files in the `tasks/` directory from `tasks.json`
- **Parameters**: `file`, `output` (dir), `projectRoot`, `tag`
- **Behavior**: Writes individual files to the chosen output directory
- **Flow**: Tool → `generateTaskFilesDirect`
- **To-dos**:
  - Confirm overwrite behavior and idempotency

### 6.5. Task CRUD Operations

#### L) `add_task` / CLI: `task-master add-task`
- **Summary**: Creates a new task, supporting AI creation via prompt or manual fields, with optional research, dependencies, and priority
- **Parameters**: `prompt`, `title`, `description`, `details`, `testStrategy`, `dependencies`, `priority`, `file`, `projectRoot`, `tag`, `research`
- **Behavior**: Adds a new task to `tasks.json`; may call an AI provider if a prompt is provided
- **Flow**: Tool → `addTaskDirect`
- **To-dos**:
  - Validate dependency IDs; ensure consistent priority enum (see src/constants/task-priority.js)

#### M) `add_subtask` / CLI: `task-master add-subtask`
- **Summary**: Adds a subtask by creating a new one or converting an existing task
- **Parameters**: `id` (parent), `taskId` (convert), `title`/`description`/`details`, `status`, `dependencies` (csv), `file`, `skipGenerate`, `projectRoot`, `tag`
- **Behavior**: Updates `tasks.json`; can skip file generation
- **Flow**: Tool → `addSubtaskDirect`
- **To-dos**:
  - Validate parent existence and convert constraints

#### N) `update_task` / CLI: `task-master update-task`
- **Summary**: Updates a single task with new context; can append or fully update; optional research
- **Parameters**: `id`, `prompt`, `research` (bool), `append` (bool), `file`, `projectRoot`, `tag`
- **Behavior**: Edits task details; `append` adds a timestamped note
- **Flow**: Tool → `updateTaskByIdDirect`
- **To-dos**:
  - Confirm immutable fields (id) are not modified

#### O) `update_subtask` / CLI: `task-master update-subtask`
- **Summary**: Appends timestamped information to a subtask; optional research
- **Parameters**: `id` (e.g., `5.2`), `prompt`, `research`, `file`, `projectRoot`, `tag`
- **Behavior**: Writes an append-only note to the subtask
- **Flow**: Tool → `updateSubtaskByIdDirect`
- **To-dos**:
  - Validate subtask path exists

#### P) `update` / CLI: `task-master update`
- **Summary**: Batch-updates tasks with an ID >= `from` using new context; optional research
- **Parameters**: `from` (string), `prompt`, `research`, `file`, `projectRoot`, `tag`
- **Behavior**: Scans target tasks and applies an AI-backed update
- **Flow**: Tool → `updateTasksDirect`
- **To-dos**:
  - Confirm deterministic ordering and cutoff by tag list

#### Q) `remove_task` / CLI: `task-master remove-task`
- **Summary**: Removes one or more tasks/subtasks by ID
- **Parameters**: `id` (csv), `file`, `projectRoot`, `confirm` (bool), `tag`
- **Behavior**: Deletes tasks; confirmation is handled by the direct function
- **Flow**: Tool → `removeTaskDirect`
- **To-dos**:
  - Validate ancestor/descendant deletion semantics; reflect in result message

#### R) `remove_subtask` / CLI: `task-master remove-subtask`
- **Summary**: Removes a subtask; optionally converts it to a standalone task; can skip file generation
- **Parameters**: `id`, `convert` (bool), `file`, `skipGenerate`, `projectRoot`, `tag`
- **Behavior**: Removes or converts the subtask
- **Flow**: Tool → `removeSubtaskDirect`
- **To-dos**:
  - Confirm conversion target placement and ID generation

#### S) `clear_subtasks` / CLI: `task-master clear-subtasks`
- **Summary**: Removes all subtasks from a specific task or all tasks
- **Parameters**: `id` (csv) or `all` (bool), `file`, `projectRoot`, `tag`
- **Behavior**: Clears subtasks; supports a global clear via `all`
- **Flow**: Tool → `clearSubtasksDirect`
- **To-dos**:
  - Safeguards for destructive global operation

### 6.6. Dependency Management

#### T) `add_dependency` / CLI: `task-master add-dependency`
- **Summary**: Makes task A depend on task B
- **Parameters**: `id` (task), `dependsOn` (task), `file`, `projectRoot`, `tag`
- **Behavior**: Inserts a dependency; cycle validation is handled elsewhere
- **Flow**: Tool → `addDependencyDirect`
- **To-dos**:
  - Validate non-circular result; detect missing IDs

#### U) `remove_dependency` / CLI: `task-master remove-dependency`
- **Summary**: Removes a dependency link between tasks
- **Parameters**: `id`, `dependsOn`, `file`, `projectRoot`, `tag`
- **Behavior**: Removes the specified dependency link
- **Flow**: Tool → `removeDependencyDirect`
- **To-dos**:
  - Report when no-op (link didn't exist)

#### V) `validate_dependencies` / CLI: `task-master validate-dependencies`
- **Summary**: Checks for dependency issues (e.g., circular references, broken links) without modifying data
- **Parameters**: `file`, `projectRoot`, `tag`
- **Behavior**: Runs validations and returns a report
- **Flow**: Tool → `validateDependenciesDirect`
- **To-dos**:
  - Ensure cross-tag rules documented (allowed? warnings?)

#### W) `fix_dependencies` / CLI: `task-master fix-dependencies`
- **Summary**: Automatically fixes invalid task dependencies where possible
- **Parameters**: `file`, `projectRoot`, `tag`
- **Behavior**: Attempts to repair dependencies and returns a summary
- **Flow**: Tool → `fixDependenciesDirect`
- **To-dos**:
  - Document fix strategies; ensure safe default

### 6.7. Task Expansion

#### X) `expand_task` / CLI: `task-master expand`
- **Summary**: Expands a single task into subtasks, optionally guided by a complexity report, prompt, or research; can force overwrite of existing subtasks
- **Parameters**: `id`, `num` (target size), `research` (bool), `prompt`, `file`, `projectRoot`, `force` (bool), `tag`
- **Behavior**: AI-backed subtask creation with codebase-aware context when applicable
- **Flow**: Tool → `expandTaskDirect`
- **To-dos**:
  - Clarify merge vs replace behavior when subtasks exist

#### Y) `expand_all` / CLI: `task-master expand --all`
- **Summary**: Batch-expands all pending tasks; can enforce a subtask count, add a prompt, use research, and force regeneration
- **Parameters**: `num`, `research`, `prompt`, `force`, `file`, `projectRoot`, `tag`
- **Behavior**: Iterates through tasks and expands them according to the specified policy
- **Flow**: Tool → `expandAllTasksDirect`
- **To-dos**:
  - Rate-limit or progress reporting for large sets

### 6.8. Tag Management

#### Z) `list_tags` / CLI: `task-master tags`
- **Summary**: Lists all available tags with task counts and optional metadata
- **Parameters**: `showMetadata` (bool), `file`, `projectRoot`
- **Behavior**: Summarizes tag contexts
- **Flow**: Tool → `listTagsDirect`
- **To-dos**:
  - Include current tag indicator in output (version/tag metadata already included)

#### AA) `add_tag` / CLI: `task-master tag <name>`
- **Summary**: Creates a new tag, optionally copying from an existing tag or deriving the name from the current git branch
- **Parameters**: `name`, `copyFromCurrent` (bool), `copyFromTag`, `fromBranch` (bool), `description`, `file`, `projectRoot`
- **Behavior**: Adds a new top-level tag bucket to `tasks.json`
- **Flow**: Tool → `addTagDirect`
- **To-dos**:
  - Validate unique name; enforce naming conventions

#### AB) `delete_tag` / CLI: `task-master tag --delete`
- **Summary**: Deletes an existing tag and all tasks within it; non-interactive by default under MCP
- **Parameters**: `name`, `yes` (bool, default: `true`), `file`, `projectRoot`
- **Behavior**: Removes the tag key and associated data
- **Flow**: Tool → `deleteTagDirect`
- **To-dos**:
  - Protect 'master' tag by policy? Document behavior

#### AC) `use_tag` / CLI: `task-master tag --use`
- **Summary**: Switches the current active tag for subsequent operations
- **Parameters**: `name`, `file`, `projectRoot`
- **Behavior**: Updates the state to change the current tag
- **Flow**: Tool → `useTagDirect`
- **To-dos**:
  - Ensure state persistence across sessions

#### AD) `rename_tag` / CLI: `task-master tag --rename`
- **Summary**: Renames an existing tag
- **Parameters**: `oldName`, `newName`, `file`, `projectRoot`
- **Behavior**: Renames the tag key and carries over its tasks and metadata
- **Flow**: Tool → `renameTagDirect`
- **To-dos**:
  - Validate collisions and update references

#### AE) `copy_tag` / CLI: `task-master tag --copy`
- **Summary**: Duplicates a tag (including its tasks and metadata) to create a new tag
- **Parameters**: `sourceName`, `targetName`, `description`, `file`, `projectRoot`
- **Behavior**: Creates a new tag bucket cloned from the source
- **Flow**: Tool → `copyTagDirect`
- **To-dos**:
  - Ensure deep copy of nested structures; record provenance

### 6.9. Movement & Scope Adjustment

#### AF) `move_task` / CLI: `task-master move`
- **Summary**: Moves tasks within a tag (from → to) or across tags (fromTag → toTag) with optional dependency handling
- **Parameters**:
  - `from` (csv), `to` (required for within-tag moves)
  - `projectRoot`, `tag`
  - Cross-tag moves: `fromTag`, `toTag`, `withDependencies` (bool), `ignoreDependencies` (bool)
  - `file` (custom `tasks.json` path)
- **Behavior**: 
  - Within-tag: reorder/move between tasks/subtasks; supports 1:1 or batch mapping; generates files at end
  - Cross-tag: move source IDs to targetTag keeping IDs; can bring dependencies or ignore them
- **Flow**: Tool → `moveTaskDirect` (within-tag) or `moveTaskCrossTagDirect` (cross-tag)
- **To-dos**:
  - Validate batch mapping length; report skipped identical ID moves
  - Document dependency migration semantics

#### AG) `scope_up_task` / CLI: `task-master scope-up`
- **Summary**: Increases the scope/complexity of one or more tasks using AI, with strength presets and optional prompt/research
- **Parameters**: `id` (csv), `strength` (`light`|`regular`|`heavy`), `prompt`, `file`, `projectRoot`, `tag`, `research`
- **Behavior**: Adjusts task fields to reflect an increased scope
- **Flow**: Tool → `scopeUpDirect`
- **To-dos**:
  - Ensure compatibility with existing subtasks; avoid duplication

#### AH) `scope_down_task` / CLI: `task-master scope-down`
- **Summary**: Decreases the scope/complexity of one or more tasks
- **Parameters**: `id` (csv), `strength`, `prompt`, `file`, `projectRoot`, `tag`, `research`
- **Behavior**: Tightens the task's scope
- **Flow**: Tool → `scopeDownDirect`
- **To-dos**:
  - Ensure downstream dependencies remain valid

### 6.10. Research & Language

#### AI) `research` / CLI: `task-master research`
- **Summary**: Runs AI-powered research using project context (tasks, files, custom text), optionally saving results to a task or research docs
- **Parameters**: `query` (required), `taskIds` (csv), `filePaths` (csv), `customContext` (string), `includeProjectTree` (bool), `detailLevel` (`low`|`medium`|`high`), `saveTo` (task/subtask ID), `saveToFile` (bool), `projectRoot`, `tag`
- **Behavior**: Calls a research pipeline and optionally persists the output
- **Flow**: Tool → `researchDirect`
- **To-dos**:
  - Validate file paths; sanitize large context inclusion

#### AJ) `response-language` / CLI: Response Language Setting
- **Summary**: Gets or sets the response language for the project (e.g., `中文`, `English`, `español`)
- **Parameters**: `projectRoot` (required), `language` (string)
- **Behavior**: Updates the configuration so that subsequent content honors the language preference
- **Flow**: Tool → `responseLanguageDirect`
- **To-dos**:
  - Clarify persistence location; ensure validated language values

### 6.11. Unregistered Tools

- `get_operation_status` (`mcp-server/src/tools/get-operation-status.js`) exists but is not wired into `tools/index.js`. To enable it, it must be registered and the `AsyncOperationManager` must be implemented.

## 7. AI Integration

### AI Service Layer
**Unified AI Interface** (`scripts/modules/ai-services-unified.js`) provides:
- Provider-agnostic AI calls using Vercel AI SDK
- Automatic fallback and retry logic
- Role-based model selection (main, research, fallback)
- Support for 10+ AI providers including Claude Code (no API key required)

### Supported Providers

1. **Anthropic** - Claude models
2. **OpenAI** - GPT models (including GPT-5)
3. **Google** - Gemini models
4. **Perplexity** - Research-focused models with web search
5. **Groq** - Fast inference models
6. **Mistral** - Open-weight models
7. **XAI** - Grok models
8. **OpenRouter** - Multi-provider gateway
9. **Ollama** - Local model hosting
10. **AWS Bedrock** - Enterprise AI services
11. **Azure OpenAI** - Microsoft-hosted models
12. **Google Vertex** - Enterprise Google AI
13. **MCP** - Dynamic provider via Claude

### AI Features

- **Multi-role configuration**: Separate models for main, research, and fallback
- **Streaming support**: Real-time response streaming with progress
- **Token tracking**: Usage and cost calculation
- **Retry logic**: Automatic retry with exponential backoff
- **Context management**: Intelligent context windowing
- **Research mode**: Enhanced context gathering via web search
- **Temperature control**: Adjustable creativity levels

### Model Configuration

```bash
# Interactive setup (recommended)
task-master models --setup

# Set specific models
task-master models --set-main claude-3-5-sonnet-20241022
task-master models --set-research perplexity-llama-3.1-sonar-large-128k-online
task-master models --set-fallback gpt-4o-mini
```

## 8. MCP Server Implementation

### Session Management
- FastMCP-based implementation
- STDIO transport protocol
- Session-based provider registration
- Sampling capability detection
- Logging integration
- Timeout handling (120-second default)

### Tool Registration
The MCP server exposes 42 tools organized into logical groups:
1. Initialization & Setup (4 tools)
2. Task Analysis & Expansion (5 tools)
3. Task Listing & Viewing (4 tools)
4. Task Status & Management (2 tools)
5. Task Creation & Modification (9 tools)
6. Dependency Management (4 tools)
7. Tag Management (6 tools)
8. Research Features (1 tool)
9. Configuration (2 tools)
10. Scope Adjustment (2 tools)

### MCP Configuration

Configure in `.mcp.json`:

```json
{
  "mcpServers": {
    "task-master-ai": {
      "command": "npx",
      "args": ["-y", "--package=task-master-ai", "task-master-ai"],
      "env": {
        "ANTHROPIC_API_KEY": "your_key_here",
        "PERPLEXITY_API_KEY": "your_key_here",
        "OPENAI_API_KEY": "OPENAI_API_KEY_HERE",
        "GOOGLE_API_KEY": "GOOGLE_API_KEY_HERE",
        "XAI_API_KEY": "XAI_API_KEY_HERE",
        "OPENROUTER_API_KEY": "OPENROUTER_API_KEY_HERE",
        "MISTRAL_API_KEY": "MISTRAL_API_KEY_HERE",
        "AZURE_OPENAI_API_KEY": "AZURE_OPENAI_API_KEY_HERE",
        "OLLAMA_API_KEY": "OLLAMA_API_KEY_HERE"
      }
    }
  }
}
```

## 9. Development Workflow

### Branch Strategy
- **`main`**: Production-ready code
- **`next`**: Development branch - **target this for PRs**
- **Feature branches**: `feature/description` or `fix/description`

### Testing Requirements
All changes must pass CI checks:
- Unit tests: `npm test`
- Format check: `npm run format-check`
- E2E tests: `npm run test:e2e`

### Common Commands

#### Development & Build
```bash
# Install dependencies
npm install

# Run tests
npm test
npm run test:watch            # Run tests in watch mode
npm run test:coverage         # Run tests with coverage
npm run test:e2e             # Run end-to-end tests

# Code formatting
npm run format-check         # Check code formatting
npm run format               # Fix code formatting

# MCP server inspection
npm run inspector           # Inspect MCP server with MCP Inspector
npm run mcp-server          # Run MCP server directly
```

#### Testing Individual Components
```bash
# Test specific modules
npx jest tests/unit/task-manager.test.js
npx jest tests/unit/ai-services.test.js

# Test MCP functionality
node mcp-test.js

# Test CLI commands directly
node bin/task-master.js --help
```

#### Release Management
```bash
# Create changesets (required for releases)
npm run changeset

# Publish releases
npm run release
```

### Changeset Process
Required for user-facing changes:
```bash
npm run changeset  # Create changeset after making changes
```

**When to create changesets:**
- New features, bug fixes, breaking changes
- Performance improvements, user-facing docs
- Skip for: internal docs, test-only changes, formatting

**Changeset Guidelines:**
- When creating changesets, remember that it's user-facing, meaning we don't have to get into the specifics of the code, but rather mention what the end-user is getting or fixing from this changeset

## 10. Key Workflows

### 10.1. Project Setup Workflow
1. Initialize project: `task-master init`
2. Configure models: `task-master models --setup`
3. Create/import PRD document
4. Parse PRD: `task-master parse-prd`
5. Analyze complexity: `task-master analyze-complexity`
6. Expand tasks: `task-master expand --all`

### 10.2. Development Workflow
1. Get next task: `task-master next`
2. View details: `task-master show <id>`
3. Update status: `task-master set-status --id=<id> --status=in-progress`
4. Add notes: `task-master update-subtask --id=<id>`
5. Complete: `task-master set-status --id=<id> --status=done`

### 10.3. Multi-Workflow Management
1. Create tag: `task-master tag feature-branch`
2. Switch context: `task-master tag --use feature-branch`
3. Work on tagged tasks
4. Switch back: `task-master tag --use master`

### 10.4. Cross-Tag Task Movement
```bash
# Move task with dependencies
task-master move --from=5 --from-tag=backlog --to-tag=feature-1 --with-dependencies

# Move multiple tasks
task-master move --from=5,6,7 --from-tag=backlog --to-tag=done
```

## 11. Project Structure & Key Files

### Configuration Files
- `.taskmaster/config.json` - AI model configuration (modify via `task-master models`)
- `.taskmaster/tasks/tasks.json` - Main task database (auto-managed)
- `.taskmaster/state.json` - Tag system state and migration tracking
- `.env` - API keys for CLI usage
- `.mcp.json` - MCP server configuration (project-specific)

### Development Rules & Guidelines
The project includes comprehensive development rules in `.cursor/rules/`:
- `architecture.mdc` - System architecture patterns
- `ai_services.mdc` - AI service integration guidelines
- `mcp.mdc` - MCP server patterns
- `commands.mdc` - CLI command structure
- `utilities.mdc` - Utility function patterns

### Important Implementation Patterns

#### Task ID Format
- Main tasks: `1`, `2`, `3`
- Subtasks: `1.1`, `1.2`, `2.1`
- Sub-subtasks: `1.1.1`, `1.1.2`

#### Task Status Values
- `pending` - Ready to work on
- `in-progress` - Currently being worked on
- `done` - Completed and verified
- `deferred` - Postponed
- `cancelled` - No longer needed
- `blocked` - Waiting on external factors

## 12. Error Handling & Response Contract

### Error Handling
- Comprehensive error codes for all operations
- Graceful degradation (streaming → non-streaming)
- Detailed error messages with recovery hints
- Debug mode for verbose logging
- Validation at multiple levels
- Rollback capabilities for critical operations

### Response Contract
- On success: `{ data: <payload>, version: {name,version}, tag?: {currentTag,availableTags} }` wrapped as MCP text content
- On error: `createErrorResponse()` returns text content including version and current tag when available
- Task payload normalization: `processMCPResponseData` removes verbose fields (details, testStrategy) by default; get_task custom processor may return only the task object

## 13. Performance & Non-Functional Requirements

### Performance Characteristics
- **Streaming operations**: 2-minute timeout with fallback
- **AI operations**: Retry with exponential backoff
- **File operations**: Synchronous with validation
- **Token limits**: Provider-specific context windows
- **Concurrency**: Single-threaded with async AI calls
- **Caching**: LRU cache for provider responses

### Non-Functional Requirements
- **Reliability**: Consistent response shape; all tools must run with normalized projectRoot
- **Performance**: Heavy AI operations should use progress, and avoid unnecessary file I/O; caching available via contextManager (used by some utilities)
- **Observability**: Logger honors silent mode and log levels; server sends session log messages on connect

### Progress and Long-Running Operations
- Tools that can emit progress (when supported by host): parse_prd, expand_task, expand_all, analyze_project_complexity, update_task, add_task, update (multi)
- Pattern: checkProgressCapability() gate; if absent, tool runs without emitting progress

## 14. Security & Privacy

### Security and Environment
- API keys stored in environment variables or `.env` file
- No telemetry or usage tracking to external services
- Local-first data storage
- Optional MCP integration for Claude
- Configurable provider endpoints
- No automatic key transmission
- Project root precedence: `TASK_MASTER_PROJECT_ROOT` env > args.projectRoot > session roots > cwd; normalization strips file:// and decodes URIs
- API keys are taken from environment; the server does not log secrets

## 15. Special Features

### Claude Code Integration
- Supports `claude-code/opus` and `claude-code/sonnet` models
- No API key required (uses local Claude instance)
- Includes specialized sub-agents: task-orchestrator, task-executor, task-checker
- Automatic codebase analysis for context-aware task generation

### Research Mode
Add `--research` flag to commands for enhanced AI-powered analysis:
```bash
task-master expand --id=1 --research  # Research-enhanced task expansion
task-master analyze-complexity --research  # Research-based complexity analysis
```

## 16. Acceptance Criteria (per tool)

For each tool, the following acceptance criteria apply:
- Parameter validation errors are returned as explicit messages
- Paths are resolved deterministically and logged at info level
- Tag resolution is visible in response.tag metadata
- Errors include version and, when available, currentTag in the message payload
- Success includes a helpful message and the minimal necessary data

## 17. Consolidated To-Do Checklist by Tool

- **initialize_project**: Validate writable root, idempotency on re-run
- **models**: Validate model/provider/key; surface clear guidance when keys are missing
- **rules**: Validate profiles exist; atomic updates; provide diff summary in response
- **parse_prd**: Validate PRD path; document streaming vs non-streaming behavior; cap numTasks
- **analyze_project_complexity**: Validate id/range; ensure tag-aware output path
- **complexity_report**: Clear missing-report errors and next-step hints
- **get_tasks**: Validate statuses; consider pagination or compact option in future
- **get_task**: Partial-failure reporting for multi-ID queries
- **next_task**: Clarify tie-breakers and include reason in output
- **set_task_status**: Consider transition validation or warnings; batch-result breakdown
- **generate**: Clarify overwrite policy; idempotent reruns
- **add_task**: Validate dependencies; enforce priority enum; guard against empty prompt + no manual fields
- **add_subtask**: Validate parent exists; safe conversion from task to subtask; skipGenerate honored
- **update_task**: Append vs full update semantics; research mode guards
- **update_subtask**: Ensure subtask exists; append-only with timestamp
- **update**: Deterministic ordering; large batch safeguards
- **remove_task**: Confirm descendant deletion behavior; batch reporting
- **remove_subtask**: Conversion positioning and ID assignment rules
- **clear_subtasks**: Guardrails for all=true; confirm scope in message
- **add_dependency**: Detect cycles early; validate IDs; report no-op if already linked
- **remove_dependency**: Report no-op when link doesn't exist
- **validate_dependencies**: Document cross-tag rules; provide actionable suggestions
- **fix_dependencies**: Document fix strategies; dry-run option (future) worth considering
- **expand_task**: Merge vs replace subtask policy; respect 'force' semantics
- **expand_all**: Rate limits/progress; partial failures handling
- **list_tags**: Include current tag in response; optionally include metadata when requested
- **add_tag**: Unique naming; branch-derived naming normalization rules
- **delete_tag**: Protection policy for 'master' (decision), and confirmation default noted
- **use_tag**: Persist selection; reflect in response.tag.currentTag
- **rename_tag**: Collision handling; update of related references
- **copy_tag**: Deep copy correctness; provenance note
- **move_task**: Batch mapping; cross-tag dependency migration semantics; detailed results for skipped moves
- **scope_up_task / scope_down_task**: Strength mapping, AI prompts, and compatibility with existing subtasks
- **research**: Context size management; file path validation; safe persistence of results
- **response-language**: Persisted location and allowed values
- **get_operation_status** (unregistered): Decide whether to register; add AsyncOperationManager if needed

## 18. Integration Points

1. **Claude Code**: Native MCP integration
2. **Git**: Commit message integration
3. **GitHub CLI**: PR description templates
4. **CI/CD**: Task status webhooks (planned)
5. **IDE**: VSCode extension (planned)
6. **API**: REST API server (planned)

## 19. Open Questions

- Should `delete_tag` be disallowed for the default 'master' tag?
- Should formal status transition rules (e.g., `in-progress` → `review` → `done`) be implemented?
- Should `expand_task` support an additive mode in addition to the current `force` (replace) mode?
- Should a dry-run mode be added for destructive operations like `fix_dependencies` and `move_task`?
- Do we want formal status transition rules (e.g., in-progress → review → done), or continue permissive updates?

## 20. References (Internal)

- **Entry points**: `mcp-server/server.js`, `mcp-server/src/index.js`
- **Tool registry**: `mcp-server/src/tools/index.js`
- **Tool utilities**: `mcp-server/src/tools/utils.js` (withNormalizedProjectRoot, handleApiResult, createErrorResponse, getTagInfo, processMCPResponseData, etc.)
- **Path utils**: `mcp-server/src/core/utils/path-utils.js` (MCP-aware wrappers around src/utils/path-utils.js)
- **Direct functions hub**: `mcp-server/src/core/task-master-core.js` → `mcp-server/src/core/direct-functions/*`
- **Core logic**: `scripts/modules/task-manager/*`, `ai-services-unified.js`, `dependency-manager.js`, `config-manager.js`, `ui.js`, `utils.js`
- **Tags & state**: `.taskmaster/*` files

## 21. Claude Code Instructions

### Task Master AI Instructions
**Import Task Master's development workflow commands and guidelines, treat as if import is in the main CLAUDE.md file.**
@./.taskmaster/CLAUDE.md

## 22. Future Enhancements (Roadmap)

- Web UI dashboard
- REST API server
- Real-time collaboration
- Task templates library
- Custom AI prompts
- Workflow automation
- Integration marketplace
- Mobile companion app
- Analytics dashboard
- Export formats (JIRA, Asana, etc.)

---

*This comprehensive PRD represents the complete feature set, architecture, and implementation details of Task Master AI v0.25.0, combining all documentation from WARP-GEM-PRD.md, WARP-PRD.md, CLAUDE-PRD.md, CLAUDE.md, and WARP.md*