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
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.use_case import (
    UseCaseArgsBase,
    UseCaseResultBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInUseCaseContext,
    AppTransactionalLoggedInReadOnlyUseCase,
)


@dataclass
class GetSummariesArgs(UseCaseArgsBase):
    """Get summaries args."""

    allow_archived: Optional[bool] = None
    include_default_project: Optional[bool] = None
    include_vacations: Optional[bool] = None
    include_projects: Optional[bool] = None
    include_inbox_tasks: Optional[bool] = None
    include_habits: Optional[bool] = None
    include_chores: Optional[bool] = None
    include_big_plans: Optional[bool] = None
    include_smart_lists: Optional[bool] = None
    include_metrics: Optional[bool] = None
    include_persons: Optional[bool] = None


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
    AppTransactionalLoggedInReadOnlyUseCase[GetSummariesArgs, GetSummariesResult]
):
    """The use case for retrieving summaries about entities."""

    async def _perform_transactional_read(
        self,
        uow: DomainUnitOfWork,
        context: AppLoggedInUseCaseContext,
        args: GetSummariesArgs,
    ) -> GetSummariesResult:
        """Execute the command."""
        workspace = context.workspace
        allow_archived = args.allow_archived is True

        vacation_collection = await uow.vacation_collection_repository.load_by_parent(
            workspace.ref_id,
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
        big_plan_collection = await uow.big_plan_collection_repository.load_by_parent(
            workspace.ref_id,
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
        if (
            workspace.is_feature_available(WorkspaceFeature.VACATIONS)
            and args.include_vacations
        ):
            vacations = await uow.fast_into_repository.find_all_vacation_summaries(
                parent_ref_id=vacation_collection.parent_ref_id,
                allow_archived=allow_archived,
            )
        projects = None
        if (
            workspace.is_feature_available(WorkspaceFeature.PROJECTS)
            and args.include_projects
        ):
            projects = await uow.fast_into_repository.find_all_project_summaries(
                parent_ref_id=project_collection.parent_ref_id,
                allow_archived=allow_archived,
            )
        inbox_tasks = None
        if (
            workspace.is_feature_available(WorkspaceFeature.INBOX_TASKS)
            and args.include_inbox_tasks
        ):
            inbox_tasks = await uow.fast_into_repository.find_all_inbox_task_summaries(
                parent_ref_id=inbox_task_collection.parent_ref_id,
                allow_archived=allow_archived,
            )
        habits = None
        if (
            workspace.is_feature_available(WorkspaceFeature.HABITS)
            and args.include_habits
        ):
            habits = await uow.fast_into_repository.find_all_habit_summaries(
                parent_ref_id=habit_collection.parent_ref_id,
                allow_archived=allow_archived,
            )
        chores = None
        if (
            workspace.is_feature_available(WorkspaceFeature.CHORES)
            and args.include_chores
        ):
            chores = await uow.fast_into_repository.find_all_chore_summaries(
                parent_ref_id=chore_collection.parent_ref_id,
                allow_archived=allow_archived,
            )
        big_plans = None
        if (
            workspace.is_feature_available(WorkspaceFeature.BIG_PLANS)
            and args.include_big_plans
        ):
            big_plans = await uow.fast_into_repository.find_all_big_plan_summaries(
                parent_ref_id=big_plan_collection.parent_ref_id,
                allow_archived=allow_archived,
            )
        smart_lists = None
        if (
            workspace.is_feature_available(WorkspaceFeature.SMART_LISTS)
            and args.include_smart_lists
        ):
            smart_lists = await uow.fast_into_repository.find_all_smart_list_summaries(
                parent_ref_id=smart_list_collection.parent_ref_id,
                allow_archived=allow_archived,
            )
        metrics = None
        if (
            workspace.is_feature_available(WorkspaceFeature.METRICS)
            and args.include_metrics
        ):
            metrics = await uow.fast_into_repository.find_all_metric_summaries(
                parent_ref_id=metric_collection.parent_ref_id,
                allow_archived=allow_archived,
            )
        persons = None
        if (
            workspace.is_feature_available(WorkspaceFeature.PERSONS)
            and args.include_persons
        ):
            persons = await uow.fast_into_repository.find_all_person_summaries(
                parent_ref_id=person_collection.parent_ref_id,
                allow_archived=allow_archived,
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
