"""Service for archiving an email task and associated entities."""
from typing import Final

from jupiter.core.domain.inbox_tasks.service.archive_service import (
    InboxTaskArchiveService,
)
from jupiter.core.domain.push_integrations.email.email_task import EmailTask
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.use_case import ProgressReporter
from jupiter.core.utils.time_provider import TimeProvider


class EmailTaskArchiveService:
    """Shared service for archiving a email task."""

    _source: Final[EventSource]
    _time_provider: Final[TimeProvider]

    def __init__(
        self,
        source: EventSource,
        time_provider: TimeProvider,
    ) -> None:
        """Constructor."""
        self._source = source
        self._time_provider = time_provider

    async def do_it(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        email_task: EmailTask,
    ) -> None:
        """Execute the service's action."""
        if email_task.archived:
            return

        email_task_collection = await uow.email_task_collection_repository.load_by_id(
            email_task.email_task_collection_ref_id,
        )
        push_integration_group = await uow.push_integration_group_repository.load_by_id(
            email_task_collection.push_integration_group_ref_id,
        )
        inbox_task_collection = (
            await uow.inbox_task_collection_repository.load_by_parent(
                push_integration_group.workspace_ref_id,
            )
        )

        inbox_tasks_to_archive = await uow.inbox_task_repository.find_all_with_filters(
            parent_ref_id=inbox_task_collection.ref_id,
            allow_archived=False,
            filter_email_task_ref_ids=[email_task.ref_id],
        )

        inbox_task_archive_service = InboxTaskArchiveService(
            EventSource.CLI,
            self._time_provider,
        )
        for inbox_task in inbox_tasks_to_archive:
            await inbox_task_archive_service.do_it(uow, progress_reporter, inbox_task)

        email_task = email_task.mark_archived(
            self._source,
            self._time_provider.get_current_time(),
        )
        await uow.email_task_repository.save(email_task)
        await progress_reporter.mark_updated(email_task)
