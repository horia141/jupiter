"""UseCase for removing a habit."""

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.core.use_cases.habits.archive import HabitArchiveUseCase


class HabitArchive(LoggedInMutationCommand[HabitArchiveUseCase]):
    """UseCase class for removing a habit."""
