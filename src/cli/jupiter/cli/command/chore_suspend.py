"""UseCase for suspending of a chore."""

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.core.use_cases.chores.suspend import ChoreSuspendUseCase


class ChoreSuspend(LoggedInMutationCommand[ChoreSuspendUseCase]):
    """UseCase class for suspending a chore."""
