# Integration Tests

This directory contains integration tests that make real API calls to external services.

## Prerequisites

1. **Environment Variables**: Set up required API keys in your `.env` file:
   ```bash
   ANTHROPIC_API_KEY=your_anthropic_key_here
   LINEAR_API_KEY=your_linear_key_here
   ```

2. **Dependencies**: Install project dependencies:
   ```bash
   uv sync
   ```

## Running Integration Tests

### AI Services Integration Test
Tests the complete AI services functionality with real Anthropic API calls:

```bash
# Run from project root
uv run python tests/integration/test_ai_integration.py
```

This test verifies:
- Provider initialization
- Simple completions
- Task generation from specifications
- Task decomposition
- Complexity assessment
- Research functionality
- Streaming responses
- Token counting
- Usage tracking

### Notes

- **Cost**: These tests make real API calls that consume tokens and may incur costs
- **Network**: Tests require internet connectivity
- **Rate Limits**: Be aware of API rate limits when running frequently
- **CI/CD**: These tests are not run in CI/CD pipelines by default

## Adding New Integration Tests

1. Create test files following the pattern `test_*.py`
2. Import required modules using the path setup pattern
3. Include proper error handling and cost warnings
4. Document any specific prerequisites or setup requirements