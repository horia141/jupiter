"""Service for archiving an email task and associated entities."""
import logging
from typing import Final

from jupiter.domain.inbox_tasks.infra.inbox_task_notion_manager import (
    InboxTaskNotionManager,
    NotionInboxTaskNotFoundError,
)
from jupiter.domain.push_integrations.email.email_task import EmailTask
from jupiter.domain.push_integrations.email.infra.email_task_notion_manager import (
    EmailTaskNotionManager,
    NotionEmailTaskNotFoundError,
)
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.framework.event import EventSource
from jupiter.framework.use_case import ProgressReporter, MarkProgressStatus
from jupiter.utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class EmailTaskArchiveService:
    """Shared service for archiving a email task."""

    _source: Final[EventSource]
    _time_provider: Final[TimeProvider]
    _storage_engine: Final[DomainStorageEngine]
    _inbox_task_notion_manager: Final[InboxTaskNotionManager]
    _email_task_notion_manager: Final[EmailTaskNotionManager]

    def __init__(
        self,
        source: EventSource,
        time_provider: TimeProvider,
        storage_engine: DomainStorageEngine,
        inbox_task_notion_manager: InboxTaskNotionManager,
        email_task_notion_manager: EmailTaskNotionManager,
    ) -> None:
        """Constructor."""
        self._source = source
        self._time_provider = time_provider
        self._storage_engine = storage_engine
        self._inbox_task_notion_manager = inbox_task_notion_manager
        self._email_task_notion_manager = email_task_notion_manager

    def do_it(self, progress_reporter: ProgressReporter, email_task: EmailTask) -> None:
        """Execute the service's action."""
        if email_task.archived:
            return

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

            inbox_tasks_to_archive = uow.inbox_task_repository.find_all_with_filters(
                parent_ref_id=inbox_task_collection.ref_id,
                allow_archived=False,
                filter_email_task_ref_ids=[email_task.ref_id],
            )

        for inbox_task in inbox_tasks_to_archive:
            with progress_reporter.start_archiving_entity(
                "inbox task", inbox_task.ref_id, str(inbox_task.name)
            ) as entity_reporter:
                with self._storage_engine.get_unit_of_work() as uow:
                    inbox_task = inbox_task.mark_archived(
                        self._source, self._time_provider.get_current_time()
                    )
                    uow.inbox_task_repository.save(inbox_task)
                    entity_reporter.mark_local_change()

                try:
                    self._inbox_task_notion_manager.remove_leaf(
                        inbox_task.inbox_task_collection_ref_id, inbox_task.ref_id
                    )
                    entity_reporter.mark_remote_change()
                except NotionInboxTaskNotFoundError:
                    # If we can't find this locally it means it's already gone
                    LOGGER.info(
                        "Skipping archival on Notion side because inbox task was not found"
                    )
                    entity_reporter.mark_remote_change(MarkProgressStatus.FAILED)

        with progress_reporter.start_archiving_entity(
            "email task", email_task.ref_id, str(email_task.simple_name)
        ) as entity_reporter:
            with self._storage_engine.get_unit_of_work() as uow:
                email_task = email_task.mark_archived(
                    self._source, self._time_provider.get_current_time()
                )
                uow.email_task_repository.save(email_task)
                entity_reporter.mark_local_change()

            try:
                self._email_task_notion_manager.remove_leaf(
                    email_task.email_task_collection_ref_id, email_task.ref_id
                )
                entity_reporter.mark_remote_change()
            except NotionEmailTaskNotFoundError:
                # If we can't find this locally it means it's already gone
                LOGGER.info(
                    "Skipping archival on Notion side because Email task was not found"
                )
                entity_reporter.mark_remote_change(MarkProgressStatus.FAILED)
