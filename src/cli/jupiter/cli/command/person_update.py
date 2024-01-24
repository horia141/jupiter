"""UseCase for updating a person."""

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.core.use_cases.persons.update import PersonUpdateUseCase


class PersonUpdate(LoggedInMutationCommand[PersonUpdateUseCase]):
    """UseCase class for updating a person."""
