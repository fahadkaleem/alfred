"""Builds prompts using Python string formatting"""

from typing import Optional, List
from alfred.models.workflow import (
    Workflow,
    Phase,
    Persona,
    PhaseStep,
    WorkflowContext,
    Subagent,
)


class PromptBuilder:
    """Builds prompts preserving exact V1 structure without Jinja2"""

    def __init__(self, subagent_registry: Optional["SubagentRegistry"] = None):
        """
        Args:
            subagent_registry: Optional registry for subagent definitions
        """
        self.subagent_registry = subagent_registry

    def build_phase_prompt(
        self,
        phase: Phase,
        persona: Persona,
        context: WorkflowContext,
        subagents: Optional[List[Subagent]] = None,
    ) -> str:
        """
        Build phase execution prompt

        CRITICAL: Must generate EXACT same structure as V1
        """
        sections = []

        # 1. Header
        sections.append(f"# {phase.name}")

        # 2. Role
        sections.append(self._build_role_section(persona))

        # 3. Core Principles
        if persona.principles:
            sections.append(self._build_principles_section(persona))

        # 4. Goal
        sections.append(self._build_goal_section(phase))

        # 5. Current Task
        sections.append(f"## Current Task\nWorking on ticket: {context.task_id}")

        # 6. Previous Context (if needed)
        if context.need_context and context.previous_contexts:
            sections.append(self._build_context_section(context.previous_contexts))

        # 7. Available Specialized Assistance
        if subagents:
            sections.append(self._build_subagents_section(subagents))

        # 8. Execution Process with Hierarchical Todos
        sections.append(self._build_hierarchical_todos_section(phase))

        # 9. Context Management
        sections.append(self._build_context_management_section(phase))

        # 10. Quality Standards (always include - matches V1)
        sections.append(self._build_quality_standards_section(persona))

        # 11. Phase Completion
        sections.append(self._build_phase_completion_section())

        # Join sections with double newline
        return "\n\n".join(sections)

    def _build_role_section(self, persona: Persona) -> str:
        """Build role section"""
        lines = ["## Role", f"You are a {persona.role} with {persona.experience}."]
        return "\n".join(lines)

    def _build_principles_section(self, persona: Persona) -> str:
        """Build core principles section"""
        lines = ["## Core Principles"]
        for principle in persona.principles:
            lines.append(f"- {principle}")
        return "\n".join(lines)

    def _build_goal_section(self, phase: Phase) -> str:
        """Build goal section"""
        return f"## Goal\n{phase.goal}"

    def _build_context_section(self, previous_contexts: list[dict]) -> str:
        """Build previous context section"""
        lines = ["## Previous Context"]
        for ctx in previous_contexts:
            phase_name = ctx.get("phase", "Unknown")
            content = ctx.get("content", "")
            lines.append(f"### From {phase_name} phase:")
            lines.append(content)
        return "\n".join(lines)

    def _build_subagents_section(self, subagents: List[Subagent]) -> str:
        """Build available subagents section with full details - match V1 format exactly"""
        lines = [
            "## Available Specialized Assistance",
            "",
            "For complex tasks in this phase, you can delegate to specialized subagents:",
            "",
        ]

        for subagent in subagents:
            lines.append(f"**{subagent.id}**: {subagent.description}")
            lines.append(f"- **Use when**: {subagent.when_to_use}")
            lines.append(
                f'- **Command**: `Task(description="...", subagent_type="{subagent.claude_subagent}")`'
            )
            lines.append("")  # Empty line after command

            # Add example prompts if available - match V1 format with separate lines
            if subagent.example_prompts:
                lines.append("- **Example prompts**:")
                for example in subagent.example_prompts[:2]:  # Limit to 2 examples
                    lines.append(f'  - "{example}"')
                lines.append("")

        return "\n".join(lines)

    def _build_hierarchical_todos_section(self, phase: Phase) -> str:
        """
        Build hierarchical todos section
        CRITICAL: This MUST match V1 exactly
        """
        # Clean phase name for display (remove " Phase" if present)
        clean_phase = phase.name.replace(" Phase", "")

        lines = [
            "## Execution Process",
            "",
            "First, understand the hierarchical todo pattern:",
            'load_instructions("claude/todowrite")',
            "",
            "## Smart Todo Title Generation",
            "",
            "When creating subtasks, use this format:",
            f"- '[{clean_phase}] - Brief action description'",
            "- Keep titles concise (under 60 characters)",
            "- Focus on the specific action, not the process",
            "",
            "Examples:",
            f"- '[{clean_phase}] - Analyze existing implementation'",
            f"- '[{clean_phase}] - Extract requirements from ticket'",
            f"- '[{clean_phase}] - Create detailed task breakdown'",
            "",
            "## Create these subtasks under the current parent todo:",
            "",
        ]

        for i, step in enumerate(phase.steps, 1):
            # Build the X.N format line
            step_line = f"X.{i} **{step.name}**"

            # Add instruction reference if present
            if step.instruction:
                step_line += f' → load_instructions("{step.instruction}")'

            lines.append(step_line)

            # Add description and suggested title
            if step.description:
                lines.append(f"   {step.description}")
                lines.append(f"   Suggested title: '[{clean_phase}] - {step.name}'")

        lines.extend(
            [
                "",
                # TODO: CONFUSING - This appears to reference Task Master's numbering system, not Alfred's Linear integration
                "Replace X with the current parent todo number. For example, if the parent todo is #3, create subtasks as 3.1, 3.2, etc.",
                "",
                "Execute each subtask by:",
                "1. Create todo with smart title",
                "2. Mark as in_progress",
                "3. Load and follow instructions",
                "4. Mark as completed",
                "",
                "Only mark the parent phase todo as completed after ALL subtasks are done.",
            ]
        )

        return "\n".join(lines)

    def _build_context_management_section(self, phase: Phase) -> str:
        """Build context management section - match V1 exactly"""
        lines = [
            "## Context Management",
            f'IMPORTANT: Load the save_context instruction ONLY ONCE per conversation using: load_instructions("{phase.context_instruction}")',
            "After completing significant work (not every step), save context with the loaded instruction guidance.",
        ]
        return "\n".join(lines)

    def _build_quality_standards_section(self, persona: Persona) -> str:
        """Build quality standards section - match V1 format exactly"""
        lines = []

        # Always add Quality Standards header (V1 does this)
        lines.append("## Quality Standards")

        # Only add content if quality_standards exists and has items
        if persona.quality_standards:
            for standard, criteria in persona.quality_standards.items():
                lines.extend([f"### {standard}", str(criteria)])

        # Add Communication Style if it exists (with blank line separator)
        if persona.communication_style:
            lines.extend(["", "## Communication Style", persona.communication_style])

        return "\n".join(lines)

    def _build_phase_completion_section(self) -> str:
        """Build phase completion section - match V1 exactly"""
        lines = [
            "## Phase Completion",
            "- Complete all steps before marking phase as COMPLETE",
            '- Save final context with status="COMPLETE" ',  # Note: trailing space to match V1
            "- Provide clear next steps for user",
        ]
        return "\n".join(lines)

    def build_workflow_list_prompt(self, workflows: dict[str, Workflow]) -> str:
        """Build workflow list prompt"""
        lines = ["# Available Workflows", ""]

        for workflow_id, workflow in workflows.items():
            lines.append(f"## {workflow.name} ({workflow_id})")
            lines.append(f"**Goal**: {workflow.goal}")
            lines.append(f"**Phases**: {', '.join([p.name for p in workflow.phases])}")
            lines.append("")

        return "\n".join(lines)
