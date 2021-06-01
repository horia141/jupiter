"""Archive a person."""
import logging
from typing import Final

from domain.prm.infra.prm_engine import PrmEngine
from domain.prm.infra.prm_notion_manager import PrmNotionManager
from models.framework import Command, EntityId
from remote.notion.common import CollectionEntityNotFound
from service.inbox_tasks import InboxTasksService
from utils.time_provider import TimeProvider


LOGGER = logging.getLogger(__name__)


class PersonArchiveCommand(Command[EntityId, None]):
    """The command for archiving a person."""

    _time_provider: Final[TimeProvider]
    _engine: Final[PrmEngine]
    _notion_manager: Final[PrmNotionManager]
    _inbox_tasks_service: Final[InboxTasksService]

    def __init__(
            self, time_provider: TimeProvider, engine: PrmEngine,
            notion_manager: PrmNotionManager, inbox_tasks_service: InboxTasksService) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._engine = engine
        self._notion_manager = notion_manager
        self._inbox_tasks_service = inbox_tasks_service

    def execute(self, args: EntityId) -> None:
        """Execute the command's action."""
        with self._engine.get_unit_of_work() as uow:
            person = uow.person_repository.get_by_id(args)

            for inbox_task in self._inbox_tasks_service.load_all_inbox_tasks(
                    filter_person_ref_ids=[person.ref_id]):
                self._inbox_tasks_service.archive_inbox_task(inbox_task.ref_id)

            person.mark_archived(archived_time=self._time_provider.get_current_time())
            uow.person_repository.save(person)

        try:
            self._notion_manager.remove_person(person.ref_id)
        except CollectionEntityNotFound:
            LOGGER.warning("Skipping archival on Notion side because person was not found")
