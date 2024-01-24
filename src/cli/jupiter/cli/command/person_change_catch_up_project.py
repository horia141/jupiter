"""UseCase for updating the person database."""

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.core.use_cases.persons.change_catch_up_project import (
    PersonChangeCatchUpProjectUseCase,
)


class PersonChangeCatchUpProject(
    LoggedInMutationCommand[PersonChangeCatchUpProjectUseCase]
):
    """UseCase for updating the person database."""
