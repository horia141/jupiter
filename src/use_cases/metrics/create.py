"""The command for creating a metric."""
from dataclasses import dataclass
from typing import Optional, Final, List

from domain.difficulty import Difficulty
from domain.eisen import Eisen
from domain.entity_name import EntityName
from domain.errors import ServiceError
from domain.metrics.infra.metric_engine import MetricEngine
from domain.metrics.infra.metric_notion_manager import MetricNotionManager
from domain.metrics.metric import Metric
from domain.metrics.metric_key import MetricKey
from domain.metrics.metric_unit import MetricUnit
from domain.projects.infra.project_engine import ProjectEngine
from domain.projects.project_key import ProjectKey
from domain.recurring_task_due_at_day import RecurringTaskDueAtDay
from domain.recurring_task_due_at_month import RecurringTaskDueAtMonth
from domain.recurring_task_due_at_time import RecurringTaskDueAtTime
from domain.recurring_task_gen_params import RecurringTaskGenParams
from domain.recurring_task_period import RecurringTaskPeriod
from domain.workspaces.infra.workspace_engine import WorkspaceEngine
from models.framework import Command
from utils.time_provider import TimeProvider


class MetricCreateCommand(Command['MetricCreateCommand.Args', None]):
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
    _metric_engine: Final[MetricEngine]
    _notion_manager: Final[MetricNotionManager]
    _workspace_engine: Final[WorkspaceEngine]
    _project_engine_: Final[ProjectEngine]

    def __init__(
            self, time_provider: TimeProvider, metric_engine: MetricEngine,
            notion_manager: MetricNotionManager, workspace_engine: WorkspaceEngine,
            projects_engine_: ProjectEngine) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._metric_engine = metric_engine
        self._notion_manager = notion_manager
        self._workspace_engine = workspace_engine
        self._project_engine_ = projects_engine_

    def execute(self, args: Args) -> None:
        """Execute the command's action."""
        if args.collection_period is None and args.collection_project_key is not None:
            raise ServiceError("Cannot specify a collection project if no period is given")

        collection_params = None
        if args.collection_period is not None:
            if args.collection_project_key is not None:
                with self._project_engine_.get_unit_of_work() as project_uow:
                    project = project_uow.project_repository.load_by_key(args.collection_project_key)
                project_ref_id = project.ref_id
            else:
                with self._workspace_engine.get_unit_of_work() as uow:
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

        metric = Metric.new_metric(
            args.key, args.name, collection_params, args.metric_unit, self._time_provider.get_current_time())
        with self._metric_engine.get_unit_of_work() as metric_uow:
            metric = metric_uow.metric_repository.create(metric)
        self._notion_manager.upsert_metric(metric)
