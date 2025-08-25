# Workspace Tools Developer Documentation

## Overview

The workspace tools provide foundational functionality for connecting Alfred Task Manager to Linear workspaces. These tools handle authentication, configuration persistence, and workspace discovery.

## Architecture

The workspace tools follow a clean architecture pattern with separation of concerns:

```
src/alfred/
├── core/workspace/          # Business logic (pure functions)
│   ├── initialize.py       # Workspace initialization logic
│   ├── info.py            # Workspace info retrieval
│   ├── teams.py           # Teams listing logic
│   └── projects.py        # Projects/epics listing logic
└── tools/workspace/        # MCP tool wrappers  
    ├── initialize_workspace.py
    ├── get_workspace_info.py
    ├── list_teams.py
    └── list_projects.py
```

### Design Principles

1. **Separation of Concerns**: Business logic is separated from MCP decorators
2. **Testability**: Core logic can be unit tested without MCP context
3. **One Tool Per File**: Each tool is in its own file for maintainability
4. **Thin Wrappers**: Tool decorators are minimal, just handling MCP concerns

## Tools Reference

### initialize_workspace

**Purpose**: Connect to Linear workspace and save configuration

**Parameters**:
- `workspace_id` (string, required): Linear workspace/organization ID
- `team_id` (string, required): Linear team ID

**Returns**:
```json
{
  "status": "ok",
  "message": "Workspace initialized successfully",
  "platform": "linear",
  "workspace": {
    "id": "workspace-id",
    "name": "Workspace Name"
  },
  "team": {
    "id": "team-id",
    "name": "Team Name"
  },
  "config_path": ".alfred/config.json"
}
```

**Error Conditions**:
- Missing LINEAR_API_KEY → AuthError
- Invalid API key → AuthError  
- Team not found → ValidationError
- Missing parameters → ValidationError

**Usage Example**:
```python
result = await initialize_workspace(
    workspace_id="my-org",
    team_id="c9e2a683-598a-4a34-83bf-5058187bccf3"
)
```

### get_workspace_info

**Purpose**: Get current workspace configuration and connection status

**Parameters**: None

**Returns**:
```json
{
  "status": "configured",
  "connection_status": "connected",
  "platform": "linear",
  "workspace": {
    "id": "workspace-id",
    "name": "workspace-id"
  },
  "team": {
    "id": "team-id",
    "name": "team-id"
  },
  "active_epic_id": null,
  "has_api_key": true,
  "has_ai_config": true
}
```

**Status Values**:
- `status`: "configured" or "not_configured"
- `connection_status`: "connected", "not_connected", or "connection_failed"

### list_teams

**Purpose**: List all available teams in the Linear workspace

**Parameters**: None

**Returns**:
```json
{
  "status": "ok",
  "teams": [
    {
      "id": "team-id",
      "name": "Team Name",
      "description": "Team description",
      "key": "TEAM"
    }
  ],
  "count": 1
}
```

**Error Conditions**:
- Missing LINEAR_API_KEY → AuthError
- Invalid API key → AuthError
- Network issues → APIConnectionError

### list_projects

**Purpose**: List all projects (epics) in the Linear workspace

**Parameters**: None

**Returns**:
```json
{
  "status": "ok",
  "projects": [
    {
      "id": "epic-id",
      "name": "Project Name",
      "description": "Project description",
      "url": "https://linear.app/team/epic-id"
    }
  ],
  "count": 1
}
```

**Note**: Linear uses the term "epics" for what Alfred calls "projects"

## Configuration Management

### Storage Location

Configuration is stored in two files:
- `~/.alfred/config.json`: Global Alfred configuration
- `~/.alfred/workspace.json`: Active workspace selection

### Configuration Schema

```json
{
  "platform": "linear",
  "workspace_id": "organization-id",
  "team_id": "team-uuid",
  "active_epic_id": null,
  "last_sync": "2024-01-20T10:00:00Z"
}
```

### Environment Variables

Required environment variables:
- `LINEAR_API_KEY`: Linear API key for authentication

Optional:
- `ANTHROPIC_API_KEY`: For AI features
- `JIRA_API_KEY`, `JIRA_URL`, `JIRA_EMAIL`: For Jira support (future)

## Testing

### Running Tests

```bash
# Run all workspace tests
PYTHONPATH=src uv run pytest tests/core/workspace/ -v

# Run specific test file
PYTHONPATH=src uv run pytest tests/core/workspace/test_initialize.py -v

# Run with coverage
PYTHONPATH=src uv run pytest tests/core/workspace/ --cov=alfred.core.workspace
```

### Test Structure

Tests are organized by business logic module:
- `test_initialize.py`: Tests for workspace initialization
- `test_info.py`: Tests for workspace info retrieval
- `test_teams.py`: Tests for teams listing
- `test_projects.py`: Tests for projects/epics listing

### Mocking Strategy

Tests use `unittest.mock` to mock external dependencies:
- `LinearAdapter`: Mocked to avoid API calls
- `get_config`/`set_active_workspace`: Mocked for config operations
- File system operations are not mocked (use temp directories if needed)

## Integration with Linear

### Linear API Client

The tools use the `linear-api` Python library through the `LinearAdapter` class:

```python
from alfred.adapters.linear_adapter import LinearAdapter

adapter = LinearAdapter(api_token=api_key)
teams = adapter.client.teams.get_all()
```

### GraphQL Queries

The Linear API uses GraphQL. Common queries:
- Teams: `teams.get_all()`
- Projects/Epics: `adapter.get_epics(limit=100)`
- Issues: `adapter.list_issues(filters)`

### Status Mapping

Linear statuses map to Alfred statuses:
- Linear: backlog, todo → Alfred: pending
- Linear: in_progress → Alfred: in_progress  
- Linear: done → Alfred: done
- Linear: canceled → Alfred: cancelled

## Error Handling

### Error Types

The tools use custom exception types from `alfred.adapters.base`:
- `AuthError`: Authentication failures
- `ValidationError`: Invalid input parameters
- `APIConnectionError`: Network/connection issues
- `NotFoundError`: Resource not found

### Error Response Format

Tools return structured error responses:
```json
{
  "error": "error_type",
  "message": "Human-readable error message",
  "details": {}
}
```

## Adding New Workspace Tools

To add a new workspace tool:

1. **Create business logic** in `src/alfred/core/workspace/new_operation.py`:
```python
async def new_operation_logic(param: str, api_key: str) -> Dict[str, Any]:
    """Pure business logic."""
    adapter = LinearAdapter(api_token=api_key)
    # Implementation
    return {"status": "ok", ...}
```

2. **Create tool wrapper** in `src/alfred/tools/workspace/new_tool.py`:
```python
from alfred.core.workspace.new_operation import new_operation_logic
from alfred.config import get_config

def register(server) -> int:
    @server.tool
    async def new_tool(param: str) -> dict:
        """Tool description."""
        config = get_config()
        return await new_operation_logic(
            param=param,
            api_key=config.linear_api_key
        )
    return 1
```

3. **Add tests** in `tests/core/workspace/test_new_operation.py`

4. **Update documentation** in this file

## Troubleshooting

### Common Issues

1. **"LINEAR_API_KEY not configured"**
   - Ensure LINEAR_API_KEY is set in environment or .env file
   - Check `~/.alfred/config.json` exists

2. **"Team not found"**
   - Run `list_teams` to get valid team IDs
   - Verify the team exists in your Linear workspace

3. **"Connection failed"**
   - Check network connectivity
   - Verify API key is valid and not expired
   - Check Linear API status

### Debug Logging

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Manual Testing

Test with actual Linear API:
```bash
# Set API key
export LINEAR_API_KEY="lin_api_..."

# Test with Python
python -c "
from alfred.server import create_server, register_tools
server = create_server()
register_tools(server)
# Tools are now available
"
```

## Future Enhancements

Planned improvements:
- [ ] Jira adapter implementation
- [ ] Workspace switching without config overwrite
- [ ] Team name resolution (not just IDs)
- [ ] Pagination for large team/project lists
- [ ] Caching for frequently accessed data
- [ ] Webhook support for real-time updates