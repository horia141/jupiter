"""UseCase for updating a smart list item."""

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.core.use_cases.smart_lists.item.update import (
    SmartListItemUpdateUseCase,
)


class SmartListItemUpdate(LoggedInMutationCommand[SmartListItemUpdateUseCase]):
    """UseCase for updating a smart list item."""
