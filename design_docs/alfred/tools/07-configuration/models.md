# models

## Purpose
Configure and manage AI model settings for Alfred task operations.

## Description
The `models` tool allows users to view current AI model configuration and switch between available Anthropic Claude models for different use cases. While Alfred supports only Anthropic for MVP, this tool provides flexibility to switch between different Claude models based on task requirements (speed vs capability trade-offs).

## MCP Tool Specification

### Tool Name
`models`

### Parameters
```yaml
configure_model:
  type: object
  properties:
    model_id:
      type: string
      description: "Claude model to use"
      enum: 
        - "claude-3-5-sonnet-20241022"  # Most capable
        - "claude-3-5-haiku-20241022"   # Fastest
        - "claude-3-opus-20240229"      # Previous generation
      required: false
    show_current:
      type: boolean
      description: "Display current model configuration"
      default: true
    list_available:
      type: boolean
      description: "List all available models with details"
      default: false
```

## Implementation Details

### Available Models (MVP)
```python
AVAILABLE_MODELS = {
    "claude-3-5-sonnet-20241022": {
        "name": "Claude 3.5 Sonnet",
        "context_window": 200000,
        "output_limit": 8192,
        "strengths": ["Complex reasoning", "Code generation", "Analysis"],
        "speed": "medium",
        "cost": "medium"
    },
    "claude-3-5-haiku-20241022": {
        "name": "Claude 3.5 Haiku", 
        "context_window": 200000,
        "output_limit": 8192,
        "strengths": ["Fast responses", "Simple tasks", "High volume"],
        "speed": "fast",
        "cost": "low"
    },
    "claude-3-opus-20240229": {
        "name": "Claude 3 Opus",
        "context_window": 200000,
        "output_limit": 4096,
        "strengths": ["Deep analysis", "Creative tasks"],
        "speed": "slow",
        "cost": "high"
    }
}
```

### Configuration Storage
Model selection is stored in `.alfred/config.json`:
```json
{
  "ai": {
    "provider": "anthropic",
    "model_id": "claude-3-5-sonnet-20241022",
    "temperature": 0.7,
    "max_tokens": 4096
  }
}
```

### Environment Variables
```bash
# Required
ANTHROPIC_API_KEY=sk-ant-xxx

# Optional overrides
ALFRED_MODEL=claude-3-5-sonnet-20241022
ALFRED_TEMPERATURE=0.7
ALFRED_MAX_TOKENS=4096
```

## Workflow Examples

### View Current Configuration
```python
# User wants to see current model
await models(show_current=True)

# Returns:
{
  "current_model": {
    "id": "claude-3-5-sonnet-20241022",
    "name": "Claude 3.5 Sonnet",
    "context_window": 200000,
    "api_key_status": "configured"
  }
}
```

### List Available Models
```python
# User wants to see all options
await models(list_available=True)

# Returns detailed list with capabilities
```

### Switch Model
```python
# User wants faster responses for simple tasks
await models(model_id="claude-3-5-haiku-20241022")

# Returns:
{
  "previous_model": "claude-3-5-sonnet-20241022",
  "new_model": "claude-3-5-haiku-20241022",
  "status": "Model updated successfully"
}
```

## Linear/Jira Integration
Not applicable - this tool manages Alfred's AI configuration only.

## Error Handling
- Invalid model ID → List available models
- Missing API key → Provide setup instructions
- API key validation → Test with simple completion

## Future Enhancements
1. **Multi-provider support** (post-MVP)
   - OpenAI GPT models
   - Google Gemini
   - Open source via Ollama

2. **Role-based models**
   - Main: Primary task operations
   - Research: Web-enabled models
   - Fallback: Backup when primary fails

3. **Usage tracking**
   - Token consumption
   - Cost estimation
   - Performance metrics

4. **Model recommendations**
   - Suggest model based on task type
   - Auto-switch for optimal performance

## Related Tools
- `initialize_project` - Sets up initial model configuration
- All task creation/update tools use the configured model

## Notes
- Model selection affects speed, cost, and quality of AI operations
- Sonnet recommended for complex task analysis
- Haiku recommended for bulk operations
- Configuration persists across sessions