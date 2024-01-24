"""UseCase for removing a vacation."""


from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.core.use_cases.vacations.archive import (
    VacationArchiveUseCase,
)


class VacationArchive(LoggedInMutationCommand[VacationArchiveUseCase]):
    """UseCase class for removing a vacation."""
