"""Research tool for AI-powered context gathering and analysis."""

import asyncio
from typing import Dict, Any

from alfred.core.research.perform_research import perform_research
from alfred.core.research.models import ResearchRequest


def register(server) -> int:
    """Register the research tool."""

    @server.tool
    async def research(
        query: str,
        taskIds: str = None,
        filePaths: str = None,
        customContext: str = None,
        includeProjectTree: bool = False,
        detailLevel: str = "medium",
        saveTo: str = None,
        saveToFile: bool = False,
        projectRoot: str = None,
        tag: str = None,
    ) -> Dict[str, Any]:
        """
        Perform AI-powered research queries with intelligent project context gathering.

        Args:
            query: Research query/prompt (required)
            taskIds: Comma-separated task/subtask IDs for context (e.g., "15,16.2,17")
            filePaths: Comma-separated file paths for context (e.g., "src/api.js,docs/readme.md")
            customContext: Additional custom context text
            includeProjectTree: Include project file tree structure in context
            detailLevel: Response detail level - "low", "medium", or "high"
            saveTo: Auto-save to task/subtask ID (e.g., "15" or "15.2")
            saveToFile: Save to .taskmaster/docs/research/ directory
            projectRoot: Absolute path to project directory (required)
            tag: Tag context to operate on

        Returns:
            Research results with context information and token usage
        """
        if not query:
            return {
                "success": False,
                "error": {
                    "code": "MISSING_PARAMETER",
                    "message": "The query parameter is required and must be a non-empty string",
                },
            }

        if not projectRoot:
            return {
                "success": False,
                "error": {
                    "code": "MISSING_PARAMETER",
                    "message": "The projectRoot parameter is required",
                },
            }

        if detailLevel not in ["low", "medium", "high"]:
            return {
                "success": False,
                "error": {
                    "code": "INVALID_PARAMETER",
                    "message": f"Invalid detailLevel '{detailLevel}'. Must be 'low', 'medium', or 'high'",
                },
            }

        try:
            request = ResearchRequest(
                query=query,
                task_ids=taskIds,
                file_paths=filePaths,
                custom_context=customContext,
                include_project_tree=includeProjectTree,
                detail_level=detailLevel,
                save_to=saveTo,
                save_to_file=saveToFile,
            )

            response = await perform_research(request, projectRoot)

            return {"success": True, "data": response.model_dump()}

        except ValueError as e:
            return {
                "success": False,
                "error": {"code": "INVALID_PARAMETER", "message": str(e)},
            }
        except Exception as e:
            return {
                "success": False,
                "error": {
                    "code": "RESEARCH_ERROR",
                    "message": f"Research failed: {str(e)}",
                },
            }

    return 1
