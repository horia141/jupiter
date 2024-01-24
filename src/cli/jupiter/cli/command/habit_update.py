"""UseCase for updating a habit."""

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.core.use_cases.habits.update import HabitUpdateUseCase


class HabitUpdate(LoggedInMutationCommand[HabitUpdateUseCase]):
    """UseCase class for creating a habit."""
