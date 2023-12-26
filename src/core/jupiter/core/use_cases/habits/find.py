"""The command for finding a habit."""
from dataclasses import dataclass
from typing import List, Optional

from jupiter.core.domain.features import (
    FeatureUnavailableError,
    WorkspaceFeature,
)
from jupiter.core.domain.habits.habit import Habit
from jupiter.core.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.projects.project import Project
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import (
    UseCaseArgsBase,
    UseCaseResultBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInReadonlyUseCaseContext,
    AppTransactionalLoggedInReadOnlyUseCase,
    readonly_use_case,
)


@dataclass
class HabitFindArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    allow_archived: bool
    include_project: bool
    include_inbox_tasks: bool
    filter_ref_ids: Optional[List[EntityId]] = None
    filter_project_ref_ids: Optional[List[EntityId]] = None


@dataclass
class HabitFindResultEntry:
    """A single entry in the load all habits response."""

    habit: Habit
    project: Optional[Project] = None
    inbox_tasks: Optional[List[InboxTask]] = None


@dataclass
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

        project_collection = await uow.project_collection_repository.load_by_parent(
            workspace.ref_id,
        )

        if args.include_project:
            projects = await uow.project_repository.find_all_with_filters(
                parent_ref_id=project_collection.ref_id,
                filter_ref_ids=args.filter_project_ref_ids,
            )
            project_by_ref_id = {p.ref_id: p for p in projects}
        else:
            project_by_ref_id = None

        inbox_task_collection = (
            await uow.inbox_task_collection_repository.load_by_parent(
                workspace.ref_id,
            )
        )
        habit_collection = await uow.habit_collection_repository.load_by_parent(
            workspace.ref_id,
        )

        habits = await uow.habit_repository.find_all_with_filters(
            parent_ref_id=habit_collection.ref_id,
            allow_archived=args.allow_archived,
            filter_ref_ids=args.filter_ref_ids,
            filter_project_ref_ids=args.filter_project_ref_ids,
        )

        if args.include_inbox_tasks:
            inbox_tasks = await uow.inbox_task_repository.find_all_with_filters(
                parent_ref_id=inbox_task_collection.ref_id,
                allow_archived=True,
                filter_habit_ref_ids=(bp.ref_id for bp in habits),
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
