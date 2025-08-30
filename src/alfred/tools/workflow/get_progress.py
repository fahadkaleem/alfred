"""MCP tool wrapper for get_progress."""

from alfred.mcp import mcp
from alfred.core.workflow.operations.get_progress import get_progress_logic


@mcp.tool
async def get_progress(task_id: str) -> dict:
    """Display comprehensive workflow progress and status overview for a task.

    - Provides complete visibility into task progress across all workflow phases
    - Shows detailed completion status, timeline, and accomplishments
    - Essential for project management and progress tracking
    - Useful for team coordination and status reporting
    - Identifies bottlenecks and workflow health issues

    Parameters
    task_id [string] (required) - The task to analyze progress for:
        - External task keys: "PROJ-123", "AL-456"
        - Local Alfred tasks: AL-1, AL-2, AL-3, etc.
        - Must be valid existing task with workflow assigned

    Usage scenarios:
    - Progress review: Checking current status and recent accomplishments
    - Team coordination: Sharing status updates and completion estimates
    - Project management: Tracking deliverables and timeline adherence
    - Workflow troubleshooting: Identifying stuck phases or process issues
    - Planning: Understanding remaining work and resource requirements

    Progress analysis:
    - Phase-by-phase completion status with timestamps
    - Overall workflow completion percentage
    - Time spent in each phase and total elapsed time
    - Quality of phase completion and deliverable status
    - Identification of bottlenecks and delayed phases

    Returns
        ToolResponse with comprehensive progress data:
        - overall_progress: Workflow completion percentage and status
        - phase_status: Detailed status of each workflow phase
        - completed_phases: Summaries and accomplishments from finished phases
        - current_phase: Active phase with progress and next steps
        - timeline_data: Start times, durations, and estimated completion
        - workflow_health: Assessment of progress quality and potential issues
        - recommendations: Suggested actions for improving progress

    Phase status indicators:
    - "not_started" - Phase not yet begun
    - "in_progress" - Currently active phase with work underway
    - "completed" - Phase finished with saved context and deliverables
    - "blocked" - Phase cannot proceed due to dependencies or issues
    - "review_required" - Phase needs review before completion

    Examples
        # Check overall task progress
        get_progress("PROJ-123")

        # Review team member's work status
        get_progress("AL-456")

        # Assess project timeline
        get_progress("TASK-789")

    Workflow insights:
    - Completion velocity and phase duration patterns
    - Quality assessment based on context richness
    - Bottleneck identification and resolution suggestions
    - Resource allocation and effort distribution analysis
    - Timeline predictions and completion estimates

    Integration capabilities:
    - Data suitable for project dashboards and reporting
    - Compatible with external task tracking
    - Supports team standup and review meetings
    - Enables workflow optimization and process improvement

    Error conditions:
    - Task not found or invalid task ID
    - Task has no assigned workflow
    - Workflow state corruption or missing data
    - Storage access failures or permission issues

    """
    result = await get_progress_logic(task_id)
    return result.model_dump()
