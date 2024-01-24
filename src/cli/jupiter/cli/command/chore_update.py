"""UseCase for updating a chore."""


from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.core.use_cases.chores.update import ChoreUpdateUseCase


class ChoreUpdate(LoggedInMutationCommand[ChoreUpdateUseCase]):
    """UseCase class for creating a chore."""
