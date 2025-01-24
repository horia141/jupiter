"""The command for creating a metric."""

from jupiter.core.domain.application.gen.service.gen_service import GenService
from jupiter.core.domain.concept.metrics.metric import Metric
from jupiter.core.domain.concept.metrics.metric_collection import MetricCollection
from jupiter.core.domain.concept.metrics.metric_name import MetricName
from jupiter.core.domain.concept.metrics.metric_unit import MetricUnit
from jupiter.core.domain.core.difficulty import Difficulty
from jupiter.core.domain.core.eisen import Eisen
from jupiter.core.domain.core.entity_icon import EntityIcon
from jupiter.core.domain.core.recurring_task_due_at_day import RecurringTaskDueAtDay
from jupiter.core.domain.core.recurring_task_due_at_month import RecurringTaskDueAtMonth
from jupiter.core.domain.core.recurring_task_gen_params import RecurringTaskGenParams
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.domain.sync_target import SyncTarget
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
    icon: EntityIcon | None
    collection_period: RecurringTaskPeriod | None
    collection_eisen: Eisen | None
    collection_difficulty: Difficulty | None
    collection_actionable_from_day: RecurringTaskDueAtDay | None
    collection_actionable_from_month: RecurringTaskDueAtMonth | None
    collection_due_at_day: RecurringTaskDueAtDay | None
    collection_due_at_month: RecurringTaskDueAtMonth | None
    metric_unit: MetricUnit | None


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
        metric_collection = await uow.get_for(MetricCollection).load_by_parent(
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
        new_metric = await uow.get_for(Metric).create(new_metric)
        await progress_reporter.mark_created(new_metric)

        return MetricCreateResult(new_metric=new_metric)

    async def _perform_post_mutation_work(
        self,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: MetricCreateArgs,
        result: MetricCreateResult,
    ) -> None:
        """Execute the command's post-mutation work."""
        if args.collection_period is None:
            return
        await GenService(self._domain_storage_engine).do_it(
            context.domain_context,
            progress_reporter=progress_reporter,
            user=context.user,
            workspace=context.workspace,
            gen_even_if_not_modified=False,
            today=self._time_provider.get_current_date(),
            gen_targets=[SyncTarget.METRICS],
            period=[args.collection_period],
            filter_metric_ref_ids=[result.new_metric.ref_id],
        )
