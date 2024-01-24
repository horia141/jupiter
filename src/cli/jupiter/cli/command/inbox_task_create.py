"""UseCase for creating an inbox task."""


from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.core.use_cases.inbox_tasks.create import (
    InboxTaskCreateUseCase,
)


class InboxTaskCreate(LoggedInMutationCommand[InboxTaskCreateUseCase]):
    """UseCase class for creating inbox tasks."""
