"""The command for creating a metric entry."""
from dataclasses import dataclass
from typing import Iterable, Optional

from jupiter.core.domain.adate import ADate
from jupiter.core.domain.features import Feature
from jupiter.core.domain.metrics.metric_entry import MetricEntry
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.use_case import (
    ContextProgressReporter,
    UseCaseArgsBase,
    UseCaseResultBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCase,
    AppLoggedInUseCaseContext,
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
    AppLoggedInMutationUseCase[MetricEntryCreateArgs, MetricEntryCreateResult],
):
    """The command for creating a metric entry."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[Feature] | Feature | None:
        """The feature the use case is scope to."""
        return Feature.METRICS

    async def _perform_mutation(
        self,
        progress_reporter: ContextProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: MetricEntryCreateArgs,
    ) -> MetricEntryCreateResult:
        """Execute the command's action."""
        simple_name = (
            f"Entry for {ADate.to_user_date_str(args.collection_time)} value={args.value}"
            + (f"notes={args.notes}" if args.notes else "")
        )

        async with progress_reporter.start_creating_entity(
            "metric entry",
            simple_name,
        ) as entity_reporter:
            async with self._domain_storage_engine.get_unit_of_work() as uow:
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
                await entity_reporter.mark_known_entity(new_metric_entry)
                await entity_reporter.mark_local_change()

        return MetricEntryCreateResult(new_metric_entry=new_metric_entry)
