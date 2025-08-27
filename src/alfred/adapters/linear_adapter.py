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
        try:
            task: TaskDict = {
                "id": issue.identifier,
                "title": issue.title,
                "description": issue.description,
                "status": issue.state.name
                if hasattr(issue, "state") and issue.state
                else None,
                "epic_id": issue.project.id
                if hasattr(issue, "project") and issue.project
                else None,
                "parent_id": issue.parent.id
                if hasattr(issue, "parent") and issue.parent
                else None,
                "url": issue.url if hasattr(issue, "url") else None,
                "created_at": issue.created_at.isoformat()
                if hasattr(issue, "created_at") and issue.created_at
                else None,
                "updated_at": issue.updated_at.isoformat()
                if hasattr(issue, "updated_at") and issue.updated_at
                else None,
            }
            return task
        except Exception as e:
            raise MappingError(f"Failed to map Linear issue to task: {e}")

    def _map_linear_project_to_epic(self, project) -> EpicDict:
        """Map Linear Project to normalized EpicDict.

        Args:
            project: LinearProject object

        Returns:
            Normalized EpicDict
        """
        try:
            epic: EpicDict = {
                "id": project.id,
                "name": project.name,
                "description": project.description
                if hasattr(project, "description")
                else None,
                "url": project.url if hasattr(project, "url") else None,
                "created_at": project.created_at.isoformat()
                if hasattr(project, "created_at") and project.created_at
                else None,
                "updated_at": project.updated_at.isoformat()
                if hasattr(project, "updated_at") and project.updated_at
                else None,
            }
            return epic
        except Exception as e:
            raise MappingError(f"Failed to map Linear project to epic: {e}")

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
            epic_id: Project ID to add the task to (not used directly as we use project name)

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
                projectName=self.default_project_name,
                priority=LinearPriority.MEDIUM,
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
                if status_list and hasattr(issue, "state") and issue.state:
                    if issue.state.name not in status_list:
                        continue

                # Apply project filter if provided
                if epic_id and hasattr(issue, "project") and issue.project:
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
            # Find the issue by identifier
            all_issues = self.client.issues.get_all()
            target_issue = None

            for issue_id, issue in all_issues.items():
                if issue.identifier == task_id:
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
            if hasattr(parent_issue, "project") and parent_issue.project:
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
            # Create project in Linear
            # Note: The linear-api library doesn't directly expose project creation
            # We'll need to use GraphQL directly for this
            query = """
            mutation CreateProject($name: String!, $description: String, $teamIds: [String!]!) {
                projectCreate(input: {name: $name, description: $description, teamIds: $teamIds}) {
                    project {
                        id
                        name
                        description
                        url
                        createdAt
                        updatedAt
                    }
                    success
                }
            }
            """

            # Get team ID first
            teams = self.client.teams.get_all()
            team_id = None
            for tid, team in teams.items():
                if team.name == self.team_name:
                    team_id = tid
                    break

            if not team_id:
                # Use first available team
                team_id = list(teams.keys())[0] if teams else None

            if not team_id:
                raise APIResponseError("No teams found")

            variables = {
                "name": name,
                "description": description or "",
                "teamIds": [team_id],
            }

            result = self.client.execute_graphql(query, variables)

            if not result or not result.get("projectCreate", {}).get("success"):
                raise APIResponseError("Failed to create project in Linear")

            project = result["projectCreate"]["project"]

            return {
                "id": project["id"],
                "name": project["name"],
                "description": project.get("description"),
                "url": project.get("url"),
                "created_at": project.get("createdAt"),
                "updated_at": project.get("updatedAt"),
            }

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
                "alfred_mappings": team_states.alfred_mappings
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
