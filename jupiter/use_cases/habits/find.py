"""The command for finding a habit."""
from dataclasses import dataclass
from typing import Iterable, Optional, List

from jupiter.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.domain.projects.project_key import ProjectKey
from jupiter.domain.habits.habit import Habit
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.use_case import UseCaseArgsBase, UseCaseResultBase
from jupiter.use_cases.infra.use_cases import AppReadonlyUseCase, AppUseCaseContext


class HabitFindUseCase(
    AppReadonlyUseCase["HabitFindUseCase.Args", "HabitFindUseCase.Result"]
):
    """The command for finding a habit."""

    @dataclass(frozen=True)
    class Args(UseCaseArgsBase):
        """Args."""

        show_archived: bool
        filter_ref_ids: Optional[Iterable[EntityId]]
        filter_project_keys: Optional[Iterable[ProjectKey]]

    @dataclass(frozen=True)
    class ResultEntry:
        """A single entry in the load all habits response."""

        habit: Habit
        inbox_tasks: Iterable[InboxTask]

    @dataclass(frozen=True)
    class Result(UseCaseResultBase):
        """The result."""

        habits: Iterable["HabitFindUseCase.ResultEntry"]

    def _execute(self, context: AppUseCaseContext, args: Args) -> "Result":
        """Execute the command's action."""
        workspace = context.workspace

        with self._storage_engine.get_unit_of_work() as uow:
            filter_project_ref_ids: Optional[List[EntityId]] = None
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
            habit_collection = uow.habit_collection_repository.load_by_parent(
                workspace.ref_id
            )

            habits = uow.habit_repository.find_all_with_filters(
                parent_ref_id=habit_collection.ref_id,
                allow_archived=args.show_archived,
                filter_ref_ids=args.filter_ref_ids,
                filter_project_ref_ids=filter_project_ref_ids,
            )

            inbox_tasks = uow.inbox_task_repository.find_all_with_filters(
                parent_ref_id=inbox_task_collection.ref_id,
                allow_archived=True,
                filter_habit_ref_ids=(bp.ref_id for bp in habits),
            )

        return HabitFindUseCase.Result(
            habits=[
                HabitFindUseCase.ResultEntry(
                    habit=rt,
                    inbox_tasks=[
                        it for it in inbox_tasks if it.habit_ref_id == rt.ref_id
                    ],
                )
                for rt in habits
            ]
        )
