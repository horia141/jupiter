"""The command for removing a inbox task."""
from dataclasses import dataclass
from typing import Final

from domain.inbox_tasks.infra.inbox_task_engine import InboxTaskEngine
from domain.inbox_tasks.infra.inbox_task_notion_manager import InboxTaskNotionManager
from domain.inbox_tasks.service.remove_service import InboxTaskRemoveService
from models.framework import Command, EntityId
from utils.time_provider import TimeProvider


class InboxTaskRemoveCommand(Command['InboxTaskRemoveCommand.Args', None]):
    """The command for removing a inbox task."""

    @dataclass()
    class Args:
        """Args."""
        ref_id: EntityId

    _time_provider: Final[TimeProvider]
    _inbox_task_engine: Final[InboxTaskEngine]
    _inbox_task_notion_manager: Final[InboxTaskNotionManager]

    def __init__(
            self, time_provider: TimeProvider, inbox_task_engine: InboxTaskEngine,
            inbox_task_notion_manager: InboxTaskNotionManager) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._inbox_task_engine = inbox_task_engine
        self._inbox_task_notion_manager = inbox_task_notion_manager

    def execute(self, args: Args) -> None:
        """Execute the command's action."""
        with self._inbox_task_engine.get_unit_of_work() as uow:
            inbox_task = uow.inbox_task_repository.load_by_id(args.ref_id)
        InboxTaskRemoveService(
            self._time_provider, self._inbox_task_engine, self._inbox_task_notion_manager).do_it(inbox_task)
