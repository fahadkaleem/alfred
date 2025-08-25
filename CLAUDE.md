# Alfred Task Manager - Development Guide

## Task Master AI Instructions
**Import Task Master's development workflow commands and guidelines, treat as if import is in the main CLAUDE.md file.**
@./.taskmaster/CLAUDE.md

## Research and Documentation

- **Always use Perplexity MCP** (`mcp__perplexity-ask__perplexity_ask`) for researching implementation patterns, best practices, and technical questions
- **Use Context7 MCP** for fetching library documentation and code examples when working with specific frameworks
- Prefer these tools over web search for more accurate and up-to-date information

## Project Structure

Follow the directory structure defined in README.md:

```
alfred/
├── src/alfred/
│   ├── server.py              # Main MCP server
│   ├── tools/                 # MCP tool implementations
│   ├── resources/             # MCP resources
│   ├── prompts/               # MCP prompts
│   ├── core/                  # Business logic
│   ├── adapters/              # Linear/Jira API adapters
│   ├── ai_services/          # AI provider integration
│   ├── storage/               # Data persistence
│   └── utils/                 # Utilities
├── tests/                     # Test suite
├── .alfred/                   # Data directory
└── pyproject.toml            # Project configuration
```

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

## Linear Integration

The project uses the `linear-api` Python package for Linear integration:

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
