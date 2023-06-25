"""Use case for loading a particular habit."""
from dataclasses import dataclass

from jupiter.core.domain.habits.habit import Habit
from jupiter.core.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.projects.project import Project
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import (
    UseCaseArgsBase,
    UseCaseResultBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInReadonlyUseCase,
    AppLoggedInUseCaseContext,
)


@dataclass
class HabitLoadArgs(UseCaseArgsBase):
    """HabitLoadArgs."""

    ref_id: EntityId
    allow_archived: bool


@dataclass
class HabitLoadResult(UseCaseResultBase):
    """HabitLoadResult."""

    habit: Habit
    project: Project
    inbox_tasks: list[InboxTask]


class HabitLoadUseCase(AppLoggedInReadonlyUseCase[HabitLoadArgs, HabitLoadResult]):
    """Use case for loading a particular habit."""

    async def _execute(
        self,
        context: AppLoggedInUseCaseContext,
        args: HabitLoadArgs,
    ) -> HabitLoadResult:
        """Execute the command's action."""
        workspace = context.workspace
        async with self._storage_engine.get_unit_of_work() as uow:
            habit = await uow.habit_repository.load_by_id(
                args.ref_id, allow_archived=args.allow_archived
            )
            project = await uow.project_repository.load_by_id(habit.project_ref_id)
            inbox_task_collection = (
                await uow.inbox_task_collection_repository.load_by_parent(
                    workspace.ref_id,
                )
            )
            inbox_tasks = await uow.inbox_task_repository.find_all_with_filters(
                parent_ref_id=inbox_task_collection.ref_id,
                allow_archived=True,
                filter_habit_ref_ids=[args.ref_id],
            )

        return HabitLoadResult(habit=habit, project=project, inbox_tasks=inbox_tasks)
