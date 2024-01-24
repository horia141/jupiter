"""Change the project for a habit."""

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.core.use_cases.habits.change_project import (
    HabitChangeProjectUseCase,
)


class HabitChangeProject(LoggedInMutationCommand[HabitChangeProjectUseCase]):
    """UseCase class for hard removing habits."""
