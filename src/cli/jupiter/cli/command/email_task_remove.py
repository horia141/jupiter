"""UseCase for hard remove email tasks."""

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.core.use_cases.push_integrations.email.remove import (
    EmailTaskRemoveUseCase,
)


class EmailTaskRemove(LoggedInMutationCommand[EmailTaskRemoveUseCase]):
    """UseCase class for hard removing email tasks."""
