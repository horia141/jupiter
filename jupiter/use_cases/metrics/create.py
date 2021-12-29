"""The command for creating a metric."""
from dataclasses import dataclass
from typing import Optional, Final, List

from jupiter.domain.difficulty import Difficulty
from jupiter.domain.eisen import Eisen
from jupiter.domain.entity_name import EntityName
from jupiter.domain.metrics.infra.metric_notion_manager import MetricNotionManager
from jupiter.domain.metrics.infra.metric_repository import MetricAlreadyExistsError
from jupiter.domain.metrics.metric import Metric
from jupiter.domain.metrics.metric_key import MetricKey
from jupiter.domain.metrics.metric_unit import MetricUnit
from jupiter.domain.metrics.notion_metric import NotionMetric
from jupiter.domain.projects.project_key import ProjectKey
from jupiter.domain.recurring_task_due_at_day import RecurringTaskDueAtDay
from jupiter.domain.recurring_task_due_at_month import RecurringTaskDueAtMonth
from jupiter.domain.recurring_task_due_at_time import RecurringTaskDueAtTime
from jupiter.domain.recurring_task_gen_params import RecurringTaskGenParams
from jupiter.domain.recurring_task_period import RecurringTaskPeriod
from jupiter.domain.storage_engine import StorageEngine
from jupiter.framework.errors import InputValidationError
from jupiter.framework.use_case import UseCase
from jupiter.utils.time_provider import TimeProvider


class MetricCreateUseCase(UseCase['MetricCreateUseCase.Args', None]):
    """The command for creating a metric."""

    @dataclass()
    class Args:
        """Args."""
        key: MetricKey
        name: EntityName
        collection_project_key: Optional[ProjectKey]
        collection_period: Optional[RecurringTaskPeriod]
        collection_eisen: List[Eisen]
        collection_difficulty: Optional[Difficulty]
        collection_actionable_from_day: Optional[RecurringTaskDueAtDay]
        collection_actionable_from_month: Optional[RecurringTaskDueAtMonth]
        collection_due_at_time: Optional[RecurringTaskDueAtTime]
        collection_due_at_day: Optional[RecurringTaskDueAtDay]
        collection_due_at_month: Optional[RecurringTaskDueAtMonth]
        metric_unit: Optional[MetricUnit]

    _time_provider: Final[TimeProvider]
    _storage_engine: Final[StorageEngine]
    _metric_notion_manager: Final[MetricNotionManager]

    def __init__(
            self, time_provider: TimeProvider, storage_engine: StorageEngine,
            metric_notion_manager: MetricNotionManager) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._storage_engine = storage_engine
        self._metric_notion_manager = metric_notion_manager

    def execute(self, args: Args) -> None:
        """Execute the command's action."""
        if args.collection_period is None and args.collection_project_key is not None:
            raise InputValidationError("Cannot specify a collection project if no period is given")

        collection_params = None
        with self._storage_engine.get_unit_of_work() as uow:
            if args.collection_period is not None:
                if args.collection_project_key is not None:
                    project = uow.project_repository.load_by_key(args.collection_project_key)
                    project_ref_id = project.ref_id
                else:
                    workspace = uow.workspace_repository.load()
                    project_ref_id = workspace.default_project_ref_id
                collection_params = RecurringTaskGenParams(
                    project_ref_id=project_ref_id,
                    period=args.collection_period,
                    eisen=args.collection_eisen,
                    difficulty=args.collection_difficulty,
                    actionable_from_day=args.collection_actionable_from_day,
                    actionable_from_month=args.collection_actionable_from_month,
                    due_at_time=args.collection_due_at_time,
                    due_at_day=args.collection_due_at_day,
                    due_at_month=args.collection_due_at_month)

            try:
                metric = Metric.new_metric(
                    args.key, args.name, collection_params, args.metric_unit, self._time_provider.get_current_time())
                metric = uow.metric_repository.create(metric)
            except MetricAlreadyExistsError:
                raise InputValidationError(f"Metric with key {metric.key} already exists")

        notion_metric = NotionMetric.new_notion_row(metric)
        self._metric_notion_manager.upsert_metric(notion_metric)
