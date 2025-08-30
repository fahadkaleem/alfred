"""
Core workflow engine without MCP tool methods
Returns plain data/dicts, NOT ToolResponse
"""

from pathlib import Path
from typing import Dict, Optional, Any, List, Tuple
from datetime import datetime
import json
import logging

from alfred.models.workflow import (
    Workflow,
    Phase,
    WorkflowContext,
    Persona,
    PhaseStep,
    ExecutePhaseResponse,
    CompletePhaseResponse,
    GetProgressResponse,
    GetNextPhaseResponse,
    ListWorkflowsResponse,
    SaveContextResponse,
    LoadContextResponse,
)
from alfred.core.workflow.loader import WorkflowLoader
from alfred.core.workflow.prompt_builder import PromptBuilder
from alfred.core.workflow.subagent_registry import SubagentRegistry
from alfred.core.workflow.workflow_state_manager import WorkflowStateManager

logger = logging.getLogger(__name__)


class WorkflowEngine:
    """Core workflow engine that handles workflow logic"""

    def __init__(self, base_path: Path | None = None):
        """Initialize workflow engine with TaskManager integration"""
        self.base_path = base_path or Path.cwd() / ".alfred"
        self.prompts_dir = Path(__file__).parent.parent.parent / "prompts"
        self.workflows_dir = self.prompts_dir / "workflows"
        self.personas_dir = self.prompts_dir / "personas"
        self.subagents_dir = self.prompts_dir / "subagents"

        # Initialize components
        self.loader = WorkflowLoader(self.workflows_dir, self.personas_dir)
        self.subagent_registry = SubagentRegistry(self.subagents_dir / "registry.yaml")
        self.builder = PromptBuilder(self.subagent_registry)

        # Initialize workflow state manager
        self.state_manager = WorkflowStateManager(self.base_path)

        # Cache for loaded workflows
        self._workflows: Dict[str, Workflow] = {}

        # Run validation on startup
        self._validation_errors = self._validate_instruction_references()

    def _validate_task_id(self, task_id: str) -> None:
        """Validate task_id for security"""
        if not task_id:
            raise ValueError("task_id cannot be empty")
        if ".." in task_id or "/" in task_id or "\\" in task_id:
            raise ValueError(f"Invalid task_id: {task_id}")
        if len(task_id) > 255:
            raise ValueError(f"task_id too long: {task_id}")

    def execute_phase(
        self,
        task_id: str,
        phase: str,
        workflow_id: Optional[str] = None,
        need_context: bool = True,
    ) -> ExecutePhaseResponse:
        """Execute a workflow phase"""
        self._validate_task_id(task_id)
        logger.info(f"Executing phase {phase} for task {task_id}")

        state = self.state_manager.get_or_create_state(task_id)
        if not state:
            raise ValueError(f"Task {task_id} not found")

        # Get workflow ID
        if not workflow_id:
            workflow_id = state.workflow_id
        if not workflow_id:
            raise ValueError("No workflow assigned to this task")

        # Load workflow
        workflow = self._get_workflow(workflow_id)

        # Get phase
        phase_obj = workflow.get_phase(phase)
        if not phase_obj:
            # Check for dynamic review phase
            if phase.endswith("_review"):
                phase_obj = self._create_review_phase(phase, workflow)
            else:
                return {
                    "error": "phase_not_found",
                    "message": f"Phase '{phase}' not found",
                }

        # Load persona
        persona = self.loader.load_persona(phase_obj.persona_ref)

        # Apply dynamic steps
        completed_steps = self._get_completed_steps_from_task(state, phase)
        dynamic_steps = self._create_dynamic_steps(phase_obj, completed_steps)
        phase_obj.steps = dynamic_steps

        # Build context
        context = WorkflowContext(
            task_id=task_id,
            workflow_id=workflow_id,
            phase_id=phase,
            need_context=need_context,
            previous_contexts=self._get_previous_contexts(state)
            if need_context
            else [],
            completed_phases=state.completed_phases,
        )

        # Get subagents if specified
        subagents = None
        if phase_obj.available_subagents:
            subagents = self.subagent_registry.get_subagents(
                phase_obj.available_subagents
            )

        # Generate prompt
        prompt = self.builder.build_phase_prompt(phase_obj, persona, context, subagents)

        # Mark phase as started
        if phase not in state.started_phases:
            self.state_manager.mark_phase_started(task_id, phase)

        # Return Pydantic model
        return ExecutePhaseResponse(
            prompt=prompt, task_id=task_id, phase=phase, workflow_id=workflow_id
        )

    def save_context(
        self,
        task_id: str,
        phase: str,
        content: str,
        status: str = "IN_PROGRESS",
        metadata: Optional[dict] = None,
    ) -> SaveContextResponse:
        """Save context with artifact tracking"""
        state = self.state_manager.get_or_create_state(task_id)
        if not state:
            raise ValueError(f"Task {task_id} not found")

        # Save context
        self.state_manager.save_context(task_id, phase, content, metadata)

        # Track artifacts if present
        if metadata and "artifacts_created" in metadata:
            self._track_artifacts(task_id, state, metadata["artifacts_created"])

        # Handle phase completion
        if status == "COMPLETE":
            self.state_manager.mark_phase_completed(task_id, phase)

        return SaveContextResponse(
            task_id=task_id,
            phase=phase,
            content=content,
            status=status,
            metadata=metadata,
        )

    def load_context(
        self, task_id: str, phase: Optional[str] = None
    ) -> LoadContextResponse:
        """Load saved context"""
        state = self.state_manager.get_or_create_state(task_id)
        if not state:
            raise ValueError(f"Task {task_id} not found")

        contexts_data = self.state_manager.load_context(task_id, phase)

        if phase:
            contexts = contexts_data or []
        else:
            contexts = []
            for phase_name, phase_contexts in (contexts_data or {}).items():
                for ctx in phase_contexts:
                    ctx_with_phase = ctx.copy()
                    ctx_with_phase["phase"] = phase_name
                    contexts.append(ctx_with_phase)

        # Build phase summaries
        phase_summaries = {}
        for phase_name, phase_contexts in state.contexts.items():
            if phase_contexts:
                latest = phase_contexts[-1]
                phase_summaries[phase_name] = latest.content

        return LoadContextResponse(
            task_id=task_id,
            contexts={phase: contexts} if phase else state.contexts,
            phase_summaries=phase_summaries,
            metadata={"context_count": len(contexts)},
        )

    def search_contexts(
        self, task_id: str, query: str, phase: Optional[str] = None
    ) -> dict:
        """Search through saved contexts"""
        state = self.state_manager.get_or_create_state(task_id)
        if not state:
            return {
                "task_id": task_id,
                "query": query,
                "results_count": 0,
                "results": [],
            }

        results = []
        search_contexts = state.contexts.get(phase, []) if phase else []
        if not phase:
            for phase_name, phase_contexts in state.contexts.items():
                for ctx in phase_contexts:
                    ctx_with_phase = ctx.copy()
                    ctx_with_phase["phase"] = phase_name
                    search_contexts.append(ctx_with_phase)

        # Simple search implementation
        query_lower = query.lower()
        for ctx in search_contexts:
            # Handle both ContextEntry objects and dicts with phase info
            content = ctx.content if hasattr(ctx, "content") else ctx.get("content", "")
            if query_lower in content.lower():
                results.append(ctx)

        return {
            "task_id": task_id,
            "query": query,
            "results_count": len(results),
            "results": results,
        }

    def get_status(self, task_id: str) -> dict:
        """Get workflow status for a task"""
        state = self.state_manager.get_or_create_state(task_id)
        if not state:
            return {"task_id": task_id, "error": "Task not found"}

        return {
            "task_id": task_id,
            "workflow_id": state.workflow_id,
            "completed_phases": state.completed_phases,
            "started_phases": state.started_phases,
            "current_phase": self._get_current_phase(state),
            "progress_percentage": self._calculate_progress(state),
        }

    def get_artifacts(self, task_id: str) -> dict[str, Any]:
        """Get artifacts for a task"""
        state = self.state_manager.get_or_create_state(task_id)
        if not state:
            return {}
        return state.artifacts

    def get_phase_progress(self, task_id: str, phase: str) -> dict[str, Any]:
        """Get progress for a specific phase"""
        state = self.state_manager.get_or_create_state(task_id)
        if not state:
            return {"phase": phase, "error": "Task not found"}

        return {
            "phase": phase,
            "is_started": phase in state.started_phases,
            "is_completed": phase in state.completed_phases,
            "context_entries": len(state.contexts.get(phase, [])),
            "artifacts": [
                a
                for a in state.artifacts.get("tasks", {}).get("subtasks", [])
                if a.get("created_in_phase") == phase
            ],
        }

    def get_next_incomplete_phase(self, task_id: str) -> dict:
        """
        Get next phase to execute
        Returns data dict, not ToolResponse
        """
        state = self.state_manager.get_or_create_state(task_id)
        if not state:
            return {"error": "task_not_found", "message": f"Task {task_id} not found"}

        if not state.workflow_id:
            return {"error": "no_workflow", "message": "No workflow assigned"}

        workflow = self._get_workflow(state.workflow_id)

        # Get expanded sequence with dynamic reviews
        sequence = self.get_expanded_phase_sequence(
            state.workflow_id, state.completed_phases
        )

        # Find next incomplete phase
        for phase_name, is_review, original in sequence:
            if phase_name not in state.completed_phases:
                phase_obj = workflow.get_phase(phase_name)
                if not phase_obj and is_review:
                    phase_obj = self._create_review_phase(phase_name, workflow)

                return {
                    "next_phase": phase_name,
                    "is_review_phase": is_review,
                    "status": "ready",
                }

        return {"complete": True, "message": "All phases completed"}

    def get_expanded_phase_sequence(
        self, workflow_id: str, completed_phases: List[str]
    ) -> List[Tuple[str, bool, str]]:
        """
        Generate expanded phase sequence with dynamic review insertion

        Returns: List of (phase_name, is_review_phase, original_phase_name)
        """
        workflow = self._get_workflow(workflow_id)
        expanded = []

        for phase in workflow.phases:
            # Add regular phase
            expanded.append((phase.id, False, phase.id))

            # Check for dynamic review
            if phase.id in completed_phases and phase.requires_review:
                review_phase = f"{phase.id}_review"
                expanded.append((review_phase, True, phase.id))

        return expanded

    def get_full_phase_sequence(self, workflow_id: str) -> List[Tuple[str, bool, str]]:
        """
        Generate the full phase sequence including ALL potential review phases.
        This shows the complete workflow with all possible phases upfront.

        Returns: List of (phase_name, is_review_phase, original_phase_name)
        """
        workflow = self._get_workflow(workflow_id)
        expanded = []

        for phase in workflow.phases:
            # Add regular phase
            expanded.append((phase.id, False, phase.id))

            # Add review phase if this phase requires review
            if phase.requires_review:
                review_phase = f"{phase.id}_review"
                expanded.append((review_phase, True, phase.id))

        return expanded

    def mark_phase_complete(self, task_id: str, phase: str, summary: str) -> dict:
        """
        Mark phase as complete
        Returns data dict, not ToolResponse
        """
        state = self.state_manager.get_or_create_state(task_id)
        if not state:
            return {"error": "task_not_found", "message": f"Task {task_id} not found"}

        # Mark phase complete
        if phase not in state.completed_phases:
            self.state_manager.mark_phase_completed(task_id, phase)

        # Get next phase
        next_phase_info = self.get_next_incomplete_phase(task_id)

        return {
            "completed_phase": phase,
            "summary": summary,
            "next_phase_info": next_phase_info,
        }

    def list_workflows(self) -> Dict[str, Workflow]:
        """
        List all workflows - matches V1 naming
        Returns dict of workflow objects for consistency
        """
        workflow_ids = self.loader.list_workflows()
        workflows = {}

        for wf_id in workflow_ids:
            workflows[wf_id] = self._get_workflow(wf_id)

        return workflows

    def get_workflow_info(self, workflow_id: str) -> Optional[dict]:
        """Get information about a specific workflow"""
        try:
            workflow = self._get_workflow(workflow_id)
            return workflow.model_dump()
        except Exception:
            return None

    def list_available_workflows(self) -> dict:
        """
        List available workflows with metadata
        Returns data dict with prompt, not ToolResponse
        """
        workflows = self.list_workflows()
        prompt = self.builder.build_workflow_list_prompt(workflows)

        return {
            "workflow_ids": list(workflows.keys()),
            "workflows": {
                wf_id: {
                    "name": wf.name,
                    "goal": wf.goal,
                    "phases": [p.name for p in wf.phases],
                }
                for wf_id, wf in workflows.items()
            },
            "prompt": prompt,
        }

    def set_workflow(
        self, workflow_id: str, task_id: Optional[str] = None, force: bool = False
    ) -> dict:
        """
        Assign workflow to task
        Returns data dict, not ToolResponse
        """
        # Validate workflow exists
        try:
            workflow = self._get_workflow(workflow_id)
        except FileNotFoundError:
            return {
                "error": "workflow_not_found",
                "message": f"Workflow '{workflow_id}' not found",
            }

        if task_id:
            # Assign to specific task
            state = self.state_manager.get_or_create_state(task_id)
            if not state:
                return {
                    "error": "task_not_found",
                    "message": f"Task '{task_id}' not found",
                }

            if state.workflow_id and not force:
                return {
                    "error": "workflow_exists",
                    "message": f"Task already has workflow '{state.workflow_id}'",
                }

            self.state_manager.assign_workflow(task_id, workflow_id)

            return {"workflow_id": workflow_id, "task_id": task_id}
        else:
            # Store as pending
            self._save_pending_workflow(workflow_id)
            return {"workflow_id": workflow_id, "pending": True}

    # Private helper methods

    def _get_workflow(self, workflow_id: str) -> Workflow:
        """Get workflow, loading if needed"""
        if workflow_id not in self._workflows:
            self._workflows[workflow_id] = self.loader.load_workflow(workflow_id)
        return self._workflows[workflow_id]

    def _get_previous_contexts(self, state) -> List[dict]:
        """Get previous phase contexts from state"""
        contexts = []
        for phase_name, phase_contexts in state.contexts.items():
            for ctx in phase_contexts:
                contexts.append(
                    {
                        "phase": phase_name,
                        "content": ctx["content"],
                        "timestamp": ctx["timestamp"],
                    }
                )
        return contexts

    def _create_dynamic_steps(
        self, phase: Phase, completed_steps: List[str]
    ) -> List[PhaseStep]:
        """Create dynamic steps with checkpoints"""
        dynamic_steps = []

        for step in phase.steps:
            # Add original step
            dynamic_steps.append(step)

            # Add checkpoint if step has checkpoint enabled and is completed
            if step.checkpoint and step.name in completed_steps:
                checkpoint_step = PhaseStep(
                    name=f"Save {step.name} checkpoint",
                    description=f"Save context for completed {step.name} step",
                    instruction=step.checkpoint_instruction,
                    checkpoint=False,  # Don't recurse
                )
                dynamic_steps.append(checkpoint_step)

        # Add phase-level checkpoint if enabled
        if phase.auto_checkpoint:
            checkpoint_step = PhaseStep(
                name=f"Save {phase.name} context",
                description=f"Save comprehensive context for completed {phase.name} phase",
                instruction=phase.checkpoint_instruction,
                checkpoint=False,
            )
            dynamic_steps.append(checkpoint_step)

        return dynamic_steps

    def _create_review_phase(self, phase_name: str, workflow: Workflow) -> Phase:
        """Create dynamic review phase (exactly like V1)"""
        # Find original phase
        original_name = phase_name.replace("_review", "")
        original = workflow.get_phase(original_name)

        if not original:
            return None

        # Create review phase
        return Phase(
            id=phase_name,
            name=f"{original.name} Review",
            goal=f"Review the {original.name.lower()} phase implementation",
            persona_ref="qa_engineer",  # Use QA persona for reviews
            steps=[
                PhaseStep(
                    name="Review implementation",
                    description="Review what was implemented",
                    instruction=original.review_instruction,
                )
            ],
            context_instruction=original.context_instruction,
            available_subagents=["code-reviewer"],
        )

    def _track_artifacts(self, task_id: str, state, artifacts: List[dict]) -> None:
        """Track artifacts created during phases"""
        if "tasks" not in state.artifacts:
            state.artifacts["tasks"] = {"subtasks": []}

        for artifact in artifacts:
            artifact["created_at"] = datetime.utcnow().isoformat()
            state.artifacts["tasks"]["subtasks"].append(artifact)

        # Save updated task
        self.state_manager._save_storage()

    def _save_pending_workflow(self, workflow_id: str) -> None:
        """Save pending workflow assignment"""
        pending_file = self.base_path / "pending_workflow.json"

        data = {"workflow_id": workflow_id}

        with pending_file.open("w") as f:
            json.dump(data, f, indent=2)

    def _get_and_clear_pending_workflow(self) -> Optional[str]:
        """Get and clear pending workflow"""
        pending_file = self.base_path / "pending_workflow.json"

        if not pending_file.exists():
            return None

        try:
            with pending_file.open() as f:
                data = json.load(f)

            workflow_id = data.get("workflow_id")
            pending_file.unlink()  # Delete file
            return workflow_id
        except Exception:
            return None

    def _get_completed_steps_from_task(self, state, phase: str) -> List[str]:
        """Get completed steps for a phase from state"""
        completed_steps = []

        # Check metadata in contexts for completed steps
        if phase in state.contexts:
            for ctx in state.contexts[phase]:
                metadata = ctx.get("metadata", {})
                if "step_completed" in metadata:
                    completed_steps.append(metadata["step_completed"])

        return completed_steps

    def _validate_instruction_references(self) -> List[str]:
        """Validate all instruction references exist"""
        errors = []
        instructions_dir = self.prompts_dir / "instructions"

        # Check all workflows
        for workflow_id in self.loader.list_workflows():
            try:
                workflow = self._get_workflow(workflow_id)

                for phase in workflow.phases:
                    for step in phase.steps:
                        if step.instruction:
                            instruction_file = (
                                instructions_dir / f"{step.instruction}.md"
                            )
                            if not instruction_file.exists():
                                errors.append(
                                    f"Missing instruction: {step.instruction} "
                                    f"(workflow: {workflow_id}, phase: {phase.id}, step: {step.name})"
                                )
            except Exception as e:
                errors.append(f"Error validating workflow {workflow_id}: {e}")

        return errors

    def get_validation_report(self) -> dict[str, List[str]]:
        """Get validation report"""
        return {
            "instruction_errors": self._validation_errors,
            "workflows_loaded": list(self._workflows.keys()),
            "personas_loaded": list(self.loader._persona_cache.keys()),
            "subagents_loaded": list(self.subagent_registry._registry.keys()),
        }

    def _get_current_phase(self, state) -> Optional[str]:
        """Get current phase being worked on"""
        if not state.workflow_id:
            return None

        # Get the last started but not completed phase
        for phase in reversed(state.started_phases):
            if phase not in state.completed_phases:
                return phase

        return None

    def _calculate_progress(self, state) -> float:
        """Calculate progress percentage"""
        if not state.workflow_id:
            return 0.0

        try:
            workflow = self._get_workflow(state.workflow_id)
            total_phases = len(workflow.phases)

            if total_phases == 0:
                return 0.0

            completed_count = len(state.completed_phases)
            return (completed_count / total_phases) * 100
        except Exception:
            return 0.0
