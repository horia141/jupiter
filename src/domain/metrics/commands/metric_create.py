"""The command for creating a metric."""
from dataclasses import dataclass
from typing import Optional, Final, List

from domain.metrics.infra.metric_engine import MetricEngine
from domain.metrics.metric import Metric
from domain.shared import RecurringTaskGenParams
from domain.metrics.infra.metric_notion_manager import MetricNotionManager
from models.basic import MetricKey, RecurringTaskPeriod, MetricUnit, EntityName, ProjectKey, Eisen, Difficulty
from models.framework import Command
from service.errors import ServiceError
from service.projects import ProjectsService
from service.workspaces import WorkspacesService
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
        collection_actionable_from_day: Optional[int]
        collection_actionable_from_month: Optional[int]
        collection_due_at_time: Optional[str]
        collection_due_at_day: Optional[int]
        collection_due_at_month: Optional[int]
        metric_unit: Optional[MetricUnit]

    _time_provider: Final[TimeProvider]
    _metric_engine: Final[MetricEngine]
    _notion_manager: Final[MetricNotionManager]
    _workspaces_service: Final[WorkspacesService]
    _projects_service: Final[ProjectsService]

    def __init__(
            self, time_provider: TimeProvider, metric_engine: MetricEngine,
            notion_manager: MetricNotionManager, workspaces_service: WorkspacesService,
            projects_service: ProjectsService) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._metric_engine = metric_engine
        self._notion_manager = notion_manager
        self._workspaces_service = workspaces_service
        self._projects_service = projects_service

    def execute(self, args: Args) -> None:
        """Execute the command's action."""
        if args.collection_period is None and args.collection_project_key is not None:
            raise ServiceError("Cannot specify a collection project if no period is given")

        collection_params = None
        if args.collection_period is not None:
            if args.collection_project_key is not None:
                project = self._projects_service.load_project_by_key(args.collection_project_key)
                project_ref_id = project.ref_id
            else:
                workspace = self._workspaces_service.load_workspace()
                if workspace.default_project_ref_id is None:
                    raise ServiceError("Cannot specify a collection period without a project (or a default one)")
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
        with self._metric_engine.get_unit_of_work() as uow:
            metric = uow.metric_repository.create(metric)
        self._notion_manager.upsert_metric(metric)
