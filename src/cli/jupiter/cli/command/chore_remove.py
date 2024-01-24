"""UseCase for hard removing chores."""

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.core.use_cases.chores.remove import ChoreRemoveUseCase


class ChoreRemove(LoggedInMutationCommand[ChoreRemoveUseCase]):
    """UseCase class for hard removing chores."""
