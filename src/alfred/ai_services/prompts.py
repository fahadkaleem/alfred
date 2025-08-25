"""Prompt templates for AI operations.

This module provides reusable prompt templates that are provider-agnostic.
Templates focus on clear instructions and structured output formats.
"""

from typing import Dict, Any, List, Optional
import json
import re


class PromptTemplates:
    """Collection of prompt templates for various AI operations."""

    @staticmethod
    def sanitize_text(text: str, max_length: Optional[int] = None) -> str:
        """Sanitize and normalize text for use in prompts.

        Args:
            text: Text to sanitize
            max_length: Optional maximum length to truncate to

        Returns:
            Sanitized text
        """
        # Normalize whitespace
        text = re.sub(r"\s+", " ", text.strip())

        # Truncate if needed
        if max_length and len(text) > max_length:
            text = text[: max_length - 3] + "..."

        return text

    @staticmethod
    def format_messages(system: Optional[str], user: str) -> List[Dict[str, str]]:
        """Format system and user prompts into message list.

        Args:
            system: Optional system prompt
            user: User prompt

        Returns:
            List of message dictionaries
        """
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": user})
        return messages

    @staticmethod
    def render_create_tasks_from_spec(
        spec_content: str, num_tasks: int = 5, project_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Render prompt for creating tasks from a specification.

        Args:
            spec_content: The specification content
            num_tasks: Number of tasks to generate
            project_context: Optional project context

        Returns:
            Dict with system prompt, user prompt, and formatted messages
        """
        system = (
            "You are Alfred, an expert software project manager and engineer. "
            "You break down specifications into clear, actionable development tasks. "
            "Always respond with valid JSON matching the requested structure."
        )

        context_section = ""
        if project_context:
            context_section = f"\n\nProject Context:\n{PromptTemplates.sanitize_text(project_context, 1000)}"

        user = f"""Analyze this specification and create exactly {num_tasks} structured development tasks.

Specification:
{PromptTemplates.sanitize_text(spec_content, 8000)}
{context_section}

Requirements:
1. Create {num_tasks} clear, actionable tasks
2. Each task should be independently completable
3. Include detailed acceptance criteria
4. Consider logical dependencies between tasks
5. Assign appropriate priority levels
6. Estimate complexity (1-10 scale)
7. Be specific about technical implementation

Return as JSON array with EXACTLY {num_tasks} tasks:
[
  {{
    "title": "Clear, action-oriented title (e.g., 'Implement user authentication API')",
    "description": "Detailed description of what needs to be done and why",
    "acceptance_criteria": [
      "Specific, measurable criterion 1",
      "Specific, measurable criterion 2"
    ],
    "priority": "critical|high|medium|low",
    "complexity": 1-10,
    "estimated_hours": number,
    "dependencies": ["title of task this depends on"],
    "technical_notes": "Implementation approach, libraries to use, patterns to follow"
  }}
]"""

        return {
            "system": system,
            "user": user,
            "messages": PromptTemplates.format_messages(system, user),
        }

    @staticmethod
    def render_decompose_task(
        task: str, num_subtasks: int = 3, parent_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Render prompt for decomposing a task into subtasks.

        Args:
            task: Task description or JSON
            num_subtasks: Number of subtasks to generate
            parent_context: Optional context about parent task

        Returns:
            Dict with system prompt, user prompt, and formatted messages
        """
        system = (
            "You are an expert at task decomposition and work breakdown structures. "
            "You create specific, implementable subtasks that fully cover the parent task. "
            "Always respond with valid JSON."
        )

        context_section = ""
        if parent_context:
            context_section = f"\n\nAdditional Context:\n{PromptTemplates.sanitize_text(parent_context, 1000)}"

        # Handle both string and dict task input
        if isinstance(task, dict):
            task_info = f"Task: {task.get('title', 'Untitled')}\nDescription: {task.get('description', '')}"
        else:
            task_info = f"Task: {task}"

        user = f"""Break down this task into exactly {num_subtasks} detailed subtasks.

{task_info}
{context_section}

Create {num_subtasks} subtasks that:
1. Are specific and measurable
2. Can be completed independently or with clear dependencies
3. Cover all aspects of the parent task comprehensively
4. Include technical implementation details
5. Follow a logical execution order

Return as JSON array with EXACTLY {num_subtasks} subtasks:
[
  {{
    "title": "Specific subtask title",
    "description": "What needs to be done and how",
    "technical_details": "Step-by-step implementation approach",
    "dependencies": ["subtask this depends on (by title)"],
    "estimated_hours": number,
    "acceptance_criteria": ["Specific success criterion"]
  }}
]"""

        return {
            "system": system,
            "user": user,
            "messages": PromptTemplates.format_messages(system, user),
        }

    @staticmethod
    def render_assess_complexity(
        task: str, include_recommendations: bool = True
    ) -> Dict[str, Any]:
        """Render prompt for assessing task complexity.

        Args:
            task: Task or tasks to assess (string or JSON)
            include_recommendations: Whether to include decomposition recommendations

        Returns:
            Dict with system prompt, user prompt, and formatted messages
        """
        system = (
            "You are a technical lead with expertise in effort estimation and risk assessment. "
            "You provide accurate complexity assessments and actionable recommendations. "
            "Be conservative in your estimates. Always respond with valid JSON."
        )

        # Handle both single task and multiple tasks
        if isinstance(task, (list, dict)):
            task_info = json.dumps(task, indent=2)
        else:
            task_info = task

        recommendations_section = ""
        if include_recommendations:
            recommendations_section = """
5. Should this be decomposed? (boolean)
6. Recommended number of subtasks if decomposition needed
7. Decomposition strategy"""

        user = f"""Analyze the complexity of this task/these tasks and provide detailed assessment.

Task(s) to analyze:
{task_info}

Evaluate and provide:
1. Technical complexity score (1-10 scale)
2. Risk level (low/medium/high/critical)  
3. Estimated effort in hours
4. Required skills and expertise
{recommendations_section}

Return as JSON:
{{
  "complexity_score": 1-10,
  "risk_level": "low|medium|high|critical",
  "estimated_hours": number,
  "required_skills": ["skill1", "skill2"],
  "risk_factors": ["specific risk 1", "specific risk 2"],
  "complexity_reasoning": "Detailed explanation of complexity factors",
  "should_decompose": boolean,
  "recommended_subtasks": number or null,
  "decomposition_strategy": "How to break this down effectively" or null
}}"""

        return {
            "system": system,
            "user": user,
            "messages": PromptTemplates.format_messages(system, user),
        }

    @staticmethod
    def render_enhance_task(
        task: str, context: str, enhancement_type: str = "general"
    ) -> Dict[str, Any]:
        """Render prompt for enhancing a task with additional details.

        Args:
            task: Current task (string or JSON)
            context: Enhancement context or requirements
            enhancement_type: Type of enhancement (general, technical, testing, etc.)

        Returns:
            Dict with system prompt, user prompt, and formatted messages
        """
        system = (
            "You are a detail-oriented technical project manager. "
            "You enhance tasks with comprehensive information while maintaining clarity. "
            "Always preserve existing valid information and respond with valid JSON."
        )

        # Handle both string and dict task input
        if isinstance(task, dict):
            task_info = json.dumps(task, indent=2)
        else:
            task_info = task

        enhancement_focus = {
            "general": "overall clarity and completeness",
            "technical": "technical implementation details and architecture",
            "testing": "test strategy and quality assurance",
            "acceptance": "acceptance criteria and definition of done",
            "dependencies": "dependencies and integration points",
        }.get(enhancement_type, "overall improvement")

        user = f"""Enhance this task with additional details, focusing on {enhancement_focus}.

Current task:
{task_info}

Enhancement context:
{PromptTemplates.sanitize_text(context, 2000)}

Requirements:
1. Preserve all valid existing information
2. Add missing details based on the context
3. Improve clarity and specificity
4. Ensure technical accuracy
5. Add or refine acceptance criteria
6. Include edge cases and error handling considerations

Return the enhanced task as complete JSON with all fields:
{{
  "title": "Enhanced title if needed",
  "description": "Comprehensive description",
  "acceptance_criteria": ["Detailed criterion 1", "Detailed criterion 2"],
  "technical_details": "Implementation approach and patterns",
  "test_strategy": "How to test this effectively",
  "edge_cases": ["Edge case 1", "Edge case 2"],
  "dependencies": ["dependency 1"],
  "estimated_hours": number,
  "priority": "critical|high|medium|low",
  "complexity": 1-10
}}"""

        return {
            "system": system,
            "user": user,
            "messages": PromptTemplates.format_messages(system, user),
        }

    @staticmethod
    def render_research(
        query: str, context: str = "", detail_level: str = "medium"
    ) -> Dict[str, Any]:
        """Render prompt for research queries.

        Args:
            query: Research query
            context: Additional context
            detail_level: Level of detail (low, medium, high)

        Returns:
            Dict with system prompt, user prompt, and formatted messages
        """
        system = (
            "You are a knowledgeable technical researcher and architect. "
            "You provide accurate, practical insights with a focus on implementation. "
            "Always cite best practices and consider trade-offs."
        )

        detail_instructions = {
            "low": "Provide a concise summary with key points only.",
            "medium": "Provide a balanced explanation with examples.",
            "high": "Provide comprehensive analysis with detailed examples and edge cases.",
        }.get(detail_level, "Provide a thorough response.")

        context_section = ""
        if context:
            context_section = (
                f"\n\nContext:\n{PromptTemplates.sanitize_text(context, 2000)}"
            )

        user = f"""Research and provide insights on the following query:

Query: {query}
{context_section}

Requirements:
1. {detail_instructions}
2. Include practical, implementable recommendations
3. Consider best practices and industry standards
4. Identify potential pitfalls and how to avoid them
5. Provide code examples where relevant
6. Structure your response clearly with sections

Return as JSON:
{{
  "summary": "Brief overview of findings",
  "key_insights": ["Insight 1", "Insight 2"],
  "recommendations": ["Actionable recommendation 1", "Actionable recommendation 2"],
  "best_practices": ["Best practice 1", "Best practice 2"],
  "potential_issues": ["Issue to watch for", "Common pitfall"],
  "examples": ["Code or configuration example if relevant"],
  "references": ["Relevant documentation or resources"],
  "next_steps": ["Suggested action 1", "Suggested action 2"]
}}"""

        return {
            "system": system,
            "user": user,
            "messages": PromptTemplates.format_messages(system, user),
        }
