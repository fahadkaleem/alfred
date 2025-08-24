# Alfred Configuration System

## Overview

Alfred uses a robust configuration system built on Pydantic for validation and `.env` files for secrets management. This ensures type safety, security, and ease of use across different environments.

## Architecture

### Core Components

1. **Pydantic Settings**: Type-safe configuration with validation
2. **Environment Files**: Secure storage of API keys and secrets
3. **Local Config**: Workspace selection persistence
4. **Configuration Manager**: Centralized config lifecycle management

## Configuration Schema

### Settings Model (`alfred/config/settings.py`)

```python
from pydantic import BaseSettings, Field, validator
from typing import Optional, Literal
from pathlib import Path

class AlfredSettings(BaseSettings):
    """Alfred configuration with Pydantic validation."""
    
    # Platform Selection
    platform: Literal["linear", "jira"] = Field(
        default="linear",
        description="Task management platform to use"
    )
    
    # API Keys (from environment)
    linear_api_key: Optional[str] = Field(
        default=None,
        env="LINEAR_API_KEY",
        description="Linear API key"
    )
    jira_api_key: Optional[str] = Field(
        default=None,
        env="JIRA_API_KEY",
        description="Jira API key"
    )
    jira_url: Optional[str] = Field(
        default=None,
        env="JIRA_URL",
        description="Jira instance URL"
    )
    jira_email: Optional[str] = Field(
        default=None,
        env="JIRA_EMAIL",
        description="Jira user email"
    )
    anthropic_api_key: str = Field(
        ...,  # Required
        env="ANTHROPIC_API_KEY",
        description="Anthropic API key for Claude"
    )
    
    # Workspace Configuration
    workspace_id: Optional[str] = Field(
        default=None,
        description="Active workspace/instance ID"
    )
    team_id: Optional[str] = Field(
        default=None,
        description="Active team/project ID"
    )
    default_epic_id: Optional[str] = Field(
        default=None,
        description="Default epic for new tasks"
    )
    
    # AI Configuration
    claude_model: str = Field(
        default="claude-3-5-sonnet-20241022",
        env="CLAUDE_MODEL",
        description="Claude model to use"
    )
    max_tokens: int = Field(
        default=4096,
        env="MAX_TOKENS",
        description="Max tokens for AI responses"
    )
    temperature: float = Field(
        default=0.7,
        env="TEMPERATURE",
        description="AI temperature setting",
        ge=0.0,
        le=1.0
    )
    
    # Behavior Configuration
    auto_decompose_threshold: int = Field(
        default=5,
        description="Complexity score threshold for auto-decomposition"
    )
    default_subtask_count: int = Field(
        default=3,
        description="Default number of subtasks when decomposing"
    )
    
    # Paths
    config_dir: Path = Field(
        default=Path.home() / ".alfred",
        description="Alfred configuration directory"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
```

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `ANTHROPIC_API_KEY` | Anthropic API key for Claude | `sk-ant-api03-xxx...` |
| `LINEAR_API_KEY` | Linear API key (if using Linear) | `lin_api_xxx...` |
| `JIRA_API_KEY` | Jira API token (if using Jira) | `ATATT3xFfGF0xxx...` |
| `JIRA_URL` | Jira instance URL (if using Jira) | `https://company.atlassian.net` |
| `JIRA_EMAIL` | Jira user email (if using Jira) | `user@company.com` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PLATFORM` | Platform to use (`linear` or `jira`) | `linear` |
| `CLAUDE_MODEL` | Claude model version | `claude-3-5-sonnet-20241022` |
| `MAX_TOKENS` | Maximum tokens for AI responses | `4096` |
| `TEMPERATURE` | AI temperature (0.0-1.0) | `0.7` |

## Configuration Files

### `.env` File
Primary configuration file containing API keys and settings:

```bash
# Platform Configuration
PLATFORM=linear

# Linear Configuration
LINEAR_API_KEY=lin_api_xxxxxxxxxxxxxxxxxxxxx

# AI Configuration
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxx

# Optional AI Settings
CLAUDE_MODEL=claude-3-5-sonnet-20241022
MAX_TOKENS=4096
TEMPERATURE=0.7
```

### `.env.example` File
Template file created during initialization:

```bash
# Alfred Configuration
# Copy this file to .env and fill in your API keys

# Platform Configuration
# Options: linear, jira
PLATFORM=linear

# Linear Configuration (required if PLATFORM=linear)
LINEAR_API_KEY=your_linear_api_key_here

# Jira Configuration (required if PLATFORM=jira)
# JIRA_API_KEY=your_jira_api_token
# JIRA_URL=https://yourcompany.atlassian.net
# JIRA_EMAIL=you@company.com

# AI Configuration (required)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Optional: Override default Claude model
# CLAUDE_MODEL=claude-3-5-sonnet-20241022

# Optional: AI behavior settings
# MAX_TOKENS=4096
# TEMPERATURE=0.7
```

### `.alfred/workspace.json`
Persists workspace selection between sessions:

```json
{
  "platform": "linear",
  "workspace_id": "workspace-uuid",
  "team_id": "team-uuid",
  "default_epic_id": "project-uuid"
}
```

## Configuration Manager

### Singleton Pattern
```python
class ConfigManager:
    """Manages Alfred configuration lifecycle."""
    
    _instance: Optional[AlfredSettings] = None
    
    @classmethod
    def get_settings(cls) -> AlfredSettings:
        """Get or create settings singleton."""
        if cls._instance is None:
            cls._instance = AlfredSettings.load()
        return cls._instance
```

### Initialization Process
```python
@classmethod
def initialize_project(cls, target_dir: Path = Path.cwd()):
    """Initialize Alfred configuration in a project."""
    alfred_dir = target_dir / ".alfred"
    alfred_dir.mkdir(exist_ok=True)
    
    # Create .env.example
    env_example = target_dir / ".env.example"
    if not env_example.exists():
        env_example.write_text(cls._get_env_template())
    
    # Update .gitignore
    gitignore = target_dir / ".gitignore"
    if gitignore.exists():
        content = gitignore.read_text()
        if ".env" not in content:
            gitignore.write_text(content + "\n.env\n.alfred/\n")
    
    return alfred_dir
```

## Usage in MCP Tools

### Loading Configuration
```python
from alfred.config import ConfigManager

async def some_tool(args):
    # Get validated settings
    settings = ConfigManager.get_settings()
    
    # Access configuration
    if settings.platform == "linear":
        api_key = settings.linear_api_key
        team_id = settings.team_id
```

### Saving Workspace Selection
```python
# After user selects workspace/team
settings.workspace_id = selected_workspace
settings.team_id = selected_team
settings.save_workspace_config()
```

## Validation Rules

### Platform-Specific Validation
- If `platform == "linear"`: Requires `LINEAR_API_KEY`
- If `platform == "jira"`: Requires `JIRA_API_KEY`, `JIRA_URL`, `JIRA_EMAIL`
- Always requires: `ANTHROPIC_API_KEY`

### Type Validation
- `platform`: Must be "linear" or "jira"
- `temperature`: Must be between 0.0 and 1.0
- `max_tokens`: Must be positive integer
- API keys: Must be non-empty strings when required

## Security Considerations

### Best Practices
1. **Never commit `.env` files**: Always in `.gitignore`
2. **Use `.env.example`**: Template without real keys
3. **Environment isolation**: Different `.env` per environment
4. **Key rotation**: Regular API key updates
5. **Minimal permissions**: Use read/write only keys

### File Permissions
```bash
# Recommended permissions
chmod 600 .env  # Read/write for owner only
chmod 644 .env.example  # Readable by all
```

## Error Handling

### Configuration Errors
```python
try:
    settings = ConfigManager.get_settings()
except ValidationError as e:
    # Handle missing or invalid configuration
    print(f"Configuration error: {e}")
    print("Please check your .env file")
```

### Connection Validation
```python
if not ConfigManager.validate_connection():
    print(f"Failed to connect to {settings.platform}")
    print("Please check your API credentials")
```

## Testing Configuration

### Unit Tests
```python
def test_configuration():
    # Mock environment variables
    with mock.patch.dict(os.environ, {
        "ANTHROPIC_API_KEY": "test-key",
        "LINEAR_API_KEY": "test-linear-key",
        "PLATFORM": "linear"
    }):
        settings = AlfredSettings()
        assert settings.platform == "linear"
        assert settings.anthropic_api_key == "test-key"
```

### Integration Tests
```python
async def test_platform_connection():
    settings = ConfigManager.get_settings()
    assert await ConfigManager.validate_connection()
```

## Migration from TaskMaster

### Key Differences
1. **No local task storage**: All data in Linear/Jira
2. **Simplified configuration**: Just API keys and workspace
3. **Platform-specific**: Choose Linear or Jira, not both
4. **Single AI provider**: Anthropic only for MVP

### Migration Steps
1. Create `.env` file with API keys
2. Run `alfred init` to set up configuration
3. Select workspace/team during initialization
4. No data migration needed (stateless)

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| "Configuration error" | Check `.env` file exists and has required keys |
| "Invalid API key" | Verify API key format and permissions |
| "Connection failed" | Check network and API endpoint URLs |
| "Workspace not found" | Re-run initialization to select workspace |

### Debug Mode
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Check loaded configuration
settings = ConfigManager.get_settings()
print(settings.dict(exclude={"anthropic_api_key", "linear_api_key"}))
```

## Future Enhancements

### Planned Features
1. **OAuth support**: Replace API keys with OAuth flow
2. **Multi-workspace**: Support multiple workspace configurations
3. **Secrets management**: Integration with key vaults
4. **Configuration profiles**: Dev/staging/prod environments
5. **Dynamic reloading**: Hot-reload configuration changes

---

*This configuration system provides a secure, type-safe, and maintainable foundation for Alfred's settings management.*