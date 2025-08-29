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
        spec_content: str,
        num_tasks: int = 5,
        project_context: Optional[str] = None,
        research_mode: bool = False,
        is_claude_code: bool = False,
    ) -> Dict[str, Any]:
        """Render prompt for creating tasks from a specification.

        Args:
            spec_content: The specification content
            num_tasks: Number of tasks to generate
            project_context: Optional project context
            research_mode: Whether to enable research mode for enhanced analysis
            is_claude_code: Whether running in Claude Code environment

        Returns:
            Dict with system prompt, user prompt, and formatted messages
        """
        # TaskMaster-inspired system prompt with Alfred's identity
        research_section = ""
        if research_mode:
            research_section = """
Before breaking down the PRD into tasks, you will:
1. Research and analyze the latest technologies, libraries, frameworks, and best practices that would be appropriate for this project
2. Identify any potential technical challenges, security concerns, or scalability issues not explicitly mentioned in the PRD without discarding any explicit requirements or going overboard with complexity -- always aim to provide the most direct path to implementation, avoiding over-engineering or roundabout approaches
3. Consider current industry standards and evolving trends relevant to this project (this step aims to solve LLM hallucinations and out of date information due to training data cutoff dates)
4. Evaluate alternative implementation approaches and recommend the most efficient path
5. Include specific library versions, helpful APIs, and concrete implementation guidance based on your research
6. Always aim to provide the most direct path to implementation, avoiding over-engineering or roundabout approaches

Your task breakdown should incorporate this research, resulting in more detailed implementation guidance, more accurate dependency mapping, and more precise technology recommendations than would be possible from the PRD text alone, while maintaining all explicit requirements and best practices and all details and nuances of the PRD."""

        num_tasks_instruction = (
            f"approximately {num_tasks}"
            if num_tasks > 0
            else "an appropriate number of"
        )

        system = f"""You are Alfred, an AI assistant specialized in analyzing Product Requirements Documents (PRDs) and generating a structured, logically ordered, dependency-aware and sequenced list of development tasks in JSON format.{research_section}

Analyze the provided PRD content and generate {num_tasks_instruction} top-level development tasks. If the complexity or the level of detail of the PRD is high, generate more tasks relative to the complexity of the PRD.
Each task should represent a logical unit of work needed to implement the requirements and focus on the most direct and effective way to implement the requirements without unnecessary complexity or overengineering. Include pseudo-code, implementation details, and test strategy for each task. Find the most up to date information to implement each task.
Assign sequential IDs starting from 1. Infer title, description, details, and test strategy for each task based *only* on the PRD content.
Set status to 'pending', dependencies to an empty array [], and priority to 'medium' initially for all tasks.
Respond ONLY with a valid JSON object containing a single key "tasks", where the value is an array of task objects adhering to the provided schema. Do not include any explanation or markdown formatting."""

        context_section = ""
        if project_context:
            context_section = f"\n\nProject Context:\n{PromptTemplates.sanitize_text(project_context, 2000)}"

        claude_code_section = ""
        if is_claude_code:
            claude_code_section = """## IMPORTANT: Codebase Analysis Required

You have access to powerful codebase analysis tools. Before generating tasks:

1. Use the Glob tool to explore the project structure (e.g., "**/*.js", "**/*.json", "**/README.md")
2. Use the Grep tool to search for existing implementations, patterns, and technologies
3. Use the Read tool to examine key files like package.json, README.md, and main entry points
4. Analyze the current state of implementation to understand what already exists

Based on your analysis:
- Identify what components/features are already implemented
- Understand the technology stack, frameworks, and patterns in use
- Generate tasks that build upon the existing codebase rather than duplicating work
- Ensure tasks align with the project's current architecture and conventions

"""

        # Determine task count guidance
        task_count_guidance_prefix = (
            "Unless requirements warrant otherwise"
            if num_tasks > 0
            else "Depending on the requirements"
        )
        task_count_guidance = (
            f"exactly {num_tasks}" if num_tasks > 0 else "an appropriate number of"
        )

        user = f"""{
            claude_code_section
        }Here's the Product Requirements Document (PRD) to break down into {
            num_tasks_instruction
        } tasks:{
            ""
            if not research_mode
            else '''

Remember to thoroughly research current best practices and technologies before task breakdown to provide specific, actionable implementation details.'''
        }

{PromptTemplates.sanitize_text(spec_content, 8000)}
{context_section}

Each task should follow this JSON structure:
{{
    "id": number,
    "title": string,
    "description": string,
    "status": "pending",
    "dependencies": number[] (IDs of tasks this depends on),
    "priority": "high" | "medium" | "low",
    "details": string (implementation details),
    "testStrategy": string (validation approach),
    "acceptance_criteria": ["criterion 1", "criterion 2"],
    "technical_notes": string (implementation approach, libraries, patterns),
    "estimated_hours": number
}}

Guidelines:
1. {task_count_guidance_prefix}, create {
            task_count_guidance
        } tasks, numbered sequentially starting from 1
2. Each task should be atomic and focused on a single responsibility following the most up to date best practices and standards
3. Order tasks logically - consider dependencies and implementation sequence
4. Early tasks should focus on setup, core functionality first, then advanced features
5. Include clear validation/testing approach for each task
6. Set appropriate dependency IDs (a task can only depend on tasks with lower IDs)
7. Assign priority (high/medium/low) based on criticality and dependency order
8. Include detailed implementation guidance in the "details" field{
            ", with specific libraries and version recommendations based on your research"
            if research_mode
            else ""
        }
9. If the PRD contains specific requirements for libraries, database schemas, frameworks, tech stacks, or any other implementation details, STRICTLY ADHERE to these requirements in your task breakdown and do not discard them under any circumstance
10. Focus on filling in any gaps left by the PRD or areas that aren't fully specified, while preserving all explicit requirements
11. Always aim to provide the most direct path to implementation, avoiding over-engineering or roundabout approaches{
            f'''
12. For each task, include specific, actionable guidance based on current industry standards and best practices discovered through research'''
            if research_mode
            else ""
        }

Return your response in this format:
{{
    "tasks": [
        {{
            "id": 1,
            "title": "Setup Project Repository",
            "description": "...",
            ...
        }},
        ...
    ]
}}"""

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
