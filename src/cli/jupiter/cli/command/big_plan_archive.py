"""UseCase for archiving a big plan."""

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.core.use_cases.big_plans.archive import (
    BigPlanArchiveUseCase,
)


class BigPlanArchive(LoggedInMutationCommand[BigPlanArchiveUseCase]):
    """UseCase class for archiving a big plan."""
