"""UseCase for archiving done tasks."""

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.core.use_cases.gc.do import GCDoUseCase


class GCDo(LoggedInMutationCommand[GCDoUseCase]):
    """UseCase class for archiving done tasks."""
