"""UseCase for archiving a person."""

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.core.use_cases.persons.archive import (
    PersonArchiveUseCase,
)


class PersonArchive(LoggedInMutationCommand[PersonArchiveUseCase]):
    """UseCase for archiving a person."""
