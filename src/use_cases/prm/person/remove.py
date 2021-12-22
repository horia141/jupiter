"""Remove a person."""
import logging
from typing import Final

from domain.inbox_tasks.infra.inbox_task_engine import InboxTaskEngine
from domain.inbox_tasks.infra.inbox_task_notion_manager import InboxTaskNotionManager
from domain.prm.infra.prm_engine import PrmEngine
from domain.prm.infra.prm_notion_manager import PrmNotionManager
from domain.prm.service.remove_service import PersonRemoveService
from models.framework import Command, EntityId
from utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class PersonRemoveCommand(Command[EntityId, None]):
    """The command for removing a person."""

    _time_provider: Final[TimeProvider]
    _prm_engine: Final[PrmEngine]
    _prm_notion_manager: Final[PrmNotionManager]
    _inbox_task_engine: Final[InboxTaskEngine]
    _inbox_task_notion_manager: Final[InboxTaskNotionManager]

    def __init__(
            self, time_provider: TimeProvider, inbox_task_engine: InboxTaskEngine,
            inbox_task_notion_manager: InboxTaskNotionManager, prm_engine: PrmEngine,
            prm_notion_manager: PrmNotionManager) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._prm_engine = prm_engine
        self._prm_notion_manager = prm_notion_manager
        self._inbox_task_engine = inbox_task_engine
        self._inbox_task_notion_manager = inbox_task_notion_manager

    def execute(self, args: EntityId) -> None:
        """Execute the command's action."""
        with self._prm_engine.get_unit_of_work() as uow:
            person = uow.person_repository.load_by_id(args)

        PersonRemoveService(
            self._time_provider, self._prm_engine, self._prm_notion_manager, self._inbox_task_engine,
            self._inbox_task_notion_manager).do_it(person)
