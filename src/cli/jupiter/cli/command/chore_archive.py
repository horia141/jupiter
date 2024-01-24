"""UseCase for removing a chore."""

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.core.use_cases.chores.archive import ChoreArchiveUseCase


class ChoreArchive(LoggedInMutationCommand[ChoreArchiveUseCase]):
    """UseCase class for removing a chore."""
