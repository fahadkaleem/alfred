"""Models for research functionality."""

from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class ResearchContext(BaseModel):
    """Context gathered for research queries."""

    tasks: List[Dict[str, Any]] = Field(default_factory=list)
    files: List[Dict[str, str]] = Field(default_factory=list)
    custom_context: Optional[str] = None
    project_tree: Optional[str] = None
    token_breakdown: Dict[str, int] = Field(default_factory=dict)


class ResearchRequest(BaseModel):
    """Request for research operation."""

    query: str
    task_ids: Optional[str] = None
    file_paths: Optional[str] = None
    custom_context: Optional[str] = None
    include_project_tree: bool = False
    detail_level: str = "medium"
    save_to: Optional[str] = None
    save_to_file: bool = False


class ResearchResponse(BaseModel):
    """Response from research operation."""

    query: str
    result: str
    context_size: int
    context_tokens: int
    token_breakdown: Dict[str, int]
    system_prompt_tokens: int
    user_prompt_tokens: int
    total_input_tokens: int
    detail_level: str
    saved_file_path: Optional[str] = None
    telemetry_data: Dict[str, Any] = Field(default_factory=dict)


class FuzzySearchResult(BaseModel):
    """Result from fuzzy search."""

    task_id: int
    relevance_score: float
    match_type: str
