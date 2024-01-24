"""Change the project for a inbox task."""

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.core.use_cases.inbox_tasks.change_project import (
    InboxTaskChangeProjectUseCase,
)


class InboxTaskChangeProject(LoggedInMutationCommand[InboxTaskChangeProjectUseCase]):
    """UseCase class for hard removing inbox tasks."""
