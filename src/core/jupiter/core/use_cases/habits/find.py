"""The command for finding a habit."""
from typing import List, Optional

from jupiter.core.domain.features import (
    FeatureUnavailableError,
    WorkspaceFeature,
)
from jupiter.core.domain.habits.habit import Habit
from jupiter.core.domain.habits.habit_collection import HabitCollection
from jupiter.core.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.inbox_tasks.inbox_task_collection import InboxTaskCollection
from jupiter.core.domain.projects.project import Project
from jupiter.core.domain.projects.project_collection import ProjectCollection
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.entity import NoFilter
from jupiter.core.framework.use_case_io import (
    UseCaseArgsBase,
    UseCaseResultBase,
    use_case_args,
    use_case_result,
    use_case_result_part,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInReadonlyUseCaseContext,
    AppTransactionalLoggedInReadOnlyUseCase,
    readonly_use_case,
)


@use_case_args
class HabitFindArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    allow_archived: bool
    include_project: bool
    include_inbox_tasks: bool
    filter_ref_ids: Optional[List[EntityId]] = None
    filter_project_ref_ids: Optional[List[EntityId]] = None


@use_case_result_part
class HabitFindResultEntry(UseCaseResultBase):
    """A single entry in the load all habits response."""

    habit: Habit
    project: Optional[Project] = None
    inbox_tasks: Optional[List[InboxTask]] = None


@use_case_result
class HabitFindResult(UseCaseResultBase):
    """The result."""

    entries: List[HabitFindResultEntry]


@readonly_use_case(WorkspaceFeature.HABITS)
class HabitFindUseCase(
    AppTransactionalLoggedInReadOnlyUseCase[HabitFindArgs, HabitFindResult]
):
    """The command for finding a habit."""

    async def _perform_transactional_read(
        self,
        uow: DomainUnitOfWork,
        context: AppLoggedInReadonlyUseCaseContext,
        args: HabitFindArgs,
    ) -> HabitFindResult:
        """Execute the command's action."""
        workspace = context.workspace

        if (
            not workspace.is_feature_available(WorkspaceFeature.PROJECTS)
            and args.filter_project_ref_ids is not None
        ):
            raise FeatureUnavailableError(WorkspaceFeature.PROJECTS)

        project_collection = await uow.get_for(ProjectCollection).load_by_parent(
            workspace.ref_id,
        )

        if args.include_project:
            projects = await uow.get_for(Project).find_all_generic(
                parent_ref_id=project_collection.ref_id,
                allow_archived=args.allow_archived,
                ref_id=args.filter_project_ref_ids or NoFilter(),
            )
            project_by_ref_id = {p.ref_id: p for p in projects}
        else:
            project_by_ref_id = None

        inbox_task_collection = await uow.get_for(
            InboxTaskCollection
        ).load_by_parent(
            workspace.ref_id,
        )
        habit_collection = await uow.get_for(HabitCollection).load_by_parent(
            workspace.ref_id,
        )

        habits = await uow.get_for(Habit).find_all_generic(
            parent_ref_id=habit_collection.ref_id,
            allow_archived=args.allow_archived,
            ref_id=args.filter_ref_ids or NoFilter(),
            project_ref_id=args.filter_project_ref_ids or NoFilter(),
        )

        if args.include_inbox_tasks:
            inbox_tasks = await uow.get_for(InboxTask).find_all_generic(
                parent_ref_id=inbox_task_collection.ref_id,
                allow_archived=True,
                habit_ref_id=[bp.ref_id for bp in habits],
            )
        else:
            inbox_tasks = None

        return HabitFindResult(
            entries=[
                HabitFindResultEntry(
                    habit=rt,
                    project=project_by_ref_id[rt.project_ref_id]
                    if project_by_ref_id is not None
                    else None,
                    inbox_tasks=[
                        it for it in inbox_tasks if it.habit_ref_id == rt.ref_id
                    ]
                    if inbox_tasks is not None
                    else None,
                )
                for rt in habits
            ],
        )
