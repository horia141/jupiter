"""UseCase for hard remove inbox tasks."""


from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.core.use_cases.inbox_tasks.remove import (
    InboxTaskRemoveUseCase,
)


class InboxTaskRemove(LoggedInMutationCommand[InboxTaskRemoveUseCase]):
    """UseCase class for hard removing inbox tasks."""
