"""UseCase for updating a vacation's properties."""


from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.core.use_cases.vacations.update import (
    VacationUpdateUseCase,
)


class VacationUpdate(LoggedInMutationCommand[VacationUpdateUseCase]):
    """UseCase for updating a vacation's properties."""
