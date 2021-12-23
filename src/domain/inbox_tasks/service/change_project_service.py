"""Service for changing the project of an inbox task."""
import logging
from typing import Final

import remote
from domain.inbox_tasks.inbox_task import InboxTask
from domain.inbox_tasks.infra.inbox_task_engine import InboxTaskEngine
from domain.inbox_tasks.infra.inbox_task_notion_manager import InboxTaskNotionManager
from domain.inbox_tasks.notion_inbox_task import NotionInboxTask
from framework.entity_id import EntityId
from utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class InboxTaskChangeProjectService:
    """Service for changing the project of an inbox task."""

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

    def do_it(self, inbox_task: InboxTask, project_ref_id: EntityId) -> None:
        """Execute the service's action."""
        old_project_ref_id = inbox_task.project_ref_id
        try:
            self._inbox_task_notion_manager.hard_remove_inbox_task(old_project_ref_id, inbox_task.ref_id)
            LOGGER.info("Applied Notion changes")
        except remote.notion.common.CollectionEntityNotFound:
            LOGGER.info("Skipping hard removal on Notion side since inbox task could not be found")

        with self._inbox_task_engine.get_unit_of_work() as uow:
            inbox_task_collection = uow.inbox_task_collection_repository.load_by_project(project_ref_id)
            inbox_task.change_project(inbox_task_collection, self._time_provider.get_current_time())
            uow.inbox_task_repository.save(inbox_task)

        notion_inbox_task = NotionInboxTask.new_notion_row(inbox_task, NotionInboxTask.DirectInfo(None))
        self._inbox_task_notion_manager.upsert_inbox_task(inbox_task_collection, notion_inbox_task)
        LOGGER.info("Applied Notion changes")
