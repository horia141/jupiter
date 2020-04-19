"""Common defines for all repositories."""
import enum
from typing import NewType


class RepositoryError(Exception):
    """An exception raised when loading data from a repository."""


RefId = NewType("RefId", str)


@enum.unique
class TaskPeriod(enum.Enum):
    """A period for a particular task."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"

    def for_notion(self) -> str:
        """A prettier version of the value for Notion."""
        return str(self.value).capitalize()


@enum.unique
class TaskEisen(enum.Enum):
    """The Eisenhower status of a particular task."""
    IMPORTANT = "important"
    URGENT = "urgent"

    def for_notion(self) -> str:
        """A prettier version of the value for Notion."""
        return str(self.value).capitalize()


@enum.unique
class TaskDifficulty(enum.Enum):
    """The difficulty of a particular task."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

    def for_notion(self) -> str:
        """A prettier version of the value for Notion."""
        return str(self.value).capitalize()
