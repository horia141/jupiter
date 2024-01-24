"""UseCase for creating a smart list item."""

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.core.use_cases.smart_lists.item.create import (
    SmartListItemCreateUseCase,
)


class SmartListItemCreate(LoggedInMutationCommand[SmartListItemCreateUseCase]):
    """UseCase for creating a smart list item."""
