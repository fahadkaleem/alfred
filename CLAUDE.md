# Alfred Task Manager - Development Guide

## Task Master AI Instructions
**Import Task Master's development workflow commands and guidelines, treat as if import is in the main CLAUDE.md file.**
@./.taskmaster/CLAUDE.md

## Research and Documentation

- **Always use Perplexity MCP** (`mcp__perplexity-ask__perplexity_ask`) for researching implementation patterns, best practices, and technical questions
- **Use Context7 MCP** for fetching library documentation and code examples when working with specific frameworks
- Prefer these tools over web search for more accurate and up-to-date information

## Adding New MCP Tools

### Architecture Pattern
We use a **one tool per file** pattern with separation of business logic from MCP decorators:

1. **Business Logic** goes in `src/alfred/core/<domain>/<operation>.py`
   - Pure functions without MCP dependencies
   - Testable without MCP context
   - Takes explicit parameters (no server state access)

2. **Tool Wrapper** goes in `src/alfred/tools/<domain>/<tool_name>.py`
   - Thin wrapper with `@server.tool` decorator
   - Handles MCP-specific concerns (getting config from server state)
   - Calls business logic functions

### Step-by-Step Guide for New Tools

#### 1. Create Business Logic
```python
# src/alfred/core/tasks/create.py
from typing import Dict, Any
from alfred.adapters.linear_adapter import LinearAdapter

async def create_task_logic(
    title: str,
    description: str,
    api_key: str,
    team_id: str
) -> Dict[str, Any]:
    """Pure business logic for task creation."""
    adapter = LinearAdapter(api_token=api_key)
    # Implementation here
    return {"id": task_id, "status": "created"}
```

#### 2. Create Tool Wrapper
```python
# src/alfred/tools/tasks/create_task.py
from alfred.core.tasks.create import create_task_logic
from alfred.config import get_config

def register(server) -> int:
    """Register the create_task tool."""
    
    @server.tool
    async def create_task(title: str, description: str) -> dict:
        """
        Create a new task in Linear.
        
        Args:
            title: Task title
            description: Task description
        """
        config = get_config()
        workspace = config.get_workspace()
        
        return await create_task_logic(
            title=title,
            description=description,
            api_key=config.linear_api_key,
            team_id=workspace.team_id
        )
    
    return 1  # Number of tools registered
```

#### 3. Create Unit Tests
```python
# tests/core/tasks/test_create.py
import pytest
from unittest.mock import Mock, patch
from alfred.core.tasks.create import create_task_logic

@pytest.mark.asyncio
async def test_create_task_success():
    with patch('alfred.core.tasks.create.LinearAdapter') as MockAdapter:
        # Test the pure business logic
        result = await create_task_logic(
            title="Test Task",
            description="Test Description",
            api_key="test-key",
            team_id="team-1"
        )
        assert result["status"] == "created"
```

### Directory Structure for New Tools

When adding tools for a new domain (e.g., "reporting"):

1. Create directories:
   ```
   src/alfred/core/reporting/
   src/alfred/tools/reporting/
   tests/core/reporting/
   ```

2. Add `__init__.py` files to each directory

3. Follow the one-tool-per-file pattern

### Auto-Discovery
Tools are automatically discovered if they:
1. Are in a `.py` file under `src/alfred/tools/`
2. Have a `register(server)` function
3. Return the number of tools registered

### Best Practices
- Keep tool decorators under 20 lines
- Put complex logic in `core/` modules
- Use type hints for automatic schema generation
- Write comprehensive docstrings for tools
- Test business logic, not decorators
- Group related tools by domain (workspace, tasks, ai, etc.)

## Project Structure

Follow the directory structure defined in README.md - see README.md for full details.

## Configuration System

### Usage
```python
from alfred.config import get_config, set_config, validate_api_keys

# Get configuration (cached singleton)
config = get_config()

# Validate API keys
validate_api_keys(config, strict=True)

# Update workspace
from alfred.config import set_active_workspace
config = set_active_workspace(workspace_id="new-workspace", team_id="team-123")
```

### Configuration Precedence
1. Runtime parameters (highest)
2. Environment variables
3. `~/.alfred/config.json`
4. Default values (lowest)

### Required Environment Variables
- `ANTHROPIC_API_KEY` - Required for AI features
- `LINEAR_API_KEY` - Required when platform=linear
- `JIRA_API_KEY`, `JIRA_URL`, `JIRA_EMAIL` - Required when platform=jira

### Key Files
- `.env` - API keys and environment overrides
- `~/.alfred/config.json` - Persistent configuration
- `~/.alfred/workspace.json` - Active workspace selection

### Important Notes
- Get config once per operation, not repeatedly
- Config is cached - use `get_config(refresh=True)` to reload
- API keys are validated without network calls
- Empty strings in config are converted to None

### Data Validation
- **Use Pydantic models** for all data structures
- Define models in appropriate modules (e.g., `core/models.py`)
- Leverage Pydantic's validation capabilities for input sanitization
- Use type hints extensively

### AI Integration

#### Provider Architecture
- **Provider-agnostic design** - Easy to add OpenAI, Gemini, Ollama later
- All providers inherit from `BaseAIProvider` abstract class
- Use `AIService` for high-level operations, not providers directly
- Provider factory pattern for instantiation

#### Current Implementation
- **Default model**: `claude-sonnet-4-20250514`
- **Provider**: Anthropic (Claude)
- Set `ANTHROPIC_API_KEY` in `.env`
- Optional: Set `ANTHROPIC_MODEL` to override default

#### Code Patterns
```python
# Always use AIService, not providers directly
from alfred.ai_services import AIService

service = AIService()
tasks = await service.create_tasks_from_spec(spec, num_tasks=5)
```

#### Key Components
- `ai_services/base.py` - Abstract provider interface
- `ai_services/anthropic_provider.py` - Claude implementation
- `ai_services/service.py` - High-level service layer
- `ai_services/prompts.py` - Reusable prompt templates
- `ai_services/config.py` - Configuration with SettingsConfigDict

#### Features Implemented
- Streaming support for real-time responses
- Token counting and usage tracking
- Automatic retry with exponential backoff
- Large input chunking with overlap
- JSON response parsing with fallbacks

#### Error Handling
- Custom exceptions: `RateLimitError`, `AuthenticationError`, `InvalidRequestError`
- Retry logic for rate limits and transient errors
- Graceful degradation when API unavailable

### FastMCP Patterns
- Use decorators (`@mcp.tool`, `@mcp.resource`, `@mcp.prompt`)
- Leverage type hints for automatic schema generation
- Keep business logic separate from MCP decorators
- Use async functions where appropriate

## Development Workflow

1. Research implementation patterns using Perplexity/Context7
2. Follow the established directory structure
3. Use Pydantic for all data modeling and validation
4. Write comprehensive docstrings for MCP tools
5. Implement error handling with custom exception types
6. Add appropriate logging throughout

## Package Management

- **Always use `uv`** for Python package management and virtual environments
- Never use `pip`, `conda`, or other package managers
- Install dependencies: `uv add <package>`
- Run commands: `uv run <command>`
- Sync environment: `uv sync`

## Testing

- Write tests in the `tests/` directory
- Use `pytest` with `pytest-asyncio` for async tests
- Mock external services (Linear, Jira, AI providers)
- Test Pydantic model validation thoroughly
- Run tests: `uv run pytest tests/ -v`

### AI Service Testing
```python
# Always mock AI providers in tests
from unittest.mock import AsyncMock, MagicMock

mock_provider = MagicMock()
mock_provider.complete = AsyncMock(return_value=mock_response)
service = AIService(custom_provider=mock_provider)
```

## Linear Integration & Architecture

### CRITICAL: Clean Architecture Rules

**NEVER put GraphQL queries outside of `src/alfred/clients/linear/`!** The architecture strictly separates concerns:

#### Layer Responsibilities

1. **Client Layer** (`src/alfred/clients/linear/`)
   - **OWNS**: ALL GraphQL queries and mutations
   - **Location**: `src/alfred/clients/linear/managers/`
   - **Purpose**: Direct Linear API communication
   - **Returns**: Linear domain models (`LinearProject`, `LinearIssue`, etc.)
   - **Example files**:
     - `managers/project_manager.py` - Project/Epic CRUD with GraphQL
     - `managers/issue_manager.py` - Issue/Task CRUD with GraphQL
     - `managers/team_manager.py` - Team operations with GraphQL

2. **Adapter Layer** (`src/alfred/adapters/`)
   - **OWNS**: Data transformation ONLY
   - **Location**: `src/alfred/adapters/linear_adapter.py`
   - **Purpose**: Transform between Linear models ↔ Alfred models
   - **NEVER**: Contains GraphQL queries or direct API calls
   - **ALWAYS**: Uses `self.client` (LinearClient) for all operations
   - **Example transformations**:
     ```python
     # CORRECT: Use client, transform result
     def create_epic(self, name: str) -> EpicDict:
         project = self.client.projects.create(name=name)  # Client does API call
         return self._map_linear_project_to_epic(project)  # Adapter transforms
     
     # WRONG: GraphQL in adapter
     def create_epic(self, name: str) -> EpicDict:
         query = "mutation { ... }"  # NEVER DO THIS IN ADAPTER!
     ```

3. **Core Business Logic** (`src/alfred/core/`)
   - **OWNS**: Business rules and validation
   - **Location**: `src/alfred/core/<domain>/<operation>.py`
   - **Purpose**: Platform-agnostic business logic
   - **NEVER**: Imports from `clients/linear/`
   - **ALWAYS**: Uses adapter interfaces
   - **Example files**:
     - `core/epics/create.py` - Epic creation business logic
     - `core/tasks/update.py` - Task update business logic

### Data Flow

```
User Request
    ↓
MCP Tool (`src/alfred/tools/`)
    ↓
Business Logic (`src/alfred/core/`) - Platform agnostic
    ↓
Adapter (`src/alfred/adapters/`) - Transform only, NO GraphQL!
    ↓
Client (`src/alfred/clients/linear/`) - ALL GraphQL here
    ↓
Linear API
```

### File Placement Rules

| What | Where | Example |
|------|-------|---------|
| GraphQL queries/mutations | `clients/linear/managers/` | `project_manager.py` |
| Linear domain models | `clients/linear/domain/` | `project_models.py` |
| Model transformations | `adapters/linear_adapter.py` | `_map_linear_project_to_epic()` |
| Business logic | `core/<domain>/` | `core/epics/create.py` |
| MCP tool wrappers | `tools/<domain>/` | `tools/epics/create_epic.py` |

### Common Mistakes to Avoid

❌ **NEVER**: Put GraphQL in LinearAdapter
❌ **NEVER**: Import LinearClient in core business logic
❌ **NEVER**: Transform data in the client layer
❌ **NEVER**: Put business rules in the adapter

✅ **ALWAYS**: Keep GraphQL in client managers
✅ **ALWAYS**: Use adapter for transformations only
✅ **ALWAYS**: Keep business logic platform-agnostic
✅ **ALWAYS**: Test each layer independently

### Configuration
- Set `LINEAR_API_KEY` in `.env` file
- Optional: Set `LINEAR_TEAM_NAME` for default team
- Optional: Set `LINEAR_DEFAULT_PROJECT_NAME` for default project

### Usage
```python
from alfred.adapters import LinearAdapter

# Initialize with environment variables
adapter = LinearAdapter()

# Or with explicit configuration
adapter = LinearAdapter(
    api_token="your-api-key",
    team_name="Your Team",
    default_project_name="Your Project"
)
```

### Key Features
- Full CRUD operations for tasks and epics (projects)
- Subtask creation and management
- Task dependencies (blocking relationships)
- Automatic team discovery
- Error handling with custom exceptions

## Key Dependencies

- `fastmcp` - MCP server framework
- `pydantic` - Data validation with v2 patterns
- `pydantic-settings` - Configuration with SettingsConfigDict
- `anthropic>=0.34.0` - Claude AI provider
- `tenacity` - Retry logic with exponential backoff
- `httpx` - Async HTTP client
- `python-dotenv` - Environment variable management
- `linear-api` - Linear GraphQL API client
- `pytest-asyncio` - Async test support
