"""
Loads single YAML file with persona references
"""

from pathlib import Path
from typing import Dict, Optional
import yaml
from alfred.models.workflow import Workflow, Phase, Persona, PhaseStep


class WorkflowLoader:
    """Loads workflow definitions and resolves persona references"""

    def __init__(self, workflows_dir: Path, personas_dir: Path):
        """
        Args:
            workflows_dir: Path to workflows directory
            personas_dir: Path to personas directory
        """
        self.workflows_dir = workflows_dir
        self.personas_dir = personas_dir
        self._workflow_cache: Dict[str, Workflow] = {}
        self._persona_cache: Dict[str, Persona] = {}

    def load_workflow(self, workflow_id: str) -> Workflow:
        """
        Load a workflow from its YAML file

        Args:
            workflow_id: The workflow ID (e.g., "task", "tech_spec")

        Returns:
            Workflow model with all phases loaded
        """
        # Check cache first
        if workflow_id in self._workflow_cache:
            return self._workflow_cache[workflow_id]

        # Load from file
        workflow_file = self.workflows_dir / f"{workflow_id}.yaml"
        if not workflow_file.exists():
            raise FileNotFoundError(f"Workflow file not found: {workflow_file}")

        with workflow_file.open() as f:
            data = yaml.safe_load(f)

        if not data or "workflow" not in data:
            raise ValueError(f"Invalid workflow file: {workflow_file}")

        workflow = self._parse_workflow(data["workflow"])
        self._workflow_cache[workflow_id] = workflow
        return workflow

    def load_persona(self, persona_ref: str) -> Persona:
        """
        Load a persona from its YAML file

        Args:
            persona_ref: Reference to persona (e.g., "technical_planner")

        Returns:
            Persona model
        """
        # Check cache first
        if persona_ref in self._persona_cache:
            return self._persona_cache[persona_ref]

        # Load from file
        persona_file = self.personas_dir / f"{persona_ref}.yaml"
        if not persona_file.exists():
            return Persona.default()

        try:
            with persona_file.open() as f:
                data = yaml.safe_load(f)

            if not data or "persona" not in data:
                return Persona.default()

            persona = Persona.from_yaml_dict(data["persona"])
            self._persona_cache[persona_ref] = persona
            return persona

        except Exception:
            return Persona.default()

    def _parse_workflow(self, data: dict) -> Workflow:
        """Parse workflow data into Pydantic model"""
        phases = []
        for phase_data in data.get("phases", []):
            phase = self._parse_phase(phase_data)
            phases.append(phase)

        return Workflow(
            version=data.get("version", "2.0"),
            id=data.get("id", "unknown"),
            name=data.get("name", "Unnamed Workflow"),
            goal=data.get("goal", ""),
            create_task=data.get("create_task", False),
            defaults=data.get("defaults", {}),
            phases=phases,
        )

    def _parse_phase(self, data: dict) -> Phase:
        """Parse phase data into Pydantic model"""
        # Parse steps
        steps = []
        for step_data in data.get("steps", []):
            step = PhaseStep(
                name=step_data["name"],
                description=step_data.get("description", ""),
                instruction=step_data.get("instruction"),
                checkpoint=step_data.get("checkpoint", False),
                checkpoint_instruction=step_data.get(
                    "checkpoint_instruction", "checkpoints/generic-step"
                ),
            )
            steps.append(step)

        return Phase(
            id=data["id"],
            name=data["name"],
            goal=data.get("goal", ""),
            persona_ref=data.get("persona_ref", "default"),  # Reference, not embedded
            steps=steps,
            requires_review=data.get("requires_review", False),
            review_instruction=data.get("review_instruction", "review/generic-phase"),
            auto_checkpoint=data.get("auto_checkpoint", False),
            checkpoint_instruction=data.get(
                "checkpoint_instruction", "checkpoints/generic-phase"
            ),
            context_instruction=data.get("context_instruction", "common/save-context"),
            available_subagents=data.get("available_subagents", []),
        )

    def list_workflows(self) -> list[str]:
        """List all available workflow IDs"""
        return [f.stem for f in self.workflows_dir.glob("*.yaml")]
