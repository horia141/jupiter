"""Archive a person."""
import logging
from typing import Final

from domain.inbox_tasks.infra.inbox_task_engine import InboxTaskEngine
from domain.inbox_tasks.infra.inbox_task_notion_manager import InboxTaskNotionManager
from domain.inbox_tasks.service.archive_service import InboxTaskArchiveService
from domain.prm.infra.prm_engine import PrmEngine
from domain.prm.infra.prm_notion_manager import PrmNotionManager
from framework.base.entity_id import EntityId
from framework.use_case import UseCase
from remote.notion.common import CollectionEntityNotFound
from utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class PersonArchiveUseCase(UseCase[EntityId, None]):
    """The command for archiving a person."""

    _time_provider: Final[TimeProvider]
    _inbox_task_engine: Final[InboxTaskEngine]
    _inbox_task_notion_manager: Final[InboxTaskNotionManager]
    _prm_engine: Final[PrmEngine]
    _prm_notion_manager: Final[PrmNotionManager]

    def __init__(
            self, time_provider: TimeProvider, inbox_task_engine: InboxTaskEngine,
            inbox_task_notion_manager: InboxTaskNotionManager, prm_engine: PrmEngine,
            prm_notion_manager: PrmNotionManager) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._inbox_task_engine = inbox_task_engine
        self._inbox_task_notion_manager = inbox_task_notion_manager
        self._prm_engine = prm_engine
        self._prm_notion_manager = prm_notion_manager

    def execute(self, args: EntityId) -> None:
        """Execute the command's action."""
        with self._prm_engine.get_unit_of_work() as uow:
            person = uow.person_repository.load_by_id(args)

            person.mark_archived(archived_time=self._time_provider.get_current_time())
            uow.person_repository.save(person)

        with self._inbox_task_engine.get_unit_of_work() as inbox_task_uow:
            all_inbox_tasks = inbox_task_uow.inbox_task_repository.find_all(
                filter_metric_ref_ids=[person.ref_id])

        inbox_task_archive_service = InboxTaskArchiveService(
            self._time_provider, self._inbox_task_engine, self._inbox_task_notion_manager)
        for inbox_task in all_inbox_tasks:
            inbox_task_archive_service.do_it(inbox_task)

        try:
            self._prm_notion_manager.remove_person(person.ref_id)
        except CollectionEntityNotFound:
            LOGGER.warning("Skipping archival on Notion side because person was not found")
