"""Remove a person."""
import logging
from typing import Final

from domain.inbox_tasks.infra.inbox_task_engine import InboxTaskEngine
from domain.inbox_tasks.infra.inbox_task_notion_manager import InboxTaskNotionManager
from domain.inbox_tasks.service.remove_service import InboxTaskRemoveService
from domain.prm.infra.prm_engine import PrmEngine
from domain.prm.infra.prm_notion_manager import PrmNotionManager
from domain.prm.person import Person
from remote.notion.common import CollectionEntityNotFound
from utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class PersonRemoveService:
    """The command for removing a person."""

    _time_provider: Final[TimeProvider]
    _prm_engine: Final[PrmEngine]
    _prm_notion_manager: Final[PrmNotionManager]
    _inbox_task_engine: Final[InboxTaskEngine]
    _inbox_task_notion_manager: Final[InboxTaskNotionManager]

    def __init__(
            self, time_provider: TimeProvider, prm_engine: PrmEngine,
            prm_notion_manager: PrmNotionManager,
            inbox_task_engine: InboxTaskEngine,
            inbox_task_notion_manager: InboxTaskNotionManager) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._prm_engine = prm_engine
        self._prm_notion_manager = prm_notion_manager
        self._inbox_task_engine = inbox_task_engine
        self._inbox_task_notion_manager = inbox_task_notion_manager

    def do_it(self, person: Person) -> None:
        """Execute the command's action."""
        with self._prm_engine.get_unit_of_work() as uow:
            uow.person_repository.remove(person.ref_id)

        with self._inbox_task_engine.get_unit_of_work() as inbox_task_uow:
            all_inbox_tasks = inbox_task_uow.inbox_task_repository.find_all(
                filter_person_ref_ids=[person.ref_id])

        inbox_task_remove_service = \
            InboxTaskRemoveService(self._time_provider, self._inbox_task_engine, self._inbox_task_notion_manager)
        for inbox_task in all_inbox_tasks:
            inbox_task_remove_service.do_it(inbox_task)

        try:
            self._prm_notion_manager.remove_person(person.ref_id)
        except CollectionEntityNotFound:
            LOGGER.warning("Skipping removal on Notion side because person was not found")
