"""
Loads and manages subagent definitions
"""

from pathlib import Path
from typing import Dict, Optional
import yaml
from alfred.models.workflow import Subagent


class SubagentRegistry:
    """Manages subagent definitions from registry"""

    def __init__(self, registry_path: Path):
        """
        Args:
            registry_path: Path to subagents/registry.yaml
        """
        self.registry_path = registry_path
        self._registry: Dict[str, Subagent] = {}
        self._load_registry()

    def _load_registry(self) -> None:
        """Load subagent registry from YAML"""
        if not self.registry_path.exists():
            return

        try:
            with self.registry_path.open() as f:
                data = yaml.safe_load(f)

            if not data or "subagents" not in data:
                return

            for subagent_id, subagent_data in data["subagents"].items():
                self._registry[subagent_id] = Subagent(
                    id=subagent_id,
                    claude_subagent=subagent_data.get(
                        "claude_subagent", "general-purpose"
                    ),
                    description=subagent_data.get("description", ""),
                    when_to_use=subagent_data.get("when_to_use", ""),
                    example_prompts=subagent_data.get("example_prompts", []),
                )
        except Exception:
            # Registry loading is non-critical, continue without it
            pass

    def get_subagent(self, subagent_id: str) -> Optional[Subagent]:
        """Get subagent definition by ID"""
        return self._registry.get(subagent_id)

    def get_subagents(self, subagent_ids: list[str]) -> list[Subagent]:
        """Get multiple subagent definitions"""
        subagents = []
        for sid in subagent_ids:
            subagent = self.get_subagent(sid)
            if subagent:
                subagents.append(subagent)
        return subagents
