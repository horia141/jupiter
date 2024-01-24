"""UseCase for archiving a email task."""

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.core.use_cases.push_integrations.email.archive import (
    EmailTaskArchiveUseCase,
)


class EmailTaskArchive(LoggedInMutationCommand[EmailTaskArchiveUseCase]):
    """UseCase class for archiving an email task."""
