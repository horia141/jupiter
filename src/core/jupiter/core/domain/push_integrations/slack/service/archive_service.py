"""Service for archiving a Slack task and associated entities."""
from dataclasses import dataclass
from typing import Final

from jupiter.core.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.inbox_tasks.service.archive_service import (
    InboxTaskArchiveService,
)
from jupiter.core.domain.push_integrations.slack.slack_task import SlackTask
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.use_case import ProgressReporter
from jupiter.core.utils.time_provider import TimeProvider


@dataclass()
class SlackTaskArchiveServiceResult:
    """The result of the archive operation."""

    archived_inbox_tasks: list[InboxTask]


class SlackTaskArchiveService:
    """Shared service for archiving a slack task."""

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
        slack_task: SlackTask,
    ) -> SlackTaskArchiveServiceResult:
        """Execute the service's action."""
        if slack_task.archived:
            return SlackTaskArchiveServiceResult(archived_inbox_tasks=[])

        slack_task_collection = await uow.slack_task_collection_repository.load_by_id(
            slack_task.slack_task_collection_ref_id,
        )
        push_integration_group = await uow.push_integration_group_repository.load_by_id(
            slack_task_collection.push_integration_group_ref_id,
        )
        inbox_task_collection = (
            await uow.inbox_task_collection_repository.load_by_parent(
                push_integration_group.workspace_ref_id,
            )
        )

        inbox_tasks_to_archive = await uow.inbox_task_repository.find_all_with_filters(
            parent_ref_id=inbox_task_collection.ref_id,
            allow_archived=False,
            filter_slack_task_ref_ids=[slack_task.ref_id],
        )

        archived_inbox_taskd = []

        inbox_task_archive_service = InboxTaskArchiveService(
            EventSource.CLI,
            self._time_provider,
        )
        for inbox_task in inbox_tasks_to_archive:
            if inbox_task.archived:
                continue
            await inbox_task_archive_service.do_it(uow, progress_reporter, inbox_task)
            archived_inbox_taskd.append(inbox_task)

        slack_task = slack_task.mark_archived(
            self._source,
            self._time_provider.get_current_time(),
        )
        await uow.slack_task_repository.save(slack_task)
        await progress_reporter.mark_updated(slack_task)

        return SlackTaskArchiveServiceResult(archived_inbox_tasks=archived_inbox_taskd)
