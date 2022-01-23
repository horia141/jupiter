"""The command for removing a recurring task."""
import logging
from dataclasses import dataclass
from typing import Final

from jupiter.domain.inbox_tasks.infra.inbox_task_notion_manager import InboxTaskNotionManager
from jupiter.domain.recurring_tasks.infra.recurring_task_notion_manager import RecurringTaskNotionManager
from jupiter.domain.recurring_tasks.service.remove_service import RecurringTaskRemoveService
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.use_case import UseCase

LOGGER = logging.getLogger(__name__)


class RecurringTaskRemoveUseCase(UseCase['RecurringTaskRemoveUseCase.Args', None]):
    """The command for removing a recurring task."""

    @dataclass()
    class Args:
        """Args."""
        ref_id: EntityId

    _storage_engine: Final[DomainStorageEngine]
    _inbox_task_notion_manager: Final[InboxTaskNotionManager]
    _recurring_task_notion_manager: Final[RecurringTaskNotionManager]

    def __init__(
            self, storage_engine: DomainStorageEngine, inbox_task_notion_manager: InboxTaskNotionManager,
            recurring_task_notion_manager: RecurringTaskNotionManager) -> None:
        """Constructor."""
        self._storage_engine = storage_engine
        self._inbox_task_notion_manager = inbox_task_notion_manager
        self._recurring_task_notion_manager = recurring_task_notion_manager

    def execute(self, args: Args) -> None:
        """Execute the command's action."""
        RecurringTaskRemoveService(
            self._storage_engine, self._inbox_task_notion_manager,
            self._recurring_task_notion_manager).remove(args.ref_id)
