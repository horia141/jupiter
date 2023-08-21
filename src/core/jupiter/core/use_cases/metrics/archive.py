"""The command for archiving a metric."""
from dataclasses import dataclass
from typing import Iterable

from jupiter.core.domain.features import UserFeature, WorkspaceFeature
from jupiter.core.domain.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.inbox_tasks.service.archive_service import (
    InboxTaskArchiveService,
)
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.use_case import (
    ProgressReporter,
    UseCaseArgsBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
)


@dataclass
class MetricArchiveArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId


class MetricArchiveUseCase(
    AppTransactionalLoggedInMutationUseCase[MetricArchiveArgs, None]
):
    """The command for archiving a metric."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[
        UserFeature
    ] | UserFeature | Iterable[WorkspaceFeature] | WorkspaceFeature | None:
        """The feature the use case is scope to."""
        return WorkspaceFeature.METRICS

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: MetricArchiveArgs,
    ) -> None:
        """Execute the command's action."""
        workspace = context.workspace

        inbox_task_collection = (
            await uow.inbox_task_collection_repository.load_by_parent(
                workspace.ref_id,
            )
        )

        metric = await uow.metric_repository.load_by_id(args.ref_id)
        metric_entries_to_archive = await uow.metric_entry_repository.find_all(
            parent_ref_id=metric.ref_id,
        )
        inbox_tasks_to_archive = await uow.inbox_task_repository.find_all_with_filters(
            parent_ref_id=inbox_task_collection.ref_id,
            filter_sources=[InboxTaskSource.METRIC],
            filter_metric_ref_ids=[metric.ref_id],
        )

        inbox_task_archive_service = InboxTaskArchiveService(
            source=EventSource.CLI,
            time_provider=self._time_provider,
        )
        for inbox_task in inbox_tasks_to_archive:
            await inbox_task_archive_service.do_it(uow, progress_reporter, inbox_task)

        for metric_entry in metric_entries_to_archive:
            metric_entry = metric_entry.mark_archived(
                EventSource.CLI,
                self._time_provider.get_current_time(),
            )
            await uow.metric_entry_repository.save(metric_entry)
            await progress_reporter.mark_updated(metric_entry)

        metric = metric.mark_archived(
            EventSource.CLI,
            self._time_provider.get_current_time(),
        )
        await uow.metric_repository.save(metric)
        await progress_reporter.mark_updated(metric)
