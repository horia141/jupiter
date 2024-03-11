"""The command for creating a metric entry."""

from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.metrics.metric import Metric
from jupiter.core.domain.metrics.metric_entry import MetricEntry
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import (
    ProgressReporter,
)
from jupiter.core.framework.use_case_io import (
    UseCaseArgsBase,
    UseCaseResultBase,
    use_case_args,
    use_case_result,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
    mutation_use_case,
)


@use_case_args
class MetricEntryCreateArgs(UseCaseArgsBase):
    """MetricEntryCreate args."""

    metric_ref_id: EntityId
    value: float
    collection_time: ADate | None


@use_case_result
class MetricEntryCreateResult(UseCaseResultBase):
    """MetricEntryCreate result."""

    new_metric_entry: MetricEntry


@mutation_use_case(WorkspaceFeature.METRICS)
class MetricEntryCreateUseCase(
    AppTransactionalLoggedInMutationUseCase[
        MetricEntryCreateArgs, MetricEntryCreateResult
    ],
):
    """The command for creating a metric entry."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: MetricEntryCreateArgs,
    ) -> MetricEntryCreateResult:
        """Execute the command's action."""
        metric = await uow.get_for(Metric).load_by_id(
            args.metric_ref_id,
        )
        collection_time = (
            args.collection_time
            if args.collection_time
            else self._time_provider.get_current_date()
        )
        new_metric_entry = MetricEntry.new_metric_entry(
            context.domain_context,
            metric_ref_id=metric.ref_id,
            collection_time=collection_time,
            value=args.value,
        )
        new_metric_entry = await uow.get_for(MetricEntry).create(
            new_metric_entry,
        )
        await progress_reporter.mark_created(new_metric_entry)

        return MetricEntryCreateResult(new_metric_entry=new_metric_entry)
