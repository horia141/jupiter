"""UseCase for adding a vacation."""


from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.core.use_cases.vacations.create import (
    VacationCreateUseCase,
)


class VacationCreate(LoggedInMutationCommand[VacationCreateUseCase]):
    """UseCase class for adding a vacation."""
