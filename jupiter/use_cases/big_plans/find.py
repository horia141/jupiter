"""The command for finding a big plan."""
from dataclasses import dataclass
from typing import Iterable, Optional, List

from jupiter.domain.big_plans.big_plan import BigPlan
from jupiter.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.domain.projects.project_key import ProjectKey
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.use_case import UseCaseArgsBase, UseCaseResultBase
from jupiter.use_cases.infra.use_cases import AppReadonlyUseCase, AppUseCaseContext


class BigPlanFindUseCase(AppReadonlyUseCase['BigPlanFindUseCase.Args', 'BigPlanFindUseCase.Result']):
    """The command for finding a big plan."""

    @dataclass(frozen=True)
    class Args(UseCaseArgsBase):
        """Args."""
        allow_archived: bool
        filter_ref_ids: Optional[Iterable[EntityId]]
        filter_project_keys: Optional[Iterable[ProjectKey]]

    @dataclass(frozen=True)
    class ResultEntry:
        """A single big plan result."""
        big_plan: BigPlan
        inbox_tasks: Iterable[InboxTask]

    @dataclass(frozen=True)
    class Result(UseCaseResultBase):
        """Result."""
        big_plans: Iterable['BigPlanFindUseCase.ResultEntry']

    def _execute(self, context: AppUseCaseContext, args: Args) -> 'Result':
        """Execute the command's action."""
        filter_project_ref_ids: Optional[List[EntityId]] = None
        with self._storage_engine.get_unit_of_work() as uow:
            if args.filter_project_keys:
                projects = uow.project_repository.find_all(filter_keys=args.filter_project_keys)
                filter_project_ref_ids = [p.ref_id for p in projects]

            big_plan_collections = \
                uow.big_plan_collection_repository.find_all(filter_project_ref_ids=filter_project_ref_ids)
            big_plans = uow.big_plan_repository.find_all(
                allow_archived=args.allow_archived, filter_ref_ids=args.filter_ref_ids,
                filter_big_plan_collection_ref_ids=[bpc.ref_id for bpc in big_plan_collections])

            inbox_tasks = uow.inbox_task_repository.find_all(
                allow_archived=True, filter_big_plan_ref_ids=(bp.ref_id for bp in big_plans))

        return BigPlanFindUseCase.Result(
            big_plans=[BigPlanFindUseCase.ResultEntry(
                big_plan=bp,
                inbox_tasks=[it for it in inbox_tasks if it.big_plan_ref_id == bp.ref_id])
                       for bp in big_plans])
