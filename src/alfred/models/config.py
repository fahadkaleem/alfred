"""Configuration models using Pydantic v2."""

from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field, field_validator, ConfigDict


class Platform(str, Enum):
    """Supported platforms."""

    LINEAR = "linear"
    JIRA = "jira"


class AIProvider(str, Enum):
    """Supported AI providers."""

    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    GEMINI = "gemini"
    OLLAMA = "ollama"


class Config(BaseModel):
    """Main configuration model for Alfred."""

    # API Keys
    linear_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    jira_api_key: Optional[str] = None
    jira_url: Optional[str] = None
    jira_email: Optional[str] = None
    openai_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None

    # Workspace Configuration
    workspace_id: Optional[str] = None
    team_id: Optional[str] = None
    active_epic_id: Optional[str] = None

    # Platform Selection
    platform: Platform = Platform.LINEAR

    # AI Configuration
    ai_provider: AIProvider = AIProvider.ANTHROPIC
    claude_model: str = "claude-3-5-sonnet-20241022"
    openai_model: str = "gpt-4-turbo-preview"
    gemini_model: str = "gemini-pro"
    max_tokens: int = Field(default=4096, ge=1, le=100000)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)

    # AI Advanced Settings
    request_timeout: int = Field(default=60, ge=1, le=600)
    max_retries: int = Field(default=3, ge=0, le=10)
    rate_limit_rpm: int = Field(default=50, ge=1, le=1000)
    chunk_overlap_tokens: int = Field(default=200, ge=0, le=1000)
    max_context_percentage: float = Field(default=0.6, ge=0.1, le=1.0)

    # Behavior Configuration
    auto_decompose_threshold: int = Field(default=5, ge=1, le=20)
    default_subtask_count: int = Field(default=3, ge=1, le=10)

    @field_validator("*", mode="before")
    @classmethod
    def empty_str_to_none(cls, v):
        """Convert empty strings to None."""
        if v == "":
            return None
        return v

    def to_dict(self) -> dict:
        """Convert Config to dictionary, excluding None values."""
        return self.model_dump(exclude_none=True)

    @classmethod
    def from_dict(cls, data: dict) -> "Config":
        """Create Config from dictionary, ignoring unknown fields."""
        return cls.model_validate(data)

    model_config = ConfigDict(
        use_enum_values=True,
        json_schema_extra={
            "example": {
                "platform": "linear",
                "workspace_id": "my-workspace",
                "team_id": "team-123",
                "linear_api_key": "lin_api_xxx",
                "anthropic_api_key": "sk-ant-xxx",
            }
        },
    )
