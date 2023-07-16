"""A use case for retrieving summaries about entities."""
from dataclasses import dataclass
from typing import List, Optional

from jupiter.core.domain.fast_info_repository import (
    BigPlanSummary,
    ChoreSummary,
    HabitSummary,
    InboxTaskSummary,
    MetricSummary,
    PersonSummary,
    ProjectSummary,
    SmartListSummary,
    VacationSummary,
)
from jupiter.core.framework.use_case import (
    UseCaseArgsBase,
    UseCaseResultBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInReadonlyUseCase,
    AppLoggedInUseCaseContext,
)


@dataclass
class GetSummariesArgs(UseCaseArgsBase):
    """Get summaries args."""

    allow_archived: bool
    include_default_project: bool
    include_vacations: bool
    include_projects: bool
    include_inbox_tasks: bool
    include_habits: bool
    include_chores: bool
    include_big_plans: bool
    include_smart_lists: bool
    include_metrics: bool
    include_persons: bool


@dataclass
class GetSummariesResult(UseCaseResultBase):
    """Get summaries result."""

    default_project: Optional[ProjectSummary] = None
    vacations: Optional[List[VacationSummary]] = None
    projects: Optional[List[ProjectSummary]] = None
    inbox_tasks: Optional[List[InboxTaskSummary]] = None
    habits: Optional[List[HabitSummary]] = None
    chores: Optional[List[ChoreSummary]] = None
    big_plans: Optional[List[BigPlanSummary]] = None
    smart_lists: Optional[List[SmartListSummary]] = None
    metrics: Optional[List[MetricSummary]] = None
    persons: Optional[List[PersonSummary]] = None


class GetSummariesUseCase(
    AppLoggedInReadonlyUseCase[GetSummariesArgs, GetSummariesResult]
):
    """The use case for retrieving summaries about entities."""

    async def _execute(
        self,
        context: AppLoggedInUseCaseContext,
        args: GetSummariesArgs,
    ) -> GetSummariesResult:
        """Execute the command."""
        workspace = context.workspace

        async with self._storage_engine.get_unit_of_work() as uow:
            vacation_collection = (
                await uow.vacation_collection_repository.load_by_parent(
                    workspace.ref_id,
                )
            )
            project_collection = await uow.project_collection_repository.load_by_parent(
                workspace.ref_id,
            )
            inbox_task_collection = (
                await uow.inbox_task_collection_repository.load_by_parent(
                    workspace.ref_id,
                )
            )
            habit_collection = await uow.habit_collection_repository.load_by_parent(
                workspace.ref_id,
            )
            chore_collection = await uow.chore_collection_repository.load_by_parent(
                workspace.ref_id,
            )
            big_plan_collection = (
                await uow.big_plan_collection_repository.load_by_parent(
                    workspace.ref_id,
                )
            )
            smart_list_collection = (
                await uow.smart_list_collection_repository.load_by_parent(
                    workspace.ref_id,
                )
            )
            metric_collection = await uow.metric_collection_repository.load_by_parent(
                workspace.ref_id,
            )
            person_collection = await uow.person_collection_repository.load_by_parent(
                workspace.ref_id,
            )

            default_project = None
            if args.include_default_project:
                default_project_full = await uow.project_repository.load_by_id(
                    workspace.default_project_ref_id,
                )
                default_project = ProjectSummary(
                    ref_id=default_project_full.ref_id,
                    name=default_project_full.name,
                )

            vacations = None
            if args.include_vacations:
                vacations = await uow.fast_into_repository.find_all_vacation_summaries(
                    parent_ref_id=vacation_collection.parent_ref_id,
                    allow_archived=args.allow_archived,
                )
            projects = None
            if args.include_projects:
                projects = await uow.fast_into_repository.find_all_project_summaries(
                    parent_ref_id=project_collection.parent_ref_id,
                    allow_archived=args.allow_archived,
                )
            inbox_tasks = None
            if args.include_inbox_tasks:
                inbox_tasks = (
                    await uow.fast_into_repository.find_all_inbox_task_summaries(
                        parent_ref_id=inbox_task_collection.parent_ref_id,
                        allow_archived=args.allow_archived,
                    )
                )
            habits = None
            if args.include_habits:
                habits = await uow.fast_into_repository.find_all_habit_summaries(
                    parent_ref_id=habit_collection.parent_ref_id,
                    allow_archived=args.allow_archived,
                )
            chores = None
            if args.include_chores:
                chores = await uow.fast_into_repository.find_all_chore_summaries(
                    parent_ref_id=chore_collection.parent_ref_id,
                    allow_archived=args.allow_archived,
                )
            big_plans = None
            if args.include_big_plans:
                big_plans = await uow.fast_into_repository.find_all_big_plan_summaries(
                    parent_ref_id=big_plan_collection.parent_ref_id,
                    allow_archived=args.allow_archived,
                )
            smart_lists = None
            if args.include_smart_lists:
                smart_lists = (
                    await uow.fast_into_repository.find_all_smart_list_summaries(
                        parent_ref_id=smart_list_collection.parent_ref_id,
                        allow_archived=args.allow_archived,
                    )
                )
            metrics = None
            if args.include_metrics:
                metrics = await uow.fast_into_repository.find_all_metric_summaries(
                    parent_ref_id=metric_collection.parent_ref_id,
                    allow_archived=args.allow_archived,
                )
            persons = None
            if args.include_persons:
                persons = await uow.fast_into_repository.find_all_person_summaries(
                    parent_ref_id=person_collection.parent_ref_id,
                    allow_archived=args.allow_archived,
                )

        return GetSummariesResult(
            default_project=default_project,
            vacations=vacations,
            projects=projects,
            inbox_tasks=inbox_tasks,
            habits=habits,
            chores=chores,
            big_plans=big_plans,
            smart_lists=smart_lists,
            metrics=metrics,
            persons=persons,
        )
