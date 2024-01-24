"""UseCase for hard removing a smart list item."""

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.core.use_cases.smart_lists.item.remove import (
    SmartListItemRemoveUseCase,
)


class SmartListItemRemove(LoggedInMutationCommand[SmartListItemRemoveUseCase]):
    """UseCase for hard removing of a smart list item."""
