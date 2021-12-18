"""The command for finding a big plan."""
from dataclasses import dataclass
from typing import Iterable, Optional, Final, List

from domain.big_plans.big_plan import BigPlan
from domain.big_plans.infra.big_plan_engine import BigPlanEngine
from domain.inbox_tasks.inbox_task import InboxTask
from domain.inbox_tasks.infra.inbox_task_engine import InboxTaskEngine
from domain.projects.infra.project_engine import ProjectEngine
from domain.projects.project_key import ProjectKey
from models.framework import Command, EntityId


class BigPlanFindCommand(Command['BigPlanFindCommand.Args', 'BigPlanFindCommand.Result']):
    """The command for finding a big plan."""

    @dataclass()
    class Args:
        """Args."""
        allow_archived: bool
        filter_ref_ids: Optional[Iterable[EntityId]]
        filter_project_keys: Optional[Iterable[ProjectKey]]

    @dataclass()
    class ResultEntry:
        """A single big plan result."""
        big_plan: BigPlan
        inbox_tasks: Iterable[InboxTask]

    @dataclass()
    class Result:
        """Result."""
        big_plans: Iterable['BigPlanFindCommand.ResultEntry']

    _project_engine: Final[ProjectEngine]
    _inbox_task_engine: Final[InboxTaskEngine]
    _big_plan_engine: Final[BigPlanEngine]

    def __init__(
            self, projects_engine: ProjectEngine, inbox_task_engine: InboxTaskEngine,
            big_plan_engine: BigPlanEngine) -> None:
        """Constructor."""
        self._project_engine = projects_engine
        self._inbox_task_engine = inbox_task_engine
        self._big_plan_engine = big_plan_engine

    def execute(self, args: Args) -> 'Result':
        """Execute the command's action."""
        filter_project_ref_ids: Optional[List[EntityId]] = None
        if args.filter_project_keys:
            with self._project_engine.get_unit_of_work() as project_uow:
                projects = project_uow.project_repository.find_all(filter_keys=args.filter_project_keys)
            filter_project_ref_ids = [p.ref_id for p in projects]

        with self._big_plan_engine.get_unit_of_work() as big_plan_uow:
            big_plan_collections = \
                big_plan_uow.big_plan_collection_repository.find_all(filter_project_ref_ids=filter_project_ref_ids)
            big_plans = big_plan_uow.big_plan_repository.find_all(
                allow_archived=args.allow_archived, filter_ref_ids=args.filter_ref_ids,
                filter_big_plan_collection_ref_ids=[bpc.ref_id for bpc in big_plan_collections])

        with self._inbox_task_engine.get_unit_of_work() as inbox_task_uow:
            inbox_tasks = inbox_task_uow.inbox_task_repository.find_all(
                allow_archived=True, filter_big_plan_ref_ids=(bp.ref_id for bp in big_plans))

        return BigPlanFindCommand.Result(
            big_plans=[BigPlanFindCommand.ResultEntry(
                big_plan=bp,
                inbox_tasks=[it for it in inbox_tasks if it.big_plan_ref_id == bp.ref_id])
                       for bp in big_plans])
