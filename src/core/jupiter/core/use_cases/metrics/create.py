"""The command for creating a metric."""
from typing import Optional

from jupiter.core.domain.core.difficulty import Difficulty
from jupiter.core.domain.core.eisen import Eisen
from jupiter.core.domain.core.entity_icon import EntityIcon
from jupiter.core.domain.core.recurring_task_due_at_day import RecurringTaskDueAtDay
from jupiter.core.domain.core.recurring_task_due_at_month import RecurringTaskDueAtMonth
from jupiter.core.domain.core.recurring_task_gen_params import RecurringTaskGenParams
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.metrics.metric import Metric
from jupiter.core.domain.metrics.metric_name import MetricName
from jupiter.core.domain.metrics.metric_unit import MetricUnit
from jupiter.core.domain.storage_engine import DomainUnitOfWork
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
class MetricCreateArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    name: MetricName
    icon: Optional[EntityIcon] = None
    collection_period: Optional[RecurringTaskPeriod] = None
    collection_eisen: Optional[Eisen] = None
    collection_difficulty: Optional[Difficulty] = None
    collection_actionable_from_day: Optional[RecurringTaskDueAtDay] = None
    collection_actionable_from_month: Optional[RecurringTaskDueAtMonth] = None
    collection_due_at_day: Optional[RecurringTaskDueAtDay] = None
    collection_due_at_month: Optional[RecurringTaskDueAtMonth] = None
    metric_unit: Optional[MetricUnit] = None


@use_case_result
class MetricCreateResult(UseCaseResultBase):
    """MetricCreate result."""

    new_metric: Metric


@mutation_use_case(WorkspaceFeature.METRICS)
class MetricCreateUseCase(
    AppTransactionalLoggedInMutationUseCase[MetricCreateArgs, MetricCreateResult]
):
    """The command for creating a metric."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: MetricCreateArgs,
    ) -> MetricCreateResult:
        """Execute the command's action."""
        workspace = context.workspace

        collection_params = None
        metric_collection = await uow.metric_collection_repository.load_by_parent(
            workspace.ref_id,
        )

        if args.collection_period is not None:
            collection_params = RecurringTaskGenParams(
                period=args.collection_period,
                eisen=args.collection_eisen,
                difficulty=args.collection_difficulty,
                actionable_from_day=args.collection_actionable_from_day,
                actionable_from_month=args.collection_actionable_from_month,
                due_at_day=args.collection_due_at_day,
                due_at_month=args.collection_due_at_month,
            )

        new_metric = Metric.new_metric(
            context.domain_context,
            metric_collection_ref_id=metric_collection.ref_id,
            name=args.name,
            icon=args.icon,
            collection_params=collection_params,
            metric_unit=args.metric_unit,
        )
        new_metric = await uow.metric_repository.create(new_metric)
        await progress_reporter.mark_created(new_metric)

        return MetricCreateResult(new_metric=new_metric)
