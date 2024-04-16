from enum import Enum


class ChecklistBlockKind(str, Enum):
    CHECKLIST = "checklist"

    def __str__(self) -> str:
        return str(self.value)
