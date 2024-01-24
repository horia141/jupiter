"""UseCase for unsuspending of a habit."""

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.core.use_cases.habits.unsuspend import (
    HabitUnsuspendUseCase,
)


class HabitUnsuspend(LoggedInMutationCommand[HabitUnsuspendUseCase]):
    """UseCase class for unsuspending a habit."""
