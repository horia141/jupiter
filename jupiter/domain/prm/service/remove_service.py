"""Remove a person."""
import logging
from typing import Final

from jupiter.domain.inbox_tasks.infra.inbox_task_notion_manager import InboxTaskNotionManager
from jupiter.domain.inbox_tasks.service.remove_service import InboxTaskRemoveService
from jupiter.domain.prm.infra.prm_notion_manager import PrmNotionManager, NotionPersonNotFoundError
from jupiter.domain.prm.person import Person
from jupiter.domain.storage_engine import StorageEngine

LOGGER = logging.getLogger(__name__)


class PersonRemoveService:
    """The command for removing a person."""

    _storage_engine: Final[StorageEngine]
    _prm_notion_manager: Final[PrmNotionManager]
    _inbox_task_notion_manager: Final[InboxTaskNotionManager]

    def __init__(
            self, storage_engine: StorageEngine, prm_notion_manager: PrmNotionManager,
            inbox_task_notion_manager: InboxTaskNotionManager) -> None:
        """Constructor."""
        self._storage_engine = storage_engine
        self._prm_notion_manager = prm_notion_manager
        self._inbox_task_notion_manager = inbox_task_notion_manager

    def do_it(self, person: Person) -> None:
        """Execute the command's action."""
        with self._storage_engine.get_unit_of_work() as uow:
            uow.person_repository.remove(person.ref_id)
            all_inbox_tasks = uow.inbox_task_repository.find_all(
                filter_person_ref_ids=[person.ref_id])

        inbox_task_remove_service = \
            InboxTaskRemoveService(self._storage_engine, self._inbox_task_notion_manager)
        for inbox_task in all_inbox_tasks:
            inbox_task_remove_service.do_it(inbox_task)

        try:
            self._prm_notion_manager.remove_person(person.ref_id)
        except NotionPersonNotFoundError:
            LOGGER.warning("Skipping removal on Notion side because person was not found")
