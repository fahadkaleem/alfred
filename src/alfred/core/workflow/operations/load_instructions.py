"""Load instructions (tasks or checklists) by name.

This tool provides a simple interface for loading resources when agents
reference them in their instructions.
"""

from collections import defaultdict
from pathlib import Path

from alfred.models.workflow import ToolResponse


def _generate_fallback_instruction(name: str) -> str:
    """Generate a helpful fallback instruction when file is missing."""
    # Parse the instruction type from the path
    parts = name.split("/")
    category = parts[0] if len(parts) > 1 else "general"
    instruction_name = parts[-1]

    # Generate category-specific fallbacks
    if category == "development":
        return _development_fallback(instruction_name)
    if category == "jira":
        return _jira_fallback(instruction_name)
    if category == "common":
        return _common_fallback(instruction_name)
    if category == "planning":
        return _planning_fallback(instruction_name)
    if category == "review":
        return _review_fallback(instruction_name)
    if category == "testing":
        return _testing_fallback(instruction_name)
    return _generic_fallback(name)


def _development_fallback(instruction: str) -> str:
    """Fallback for development instructions."""
    if instruction == "create-branch":
        return """# Create Feature Branch

Create a feature branch for the current task:

1. Ensure you're on the main branch:
   ```bash
   git checkout main
   git pull origin main
   ```

2. Create and checkout new branch:
   ```bash
   git checkout -b feature/TASK-ID-brief-description
   ```

3. Example:
   ```bash
   git checkout -b feature/AV-123-add-oauth-support
   ```

Best practices:
- Include task ID in branch name
- Use kebab-case
- Keep description brief but clear"""

    if instruction == "push-changes":
        return """# Push Changes

Push your changes to the remote repository:

1. Add and commit changes:
   ```bash
   git add .
   git commit -m "feat: implement feature XYZ"
   ```

2. Push to remote:
   ```bash
   git push -u origin feature/TASK-ID-description
   ```

3. Create pull request:
   - Use GitHub/GitLab UI or CLI tools
   - Link to JIRA ticket
   - Add reviewers"""

    # Add other instruction fallbacks as needed
    return f"""# {instruction.replace("-", " ").title()}

No specific instructions available. Please proceed with standard {instruction.replace("-", " ")} practices.

General development workflow:
1. Review requirements
2. Plan implementation approach
3. Write clean, testable code
4. Follow project conventions
5. Test thoroughly"""


def _jira_fallback(instruction: str) -> str:
    """Fallback for JIRA instructions."""
    return f"""# {instruction.replace("-", " ").title()}

Use the Atlassian MCP tools to {instruction.replace("-", " ")}:

1. Get the Atlassian cloud ID if needed:
   ```
   mcp__atlassian__getAccessibleAtlassianResources()
   ```

2. Use the appropriate mcp__atlassian__ tool for your task

3. Handle any errors appropriately

Refer to Atlassian MCP documentation for specific tool usage."""


def _common_fallback(instruction: str) -> str:
    """Fallback for common instructions."""
    if instruction == "review-requirements":
        return """# Review Task Requirements

Thoroughly review the task requirements:

1. Read the JIRA ticket description
2. Check acceptance criteria
3. Review any attached documents
4. Note any ambiguities or questions
5. Identify technical constraints

Save important findings using save_context."""

    if instruction == "save-context":
        return """# Save Context

Save your work context using Alfred's save_context tool:

```
save_context(
    task_id="TASK-ID",
    phase="current-phase",
    content="Detailed description of work done...",
    status="IN_PROGRESS" or "COMPLETE",
    metadata={
        "step_completed": "step-name",
        "artifacts_created": [...],
        "key_decisions": [...]
    }
)
```

Always save context when:
- Completing a significant step
- Making important decisions
- Creating artifacts
- Finishing a phase"""

    return f"""# {instruction.replace("-", " ").title()}

Please proceed with {instruction.replace("-", " ")}.

General guidelines:
1. Follow project conventions
2. Document important decisions
3. Communicate clearly
4. Save context regularly"""


def _planning_fallback(instruction: str) -> str:
    """Fallback for planning instructions."""
    if instruction == "request-review":
        return """# Request Plan Review

Request review of your planning work:

1. Summarize the plan created
2. Highlight key decisions and trade-offs
3. List any open questions or concerns
4. Ask for specific feedback on:
   - Technical approach
   - Task breakdown
   - Time estimates
   - Risk areas

5. Save the plan as context with status="COMPLETE"

Example message:
"I've completed the planning phase for [TASK-ID]. The plan includes [summary].
Please review and let me know if you'd like any adjustments before I proceed with implementation.\""""

    return f"""# {instruction.replace("-", " ").title()}

Proceed with {instruction.replace("-", " ")} for the planning phase.

Planning phase guidelines:
1. Understand requirements thoroughly
2. Analyze existing code and patterns
3. Create detailed implementation plan
4. Break down into subtasks
5. Identify risks and dependencies"""


def _review_fallback(instruction: str) -> str:
    """Fallback for review instructions."""
    return f"""# {instruction.replace("-", " ").title()}

Conduct {instruction.replace("-", " ")}:

1. Check against acceptance criteria
2. Verify code quality and standards
3. Review test coverage
4. Validate documentation
5. Ensure all requirements are met

Document findings and save as context."""


def _testing_fallback(instruction: str) -> str:
    """Fallback for testing instructions."""
    return f"""# {instruction.replace("-", " ").title()}

Perform {instruction.replace("-", " ")}:

1. Write/update unit tests
2. Run existing test suite
3. Perform manual testing if needed
4. Verify edge cases
5. Document test results

Save test results and any issues found."""


def _generic_fallback(name: str) -> str:
    """Generic fallback for any instruction."""
    return f"""# {name.replace("-", " ").replace("/", " - ").title()}

This instruction file is not available. Please:

1. Check with your team for specific procedures
2. Follow project conventions
3. Use your best judgment

If this is a critical instruction, please report it to the Alfred maintainers.

You can continue with the task using general best practices for this type of work."""


async def load_instructions_logic(name: str) -> ToolResponse:
    """Load instructions by name from the centralized instructions folder.

    Instructions can be loaded by:
    1. Filename only: "check-progress" (searches for file)
    2. With subdirectory: "planner/check-progress" (direct path)

    Args:
        name: Name of the resource to load (e.g., "check-progress" or "planner/check-progress")

    Returns:
        ToolResponse with resource content

    """
    # Security: Validate name doesn't contain dangerous path elements
    if ".." in name or name.startswith(("/", "\\")):
        return ToolResponse.error(
            f"Invalid resource name '{name}': names cannot contain '..' or start with path separators"
        )

    # Additional validation: name should be a simple identifier
    if not name or name.startswith(".") or name.endswith("."):
        return ToolResponse.error(
            f"Invalid resource name '{name}': names cannot be empty or start/end with '.'"
        )

    # Get centralized instructions path
    instructions_root = Path(__file__).parent.parent / "prompts" / "instructions"

    # Build index of all instruction files (rebuild every time for immediate updates)
    file_index = defaultdict(list)
    if instructions_root.exists():
        for file in instructions_root.rglob("*.md"):
            filename = file.stem  # Without .md extension
            file_index[filename].append(file)

    # Function to load a file
    async def load_file(file_path: Path) -> ToolResponse:
        try:
            content = file_path.read_text(encoding="utf-8")

            # Return success with relative path for clarity
            relative_path = file_path.relative_to(instructions_root)
            return ToolResponse.success(
                message=f"Loaded '{name}' from instructions/{relative_path}",
                data={
                    "content": content,
                    "path": str(file_path),
                    "type": "instruction",
                },
            )
        except Exception as e:
            return ToolResponse.error(f"Failed to read '{name}': {e}")

    # Try direct path first (e.g., "planner/check-progress")
    if "/" in name:
        direct_path = instructions_root / f"{name}.md"
        if direct_path.exists():
            return await load_file(direct_path)

    # Try filename lookup in index
    name_without_ext = name.replace(".md", "")  # Remove .md if provided
    if name_without_ext in file_index:
        paths = file_index[name_without_ext]
        if len(paths) == 1:
            # Single match - load it
            return await load_file(paths[0])
        # Multiple matches - provide helpful error
        relative_paths = [str(p.relative_to(instructions_root)) for p in paths]
        return ToolResponse.error(
            f"Multiple files named '{name_without_ext}.md' found. Please specify the full path:\n"
            + "\n".join(f"  - {p}" for p in relative_paths)
            + "\n\nNote: Consider using unique filenames for better user experience.",
        )

    # Not found - generate fallback
    fallback_content = _generate_fallback_instruction(name)

    return ToolResponse.success(
        message=f"Generated fallback for '{name}' (instruction file not found)",
        data={
            "content": fallback_content,
            "path": f"fallback://{name}",
            "type": "instruction",
            "is_fallback": True,
        },
    )
