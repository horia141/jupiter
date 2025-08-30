"""Service for archiving an email task and associated entities."""

from jupiter.core.domain.concept.inbox_tasks.inbox_task import (
    InboxTask,
    InboxTaskRepository,
)
from jupiter.core.domain.concept.inbox_tasks.inbox_task_collection import (
    InboxTaskCollection,
)
from jupiter.core.domain.concept.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.concept.inbox_tasks.service.archive_service import (
    InboxTaskArchiveService,
)
from jupiter.core.domain.concept.push_integrations.email.email_task import EmailTask
from jupiter.core.domain.concept.push_integrations.email.email_task_collection import (
    EmailTaskCollection,
)
from jupiter.core.domain.concept.push_integrations.group.push_integration_group import (
    PushIntegrationGroup,
)
from jupiter.core.domain.core.archival_reason import ArchivalReason
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.use_case import ProgressReporter
from jupiter.core.framework.value import CompositeValue, value


@value
class EmailTaskArchiveServiceResult(CompositeValue):
    """The result of the archive operation."""

    archived_inbox_tasks: list[InboxTask]


class EmailTaskArchiveService:
    """Shared service for archiving an email task."""

    async def do_it(
        self,
        ctx: DomainContext,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        email_task: EmailTask,
        archival_reason: ArchivalReason,
    ) -> EmailTaskArchiveServiceResult:
        """Execute the service's action."""
        if email_task.archived:
            return EmailTaskArchiveServiceResult(archived_inbox_tasks=[])

        email_task_collection = await uow.get_for(EmailTaskCollection).load_by_id(
            email_task.email_task_collection.ref_id,
        )
        push_integration_group = await uow.get_for(PushIntegrationGroup).load_by_id(
            email_task_collection.push_integration_group.ref_id,
        )
        inbox_task_collection = await uow.get_for(InboxTaskCollection).load_by_parent(
            push_integration_group.workspace.ref_id,
        )

        inbox_tasks_to_archive = await uow.get(
            InboxTaskRepository
        ).find_all_for_source_created_desc(
            parent_ref_id=inbox_task_collection.ref_id,
            allow_archived=False,
            source=InboxTaskSource.EMAIL_TASK,
            source_entity_ref_id=email_task.ref_id,
        )

        archived_inbox_tasks = []

        inbox_task_archive_service = InboxTaskArchiveService()
        for inbox_task in inbox_tasks_to_archive:
            await inbox_task_archive_service.do_it(
                ctx, uow, progress_reporter, inbox_task, archival_reason
            )
            archived_inbox_tasks.append(inbox_task)

        email_task = email_task.mark_archived(ctx, archival_reason)
        await uow.get_for(EmailTask).save(email_task)
        await progress_reporter.mark_updated(email_task)

        return EmailTaskArchiveServiceResult(archived_inbox_tasks=archived_inbox_tasks)
