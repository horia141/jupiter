"""Service for hard removing a email task and associated inbox task."""

from jupiter.core.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.inbox_tasks.inbox_task_collection import InboxTaskCollection
from jupiter.core.domain.inbox_tasks.service.remove_service import (
    InboxTaskRemoveService,
)
from jupiter.core.domain.push_integrations.email.email_task import EmailTask
from jupiter.core.domain.push_integrations.email.email_task_collection import EmailTaskCollection
from jupiter.core.domain.push_integrations.group.push_integration_group import PushIntegrationGroup
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.use_case import ProgressReporter


class EmailTaskRemoveService:
    """Shared service for hard removing a email task."""

    async def do_it(
        self,
        ctx: DomainContext,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        email_task: EmailTask,
    ) -> None:
        """Execute the service's action."""
        email_task_collection = await uow.repository_for(EmailTaskCollection).load_by_id(
            email_task.email_task_collection.ref_id,
        )
        push_integration_group = await uow.repository_for(PushIntegrationGroup).load_by_id(
            email_task_collection.push_integration_group.ref_id,
        )
        inbox_task_collection = (
            await uow.repository_for(InboxTaskCollection).load_by_parent(
                push_integration_group.workspace.ref_id,
            )
        )
        inbox_tasks_to_remove = await uow.repository_for(InboxTask).find_all_generic(
            parent_ref_id=inbox_task_collection.ref_id,
            allow_archived=True,
            email_task_ref_id=[email_task.ref_id],
        )

        inbox_task_remove_service = InboxTaskRemoveService()
        for inbox_task in inbox_tasks_to_remove:
            await inbox_task_remove_service.do_it(
                ctx, uow, progress_reporter, inbox_task
            )

        await uow.repository_for(EmailTask).remove(email_task.ref_id)
        await progress_reporter.mark_removed(email_task)
