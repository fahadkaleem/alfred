"""Business logic for linking tasks with cycle detection."""

from typing import Dict, Any, Set, List
from alfred.adapters import get_adapter
from alfred.models.config import Config
from alfred.adapters.base import NotFoundError, ValidationError
from alfred.clients.linear.domain.enums import IssueRelationType
from .models import LinkTasksResult, TaskRelationship


def _detect_cycle(
    adapter,
    start_task_id: str,
    target_task_id: str,
    visited: Set[str],
    path: List[str],
) -> bool:
    """
    Detect if adding a relationship would create a cycle.

    Args:
        adapter: Adapter instance
        start_task_id: Current task in traversal
        target_task_id: Task we're looking for in the path
        visited: Set of visited task IDs
        path: Current path being traversed

    Returns:
        True if cycle would be created
    """
    if start_task_id == target_task_id:
        return True

    if start_task_id in visited:
        return False

    visited.add(start_task_id)
    path.append(start_task_id)

    try:
        relations = adapter.client.issues.get_relations(start_task_id)

        for relation in relations:
            if relation.type == IssueRelationType.BLOCKS and relation.relatedIssue:
                related_id = relation.relatedIssue.get("id")
                if related_id and _detect_cycle(
                    adapter, related_id, target_task_id, visited, path
                ):
                    return True

    except Exception:
        pass

    path.pop()
    return False


def link_tasks_logic(
    config: Config,
    blocker_task_id: str,
    blocked_task_id: str,
    relation_type: str = IssueRelationType.BLOCKS,
) -> Dict[str, Any]:
    """
    Create a blocking relationship between two tasks.

    Args:
        config: Alfred configuration object
        blocker_task_id: ID of task that will block
        blocked_task_id: ID of task that will be blocked
        relation_type: Type of relationship (blocks, relates, duplicates)

    Returns:
        LinkTasksResult as dict
    """
    adapter = get_adapter(config)

    if blocker_task_id == blocked_task_id:
        return LinkTasksResult(
            success=False, message="Task cannot block itself"
        ).model_dump(mode="json")

    try:
        blocker_task = adapter.get_task(blocker_task_id)
        blocked_task = adapter.get_task(blocked_task_id)

        # Get actual Linear issue UUIDs
        all_issues = adapter.client.issues.get_all()
        blocker_uuid = None
        blocked_uuid = None

        for issue_uuid, issue in all_issues.items():
            if issue.identifier == blocker_task_id:
                blocker_uuid = issue.id
            if issue.identifier == blocked_task_id:
                blocked_uuid = issue.id

        if not blocker_uuid or not blocked_uuid:
            return LinkTasksResult(
                success=False, message="Could not resolve task UUIDs"
            ).model_dump(mode="json")

    except NotFoundError as e:
        return LinkTasksResult(
            success=False, message=f"Task not found: {str(e)}"
        ).model_dump(mode="json")

    existing_relations = adapter.client.issues.get_relations(blocker_uuid)
    for relation in existing_relations:
        if (
            relation.type == relation_type
            and relation.relatedIssue
            and relation.relatedIssue.get("id") == blocked_uuid
        ):
            return LinkTasksResult(
                success=False,
                message=f"Relationship already exists between {blocker_task_id} and {blocked_task_id}",
            ).model_dump(mode="json")

    if relation_type == IssueRelationType.BLOCKS:
        visited = set()
        path = []
        if _detect_cycle(adapter, blocked_uuid, blocker_uuid, visited, path):
            return LinkTasksResult(
                success=False,
                message=f"Cannot create relationship: would create circular dependency",
            ).model_dump(mode="json")

    try:
        response = adapter.client.issues.create_relation(
            blocker_uuid, blocked_uuid, relation_type
        )

        if response.get("issueRelationCreate", {}).get("success"):
            relation_data = response["issueRelationCreate"]["issueRelation"]

            relationship = TaskRelationship(
                id=relation_data["id"],
                type=relation_data["type"],
                blocker_task_id=blocker_task_id,
                blocked_task_id=blocked_task_id,
                blocker_title=blocker_task.get("title", ""),
                blocked_title=blocked_task.get("title", ""),
            )

            return LinkTasksResult(
                success=True,
                message=f"Successfully linked tasks: {blocker_task['title']} now blocks {blocked_task['title']}",
                relationship=relationship,
                blocker_url=blocker_task.get("url"),
                blocked_url=blocked_task.get("url"),
            ).model_dump(mode="json")
        else:
            return LinkTasksResult(
                success=False, message="Failed to create relationship in Linear"
            ).model_dump(mode="json")

    except Exception as e:
        return LinkTasksResult(
            success=False, message=f"Error creating relationship: {str(e)}"
        ).model_dump(mode="json")
