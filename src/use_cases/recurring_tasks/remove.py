"""The command for removing a recurring task."""
import logging
from dataclasses import dataclass
from typing import Final

from domain.inbox_tasks.infra.inbox_task_engine import InboxTaskEngine
from domain.inbox_tasks.infra.inbox_task_notion_manager import InboxTaskNotionManager
from domain.recurring_tasks.infra.recurring_task_engine import RecurringTaskEngine
from domain.recurring_tasks.infra.recurring_task_notion_manager import RecurringTaskNotionManager
from domain.recurring_tasks.service.remove_service import RecurringTaskRemoveService
from framework.entity_id import EntityId
from framework.use_case import UseCase
from utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class RecurringTaskRemoveUseCase(UseCase['RecurringTaskRemoveUseCase.Args', None]):
    """The command for removing a recurring task."""

    @dataclass()
    class Args:
        """Args."""
        ref_id: EntityId

    _time_provider: Final[TimeProvider]
    _inbox_task_engine: Final[InboxTaskEngine]
    _inbox_task_notion_manager: Final[InboxTaskNotionManager]
    _recurring_task_engine: Final[RecurringTaskEngine]
    _recurring_task_notion_manager: Final[RecurringTaskNotionManager]

    def __init__(
            self, time_provider: TimeProvider, inbox_task_engine: InboxTaskEngine,
            inbox_task_notion_manager: InboxTaskNotionManager, recurring_task_engine: RecurringTaskEngine,
            recurring_task_notion_manager: RecurringTaskNotionManager) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._inbox_task_engine = inbox_task_engine
        self._inbox_task_notion_manager = inbox_task_notion_manager
        self._recurring_task_engine = recurring_task_engine
        self._recurring_task_notion_manager = recurring_task_notion_manager

    def execute(self, args: Args) -> None:
        """Execute the command's action."""
        RecurringTaskRemoveService(
            self._time_provider, self._inbox_task_engine, self._inbox_task_notion_manager, self._recurring_task_engine,
            self._recurring_task_notion_manager).remove(args.ref_id)
