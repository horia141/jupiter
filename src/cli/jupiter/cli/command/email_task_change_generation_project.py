"""UseCase for updating the email task generation project."""

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.core.use_cases.push_integrations.email.change_generation_project import (
    EmailTaskChangeGenerationProjectUseCase,
)


class EmailTaskChangeGenerationProject(
    LoggedInMutationCommand[EmailTaskChangeGenerationProjectUseCase]
):
    """Use case for updating the email task generation project."""
