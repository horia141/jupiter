"""UseCase for hard remove big plans."""

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.core.use_cases.big_plans.remove import (
    BigPlanRemoveUseCase,
)


class BigPlanRemove(LoggedInMutationCommand[BigPlanRemoveUseCase]):
    """UseCase class for hard removing big plans."""
