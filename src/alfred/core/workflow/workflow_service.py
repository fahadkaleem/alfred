from typing import List, Dict, Any, Optional

from alfred.tools.list_workflows import list_workflows_logic
from alfred.tools.describe_workflow import describe_workflow_logic
from alfred.tools.assign_workflow import assign_workflow_logic

from ..exceptions import WorkflowNotFoundException, ValidationException
from alfred.config import settings


class WorkflowService:
    async def list_workflows(self) -> List[Dict[str, Any]]:
        result = await list_workflows_logic()

        if result.status == "error":
            raise ValidationException(result.message)

        workflows = []
        workflow_details = result.data.get("workflow_details", {})

        for workflow_id, details in workflow_details.items():
            workflows.append(
                {
                    "id": workflow_id,
                    "name": details["name"],
                    "goal": details["goal"],
                    "phase_count": details["phase_count"],
                    "version": settings.default_workflow_version,
                }
            )

        return workflows

    async def get_workflow(self, workflow_id: str) -> Dict[str, Any]:
        result = await describe_workflow_logic(workflow_id)

        if result.status == "error":
            raise WorkflowNotFoundException(workflow_id)

        workflow_data = result.data

        return {
            "id": workflow_data["workflow_id"],
            "name": workflow_data["workflow_name"],
            "goal": workflow_data["workflow_goal"],
            "version": settings.default_workflow_version,
            "phases": workflow_data["phases"],
            "defaults": {},
            "create_task": workflow_data["creates_task"],
        }

    async def assign_workflow(
        self, workflow_id: str, task_id: Optional[str], force: bool
    ) -> Dict[str, Any]:
        result = await assign_workflow_logic(
            workflow_id=workflow_id, task_id=task_id, force=force
        )

        if result.status == "error":
            raise ValidationException(result.message)

        return result.data

    async def validate_workflow(self, workflow_id: str) -> Dict[str, Any]:
        result = await describe_workflow_logic(workflow_id)

        if result.status == "error":
            return {"valid": False, "errors": [result.message]}

        workflow_data = result.data
        validation_results = {
            "valid": True,
            "workflow_id": workflow_data["workflow_id"],
            "phase_count": workflow_data["phase_count"],
            "checks": {
                "has_phases": workflow_data["phase_count"] > 0,
                "phases_have_goals": all(
                    phase.get("goal") for phase in workflow_data["phases"]
                ),
                "phases_have_personas": all(
                    phase.get("persona") for phase in workflow_data["phases"]
                ),
            },
        }

        if not all(validation_results["checks"].values()):
            validation_results["valid"] = False

        return validation_results

    async def get_workflow_phases(self, workflow_id: str) -> List[Dict[str, Any]]:
        result = await describe_workflow_logic(workflow_id)

        if result.status == "error":
            raise WorkflowNotFoundException(workflow_id)

        return result.data.get("phases", [])
