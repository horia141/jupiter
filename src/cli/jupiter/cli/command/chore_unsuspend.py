"""UseCase for unsuspending of a chore."""

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.core.use_cases.chores.unsuspend import (
    ChoreUnsuspendUseCase,
)


class ChoreUnsuspend(LoggedInMutationCommand[ChoreUnsuspendUseCase]):
    """UseCase class for unsuspending a chore."""
