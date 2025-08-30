from typing import List, Dict, Any
from pathlib import Path

from alfred.tools.load_instructions import load_instructions_logic
from alfred.core.workflow_loader import WorkflowLoader

from ..exceptions import ValidationException
from alfred.config import settings


class InstructionService:
    def __init__(self, workflow_loader: WorkflowLoader):
        self.workflow_loader = workflow_loader

    async def list_instructions(self) -> Dict[str, Any]:
        instructions_root = settings.instructions_dir

        if not instructions_root.exists():
            return {"categories": {}, "total_count": 0}

        categories = {}
        total_count = 0

        for file in instructions_root.rglob("*.md"):
            relative_path = file.relative_to(instructions_root)
            category = (
                str(relative_path.parent)
                if relative_path.parent != Path(".")
                else "root"
            )
            filename = file.stem

            if category not in categories:
                categories[category] = []

            categories[category].append(
                {
                    "name": filename,
                    "full_path": str(relative_path),
                    "category": category,
                    "file_size": file.stat().st_size,
                }
            )
            total_count += 1

        return {
            "categories": categories,
            "total_count": total_count,
            "available_categories": list(categories.keys()),
        }

    async def get_instruction(self, name: str) -> Dict[str, Any]:
        result = await load_instructions_logic(name)

        if result.status == "error":
            raise ValidationException(f"Instruction {name} not found")

        return result.data

    async def list_personas(self) -> List[Dict[str, Any]]:
        personas_dir = settings.personas_dir

        if not personas_dir.exists():
            return []

        personas = []
        for file in personas_dir.glob("*.yaml"):
            personas.append(
                {
                    "id": file.stem,
                    "filename": file.name,
                    "file_size": file.stat().st_size,
                }
            )

        return personas

    async def get_persona(self, persona_id: str) -> Dict[str, Any]:
        try:
            persona = self.workflow_loader.load_persona(persona_id)
        except FileNotFoundError:
            raise ValidationException(f"Persona '{persona_id}' not found")
        except Exception as e:
            raise ValidationException(f"Failed to load persona: {e}")

        return {
            "id": persona.id,
            "role": persona.role,
            "experience": persona.experience,
            "principles": persona.principles,
            "traits": persona.traits,
            "communication_style": persona.communication_style,
            "meta_instructions": getattr(persona, "meta_instructions", []),
            "quality_standards": getattr(persona, "quality_standards", {}),
        }
