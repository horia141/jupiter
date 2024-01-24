"""UseCase for removing a person."""

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.core.use_cases.persons.remove import PersonRemoveUseCase


class PersonRemove(LoggedInMutationCommand[PersonRemoveUseCase]):
    """UseCase for removing a person."""
