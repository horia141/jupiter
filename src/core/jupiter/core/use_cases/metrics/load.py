"""Use case for loading a metric."""
from dataclasses import dataclass
from typing import Iterable

from jupiter.core.domain.features import Feature
from jupiter.core.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.metrics.metric import Metric
from jupiter.core.domain.metrics.metric_entry import MetricEntry
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import (
    UseCaseArgsBase,
    UseCaseResultBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInReadonlyUseCase,
    AppLoggedInUseCaseContext,
)


@dataclass
class MetricLoadArgs(UseCaseArgsBase):
    """MetricLoadArgs."""

    ref_id: EntityId
    allow_archived: bool


@dataclass
class MetricLoadResult(UseCaseResultBase):
    """MetricLoadResult."""

    metric: Metric
    metric_entries: list[MetricEntry]
    metric_collection_inbox_tasks: list[InboxTask]


class MetricLoadUseCase(AppLoggedInReadonlyUseCase[MetricLoadArgs, MetricLoadResult]):
    """Use case for loading a metric."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[Feature] | Feature | None:
        """The feature the use case is scope to."""
        return Feature.METRICS

    async def _execute(
        self,
        context: AppLoggedInUseCaseContext,
        args: MetricLoadArgs,
    ) -> MetricLoadResult:
        """Execute the command's action."""
        async with self._storage_engine.get_unit_of_work() as uow:
            await uow.metric_collection_repository.load_by_parent(
                context.workspace.ref_id
            )

            metric = await uow.metric_repository.load_by_id(
                args.ref_id, allow_archived=args.allow_archived
            )
            metric_entries = await uow.metric_entry_repository.find_all(
                metric.ref_id, allow_archived=args.allow_archived
            )

            inbox_task_collection = (
                await uow.inbox_task_collection_repository.load_by_parent(
                    context.workspace.ref_id
                )
            )
            metric_collection_inbox_tasks = (
                await uow.inbox_task_repository.find_all_with_filters(
                    inbox_task_collection.ref_id,
                    allow_archived=True,
                    filter_sources=[InboxTaskSource.METRIC],
                    filter_metric_ref_ids=[metric.ref_id],
                )
            )

        return MetricLoadResult(
            metric=metric,
            metric_entries=metric_entries,
            metric_collection_inbox_tasks=metric_collection_inbox_tasks,
        )
