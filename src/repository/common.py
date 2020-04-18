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


@enum.unique
class TaskEisen(enum.Enum):
    """The Eisenhower status of a particular task."""
    IMPORTANT = "important"
    URGENT = "urgent"


@enum.unique
class TaskDifficulty(enum.Enum):
    """The difficulty of a particular task."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
