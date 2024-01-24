"""UseCase for suspending of a habit."""

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.core.use_cases.habits.suspend import HabitSuspendUseCase


class HabitSuspend(LoggedInMutationCommand[HabitSuspendUseCase]):
    """UseCase class for suspending a habit."""
