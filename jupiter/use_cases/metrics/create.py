"""The command for creating a metric."""
from dataclasses import dataclass
from typing import Optional, Final

from jupiter.domain.difficulty import Difficulty
from jupiter.domain.eisen import Eisen
from jupiter.domain.metrics.infra.metric_notion_manager import MetricNotionManager
from jupiter.domain.metrics.infra.metric_repository import MetricAlreadyExistsError
from jupiter.domain.metrics.metric import Metric
from jupiter.domain.metrics.metric_key import MetricKey
from jupiter.domain.metrics.metric_name import MetricName
from jupiter.domain.metrics.metric_unit import MetricUnit
from jupiter.domain.metrics.notion_metric import NotionMetric
from jupiter.domain.projects.project_key import ProjectKey
from jupiter.domain.recurring_task_due_at_day import RecurringTaskDueAtDay
from jupiter.domain.recurring_task_due_at_month import RecurringTaskDueAtMonth
from jupiter.domain.recurring_task_due_at_time import RecurringTaskDueAtTime
from jupiter.domain.recurring_task_gen_params import RecurringTaskGenParams
from jupiter.domain.recurring_task_period import RecurringTaskPeriod
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.framework.errors import InputValidationError
from jupiter.framework.event import EventSource
from jupiter.framework.use_case import MutationUseCaseInvocationRecorder, UseCaseArgsBase
from jupiter.use_cases.infra.use_cases import AppMutationUseCase, AppUseCaseContext
from jupiter.utils.time_provider import TimeProvider


class MetricCreateUseCase(AppMutationUseCase['MetricCreateUseCase.Args', None]):
    """The command for creating a metric."""

    @dataclass(frozen=True)
    class Args(UseCaseArgsBase):
        """Args."""
        key: MetricKey
        name: MetricName
        collection_project_key: Optional[ProjectKey]
        collection_period: Optional[RecurringTaskPeriod]
        collection_eisen: Optional[Eisen]
        collection_difficulty: Optional[Difficulty]
        collection_actionable_from_day: Optional[RecurringTaskDueAtDay]
        collection_actionable_from_month: Optional[RecurringTaskDueAtMonth]
        collection_due_at_time: Optional[RecurringTaskDueAtTime]
        collection_due_at_day: Optional[RecurringTaskDueAtDay]
        collection_due_at_month: Optional[RecurringTaskDueAtMonth]
        metric_unit: Optional[MetricUnit]

    _metric_notion_manager: Final[MetricNotionManager]

    def __init__(
            self,
            time_provider: TimeProvider,
            invocation_recorder: MutationUseCaseInvocationRecorder,
            storage_engine: DomainStorageEngine,
            metric_notion_manager: MetricNotionManager) -> None:
        """Constructor."""
        super().__init__(time_provider, invocation_recorder, storage_engine)
        self._metric_notion_manager = metric_notion_manager

    def _execute(self, context: AppUseCaseContext, args: Args) -> None:
        """Execute the command's action."""
        if args.collection_period is None and args.collection_project_key is not None:
            raise InputValidationError("Cannot specify a collection project if no period is given")

        collection_params = None
        with self._storage_engine.get_unit_of_work() as uow:
            workspace = uow.workspace_repository.load()

            if args.collection_period is not None:
                if args.collection_project_key is not None:
                    project = uow.project_repository.load_by_key(args.collection_project_key)
                    project_ref_id = project.ref_id
                else:
                    project_ref_id = workspace.default_project_ref_id
                collection_params = RecurringTaskGenParams(
                    project_ref_id=project_ref_id,
                    period=args.collection_period,
                    eisen=args.collection_eisen if args.collection_eisen else Eisen.REGULAR,
                    difficulty=args.collection_difficulty,
                    actionable_from_day=args.collection_actionable_from_day,
                    actionable_from_month=args.collection_actionable_from_month,
                    due_at_time=args.collection_due_at_time,
                    due_at_day=args.collection_due_at_day,
                    due_at_month=args.collection_due_at_month)

            try:
                metric = Metric.new_metric(
                    workspace_ref_id=workspace.ref_id, key=args.key, name=args.name,
                    collection_params=collection_params, metric_unit=args.metric_unit, source=EventSource.CLI,
                    created_time=self._time_provider.get_current_time())
                metric = uow.metric_repository.create(metric)
            except MetricAlreadyExistsError as err:
                raise InputValidationError(f"Metric with key {metric.key} already exists") from err

        notion_metric = NotionMetric.new_notion_row(metric)
        self._metric_notion_manager.upsert_metric(notion_metric)
