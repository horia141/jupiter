"""Service for changing the project of an inbox task."""
import logging
from typing import Final

from jupiter.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.domain.inbox_tasks.infra.inbox_task_notion_manager import InboxTaskNotionManager, \
    NotionInboxTaskNotFoundError
from jupiter.domain.inbox_tasks.notion_inbox_task import NotionInboxTask
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.event import EventSource
from jupiter.utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class InboxTaskChangeProjectService:
    """Service for changing the project of an inbox task."""

    _source: Final[EventSource]
    _time_provider: Final[TimeProvider]
    _storage_engine: Final[DomainStorageEngine]
    _inbox_task_notion_manager: Final[InboxTaskNotionManager]

    def __init__(
            self, source: EventSource, time_provider: TimeProvider, storage_engine: DomainStorageEngine,
            inbox_task_notion_manager: InboxTaskNotionManager) -> None:
        """Constructor."""
        self._source = source
        self._time_provider = time_provider
        self._storage_engine = storage_engine
        self._inbox_task_notion_manager = inbox_task_notion_manager

    def do_it(self, inbox_task: InboxTask, project_ref_id: EntityId) -> None:
        """Execute the service's action."""
        try:
            self._inbox_task_notion_manager.remove_inbox_task(
                inbox_task.inbox_task_collection_ref_id, inbox_task.ref_id)
            LOGGER.info("Applied Notion changes")
        except NotionInboxTaskNotFoundError:
            LOGGER.info("Skipping hard removal on Notion side since inbox task could not be found")

        with self._storage_engine.get_unit_of_work() as uow:
            inbox_task_collection = uow.inbox_task_collection_repository.load_by_project(project_ref_id)
            inbox_task = inbox_task.change_project(
                inbox_task_collection=inbox_task_collection, source=EventSource.CLI,
                modification_time=self._time_provider.get_current_time())
            uow.inbox_task_repository.save(inbox_task)

        notion_inbox_task = NotionInboxTask.new_notion_row(inbox_task, NotionInboxTask.DirectInfo(None))
        self._inbox_task_notion_manager.upsert_inbox_task(inbox_task_collection.ref_id, notion_inbox_task)
        LOGGER.info("Applied Notion changes")
