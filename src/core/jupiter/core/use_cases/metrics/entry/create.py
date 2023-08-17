"""The command for creating a metric entry."""
from dataclasses import dataclass
from typing import Iterable, Optional

from jupiter.core.domain.adate import ADate
from jupiter.core.domain.features import UserFeature, WorkspaceFeature
from jupiter.core.domain.metrics.metric_entry import MetricEntry
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.use_case import (
    ProgressReporter,
    UseCaseArgsBase,
    UseCaseResultBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
)


@dataclass
class MetricEntryCreateArgs(UseCaseArgsBase):
    """MetricEntryCreate args."""

    metric_ref_id: EntityId
    value: float
    collection_time: Optional[ADate] = None
    notes: Optional[str] = None


@dataclass
class MetricEntryCreateResult(UseCaseResultBase):
    """MetricEntryCreate result."""

    new_metric_entry: MetricEntry


class MetricEntryCreateUseCase(
    AppTransactionalLoggedInMutationUseCase[
        MetricEntryCreateArgs, MetricEntryCreateResult
    ],
):
    """The command for creating a metric entry."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[UserFeature] | UserFeature | Iterable[WorkspaceFeature] | WorkspaceFeature | None:
        """The feature the use case is scope to."""
        return WorkspaceFeature.METRICS

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: MetricEntryCreateArgs,
    ) -> MetricEntryCreateResult:
        """Execute the command's action."""
        metric = await uow.metric_repository.load_by_id(
            args.metric_ref_id,
        )
        collection_time = (
            args.collection_time
            if args.collection_time
            else ADate.from_timestamp(self._time_provider.get_current_time())
        )
        new_metric_entry = MetricEntry.new_metric_entry(
            archived=False,
            metric_ref_id=metric.ref_id,
            collection_time=collection_time,
            value=args.value,
            notes=args.notes,
            source=EventSource.CLI,
            created_time=self._time_provider.get_current_time(),
        )
        new_metric_entry = await uow.metric_entry_repository.create(
            new_metric_entry,
        )
        await progress_reporter.mark_created(new_metric_entry)

        return MetricEntryCreateResult(new_metric_entry=new_metric_entry)
