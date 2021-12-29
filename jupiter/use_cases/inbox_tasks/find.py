"""The command for finding a inbox task."""
from dataclasses import dataclass
from typing import Optional, Iterable, List, Final

from jupiter.domain.big_plans.big_plan import BigPlan
from jupiter.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.domain.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.domain.metrics.metric import Metric
from jupiter.domain.prm.person import Person
from jupiter.domain.projects.project_key import ProjectKey
from jupiter.domain.recurring_tasks.recurring_task import RecurringTask
from jupiter.domain.storage_engine import StorageEngine
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.use_case import UseCase


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

    _storage_engine: Final[StorageEngine]

    def __init__(self, storage_engine: StorageEngine) -> None:
        """Constructor."""
        self._storage_engine = storage_engine

    def execute(self, args: Args) -> 'Result':
        """Execute the command's action."""
        with self._storage_engine.get_unit_of_work() as uow:
            filter_project_ref_ids: Optional[List[EntityId]] = None
            if args.filter_project_keys:
                projects = uow.project_repository.find_all(filter_keys=args.filter_project_keys)
                filter_project_ref_ids = [p.ref_id for p in projects]

            inbox_task_collections = \
                uow.inbox_task_collection_repository.find_all(filter_project_ref_ids=filter_project_ref_ids)
            inbox_tasks = uow.inbox_task_repository.find_all(
                filter_ref_ids=args.filter_ref_ids,
                filter_inbox_task_collection_ref_ids=[itc.ref_id for itc in inbox_task_collections],
                filter_sources=args.filter_sources)

            recurring_tasks = uow.recurring_task_repository.find_all(
                filter_ref_ids=(it.recurring_task_ref_id for it in inbox_tasks if it.recurring_task_ref_id is not None))
            recurring_tasks_map = {rt.ref_id: rt for rt in recurring_tasks}

            big_plans = uow.big_plan_repository.find_all(
                filter_ref_ids=(it.big_plan_ref_id for it in inbox_tasks if it.big_plan_ref_id is not None))
            big_plans_map = {bp.ref_id: bp for bp in big_plans}

            metrics = uow.metric_repository.find_all(
                filter_ref_ids=(it.metric_ref_id for it in inbox_tasks if it.metric_ref_id is not None))
            metrics_map = {m.ref_id: m for m in metrics}

            persons = uow.person_repository.find_all(
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
