"""Use case for loading a particular habit."""

from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.habits.habit import Habit
from jupiter.core.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.inbox_tasks.inbox_task_collection import InboxTaskCollection
from jupiter.core.domain.projects.project import Project
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case_io import (
    UseCaseArgsBase,
    UseCaseResultBase,
    use_case_args,
    use_case_result,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInReadonlyUseCaseContext,
    AppTransactionalLoggedInReadOnlyUseCase,
    readonly_use_case,
)


@use_case_args
class HabitLoadArgs(UseCaseArgsBase):
    """HabitLoadArgs."""

    ref_id: EntityId
    allow_archived: bool


@use_case_result
class HabitLoadResult(UseCaseResultBase):
    """HabitLoadResult."""

    habit: Habit
    project: Project
    inbox_tasks: list[InboxTask]


@readonly_use_case(WorkspaceFeature.HABITS)
class HabitLoadUseCase(
    AppTransactionalLoggedInReadOnlyUseCase[HabitLoadArgs, HabitLoadResult]
):
    """Use case for loading a particular habit."""

    async def _perform_transactional_read(
        self,
        uow: DomainUnitOfWork,
        context: AppLoggedInReadonlyUseCaseContext,
        args: HabitLoadArgs,
    ) -> HabitLoadResult:
        """Execute the command's action."""
        workspace = context.workspace
        habit = await uow.get_for(Habit).load_by_id(
            args.ref_id, allow_archived=args.allow_archived
        )
        project = await uow.get_for(Project).load_by_id(habit.project_ref_id)
        inbox_task_collection = await uow.get_for(InboxTaskCollection).load_by_parent(
            workspace.ref_id,
        )
        inbox_tasks = await uow.get_for(InboxTask).find_all_generic(
            parent_ref_id=inbox_task_collection.ref_id,
            allow_archived=True,
            habit_ref_id=[args.ref_id],
        )

        return HabitLoadResult(habit=habit, project=project, inbox_tasks=inbox_tasks)
