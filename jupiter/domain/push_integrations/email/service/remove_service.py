"""Service for hard removing a email task and associated inbox task."""
import logging
from typing import Final

from jupiter.domain.inbox_tasks.infra.inbox_task_notion_manager import (
    InboxTaskNotionManager,
)
from jupiter.domain.inbox_tasks.service.remove_service import InboxTaskRemoveService
from jupiter.domain.push_integrations.email.infra.email_task_notion_manager import (
    EmailTaskNotionManager,
    NotionEmailTaskNotFoundError,
)
from jupiter.domain.push_integrations.email.email_task import EmailTask
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.framework.use_case import ProgressReporter, MarkProgressStatus

LOGGER = logging.getLogger(__name__)


class EmailTaskRemoveService:
    """Shared service for hard removing a email task."""

    _storage_engine: Final[DomainStorageEngine]
    _inbox_task_notion_manager: Final[InboxTaskNotionManager]
    _email_task_notion_manager: Final[EmailTaskNotionManager]

    def __init__(
        self,
        storage_engine: DomainStorageEngine,
        inbox_task_notion_manager: InboxTaskNotionManager,
        email_task_notion_manager: EmailTaskNotionManager,
    ) -> None:
        """Constructor."""
        self._storage_engine = storage_engine
        self._inbox_task_notion_manager = inbox_task_notion_manager
        self._email_task_notion_manager = email_task_notion_manager

    def do_it(self, progress_reporter: ProgressReporter, email_task: EmailTask) -> None:
        """Execute the service's action."""
        with self._storage_engine.get_unit_of_work() as uow:
            email_task_collection = uow.email_task_collection_repository.load_by_id(
                email_task.email_task_collection_ref_id
            )
            push_integration_group = uow.push_integration_group_repository.load_by_id(
                email_task_collection.push_integration_group_ref_id
            )
            inbox_task_collection = uow.inbox_task_collection_repository.load_by_parent(
                push_integration_group.workspace_ref_id
            )
            inbox_tasks_to_remove = uow.inbox_task_repository.find_all_with_filters(
                parent_ref_id=inbox_task_collection.ref_id,
                allow_archived=True,
                filter_email_task_ref_ids=[email_task.ref_id],
            )

        inbox_task_remove_service = InboxTaskRemoveService(
            self._storage_engine, self._inbox_task_notion_manager
        )
        for inbox_task in inbox_tasks_to_remove:
            inbox_task_remove_service.do_it(progress_reporter, inbox_task)

        with progress_reporter.start_removing_entity(
            "email task", email_task.ref_id, str(email_task.simple_name)
        ) as entity_reporter:
            with self._storage_engine.get_unit_of_work() as uow:
                uow.email_task_repository.remove(email_task.ref_id)
                entity_reporter.mark_local_change()

            try:
                self._email_task_notion_manager.remove_leaf(
                    email_task.email_task_collection_ref_id, email_task.ref_id
                )
                entity_reporter.mark_remote_change()
            except NotionEmailTaskNotFoundError:
                LOGGER.info(
                    "Skipping archival on Notion side because habit was not found"
                )
                entity_reporter.mark_remote_change(MarkProgressStatus.FAILED)
