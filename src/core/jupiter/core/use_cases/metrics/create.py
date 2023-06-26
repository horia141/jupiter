"""The command for creating a metric."""
from dataclasses import dataclass
from typing import Optional

from jupiter.core.domain.difficulty import Difficulty
from jupiter.core.domain.eisen import Eisen
from jupiter.core.domain.entity_icon import EntityIcon
from jupiter.core.domain.metrics.metric import Metric
from jupiter.core.domain.metrics.metric_name import MetricName
from jupiter.core.domain.metrics.metric_unit import MetricUnit
from jupiter.core.domain.recurring_task_due_at_day import RecurringTaskDueAtDay
from jupiter.core.domain.recurring_task_due_at_month import RecurringTaskDueAtMonth
from jupiter.core.domain.recurring_task_due_at_time import RecurringTaskDueAtTime
from jupiter.core.domain.recurring_task_gen_params import RecurringTaskGenParams
from jupiter.core.domain.recurring_task_period import RecurringTaskPeriod
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
class MetricCreateArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    name: MetricName
    icon: Optional[EntityIcon] = None
    collection_period: Optional[RecurringTaskPeriod] = None
    collection_eisen: Optional[Eisen] = None
    collection_difficulty: Optional[Difficulty] = None
    collection_actionable_from_day: Optional[RecurringTaskDueAtDay] = None
    collection_actionable_from_month: Optional[RecurringTaskDueAtMonth] = None
    collection_due_at_time: Optional[RecurringTaskDueAtTime] = None
    collection_due_at_day: Optional[RecurringTaskDueAtDay] = None
    collection_due_at_month: Optional[RecurringTaskDueAtMonth] = None
    metric_unit: Optional[MetricUnit] = None


@dataclass
class MetricCreateResult(UseCaseResultBase):
    """MetricCreate result."""

    new_metric: Metric


class MetricCreateUseCase(
    AppLoggedInMutationUseCase[MetricCreateArgs, MetricCreateResult]
):
    """The command for creating a metric."""

    async def _execute(
        self,
        progress_reporter: ContextProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: MetricCreateArgs,
    ) -> MetricCreateResult:
        """Execute the command's action."""
        workspace = context.workspace

        async with progress_reporter.start_creating_entity(
            "metric",
            str(args.name),
        ) as entity_reporter:
            collection_params = None
            async with self._storage_engine.get_unit_of_work() as uow:
                metric_collection = (
                    await uow.metric_collection_repository.load_by_parent(
                        workspace.ref_id,
                    )
                )

                if args.collection_period is not None:
                    collection_params = RecurringTaskGenParams(
                        period=args.collection_period,
                        eisen=args.collection_eisen,
                        difficulty=args.collection_difficulty,
                        actionable_from_day=args.collection_actionable_from_day,
                        actionable_from_month=args.collection_actionable_from_month,
                        due_at_time=args.collection_due_at_time,
                        due_at_day=args.collection_due_at_day,
                        due_at_month=args.collection_due_at_month,
                    )

                new_metric = Metric.new_metric(
                    metric_collection_ref_id=metric_collection.ref_id,
                    name=args.name,
                    icon=args.icon,
                    collection_params=collection_params,
                    metric_unit=args.metric_unit,
                    source=EventSource.CLI,
                    created_time=self._time_provider.get_current_time(),
                )
                new_metric = await uow.metric_repository.create(new_metric)
                await entity_reporter.mark_known_entity_id(new_metric.ref_id)
                await entity_reporter.mark_local_change()

        return MetricCreateResult(new_metric=new_metric)