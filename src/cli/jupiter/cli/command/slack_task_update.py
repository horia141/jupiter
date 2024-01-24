"""UseCase for updating slack tasks."""


from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.core.use_cases.push_integrations.slack.update import (
    SlackTaskUpdateUseCase,
)


class SlackTaskUpdate(LoggedInMutationCommand[SlackTaskUpdateUseCase]):
    """UseCase class for updating slack tasks."""
