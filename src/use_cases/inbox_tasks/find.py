"""The command for finding a inbox task."""
from dataclasses import dataclass
from typing import Optional, Iterable, List, Final

from domain.big_plans.big_plan import BigPlan
from domain.big_plans.infra.big_plan_engine import BigPlanEngine
from domain.inbox_tasks.inbox_task import InboxTask
from domain.inbox_tasks.inbox_task_source import InboxTaskSource
from domain.inbox_tasks.infra.inbox_task_engine import InboxTaskEngine
from domain.metrics.infra.metric_engine import MetricEngine
from domain.metrics.metric import Metric
from domain.prm.infra.prm_engine import PrmEngine
from domain.prm.person import Person
from domain.projects.infra.project_engine import ProjectEngine
from domain.projects.project_key import ProjectKey
from domain.recurring_tasks.infra.recurring_task_engine import RecurringTaskEngine
from domain.recurring_tasks.recurring_task import RecurringTask
from framework.entity_id import EntityId
from framework.use_case import UseCase


class InboxTaskFindUseCase(UseCase['InboxTaskFindUseCase.Args', 'InboxTaskFindUseCase.Result']):
    """The command for finding a inbox task."""

    @dataclass()
    class Args:
        """Args."""
        filter_ref_ids: Optional[Iterable[EntityId]]
        filter_project_keys: Optional[Iterable[ProjectKey]]
        filter_sources: Optional[Iterable[InboxTaskSource]]

    @dataclass()
    class ResultEntry:
        """A single entry in the load all inbox tasks response."""
        inbox_task: InboxTask
        big_plan: Optional[BigPlan]
        recurring_task: Optional[RecurringTask]
        metric: Optional[Metric]
        person: Optional[Person]

    @dataclass()
    class Result:
        """Result."""
        inbox_tasks: Iterable['InboxTaskFindUseCase.ResultEntry']

    _project_engine: Final[ProjectEngine]
    _inbox_task_engine: Final[InboxTaskEngine]
    _recurring_task_engine: Final[RecurringTaskEngine]
    _big_plan_engine: Final[BigPlanEngine]
    _metric_engine: Final[MetricEngine]
    _prm_engine: Final[PrmEngine]

    def __init__(
            self, project_engine: ProjectEngine,
            inbox_task_engine: InboxTaskEngine, recurring_task_engine: RecurringTaskEngine,
            big_plan_engine: BigPlanEngine, metric_engine: MetricEngine, prm_engine: PrmEngine) -> None:
        """Constructor."""
        self._project_engine = project_engine
        self._inbox_task_engine = inbox_task_engine
        self._recurring_task_engine = recurring_task_engine
        self._big_plan_engine = big_plan_engine
        self._metric_engine = metric_engine
        self._prm_engine = prm_engine

    def execute(self, args: Args) -> 'Result':
        """Execute the command's action."""
        filter_project_ref_ids: Optional[List[EntityId]] = None
        if args.filter_project_keys:
            with self._project_engine.get_unit_of_work() as project_uow:
                projects = project_uow.project_repository.find_all(filter_keys=args.filter_project_keys)
            filter_project_ref_ids = [p.ref_id for p in projects]

        with self._inbox_task_engine.get_unit_of_work() as inbox_task_uow:
            inbox_task_collections = \
                inbox_task_uow.inbox_task_collection_repository.find_all(filter_project_ref_ids=filter_project_ref_ids)
            inbox_tasks = inbox_task_uow.inbox_task_repository.find_all(
                filter_ref_ids=args.filter_ref_ids,
                filter_inbox_task_collection_ref_ids=[itc.ref_id for itc in inbox_task_collections],
                filter_sources=args.filter_sources)
        with self._recurring_task_engine.get_unit_of_work() as recurring_task_uow:
            recurring_tasks = recurring_task_uow.recurring_task_repository.find_all(
                filter_ref_ids=(it.recurring_task_ref_id for it in inbox_tasks if it.recurring_task_ref_id is not None))
        recurring_tasks_map = {rt.ref_id: rt for rt in recurring_tasks}
        with self._big_plan_engine.get_unit_of_work() as big_plan_uow:
            big_plans = big_plan_uow.big_plan_repository.find_all(
                filter_ref_ids=(it.big_plan_ref_id for it in inbox_tasks if it.big_plan_ref_id is not None))
        big_plans_map = {bp.ref_id: bp for bp in big_plans}
        with self._metric_engine.get_unit_of_work() as metric_uow:
            metrics = metric_uow.metric_repository.find_all(
                filter_ref_ids=(it.metric_ref_id for it in inbox_tasks if it.metric_ref_id is not None))
        metrics_map = {m.ref_id: m for m in metrics}
        with self._prm_engine.get_unit_of_work() as prm_uow:
            persons = prm_uow.person_repository.find_all(
                filter_ref_ids=(it.person_ref_id for it in inbox_tasks if it.person_ref_id is not None))
        persons_map = {p.ref_id: p for p in persons}
        return InboxTaskFindUseCase.Result(
            inbox_tasks=[
                InboxTaskFindUseCase.ResultEntry(
                    inbox_task=it,
                    big_plan=big_plans_map[it.big_plan_ref_id] if it.big_plan_ref_id is not None else None,
                    recurring_task=recurring_tasks_map[it.recurring_task_ref_id]
                    if it.recurring_task_ref_id is not None else None,
                    metric=metrics_map[it.metric_ref_id] if it.metric_ref_id is not None else None,
                    person=persons_map[it.person_ref_id] if it.person_ref_id is not None else None)
                for it in inbox_tasks])
