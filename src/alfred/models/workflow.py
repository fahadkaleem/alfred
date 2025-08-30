"""
Pydantic models for workflow architecture
IMPORTANT: All models MUST be Pydantic BaseModel, no raw dicts allowed
"""

from typing import Optional, Any, Dict, List
from datetime import datetime
from pydantic import BaseModel, Field


class PhaseStep(BaseModel):
    """Single step within a phase"""

    name: str
    description: str = ""
    instruction: Optional[str] = (
        None  # Path to .md file, e.g., "planning/analyze-codebase"
    )
    checkpoint: bool = False
    checkpoint_instruction: str = "checkpoints/generic-step"

    def has_instruction(self) -> bool:
        """Check if step has an instruction file"""
        return self.instruction is not None and self.instruction != ""


class Phase(BaseModel):
    """Complete phase definition"""

    id: str
    name: str
    goal: str
    persona_ref: str  # Reference to persona file, e.g., "technical_planner"
    steps: list[PhaseStep]

    # Features
    requires_review: bool = False
    review_instruction: str = "review/generic-phase"
    auto_checkpoint: bool = False
    checkpoint_instruction: str = "checkpoints/generic-phase"

    # Context management
    context_instruction: str = "common/save-context"
    available_subagents: list[str] = Field(default_factory=list)


class Workflow(BaseModel):
    """Complete workflow definition"""

    version: str = "2.0"
    id: str
    name: str
    goal: str

    # Configuration
    create_task: bool = False
    defaults: dict[str, Any] = Field(default_factory=dict)

    # All phases defined inline
    phases: list[Phase]

    def get_phase(self, phase_id: str) -> Optional[Phase]:
        """Get phase by ID"""
        for phase in self.phases:
            if phase.id == phase_id:
                return phase
        return None

    def get_phase_sequence(self) -> list[str]:
        """Get ordered list of phase IDs"""
        return [phase.id for phase in self.phases]


class Persona(BaseModel):
    """AI persona configuration - loaded from separate files"""

    id: str
    role: str
    experience: str = ""
    principles: list[str] = Field(default_factory=list)
    traits: list[str] = Field(default_factory=list)
    communication_style: str = "Professional and helpful"
    quality_standards: dict[str, str] = Field(default_factory=dict)

    @classmethod
    def from_yaml_dict(cls, data: dict) -> "Persona":
        """Create from YAML dictionary"""
        return cls(**data)

    @classmethod
    def default(cls) -> "Persona":
        """Default persona when reference not found"""
        return cls(
            id="default",
            role="Claude Code",
            experience="an AI assistant helping you execute tasks efficiently",
            principles=[
                "Follow instructions precisely",
                "Ask for clarification when needed",
                "Complete tasks systematically",
                "Maintain clear communication",
            ],
        )


class Subagent(BaseModel):
    """Subagent definition from registry"""

    id: str
    claude_subagent: str  # Maps to Claude Code's subagent types
    description: str
    when_to_use: str
    example_prompts: list[str] = Field(default_factory=list)


class WorkflowContext(BaseModel):
    """Context for prompt generation"""

    task_id: str
    workflow_id: str
    phase_id: str
    need_context: bool = True
    previous_contexts: list[dict] = Field(default_factory=list)
    completed_phases: list[str] = Field(default_factory=list)


# Response models for WorkflowEngine methods
class ExecutePhaseResponse(BaseModel):
    """Response from execute_phase method"""

    prompt: str
    task_id: str
    phase: str
    workflow_id: str


class CompletePhaseResponse(BaseModel):
    """Response from complete_phase method"""

    task_id: str
    completed_phase: str
    completion_summary: str
    next_phase: Optional[str]
    next_phase_goal: Optional[str]
    is_next_review_phase: bool = False
    progress: str
    completed_phases: List[str]
    workflow_id: str
    workflow_complete: bool = False
    total_phases_completed: Optional[int] = None
    all_completed_phases: Optional[List[str]] = None


class GetProgressResponse(BaseModel):
    """Response from get_progress method"""

    task_id: str
    workflow_id: str
    workflow_name: str
    progress_percentage: int
    completed_phases: int
    total_phases: int
    current_phase: Optional[str]
    is_current_review_phase: bool
    overall_status: str
    completed_phase_list: List[str]
    started_phase_list: List[str]
    created_at: str
    has_contexts: bool


class GetNextPhaseResponse(BaseModel):
    """Response from get_next_phase method"""

    task_id: str
    workflow_id: str
    next_phase: str
    phase_status: str
    phase_goal: str
    is_review_phase: bool
    progress: str
    completed_phases: List[str]
    started_phases: List[str]


class ListWorkflowsResponse(BaseModel):
    """Response from list_available_workflows method"""

    workflows: Dict[str, Dict[str, Any]]
    prompt: str


class SaveContextResponse(BaseModel):
    """Response from save_context method"""

    task_id: str
    phase: str
    content: str
    status: str
    metadata: Optional[Dict[str, Any]] = None


class LoadContextResponse(BaseModel):
    """Response from load_context method"""

    task_id: str
    contexts: Dict[str, List[Dict[str, Any]]]
    phase_summaries: Dict[str, str]
    metadata: Dict[str, Any]


# Keep TaskState exactly as V1 for compatibility
class TaskState(BaseModel):
    """Task state - MUST match V1 exactly for compatibility"""

    task_id: str
    workflow_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_phases: list[str] = Field(default_factory=list)
    started_phases: list[str] = Field(default_factory=list)
    contexts: Dict[str, List[Dict[str, Any]]] = Field(default_factory=dict)
    artifacts: Dict[str, Any] = Field(default_factory=dict)
    pending_workflow: Optional[str] = None

    def mark_phase_started(self, phase: str) -> None:
        """Mark a phase as started"""
        if phase not in self.started_phases:
            self.started_phases.append(phase)
            self.updated_at = datetime.utcnow()

    def mark_phase_completed(self, phase: str) -> None:
        """Mark a phase as completed"""
        if phase not in self.completed_phases:
            self.completed_phases.append(phase)
            self.updated_at = datetime.utcnow()

    def add_context(
        self, phase: str, content: str, metadata: Optional[dict] = None
    ) -> None:
        """Add context entry for a phase"""
        if phase not in self.contexts:
            self.contexts[phase] = []

        entry = {
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {},
        }
        self.contexts[phase].append(entry)
        self.updated_at = datetime.utcnow()


# ToolResponse model for compatibility
class ToolResponse(BaseModel):
    """Standardized response from all MCP tools."""

    status: str = Field(..., description="success or error")
    message: str = Field(..., description="Human-readable message")
    next_prompt: str | None = Field(None, description="Next prompt for AI")
    data: dict[str, Any] | None = Field(None, description="Additional response data")

    @classmethod
    def success(
        cls,
        message: str,
        data: dict[str, Any] | None = None,
        next_prompt: str | None = None,
    ) -> "ToolResponse":
        """Create a success response."""
        return cls(
            status="success", message=message, next_prompt=next_prompt, data=data
        )

    @classmethod
    def error(
        cls,
        message: str,
        data: dict[str, Any] | None = None,
        next_prompt: str | None = None,
    ) -> "ToolResponse":
        """Create an error response."""
        return cls(status="error", message=message, next_prompt=next_prompt, data=data)


# Linear Workflow State models
class WorkflowState(BaseModel):
    """Linear workflow state representation"""

    id: str
    name: str
    type: str
    position: int = 0
    color: str = ""
    description: Optional[str] = None
    team_id: str
    team_name: str


class TeamWorkflowStates(BaseModel):
    """Workflow states for a specific team"""

    team_id: str
    team_name: str
    states: List[WorkflowState]


class WorkspaceWorkflowStates(BaseModel):
    """Workflow states for entire workspace"""

    workspace_id: str
    workspace_name: str
    teams: List[TeamWorkflowStates]


class WorkflowStateCache(BaseModel):
    """Cache for workflow states to avoid repeated API calls"""

    workspace_states: WorkspaceWorkflowStates
    last_updated: datetime
    expires_at: datetime
