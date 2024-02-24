"""Service for archiving a Slack task and associated entities."""

from jupiter.core.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.inbox_tasks.inbox_task_collection import InboxTaskCollection
from jupiter.core.domain.inbox_tasks.service.archive_service import (
    InboxTaskArchiveService,
)
from jupiter.core.domain.push_integrations.group.push_integration_group import PushIntegrationGroup
from jupiter.core.domain.push_integrations.slack.slack_task import SlackTask
from jupiter.core.domain.push_integrations.slack.slack_task_collection import SlackTaskCollection
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.use_case import ProgressReporter
from jupiter.core.framework.value import CompositeValue, value


@value
class SlackTaskArchiveServiceResult(CompositeValue):
    """The result of the archive operation."""

    archived_inbox_tasks: list[InboxTask]


class SlackTaskArchiveService:
    """Shared service for archiving a slack task."""

    async def do_it(
        self,
        ctx: DomainContext,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        slack_task: SlackTask,
    ) -> SlackTaskArchiveServiceResult:
        """Execute the service's action."""
        if slack_task.archived:
            return SlackTaskArchiveServiceResult(archived_inbox_tasks=[])

        slack_task_collection = await uow.repository_for(SlackTaskCollection).load_by_id(
            slack_task.slack_task_collection.ref_id,
        )
        push_integration_group = await uow.repository_for(PushIntegrationGroup).load_by_id(
            slack_task_collection.push_integration_group.ref_id,
        )
        inbox_task_collection = (
            await uow.repository_for(InboxTaskCollection).load_by_parent(
                push_integration_group.workspace.ref_id,
            )
        )

        inbox_tasks_to_archive = await uow.repository_for(InboxTask).find_all_with_filters(
            parent_ref_id=inbox_task_collection.ref_id,
            allow_archived=False,
            filter_slack_task_ref_ids=[slack_task.ref_id],
        )

        archived_inbox_taskd = []

        inbox_task_archive_service = InboxTaskArchiveService()
        for inbox_task in inbox_tasks_to_archive:
            await inbox_task_archive_service.do_it(
                ctx, uow, progress_reporter, inbox_task
            )
            archived_inbox_taskd.append(inbox_task)

        slack_task = slack_task.mark_archived(ctx)
        await uow.repository_for(SlackTask).save(slack_task)
        await progress_reporter.mark_updated(slack_task)

        return SlackTaskArchiveServiceResult(archived_inbox_tasks=archived_inbox_taskd)
