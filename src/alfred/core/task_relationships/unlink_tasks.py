"""Business logic for unlinking tasks."""

from typing import Dict, Any, Optional
from alfred.adapters.linear_adapter import LinearAdapter
from alfred.adapters.base import NotFoundError
from .models import UnlinkTasksResult, TaskRelationship


def unlink_tasks_logic(
    api_key: str, task_id_1: str, task_id_2: str, relation_type: Optional[str] = None
) -> Dict[str, Any]:
    """
    Remove a relationship between two tasks.

    Args:
        api_key: Linear API key
        task_id_1: ID of first task
        task_id_2: ID of second task
        relation_type: Optional filter for specific relation type

    Returns:
        UnlinkTasksResult as dict
    """
    adapter = LinearAdapter(api_token=api_key)

    try:
        adapter.get_task(task_id_1)
        adapter.get_task(task_id_2)

        # Get actual Linear issue UUIDs
        all_issues = adapter.client.issues.get_all()
        task_uuid_1 = None
        task_uuid_2 = None

        for issue_uuid, issue in all_issues.items():
            if issue.identifier == task_id_1:
                task_uuid_1 = issue.id
            if issue.identifier == task_id_2:
                task_uuid_2 = issue.id

        if not task_uuid_1 or not task_uuid_2:
            return UnlinkTasksResult(
                success=False, message="Could not resolve task UUIDs"
            ).model_dump(mode="json")

    except NotFoundError as e:
        return UnlinkTasksResult(
            success=False, message=f"Task not found: {str(e)}"
        ).model_dump(mode="json")

    try:
        relations = adapter.client.issues.get_relations(task_uuid_1)
        relation_to_delete = None

        for relation in relations:
            if (
                relation.relatedIssue
                and relation.relatedIssue.get("id") == task_uuid_2
                and (relation_type is None or relation.type == relation_type)
            ):
                relation_to_delete = relation
                break

        if not relation_to_delete:
            inverse_relations = adapter.client.issues.get_inverse_relations(task_uuid_1)
            for relation in inverse_relations:
                if (
                    relation.relatedIssue
                    and relation.relatedIssue.get("id") == task_uuid_2
                    and (relation_type is None or relation.type == relation_type)
                ):
                    relation_to_delete = relation
                    break

        if not relation_to_delete:
            return UnlinkTasksResult(
                success=False,
                message=f"No relationship found between {task_id_1} and {task_id_2}",
            ).model_dump(mode="json")

        response = adapter.client.issues.delete_relation(relation_to_delete.id)

        if response.get("issueRelationDelete", {}).get("success"):
            removed_relationship = TaskRelationship(
                id=relation_to_delete.id,
                type=relation_to_delete.type,
                blocker_task_id=task_id_1,
                blocked_task_id=task_id_2,
            )

            return UnlinkTasksResult(
                success=True,
                message=f"Successfully removed relationship between {task_id_1} and {task_id_2}",
                removed_relationship=removed_relationship,
            ).model_dump(mode="json")
        else:
            return UnlinkTasksResult(
                success=False, message="Failed to delete relationship in Linear"
            ).model_dump(mode="json")

    except Exception as e:
        return UnlinkTasksResult(
            success=False, message=f"Error removing relationship: {str(e)}"
        ).model_dump(mode="json")
