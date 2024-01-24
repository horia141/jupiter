"""UseCase for hard remove slack tasks."""

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.core.use_cases.push_integrations.slack.remove import (
    SlackTaskRemoveUseCase,
)


class SlackTaskRemove(LoggedInMutationCommand[SlackTaskRemoveUseCase]):
    """UseCase class for hard removing slack tasks."""
