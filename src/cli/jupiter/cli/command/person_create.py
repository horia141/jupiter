"""UseCase for adding a person."""

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.core.use_cases.persons.create import PersonCreateUseCase


class PersonCreate(LoggedInMutationCommand[PersonCreateUseCase]):
    """UseCase class for adding a person."""
