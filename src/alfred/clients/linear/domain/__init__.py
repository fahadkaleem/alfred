"""
Alfred Linear API Domain Models.

This package provides Pydantic domain models for Alfred's Linear API integration.
All Linear GraphQL types are represented as strongly-typed Python models.
"""

# Import all public classes from the base domain module
from .base_domain import LinearModel, Connection

# Import common models
from .common_models import (
    Organization,
    Comment,
    CommentConnection,
    DocumentContent,
    DocumentConnection,
    EntityExternalLinkConnection,
    Favorite,
    Template,
    TimelessDate,
    IntegrationsSettings,
    TeamMembership,
    Draft,
    IssueDraft,
    ActorBot,
    ExternalUser,
    Document,
    EntityExternalLink,
)

# Import all enums
from .enums import (
    LinearPriority,
    SLADayCountType,
    DateResolutionType,
    FrequencyResolutionType,
    ProjectUpdateHealthType,
    ProjectStatusType,
    Day,
    IntegrationService,
)

# Import issue models
from .issue_models import (
    LinearLabel,
    LinearAttachment,
    LinearAttachmentInput,
    LinearIssue,
    LinearIssueInput,
    LinearIssueUpdateInput,
    IssueRelation,
    CustomerNeedResponse,
)

# Import project models
from .project_models import (
    ProjectStatus,
    ProjectMilestone,
    ProjectMilestoneConnection,
    ProjectUpdate,
    ProjectUpdateConnection,
    ProjectHistoryConnection,
    InitiativeConnection,
    ProjectRelationConnection,
    IssueConnection,
    ProjectLabelConnection,
    CustomerNeedConnection,
    LinearProject,
    Cycle,
    CustomerNeed,
    Initiative,
    ProjectRelation,
    ProjectHistory,
)

# Import team models
from .team_models import (
    LinearState,
    LinearTeam,
    TeamConnection,
    TriageResponsibility,
    TeamMembership,
)

# Import user models
from .user_models import (
    LinearUserReference,
    LinearUser,
    UserConnection,
    Reaction,
)

# List of all public exports
__all__ = [
    # Base domain
    "LinearModel",
    "Connection",
    # Enums
    "LinearPriority",
    "SLADayCountType",
    "DateResolutionType",
    "FrequencyResolutionType",
    "ProjectUpdateHealthType",
    "ProjectStatusType",
    "Day",
    "IntegrationService",
    # Common models
    "Organization",
    "Comment",
    "CommentConnection",
    "DocumentContent",
    "DocumentConnection",
    "EntityExternalLinkConnection",
    "Favorite",
    "Template",
    "TimelessDate",
    "IntegrationsSettings",
    "TeamMembership",
    "Draft",
    "IssueDraft",
    "ActorBot",
    "ExternalUser",
    "Document",
    "EntityExternalLink",
    # User models
    "LinearUserReference",
    "LinearUser",
    "UserConnection",
    "Reaction",
    # Team models
    "LinearState",
    "LinearTeam",
    "TeamConnection",
    "TriageResponsibility",
    "TeamMembership",
    # Project models
    "ProjectStatus",
    "ProjectMilestone",
    "ProjectMilestoneConnection",
    "ProjectUpdate",
    "ProjectUpdateConnection",
    "ProjectHistoryConnection",
    "InitiativeConnection",
    "ProjectRelationConnection",
    "IssueConnection",
    "ProjectLabelConnection",
    "CustomerNeedConnection",
    "LinearProject",
    "Cycle",
    "CustomerNeed",
    "Initiative",
    "ProjectRelation",
    "ProjectHistory",
    # Issue models
    "LinearLabel",
    "LinearAttachment",
    "LinearAttachmentInput",
    "LinearIssue",
    "LinearIssueInput",
    "LinearIssueUpdateInput",
    "IssueRelation",
    "CustomerNeedResponse",
]
