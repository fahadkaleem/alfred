from typing import List, Dict, Any, Optional
from datetime import datetime

from alfred.core.taskmanager import TaskManager
from ..exceptions import TaskNotFoundException, ValidationException
from ..constants import ContextStatus


class ContextService:
    def __init__(self, task_manager: TaskManager):
        self.task_manager = task_manager

    async def get_contexts(
        self, task_id: str, phase: Optional[str] = None
    ) -> Dict[str, Any]:
        task = self.task_manager.get_task(task_id)
        if not task:
            raise TaskNotFoundException(task_id)

        contexts = self.task_manager.load_context(task_id, phase)

        if not contexts:
            if phase:
                return {phase: []}
            else:
                return {}

        if phase:
            api_contexts = []
            for i, ctx in enumerate(contexts):
                api_contexts.append(self._transform_context(task_id, phase, i, ctx))
            return {phase: api_contexts}
        else:
            result_data = {}
            for phase_name, phase_contexts in contexts.items():
                api_contexts = []
                for i, ctx in enumerate(phase_contexts):
                    api_contexts.append(
                        self._transform_context(task_id, phase_name, i, ctx)
                    )
                result_data[phase_name] = api_contexts
            return result_data

    async def save_context(
        self,
        task_id: str,
        phase: str,
        content: str,
        status: str = ContextStatus.IN_PROGRESS.value,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        task = self.task_manager.get_task(task_id)
        if not task:
            raise TaskNotFoundException(task_id)

        success = self.task_manager.save_context(
            task_id=task_id, phase=phase, content=content, metadata=metadata
        )

        if not success:
            raise ValidationException("Failed to save context")

        phase_contexts = self.task_manager.load_context(task_id, phase)
        if not phase_contexts:
            raise ValidationException("Context saved but could not retrieve")

        latest_context = phase_contexts[-1]
        context_id = f"{task_id}_{phase}_{len(phase_contexts) - 1}"

        return self._transform_context(
            task_id, phase, len(phase_contexts) - 1, latest_context
        )

    async def get_latest_context(self, task_id: str) -> Dict[str, Any]:
        task = self.task_manager.get_task(task_id)
        if not task:
            raise TaskNotFoundException(task_id)

        all_contexts = self.task_manager.load_context(task_id)

        if not all_contexts:
            raise ValidationException(f"No contexts found for task {task_id}")

        latest_context = None
        latest_timestamp = None
        latest_phase = None
        latest_index = 0

        for phase_name, phase_contexts in all_contexts.items():
            for i, ctx in enumerate(phase_contexts):
                timestamp_str = ctx.get("timestamp", "")
                if timestamp_str:
                    timestamp = datetime.fromisoformat(timestamp_str)
                    if latest_timestamp is None or timestamp > latest_timestamp:
                        latest_timestamp = timestamp
                        latest_context = ctx
                        latest_phase = phase_name
                        latest_index = i

        if not latest_context:
            raise ValidationException(f"No valid contexts found for task {task_id}")

        return self._transform_context(
            task_id, latest_phase, latest_index, latest_context
        )

    def _transform_context(
        self, task_id: str, phase: str, index: int, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        return {
            "id": f"{task_id}_{phase}_{index}",
            "phase": phase,
            "content": context.get("content", ""),
            "status": context.get("status", ContextStatus.IN_PROGRESS.value),
            "metadata": context.get("metadata"),
            "timestamp": datetime.fromisoformat(
                context.get("timestamp", datetime.now().isoformat())
            ),
        }
