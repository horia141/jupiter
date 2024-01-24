"""UseCase for adding a chore."""


from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.core.use_cases.chores.create import ChoreCreateUseCase


class ChoreCreate(LoggedInMutationCommand[ChoreCreateUseCase]):
    """UseCase class for creating a chore."""
