"""UseCase for archiving a slack task."""

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.core.use_cases.push_integrations.slack.archive import (
    SlackTaskArchiveUseCase,
)


class SlackTaskArchive(LoggedInMutationCommand[SlackTaskArchiveUseCase]):
    """UseCase class for archiving a slack task."""
