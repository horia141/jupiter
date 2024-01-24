"""Change the project for a big plan."""

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.core.use_cases.big_plans.change_project import (
    BigPlanChangeProjectUseCase,
)


class BigPlanChangeProject(LoggedInMutationCommand[BigPlanChangeProjectUseCase]):
    """UseCase class for hard removing big plans."""
