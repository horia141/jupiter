"""Change the project for a chore."""

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.core.use_cases.chores.change_project import (
    ChoreChangeProjectUseCase,
)


class ChoreChangeProject(LoggedInMutationCommand[ChoreChangeProjectUseCase]):
    """UseCase class for hard removing chores."""
