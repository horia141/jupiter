"""The command for removing a inbox task."""
from dataclasses import dataclass
from typing import Final

from jupiter.domain.inbox_tasks.infra.inbox_task_notion_manager import InboxTaskNotionManager
from jupiter.domain.inbox_tasks.service.remove_service import InboxTaskRemoveService
from jupiter.domain.storage_engine import StorageEngine
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.use_case import UseCase


class InboxTaskRemoveUseCase(UseCase['InboxTaskRemoveUseCase.Args', None]):
    """The command for removing a inbox task."""

    @dataclass()
    class Args:
        """Args."""
        ref_id: EntityId

    _storage_engine: Final[StorageEngine]
    _inbox_task_notion_manager: Final[InboxTaskNotionManager]

    def __init__(self, storage_engine: StorageEngine, inbox_task_notion_manager: InboxTaskNotionManager) -> None:
        """Constructor."""
        self._storage_engine = storage_engine
        self._inbox_task_notion_manager = inbox_task_notion_manager

    def execute(self, args: Args) -> None:
        """Execute the command's action."""
        with self._storage_engine.get_unit_of_work() as uow:
            inbox_task = uow.inbox_task_repository.load_by_id(args.ref_id)
        InboxTaskRemoveService(self._storage_engine, self._inbox_task_notion_manager).do_it(inbox_task)
