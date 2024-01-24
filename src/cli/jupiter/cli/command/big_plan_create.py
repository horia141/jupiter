"""UseCase for creating big plans."""


from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.core.use_cases.big_plans.create import (
    BigPlanCreateUseCase,
)


class BigPlanCreate(LoggedInMutationCommand[BigPlanCreateUseCase]):
    """UseCase class for creating big plans."""
