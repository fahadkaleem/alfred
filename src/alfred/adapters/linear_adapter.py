"""Linear GraphQL API adapter implementation."""

import os
from typing import Dict, List, Optional, Any, Union

from alfred.clients.linear import (
    LinearClient,
    LinearIssueInput,
    LinearIssueUpdateInput,
    LinearPriority,
)

from .base import (
    TaskAdapter,
    TaskDict,
    EpicDict,
    AdapterError,
    AuthError,
    NotFoundError,
    ValidationError,
    RateLimitError,
    APIConnectionError,
    APIResponseError,
    MappingError,
)


class LinearAdapter(TaskAdapter):
    """Linear GraphQL API adapter using linear-api library."""

    def __init__(
        self,
        api_token: Optional[str] = None,
        team_name: Optional[str] = None,
        default_project_name: Optional[str] = None,
    ):
        """Initialize Linear adapter.

        Args:
            api_token: Linear API token (or from LINEAR_API_KEY env var)
            team_name: Default team name for operations
            default_project_name: Default project name for task creation
        """
        # Get token from parameter or environment
        token = api_token or os.getenv("LINEAR_API_KEY")
        if not token:
            raise AuthError(
                "Linear API key is required. Set LINEAR_API_KEY environment variable or pass api_token parameter."
            )

        try:
            self.client = LinearClient(api_key=token)
            self.team_name = team_name or os.getenv("LINEAR_TEAM_NAME", "Default Team")
            self.default_project_name = default_project_name or os.getenv(
                "LINEAR_DEFAULT_PROJECT_NAME"
            )
        except Exception as e:
            raise APIConnectionError(f"Failed to initialize Linear client: {e}")

    def _map_linear_issue_to_task(self, issue) -> TaskDict:
        """Map Linear Issue to normalized TaskDict.

        Args:
            issue: LinearIssue object

        Returns:
            Normalized TaskDict
        """
        task: TaskDict = {
            "id": issue.identifier or issue.id,
            "title": issue.title,
            "description": issue.description,
            "status": issue.state.name if issue.state else None,
            "epic_id": issue.project.id if issue.project else None,
            "parent_id": issue.parentId if issue.parentId else None,
            "url": issue.url,
            "created_at": issue.createdAt.isoformat() if issue.createdAt else None,
            "updated_at": issue.updatedAt.isoformat() if issue.updatedAt else None,
        }
        return task

    def _map_linear_project_to_epic(self, project) -> EpicDict:
        """Map Linear Project to normalized EpicDict.

        Args:
            project: LinearProject object

        Returns:
            Normalized EpicDict
        """
        epic: EpicDict = {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "url": project.url if project.url else None,
            "created_at": project.createdAt.isoformat() if project.createdAt else None,
            "updated_at": project.updatedAt.isoformat() if project.updatedAt else None,
        }
        return epic

    def _normalize_status_filter(
        self, status: Optional[Union[str, List[str]]]
    ) -> Optional[List[str]]:
        """Normalize status filter to a list of strings.

        Args:
            status: Single status or list of statuses

        Returns:
            List of status strings or None
        """
        if status is None:
            return None
        if isinstance(status, str):
            return [status]
        return status

    def _map_priority(self, priority: Optional[str]) -> LinearPriority:
        """Map string priority to LinearPriority enum.

        Args:
            priority: Priority string (low, medium, high, urgent)

        Returns:
            LinearPriority enum value
        """
        if not priority:
            return LinearPriority.MEDIUM

        priority_map = {
            "low": LinearPriority.LOW,
            "medium": LinearPriority.MEDIUM,
            "high": LinearPriority.HIGH,
            "urgent": LinearPriority.URGENT,
            "critical": LinearPriority.URGENT,
        }

        return priority_map.get(priority.lower(), LinearPriority.MEDIUM)

    def create_task(
        self,
        title: str,
        description: Optional[str] = None,
        epic_id: Optional[str] = None,
    ) -> TaskDict:
        """Create a new task in Linear.

        Args:
            title: Task title
            description: Task description
            epic_id: Project ID to add the task to

        Returns:
            Created task as TaskDict
        """
        if not title:
            raise ValidationError("Task title cannot be empty")

        try:
            # Prepare input for Linear API
            input_data = LinearIssueInput(
                title=title,
                description=description or "",
                teamName=self.team_name,
                priority=LinearPriority.MEDIUM,
                projectId=epic_id if epic_id else None,
                projectName=self.default_project_name if not epic_id else None,
            )

            # Create issue in Linear
            issue = self.client.issues.create(input_data)

            if not issue:
                raise APIResponseError("Failed to create issue in Linear")

            return self._map_linear_issue_to_task(issue)

        except (AuthError, ValidationError, APIResponseError):
            raise
        except Exception as e:
            error_str = str(e)
            if "401" in error_str or "unauthorized" in error_str.lower():
                raise AuthError(f"Authentication failed: {e}")
            elif "rate" in error_str.lower():
                raise RateLimitError(f"Rate limit exceeded: {e}")
            elif "network" in error_str.lower() or "connection" in error_str.lower():
                raise APIConnectionError(f"Network error: {e}")
            else:
                raise APIResponseError(f"Linear API error: {e}")

    def get_tasks(
        self,
        epic_id: Optional[str] = None,
        status: Optional[Union[str, List[str]]] = None,
        limit: int = 50,
    ) -> List[TaskDict]:
        """Get tasks from Linear with optional filtering.

        Args:
            epic_id: Filter by project ID (not directly supported, would need project name)
            status: Filter by status name(s)
            limit: Maximum number of tasks

        Returns:
            List of tasks as TaskDict objects
        """
        try:
            # Get all issues from the default team
            issues_by_team = self.client.issues.get_by_team(self.team_name)

            # Convert to list and apply filters
            tasks = []
            status_list = self._normalize_status_filter(status)

            for issue_id, issue in issues_by_team.items():
                # Apply status filter if provided
                if status_list and issue.state:
                    if issue.state.name not in status_list:
                        continue

                # Apply project filter if provided
                if epic_id and issue.project:
                    if issue.project.id != epic_id:
                        continue

                tasks.append(self._map_linear_issue_to_task(issue))

                if len(tasks) >= limit:
                    break

            return tasks

        except Exception as e:
            error_str = str(e)
            if "401" in error_str or "unauthorized" in error_str.lower():
                raise AuthError(f"Authentication failed: {e}")
            elif "rate" in error_str.lower():
                raise RateLimitError(f"Rate limit exceeded: {e}")
            elif "network" in error_str.lower() or "connection" in error_str.lower():
                raise APIConnectionError(f"Network error: {e}")
            else:
                raise APIResponseError(f"Linear API error: {e}")

    def get_task(self, task_id: str) -> TaskDict:
        """Get a specific task by ID.

        Args:
            task_id: Task identifier (e.g., "TASK-123")

        Returns:
            Task as TaskDict
        """
        try:
            # Get all issues and find by identifier
            all_issues = self.client.issues.get_all()

            for issue_id, issue in all_issues.items():
                if issue.identifier == task_id:
                    return self._map_linear_issue_to_task(issue)

            raise NotFoundError(f"Task {task_id} not found")

        except NotFoundError:
            raise
        except Exception as e:
            error_str = str(e)
            if "401" in error_str or "unauthorized" in error_str.lower():
                raise AuthError(f"Authentication failed: {e}")
            elif "not found" in error_str.lower() or "404" in error_str:
                raise NotFoundError(f"Task {task_id} not found")
            elif "network" in error_str.lower() or "connection" in error_str.lower():
                raise APIConnectionError(f"Network error: {e}")
            else:
                raise APIResponseError(f"Linear API error: {e}")

    def update_task(self, task_id: str, updates: Dict[str, Any]) -> TaskDict:
        """Update a task with new values.

        Args:
            task_id: Task identifier
            updates: Fields to update (title, description, status)

        Returns:
            Updated task as TaskDict
        """
        try:
            # Find the issue by identifier or ID
            all_issues = self.client.issues.get_all()
            target_issue = None

            for issue_id, issue in all_issues.items():
                # Check both identifier (like "AL-146") and UUID
                if issue.identifier == task_id or issue.id == task_id:
                    target_issue = issue
                    break

            if not target_issue:
                raise NotFoundError(f"Task {task_id} not found")

            # Prepare update input
            update_input = {}

            if "title" in updates:
                update_input["title"] = updates["title"]

            if "description" in updates:
                update_input["description"] = updates["description"]

            if "status" in updates:
                update_input["stateName"] = updates["status"]

            # Update the issue - the linear-api library expects a model-like object
            update_obj = LinearIssueUpdateInput(**update_input)
            updated_issue = self.client.issues.update(target_issue.id, update_obj)

            if not updated_issue:
                raise APIResponseError("Failed to update issue in Linear")

            return self._map_linear_issue_to_task(updated_issue)

        except (NotFoundError, ValidationError):
            raise
        except Exception as e:
            error_str = str(e)
            if "401" in error_str or "unauthorized" in error_str.lower():
                raise AuthError(f"Authentication failed: {e}")
            elif "not found" in error_str.lower() or "404" in error_str:
                raise NotFoundError(f"Task {task_id} not found")
            elif "network" in error_str.lower() or "connection" in error_str.lower():
                raise APIConnectionError(f"Network error: {e}")
            else:
                raise APIResponseError(f"Linear API error: {e}")

    def create_subtask(
        self, parent_id: str, title: str, description: Optional[str] = None
    ) -> TaskDict:
        """Create a subtask under a parent task.

        Args:
            parent_id: Parent task ID (identifier like "TASK-123")
            title: Subtask title
            description: Subtask description

        Returns:
            Created subtask as TaskDict
        """
        if not title:
            raise ValidationError("Subtask title cannot be empty")

        try:
            # Find parent issue
            all_issues = self.client.issues.get_all()
            parent_issue = None

            for issue_id, issue in all_issues.items():
                if issue.identifier == parent_id:
                    parent_issue = issue
                    break

            if not parent_issue:
                raise NotFoundError(f"Parent task {parent_id} not found")

            # Create subtask with parent ID
            input_data = LinearIssueInput(
                title=title,
                description=description or "",
                teamName=self.team_name,
                parentId=parent_issue.id,  # Use the internal ID for parent
                priority=LinearPriority.MEDIUM,
            )

            # If parent has a project, use it
            if parent_issue.project:
                input_data.projectName = parent_issue.project.name

            subtask = self.client.issues.create(input_data)

            if not subtask:
                raise APIResponseError("Failed to create subtask in Linear")

            return self._map_linear_issue_to_task(subtask)

        except (NotFoundError, ValidationError):
            raise
        except Exception as e:
            error_str = str(e)
            if "401" in error_str or "unauthorized" in error_str.lower():
                raise AuthError(f"Authentication failed: {e}")
            elif "not found" in error_str.lower() or "404" in error_str:
                raise NotFoundError(f"Parent task {parent_id} not found")
            elif "network" in error_str.lower() or "connection" in error_str.lower():
                raise APIConnectionError(f"Network error: {e}")
            else:
                raise APIResponseError(f"Linear API error: {e}")

    def get_task_children(self, parent_id: str) -> List[TaskDict]:
        """Get all subtasks of a parent task.

        Args:
            parent_id: Parent task ID (identifier like "TASK-123")

        Returns:
            List of child tasks
        """
        # Get all issues and filter for those with this parent
        all_issues = self.client.issues.get_all()

        # Find parent issue first to get its internal ID
        parent_issue = None
        for issue_id, issue in all_issues.items():
            if issue.identifier == parent_id:
                parent_issue = issue
                break

        if not parent_issue:
            raise NotFoundError(f"Parent task not found: {parent_id}")

        # Find all issues that have this parent
        children = []
        for issue_id, issue in all_issues.items():
            if issue.parentId == parent_issue.id:
                children.append(self._map_linear_issue_to_task(issue))

        return children

    def delete_task(self, task_id: str) -> bool:
        """Delete a task.

        Args:
            task_id: Task identifier

        Returns:
            True if deletion was successful
        """
        try:
            # Find the issue
            all_issues = self.client.issues.get_all()
            target_issue = None

            for issue_id, issue in all_issues.items():
                if issue.identifier == task_id:
                    target_issue = issue
                    break

            if not target_issue:
                raise NotFoundError(f"Task {task_id} not found")

            # Delete the issue
            self.client.issues.delete(target_issue.id)

            return True

        except NotFoundError:
            raise
        except Exception as e:
            error_str = str(e)
            if "401" in error_str or "unauthorized" in error_str.lower():
                raise AuthError(f"Authentication failed: {e}")
            elif "not found" in error_str.lower() or "404" in error_str:
                raise NotFoundError(f"Task {task_id} not found")
            elif "network" in error_str.lower() or "connection" in error_str.lower():
                raise APIConnectionError(f"Network error: {e}")
            else:
                raise APIResponseError(f"Linear API error: {e}")

    def create_epic(self, name: str, description: Optional[str] = None) -> EpicDict:
        """Create a new epic (project in Linear).

        Args:
            name: Epic/project name
            description: Epic/project description

        Returns:
            Created epic as EpicDict
        """
        if not name:
            raise ValidationError("Epic name cannot be empty")

        try:
            # Use LinearClient's ProjectManager to create the project
            project = self.client.projects.create(
                name=name.strip(), team_name=self.team_name, description=description
            )

            # Transform LinearProject to EpicDict
            return self._map_linear_project_to_epic(project)

        except ValidationError:
            raise
        except Exception as e:
            error_str = str(e)
            if "401" in error_str or "unauthorized" in error_str.lower():
                raise AuthError(f"Authentication failed: {e}")
            elif "network" in error_str.lower() or "connection" in error_str.lower():
                raise APIConnectionError(f"Network error: {e}")
            else:
                raise APIResponseError(f"Linear API error: {e}")

    def get_epics(self, limit: int = 50) -> List[EpicDict]:
        """Get list of epics (projects in Linear).

        Args:
            limit: Maximum number of epics to return

        Returns:
            List of epics as EpicDict objects
        """
        try:
            # Get projects from Linear
            projects = self.client.projects.get_all()

            # Map to EpicDict
            epics = []
            for project_id, project in projects.items():
                epics.append(self._map_linear_project_to_epic(project))

                if len(epics) >= limit:
                    break

            return epics

        except Exception as e:
            error_str = str(e)
            if "401" in error_str or "unauthorized" in error_str.lower():
                raise AuthError(f"Authentication failed: {e}")
            elif "network" in error_str.lower() or "connection" in error_str.lower():
                raise APIConnectionError(f"Network error: {e}")
            else:
                raise APIResponseError(f"Linear API error: {e}")

    def link_tasks(self, task_id: str, depends_on_id: str) -> bool:
        """Create a dependency relationship between tasks.

        In Linear, the depends_on task blocks the task_id task.

        Args:
            task_id: Task that depends on another
            depends_on_id: Task that blocks the first one

        Returns:
            True if link was created successfully
        """
        try:
            # Find both issues
            all_issues = self.client.issues.get_all()
            task_issue = None
            depends_on_issue = None

            for issue_id, issue in all_issues.items():
                if issue.identifier == task_id:
                    task_issue = issue
                elif issue.identifier == depends_on_id:
                    depends_on_issue = issue

                if task_issue and depends_on_issue:
                    break

            if not task_issue:
                raise NotFoundError(f"Task {task_id} not found")

            if not depends_on_issue:
                raise NotFoundError(f"Task {depends_on_id} not found")

            # Create relation using GraphQL
            query = """
            mutation CreateRelation($issueId: String!, $relatedIssueId: String!, $type: IssueRelationType!) {
                issueRelationCreate(input: {issueId: $issueId, relatedIssueId: $relatedIssueId, type: $type}) {
                    issueRelation {
                        id
                    }
                    success
                }
            }
            """

            variables = {
                "issueId": depends_on_issue.id,  # This issue blocks...
                "relatedIssueId": task_issue.id,  # ...this issue
                "type": "blocks",
            }

            result = self.client.execute_graphql(query, variables)

            return result and result.get("issueRelationCreate", {}).get(
                "success", False
            )

        except NotFoundError:
            raise
        except Exception as e:
            error_str = str(e)
            if "401" in error_str or "unauthorized" in error_str.lower():
                raise AuthError(f"Authentication failed: {e}")
            elif "not found" in error_str.lower() or "404" in error_str:
                raise NotFoundError("One or both tasks not found")
            elif "circular" in error_str.lower():
                raise ValidationError(f"Circular dependency detected: {e}")
            elif "network" in error_str.lower() or "connection" in error_str.lower():
                raise APIConnectionError(f"Network error: {e}")
            else:
                raise APIResponseError(f"Linear API error: {e}")

    def get_workflow_states(self, team_id: Optional[str] = None) -> Dict[str, Any]:
        """Get workflow states for a team using the workflow manager.

        This method provides backward compatibility while using the new
        workflow state manager for proper architecture.

        Args:
            team_id: Optional team ID. If not provided, uses the configured team.

        Returns:
            Dictionary with workflow states and metadata for backward compatibility.
        """
        try:
            # Determine team ID if not provided
            if not team_id:
                if self.team_name:
                    teams = self.client.teams.get_all()
                    for tid, team in teams.items():
                        if team.name == self.team_name:
                            team_id = tid
                            break

                if not team_id:
                    # Use first available team as fallback
                    teams = self.client.teams.get_all()
                    team_id = list(teams.keys())[0] if teams else None

                if not team_id:
                    raise APIResponseError("No teams found to discover workflow states")

            # Use the workflow manager to get states
            team_states = self.client.workflow_states.discover_team_states(team_id)

            # Convert to the expected format for backward compatibility
            return {
                "team_id": team_states.team_id,
                "team_name": team_states.team_name,
                "states": [state.model_dump() for state in team_states.states],
                "state_names": team_states.state_names,
                "discovered_at": team_states.discovered_at.isoformat(),
                "alfred_mappings": team_states.alfred_mappings,
            }

        except Exception as e:
            error_str = str(e)
            if "401" in error_str or "unauthorized" in error_str.lower():
                raise AuthError(f"Authentication failed: {e}")
            elif "not found" in error_str.lower() or "404" in error_str:
                raise NotFoundError(f"Team {team_id or self.team_name} not found")
            elif "network" in error_str.lower() or "connection" in error_str.lower():
                raise APIConnectionError(f"Network error: {e}")
            else:
                raise APIResponseError(f"Linear API error: {e}")

    def rename_epic(self, epic_id: str, new_name: str) -> EpicDict:
        """Rename an epic (project in Linear).

        Args:
            epic_id: Epic/project ID
            new_name: New name for the epic

        Returns:
            Updated epic as EpicDict
        """
        if not epic_id:
            raise ValidationError("Epic ID cannot be empty")

        if not new_name or not new_name.strip():
            raise ValidationError("Epic name cannot be empty")

        try:
            # Use LinearClient's ProjectManager to update the project name
            project = self.client.projects.update(
                project_id=epic_id.strip(), name=new_name.strip()
            )

            # Transform LinearProject to EpicDict
            return self._map_linear_project_to_epic(project)

        except ValidationError:
            raise
        except Exception as e:
            error_str = str(e)
            if "401" in error_str or "unauthorized" in error_str.lower():
                raise AuthError(f"Authentication failed: {e}")
            elif (
                "duplicate" in error_str.lower()
                or "already exists" in error_str.lower()
            ):
                raise ValidationError(
                    f"An epic with the name '{new_name}' already exists"
                )
            elif "network" in error_str.lower() or "connection" in error_str.lower():
                raise APIConnectionError(f"Network error: {e}")
            else:
                raise APIResponseError(f"Linear API error: {e}")

    def delete_epic(self, epic_id: str) -> bool:
        """Archive/delete an epic (project in Linear).

        Args:
            epic_id: Epic/project ID to archive

        Returns:
            True if successful
        """
        if not epic_id:
            raise ValidationError("Epic ID cannot be empty")

        try:
            # Use LinearClient's ProjectManager to delete (archive) the project
            # Note: Linear's delete actually archives projects
            return self.client.projects.delete(epic_id.strip())

        except ValidationError:
            raise
        except Exception as e:
            error_str = str(e)
            if "401" in error_str or "unauthorized" in error_str.lower():
                raise AuthError(f"Authentication failed: {e}")
            elif "not found" in error_str.lower():
                raise NotFoundError(f"Epic with ID '{epic_id}' not found")
            elif "network" in error_str.lower() or "connection" in error_str.lower():
                raise APIConnectionError(f"Network error: {e}")
            else:
                raise APIResponseError(f"Linear API error: {e}")

    def get_epic_tasks(self, epic_id: str) -> List[Dict[str, Any]]:
        """Get all tasks in an epic/project.

        Args:
            epic_id: Epic/project ID

        Returns:
            List of tasks in the epic
        """
        if not epic_id:
            raise ValidationError("Epic ID cannot be empty")

        try:
            # Use LinearClient's IssueManager to get issues for this project
            issues = self.client.issues.get_by_project(epic_id.strip())

            # Transform LinearIssues to TaskDicts
            tasks = []
            for issue_id, issue in issues.items():
                task = self._map_linear_issue_to_task(issue)
                # Add epic_id to the task
                task["epic_id"] = epic_id
                tasks.append(task)

            return tasks

        except Exception as e:
            error_str = str(e)
            if "401" in error_str or "unauthorized" in error_str.lower():
                raise AuthError(f"Authentication failed: {e}")
            elif "network" in error_str.lower() or "connection" in error_str.lower():
                raise APIConnectionError(f"Network error: {e}")
            else:
                raise APIResponseError(f"Linear API error: {e}")
