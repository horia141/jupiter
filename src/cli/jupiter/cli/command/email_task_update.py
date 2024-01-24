"""UseCase for updating email tasks."""


from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.core.use_cases.push_integrations.email.update import (
    EmailTaskUpdateUseCase,
)


class EmailTaskUpdate(LoggedInMutationCommand[EmailTaskUpdateUseCase]):
    """UseCase class for updating email tasks."""
