"""Shared logic for archiving a big plan."""
from dataclasses import dataclass
from typing import Final

from jupiter.core.domain.big_plans.big_plan import BigPlan
from jupiter.core.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.inbox_tasks.service.archive_service import (
    InboxTaskArchiveService,
)
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.use_case import ProgressReporter
from jupiter.core.utils.time_provider import TimeProvider


@dataclass()
class BigPlanArchiveServiceResult:
    """The result of the archive operation."""

    archived_inbox_tasks: list[InboxTask]


class BigPlanArchiveService:
    """Shared logic for archiving a big plan."""

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
        big_plan: BigPlan,
    ) -> BigPlanArchiveServiceResult:
        """Execute the service's action."""
        if big_plan.archived:
            return BigPlanArchiveServiceResult(archived_inbox_tasks=[])

        big_plan_collection = await uow.big_plan_collection_repository.load_by_id(
            big_plan.big_plan_collection_ref_id,
        )

        inbox_task_collection = (
            await uow.inbox_task_collection_repository.load_by_parent(
                big_plan_collection.workspace_ref_id,
            )
        )
        inbox_tasks_to_archive = await uow.inbox_task_repository.find_all_with_filters(
            parent_ref_id=inbox_task_collection.ref_id,
            allow_archived=False,
            filter_big_plan_ref_ids=[big_plan.ref_id],
        )

        archived_inbox_tasks = []

        inbox_task_archive_service = InboxTaskArchiveService(
            EventSource.CLI,
            self._time_provider,
        )
        for inbox_task in inbox_tasks_to_archive:
            if inbox_task.archived:
                continue
            await inbox_task_archive_service.do_it(uow, progress_reporter, inbox_task)
            archived_inbox_tasks.append(inbox_task)

        big_plan = big_plan.mark_archived(
            self._source,
            self._time_provider.get_current_time(),
        )
        await uow.big_plan_repository.save(big_plan)
        await progress_reporter.mark_updated(big_plan)

        return BigPlanArchiveServiceResult(archived_inbox_tasks=archived_inbox_tasks)
