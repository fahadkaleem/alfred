# Alfred AI Integration - Anthropic Claude

## Overview

Alfred uses Anthropic's Claude as its sole AI provider for MVP, focusing on simplicity and reliability. The integration is designed to be modular for future expansion but currently optimized for Claude's capabilities.

## Architecture

### Single Provider Design

```python
alfred/
├── ai/
│   ├── __init__.py
│   ├── client.py          # Claude client wrapper
│   ├── prompts.py         # Prompt templates
│   └── exceptions.py      # AI-specific exceptions
```

## Claude Client Implementation

### Base Client (`alfred/ai/client.py`)

```python
from anthropic import AsyncAnthropic
from typing import Optional, Dict, Any, List
from alfred.config import ConfigManager
import logging

logger = logging.getLogger(__name__)

class ClaudeClient:
    """Anthropic Claude client for Alfred."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Claude client with API key."""
        if not api_key:
            settings = ConfigManager.get_settings()
            api_key = settings.anthropic_api_key
        
        self.client = AsyncAnthropic(api_key=api_key)
        self.model = settings.claude_model
        self.max_tokens = settings.max_tokens
        self.temperature = settings.temperature
    
    async def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """Generate text completion from Claude."""
        try:
            messages = [{"role": "user", "content": prompt}]
            
            response = await self.client.messages.create(
                model=self.model,
                messages=messages,
                system=system,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens,
                **kwargs
            )
            
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Claude API error: {e}")
            raise AIException(f"Failed to generate response: {e}")
    
    async def generate_structured(
        self,
        prompt: str,
        system: Optional[str] = None,
        response_format: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate structured JSON response from Claude."""
        
        # Add JSON instruction to prompt
        json_prompt = prompt
        if response_format:
            json_prompt += f"\n\nReturn your response as valid JSON matching this structure:\n{response_format}"
        else:
            json_prompt += "\n\nReturn your response as valid JSON."
        
        response = await self.generate(
            prompt=json_prompt,
            system=system,
            **kwargs
        )
        
        # Parse JSON response
        import json
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            raise AIException("Failed to parse JSON response")
    
    async def stream_generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        on_chunk: Optional[callable] = None,
        **kwargs
    ):
        """Stream responses from Claude."""
        messages = [{"role": "user", "content": prompt}]
        
        async with self.client.messages.stream(
            model=self.model,
            messages=messages,
            system=system,
            max_tokens=self.max_tokens,
            **kwargs
        ) as stream:
            async for chunk in stream:
                if on_chunk and chunk.type == "content_block_delta":
                    await on_chunk(chunk.delta.text)
```

## Prompt Templates

### Template System (`alfred/ai/prompts.py`)

```python
from typing import Dict, Any, Optional
from string import Template
import json

class PromptTemplate:
    """Simple prompt template system for Claude."""
    
    # Task Creation Templates
    CREATE_TASKS_FROM_SPEC = Template("""
You are an expert at breaking down specifications into actionable development tasks.

Analyze this specification and create $num_tasks structured tasks:

Specification:
$specification

${epic_context}

Requirements:
1. Create clear, actionable tasks
2. Each task should be independently completable
3. Include acceptance criteria
4. Consider dependencies between tasks
5. Use appropriate priority levels

Return as JSON array with this structure:
[
  {
    "title": "Clear, action-oriented title",
    "description": "Detailed description of what needs to be done",
    "acceptance_criteria": ["Criterion 1", "Criterion 2"],
    "priority": "low|medium|high|critical",
    "estimated_complexity": 1-10,
    "dependencies": ["task_title_this_depends_on"]
  }
]
""")
    
    # Task Decomposition Template
    DECOMPOSE_TASK = Template("""
Break down this task into $num_subtasks detailed subtasks:

Task: $task_title
Description: $task_description
${additional_context}

Create subtasks that:
1. Are specific and measurable
2. Can be completed independently
3. Cover all aspects of the parent task
4. Include implementation details

Return as JSON array with subtask structure:
[
  {
    "title": "Specific subtask title",
    "description": "What needs to be done",
    "technical_notes": "Implementation approach"
  }
]
""")
    
    # Complexity Assessment Template
    ASSESS_COMPLEXITY = Template("""
Analyze the complexity of these tasks and provide recommendations:

Tasks:
$tasks_json

Evaluate each task for:
1. Technical complexity (1-10)
2. Dependencies and integration points
3. Estimated effort (hours)
4. Risk factors
5. Suggested decomposition strategy

Return as JSON:
{
  "tasks": [
    {
      "id": "task_id",
      "complexity_score": 1-10,
      "estimated_hours": number,
      "risk_level": "low|medium|high",
      "should_decompose": boolean,
      "reasoning": "explanation",
      "decomposition_strategy": "how to break it down"
    }
  ],
  "overall_assessment": "summary and recommendations"
}
""")
    
    # Task Enhancement Template
    UPDATE_TASK = Template("""
Enhance this task with additional context and details:

Current Task:
$task_json

Update Request:
$update_prompt

${project_context}

Provide an enhanced version that:
1. Incorporates the new information
2. Maintains existing structure
3. Adds implementation details
4. Clarifies acceptance criteria

Return the complete updated task as JSON.
""")
    
    # Research Template
    RESEARCH = Template("""
Research and provide comprehensive information about:

Query: $query

Context:
$context

Provide a $detail_level response that:
1. Directly addresses the query
2. Includes practical examples
3. Considers best practices
4. Offers actionable insights

Format your response for a developer audience.
""")
    
    @classmethod
    def render(cls, template_name: str, **kwargs) -> str:
        """Render a prompt template with variables."""
        template = getattr(cls, template_name, None)
        if not template:
            raise ValueError(f"Unknown template: {template_name}")
        
        # Handle optional context fields
        for key in ['epic_context', 'additional_context', 'project_context']:
            if key not in kwargs or not kwargs[key]:
                kwargs[key] = ""
            else:
                kwargs[key] = f"\nContext: {kwargs[key]}"
        
        return template.safe_substitute(**kwargs)
```

## AI Service Layer

### Main Service (`alfred/ai/service.py`)

```python
from typing import List, Dict, Any, Optional
from alfred.ai.client import ClaudeClient
from alfred.ai.prompts import PromptTemplate
import logging

logger = logging.getLogger(__name__)

class AIService:
    """High-level AI service for Alfred operations."""
    
    def __init__(self):
        self.client = ClaudeClient()
    
    async def create_tasks_from_spec(
        self,
        specification: str,
        num_tasks: int = 5,
        epic_context: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Generate tasks from a specification."""
        
        prompt = PromptTemplate.render(
            "CREATE_TASKS_FROM_SPEC",
            specification=specification,
            num_tasks=num_tasks,
            epic_context=epic_context
        )
        
        system = "You are a senior software architect helping break down requirements into development tasks."
        
        response = await self.client.generate_structured(
            prompt=prompt,
            system=system,
            temperature=0.7
        )
        
        return response
    
    async def decompose_task(
        self,
        task: Dict[str, Any],
        num_subtasks: int = 3,
        context: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Decompose a task into subtasks."""
        
        prompt = PromptTemplate.render(
            "DECOMPOSE_TASK",
            task_title=task["title"],
            task_description=task.get("description", ""),
            num_subtasks=num_subtasks,
            additional_context=context
        )
        
        system = "You are an expert at task decomposition and work breakdown structures."
        
        response = await self.client.generate_structured(
            prompt=prompt,
            system=system,
            temperature=0.6
        )
        
        return response
    
    async def assess_complexity(
        self,
        tasks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Assess complexity of tasks."""
        
        import json
        prompt = PromptTemplate.render(
            "ASSESS_COMPLEXITY",
            tasks_json=json.dumps(tasks, indent=2)
        )
        
        system = "You are a technical lead experienced in effort estimation and risk assessment."
        
        response = await self.client.generate_structured(
            prompt=prompt,
            system=system,
            temperature=0.5
        )
        
        return response
    
    async def enhance_task(
        self,
        task: Dict[str, Any],
        update_prompt: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Enhance a task with additional information."""
        
        import json
        prompt = PromptTemplate.render(
            "UPDATE_TASK",
            task_json=json.dumps(task, indent=2),
            update_prompt=update_prompt,
            project_context=context
        )
        
        system = "You are a detail-oriented project manager helping maintain accurate task descriptions."
        
        response = await self.client.generate_structured(
            prompt=prompt,
            system=system,
            temperature=0.6
        )
        
        return response
    
    async def research(
        self,
        query: str,
        context: str = "",
        detail_level: str = "medium"
    ) -> str:
        """Perform research on a topic."""
        
        prompt = PromptTemplate.render(
            "RESEARCH",
            query=query,
            context=context,
            detail_level=detail_level
        )
        
        system = "You are a knowledgeable technical researcher providing practical insights."
        
        response = await self.client.generate(
            prompt=prompt,
            system=system,
            temperature=0.8,
            max_tokens=4096
        )
        
        return response
```

## Error Handling

### Custom Exceptions (`alfred/ai/exceptions.py`)

```python
class AIException(Exception):
    """Base exception for AI operations."""
    pass

class AIRateLimitException(AIException):
    """Rate limit exceeded."""
    pass

class AIInvalidResponseException(AIException):
    """Invalid or unparseable response."""
    pass

class AITimeoutException(AIException):
    """Request timeout."""
    pass
```

## Token Management

### Token Counting and Optimization

```python
from anthropic import count_tokens

class TokenManager:
    """Manage token usage and optimization."""
    
    @staticmethod
    def count_tokens(text: str, model: str = "claude-3-5-sonnet-20241022") -> int:
        """Count tokens in text."""
        # Use Anthropic's token counter
        return count_tokens(text, model)
    
    @staticmethod
    def truncate_to_limit(text: str, max_tokens: int = 4000) -> str:
        """Truncate text to token limit."""
        tokens = TokenManager.count_tokens(text)
        if tokens <= max_tokens:
            return text
        
        # Rough approximation: 1 token ≈ 4 characters
        char_limit = max_tokens * 4
        return text[:char_limit] + "..."
    
    @staticmethod
    def optimize_context(
        context: str,
        max_tokens: int = 2000
    ) -> str:
        """Optimize context for token efficiency."""
        # Remove redundant whitespace
        import re
        context = re.sub(r'\s+', ' ', context)
        
        # Truncate if needed
        return TokenManager.truncate_to_limit(context, max_tokens)
```

## Usage in MCP Tools

### Example Tool Implementation

```python
from alfred.ai.service import AIService

async def create_tasks_from_spec(args):
    """MCP tool to create tasks from specification."""
    
    ai_service = AIService()
    
    # Get specification
    spec = args.get("specification")
    num_tasks = args.get("num_tasks", 5)
    epic_id = args.get("epic_id")
    
    # Get epic context if provided
    epic_context = None
    if epic_id:
        # Fetch epic details from Linear/Jira
        epic_context = await get_epic_context(epic_id)
    
    # Generate tasks using AI
    tasks = await ai_service.create_tasks_from_spec(
        specification=spec,
        num_tasks=num_tasks,
        epic_context=epic_context
    )
    
    # Create tasks in Linear/Jira
    created_tasks = []
    for task_data in tasks:
        task = await create_task_in_platform(task_data)
        created_tasks.append(task)
    
    return {
        "success": True,
        "tasks_created": len(created_tasks),
        "tasks": created_tasks
    }
```

## Performance Optimization

### Caching Strategy

```python
from functools import lru_cache
from typing import Optional
import hashlib

class PromptCache:
    """Simple cache for AI responses."""
    
    def __init__(self, max_size: int = 100):
        self.cache = {}
        self.max_size = max_size
    
    def get_key(self, prompt: str, system: Optional[str] = None) -> str:
        """Generate cache key from prompt."""
        content = f"{prompt}:{system or ''}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get(self, prompt: str, system: Optional[str] = None) -> Optional[str]:
        """Get cached response."""
        key = self.get_key(prompt, system)
        return self.cache.get(key)
    
    def set(self, prompt: str, response: str, system: Optional[str] = None):
        """Cache response."""
        if len(self.cache) >= self.max_size:
            # Remove oldest entry (simple FIFO)
            self.cache.pop(next(iter(self.cache)))
        
        key = self.get_key(prompt, system)
        self.cache[key] = response
```

## Configuration

### AI Settings in Config

```python
# AI-specific configuration
claude_model: str = "claude-3-5-sonnet-20241022"
max_tokens: int = 4096
temperature: float = 0.7

# Rate limiting
max_requests_per_minute: int = 50
retry_attempts: int = 3
retry_delay: float = 1.0
```

## Testing

### Mock Client for Testing

```python
class MockClaudeClient:
    """Mock Claude client for testing."""
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """Return mock response based on prompt."""
        if "create tasks" in prompt.lower():
            return '[{"title": "Test Task", "description": "Test"}]'
        return "Mock response"
    
    async def generate_structured(self, prompt: str, **kwargs) -> Dict:
        """Return mock structured response."""
        if "create tasks" in prompt.lower():
            return [{"title": "Test Task", "description": "Test"}]
        return {"result": "mock"}
```

## Best Practices

### Prompt Engineering Guidelines

1. **Clear Instructions**: Always specify exact output format
2. **Context Limiting**: Include only relevant context
3. **Temperature Control**: Lower for structured data (0.3-0.5), higher for creative tasks (0.7-0.9)
4. **Token Efficiency**: Minimize prompt size while maintaining clarity
5. **Error Recovery**: Always validate AI responses before using

### Rate Limit Management

```python
import asyncio
from datetime import datetime, timedelta

class RateLimiter:
    """Simple rate limiter for API calls."""
    
    def __init__(self, max_calls: int = 50, period: int = 60):
        self.max_calls = max_calls
        self.period = period
        self.calls = []
    
    async def acquire(self):
        """Wait if necessary to respect rate limit."""
        now = datetime.now()
        
        # Remove old calls outside window
        self.calls = [
            call_time for call_time in self.calls
            if now - call_time < timedelta(seconds=self.period)
        ]
        
        if len(self.calls) >= self.max_calls:
            # Wait until oldest call expires
            sleep_time = self.period - (now - self.calls[0]).total_seconds()
            await asyncio.sleep(sleep_time)
        
        self.calls.append(now)
```

## Migration from TaskMaster

### Key Simplifications

1. **Single Provider**: Only Anthropic (removed 13 provider complexity)
2. **No Provider Registry**: Direct Claude client instantiation
3. **Simplified Prompts**: Templates instead of complex JSON schemas
4. **No Streaming by Default**: Simplified async operations
5. **No Research Provider**: Claude handles all operations

### Removed Features

- Multiple AI providers
- Provider fallback logic
- Complex prompt variants
- Token cost calculation
- Model role selection (main/research/fallback)

## Future Enhancements

### Planned Improvements

1. **Streaming Support**: Add streaming for long operations
2. **Function Calling**: Use Claude's function calling when available
3. **Vision Support**: Add support for image inputs
4. **Conversation Memory**: Maintain context across requests
5. **Provider Abstraction**: Add provider interface for future expansion

---

*This simplified AI integration focuses on reliability and maintainability while leveraging Claude's capabilities for all Alfred operations.*