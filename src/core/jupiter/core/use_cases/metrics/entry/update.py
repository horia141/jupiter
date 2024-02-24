"""The command for updating a metric entry's properties."""

from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.metrics.metric_entry import MetricEntry
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.update_action import UpdateAction
from jupiter.core.framework.use_case import (
    ProgressReporter,
)
from jupiter.core.framework.use_case_io import UseCaseArgsBase, use_case_args
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
    mutation_use_case,
)


@use_case_args
class MetricEntryUpdateArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId
    collection_time: UpdateAction[ADate]
    value: UpdateAction[float]


@mutation_use_case(WorkspaceFeature.METRICS)
class MetricEntryUpdateUseCase(
    AppTransactionalLoggedInMutationUseCase[MetricEntryUpdateArgs, None]
):
    """The command for updating a metric entry's properties."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: MetricEntryUpdateArgs,
    ) -> None:
        """Execute the command's action."""
        metric_entry = await uow.repository_for(MetricEntry).load_by_id(args.ref_id)

        metric_entry = metric_entry.update(
            ctx=context.domain_context,
            collection_time=args.collection_time,
            value=args.value,
        )

        await uow.repository_for(MetricEntry).save(metric_entry)
        await progress_reporter.mark_updated(metric_entry)
