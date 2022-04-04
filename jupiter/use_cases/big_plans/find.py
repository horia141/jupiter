"""The command for finding a big plan."""
from dataclasses import dataclass
from typing import Iterable, Optional, List

from jupiter.domain.big_plans.big_plan import BigPlan
from jupiter.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.domain.projects.project_key import ProjectKey
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.use_case import UseCaseArgsBase, UseCaseResultBase
from jupiter.use_cases.infra.use_cases import AppReadonlyUseCase, AppUseCaseContext


class BigPlanFindUseCase(
    AppReadonlyUseCase["BigPlanFindUseCase.Args", "BigPlanFindUseCase.Result"]
):
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

        big_plans: Iterable["BigPlanFindUseCase.ResultEntry"]

    def _execute(self, context: AppUseCaseContext, args: Args) -> "Result":
        """Execute the command's action."""
        workspace = context.workspace
        filter_project_ref_ids: Optional[List[EntityId]] = None

        with self._storage_engine.get_unit_of_work() as uow:
            if args.filter_project_keys:
                project_collection = uow.project_collection_repository.load_by_parent(
                    workspace.ref_id
                )
                projects = uow.project_repository.find_all_with_filters(
                    parent_ref_id=project_collection.ref_id,
                    filter_keys=args.filter_project_keys,
                )
                filter_project_ref_ids = [p.ref_id for p in projects]

            inbox_task_collection = uow.inbox_task_collection_repository.load_by_parent(
                workspace.ref_id
            )
            big_plan_collection = uow.big_plan_collection_repository.load_by_parent(
                workspace.ref_id
            )
            big_plans = uow.big_plan_repository.find_all_with_filters(
                parent_ref_id=big_plan_collection.ref_id,
                allow_archived=args.allow_archived,
                filter_ref_ids=args.filter_ref_ids,
                filter_project_ref_ids=filter_project_ref_ids,
            )

            inbox_tasks = uow.inbox_task_repository.find_all_with_filters(
                parent_ref_id=inbox_task_collection.ref_id,
                allow_archived=True,
                filter_big_plan_ref_ids=(bp.ref_id for bp in big_plans),
            )

        return BigPlanFindUseCase.Result(
            big_plans=[
                BigPlanFindUseCase.ResultEntry(
                    big_plan=bp,
                    inbox_tasks=[
                        it for it in inbox_tasks if it.big_plan_ref_id == bp.ref_id
                    ],
                )
                for bp in big_plans
            ]
        )
