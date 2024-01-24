"""UseCase for hard remove vacations."""

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.core.use_cases.vacations.remove import (
    VacationRemoveUseCase,
)


class VacationRemove(LoggedInMutationCommand[VacationRemoveUseCase]):
    """UseCase class for hard removing vacations."""
