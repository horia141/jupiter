"""UseCase for archiving an inbox task."""

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.core.use_cases.inbox_tasks.archive import (
    InboxTaskArchiveUseCase,
)


class InboxTaskArchive(LoggedInMutationCommand[InboxTaskArchiveUseCase]):
    """UseCase class for archiving an inbox task."""
