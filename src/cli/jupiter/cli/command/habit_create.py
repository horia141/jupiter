"""UseCase for adding a habit."""

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.core.use_cases.habits.create import HabitCreateUseCase


class HabitCreate(LoggedInMutationCommand[HabitCreateUseCase]):
    """UseCase class for creating a habit."""
