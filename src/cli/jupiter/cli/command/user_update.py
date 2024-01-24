"""Command for updating the user."""

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.core.use_cases.user.update import UserUpdateUseCase


class UserUpdate(LoggedInMutationCommand[UserUpdateUseCase]):
    """Command class for updating the user."""
