# Alfred

A sophisticated task management system designed for AI-driven development workflows. Alfred provides a powerful MCP (Model Context Protocol) server for seamless integration with AI assistants, enabling intelligent task management with hierarchical structure, dependency tracking, and AI-powered features.

## Features

### Core Capabilities
- **Hierarchical Task Management** - Organize tasks with unlimited nesting levels
- **AI-Powered Operations** - Task generation, expansion, and analysis using multiple AI providers
- **Tag-Based Contexts** - Manage multiple task contexts (like git branches)
- **Dependency Tracking** - Define and validate task dependencies
- **Complexity Analysis** - AI-driven task complexity assessment and recommendations
- **Research Mode** - Enhanced AI analysis with web search capabilities
- **Multi-Provider Support** - 13+ AI providers including Anthropic, OpenAI, Google, Perplexity

### MCP Tools (42+ Available)

#### Initialization & Configuration
- `initialize_project` - Set up Alfred project structure
- `models` - Configure AI providers and models
- `rules` - Manage coding rules and profiles

#### Task Creation & Management
- `parse_prd` - Generate tasks from Product Requirements Documents
- `add_task` - Create new tasks with AI assistance
- `expand_task` - Break tasks into subtasks
- `update_task` - Modify task details
- `remove_task` - Delete tasks

#### Task Analysis
- `analyze_complexity` - Assess task complexity
- `next_task` - Get intelligent task recommendations
- `research` - AI-powered research with project context

#### Organization & Workflow
- `add_dependency` - Create task dependencies
- `move_task` - Reorganize task hierarchy
- `scope_up` / `scope_down` - Adjust task scope
- Tag management for parallel workflows

## Installation

### Using uv (Recommended)

```bash
# Install uv if not already installed
curl -sSf https://install.python-uv.org | bash

# Clone the repository
git clone https://github.com/yourusername/alfred.git
cd alfred

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv sync
```

### Using pip

```bash
# Clone and setup
git clone https://github.com/yourusername/alfred.git
cd alfred
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
```

## Configuration

### MCP Server Setup

Add to your Claude Desktop or MCP client configuration:

```json
{
  "mcpServers": {
    "alfred": {
      "command": "uv",
      "args": ["run", "alfred-mcp"],
      "cwd": "/path/to/alfred",
      "env": {
        "ANTHROPIC_API_KEY": "your_key_here",
        "OPENAI_API_KEY": "your_key_here",
        "GOOGLE_API_KEY": "your_key_here",
        "PERPLEXITY_API_KEY": "your_key_here"
      }
    }
  }
}
```

### Environment Variables

Create a `.env` file in the project root:

```bash
# Required for AI features
ANTHROPIC_API_KEY=your_anthropic_key
OPENAI_API_KEY=your_openai_key
GOOGLE_API_KEY=your_google_key
PERPLEXITY_API_KEY=your_perplexity_key

# Optional providers
XAI_API_KEY=your_xai_key
GROQ_API_KEY=your_groq_key
MISTRAL_API_KEY=your_mistral_key
OPENROUTER_API_KEY=your_openrouter_key
```

## Usage

### Quick Start

1. **Initialize a project:**
```python
# Through MCP
await alfred.initialize_project(project_root="/path/to/project")
```

2. **Configure AI models:**
```python
await alfred.models(
    set_main="claude-3-5-sonnet-20241022",
    set_research="perplexity-llama-3.1-sonar-large-128k-online",
    set_fallback="gpt-4o-mini"
)
```

3. **Parse a PRD to generate tasks:**
```python
await alfred.parse_prd(
    input="requirements.md",
    num_tasks="10",
    research=True
)
```

4. **Analyze complexity and expand tasks:**
```python
# Analyze
await alfred.analyze_complexity(threshold=5)

# Expand high-complexity tasks
await alfred.expand_all(num=5, research=True)
```

5. **Get next task to work on:**
```python
next_task = await alfred.next_task()
```

### Working with Tags (Contexts)

```python
# Create a feature branch context
await alfred.add_tag(name="feature-auth", copy_from_current=True)

# Switch to the new context
await alfred.use_tag(name="feature-auth")

# Work on tasks in this context
await alfred.add_task(prompt="Implement JWT authentication")

# Switch back to main
await alfred.use_tag(name="master")
```

### Task Dependencies

```python
# Create dependent tasks
await alfred.add_dependency(id="2", depends_on="1")

# Validate all dependencies
await alfred.validate_dependencies()

# Auto-fix circular dependencies
await alfred.fix_dependencies()
```

## Project Structure

```
alfred/
├── src/alfred/
│   ├── server.py              # Main MCP server
│   ├── tools/                 # MCP tool implementations
│   ├── resources/             # MCP resources
│   ├── prompts/               # MCP prompts
│   ├── core/                  # Business logic
│   ├── adapters/              # Linear/Jira API adapters
│   │   ├── __init__.py
│   │   ├── base.py           # Abstract adapter interface
│   │   ├── linear.py         # Linear API implementation
│   │   └── jira.py           # Jira API implementation (future)
│   ├── ai_services/          # AI provider integration
│   │   ├── __init__.py
│   │   ├── providers.py      # Provider management
│   │   ├── prompts.py        # Prompt templates
│   │   └── unified.py        # Unified AI interface
│   ├── storage/               # Data persistence
│   └── utils/                 # Utilities
├── tests/                     # Test suite
├── .alfred/                   # Data directory
│   ├── tasks/
│   ├── config.json
│   └── reports/
└── pyproject.toml            # Project configuration
```

## Data Architecture

### Task Structure
```json
{
  "id": "1.2.3",
  "title": "Implement user authentication",
  "description": "Add JWT-based auth system",
  "status": "pending|in-progress|done|blocked|deferred|cancelled",
  "priority": "low|medium|high|critical",
  "dependencies": ["1.2.1", "1.2.2"],
  "details": "Implementation notes...",
  "testStrategy": "Unit and integration tests",
  "subtasks": [],
  "complexity": "S|M|L|XL"
}
```

### Tagged Task Lists
```json
{
  "master": {
    "tasks": [/* main branch tasks */]
  },
  "feature-auth": {
    "tasks": [/* feature branch tasks */]
  }
}
```

## Development

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=alfred

# Run specific test file
uv run pytest tests/unit/test_tools.py
```

### Code Quality

```bash
# Format code
uv run ruff format

# Lint code
uv run ruff check

# Type checking
uv run mypy src/
```

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## API Reference

### Core Tools

#### Task Management
- `get_tasks(status?, with_subtasks?)` - List all tasks
- `get_task(id)` - Get specific task details
- `add_task(prompt?, title?, description?)` - Create new task
- `update_task(id, prompt)` - Update task details
- `remove_task(id)` - Delete task
- `set_task_status(id, status)` - Update task status

#### Task Expansion
- `expand_task(id, num?, research?)` - Expand single task
- `expand_all(num?, research?)` - Expand all eligible tasks
- `scope_up(id, strength, prompt?)` - Increase task scope
- `scope_down(id, strength, prompt?)` - Decrease task scope

#### Analysis & Research
- `analyze_complexity(threshold?, research?)` - Analyze task complexity
- `research(query, task_ids?, file_paths?)` - AI-powered research
- `next_task()` - Get next recommended task

#### Dependencies
- `add_dependency(id, depends_on)` - Create dependency
- `remove_dependency(id, depends_on)` - Remove dependency
- `validate_dependencies()` - Check for issues
- `fix_dependencies()` - Auto-fix problems

#### Tag Management
- `list_tags()` - Show all contexts
- `add_tag(name, copy_from?)` - Create new context
- `use_tag(name)` - Switch context
- `delete_tag(name)` - Remove context

## Roadmap

- [ ] Web UI dashboard
- [ ] REST API server
- [ ] Real-time collaboration
- [ ] Task templates library
- [ ] Custom AI prompts
- [ ] Workflow automation
- [ ] GitHub/GitLab integration
- [ ] Export to Jira/Asana
- [ ] Mobile companion app

## License

MIT License - see [LICENSE](LICENSE) file for details

## Support

- **Documentation**: [docs.alfred.ai](https://docs.alfred.ai)
- **Issues**: [GitHub Issues](https://github.com/yourusername/alfred/issues)
- **Discord**: [Join our community](https://discord.gg/alfred)

## Acknowledgments

Built with:
- [FastMCP](https://github.com/fastmcp/fastmcp) - MCP server framework
- [Pydantic](https://pydantic-docs.helpmanual.io/) - Data validation
- [uv](https://github.com/astral-sh/uv) - Python package manager

---

*Alfred - Your AI-powered task management companion*