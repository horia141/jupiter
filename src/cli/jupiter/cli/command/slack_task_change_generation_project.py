"""UseCase for updating the slack task generation project."""

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.core.use_cases.push_integrations.slack.change_generation_project import (
    SlackTaskChangeGenerationProjectUseCase,
)


class SlackTaskChangeGenerationProject(
    LoggedInMutationCommand[SlackTaskChangeGenerationProjectUseCase]
):
    """Use case for updating the slack task generation project."""
