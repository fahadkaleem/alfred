"""Epic management core business logic."""

from .list import list_epics_logic
from .create import create_epic_logic
from .switch import switch_epic_logic
from .rename import rename_epic_logic
from .duplicate import duplicate_epic_logic
from .delete import delete_epic_logic

__all__ = [
    "list_epics_logic",
    "create_epic_logic",
    "switch_epic_logic",
    "rename_epic_logic",
    "duplicate_epic_logic",
    "delete_epic_logic",
]
