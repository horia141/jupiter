"""UseCase for hard removing habits."""

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.core.use_cases.habits.remove import HabitRemoveUseCase


class HabitRemove(LoggedInMutationCommand[HabitRemoveUseCase]):
    """UseCase class for hard removing habits."""
