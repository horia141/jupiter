"""A use case for retrieving summaries about entities."""

from jupiter.core.domain.big_plans.big_plan_collection import BigPlanCollection
from jupiter.core.domain.calendar.calendar_collection import CalendarCollection
from jupiter.core.domain.chores.chore_collection import ChoreCollection
from jupiter.core.domain.fast_info_repository import (
    BigPlanSummary,
    CalendarSummary,
    ChoreSummary,
    FastInfoRepository,
    HabitSummary,
    InboxTaskSummary,
    MetricSummary,
    PersonSummary,
    ProjectSummary,
    SmartListSummary,
    VacationSummary,
)
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.habits.habit_collection import HabitCollection
from jupiter.core.domain.inbox_tasks.inbox_task_collection import InboxTaskCollection
from jupiter.core.domain.metrics.metric_collection import MetricCollection
from jupiter.core.domain.persons.person_collection import PersonCollection
from jupiter.core.domain.projects.project import ProjectRepository
from jupiter.core.domain.projects.project_collection import ProjectCollection
from jupiter.core.domain.smart_lists.smart_list_collection import SmartListCollection
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.domain.vacations.vacation_collection import VacationCollection
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
class GetSummariesArgs(UseCaseArgsBase):
    """Get summaries args."""

    allow_archived: bool | None
    include_inbox_tasks: bool | None
    include_calendars: bool | None
    include_habits: bool | None
    include_chores: bool | None
    include_big_plans: bool | None
    include_vacations: bool | None
    include_projects: bool | None
    include_smart_lists: bool | None
    include_metrics: bool | None
    include_persons: bool | None


@use_case_result
class GetSummariesResult(UseCaseResultBase):
    """Get summaries result."""

    inbox_tasks: list[InboxTaskSummary] | None
    calendars: list[CalendarSummary] | None
    habits: list[HabitSummary] | None
    chores: list[ChoreSummary] | None
    big_plans: list[BigPlanSummary] | None
    root_project: ProjectSummary | None
    vacations: list[VacationSummary] | None
    projects: list[ProjectSummary] | None
    smart_lists: list[SmartListSummary] | None
    metrics: list[MetricSummary] | None
    persons: list[PersonSummary] | None


@readonly_use_case()
class GetSummariesUseCase(
    AppTransactionalLoggedInReadOnlyUseCase[GetSummariesArgs, GetSummariesResult]
):
    """The use case for retrieving summaries about entities."""

    async def _perform_transactional_read(
        self,
        uow: DomainUnitOfWork,
        context: AppLoggedInReadonlyUseCaseContext,
        args: GetSummariesArgs,
    ) -> GetSummariesResult:
        """Execute the command."""
        workspace = context.workspace
        allow_archived = args.allow_archived is True

        inbox_task_collection = await uow.get_for(InboxTaskCollection).load_by_parent(
            workspace.ref_id,
        )
        calendar_collection = await uow.get_for(CalendarCollection).load_by_parent(
            workspace.ref_id,
        )
        habit_collection = await uow.get_for(HabitCollection).load_by_parent(
            workspace.ref_id,
        )
        chore_collection = await uow.get_for(ChoreCollection).load_by_parent(
            workspace.ref_id,
        )
        big_plan_collection = await uow.get_for(BigPlanCollection).load_by_parent(
            workspace.ref_id,
        )
        vacation_collection = await uow.get_for(VacationCollection).load_by_parent(
            workspace.ref_id,
        )
        project_collection = await uow.get_for(ProjectCollection).load_by_parent(
            workspace.ref_id,
        )
        smart_list_collection = await uow.get_for(SmartListCollection).load_by_parent(
            workspace.ref_id,
        )
        metric_collection = await uow.get_for(MetricCollection).load_by_parent(
            workspace.ref_id,
        )
        person_collection = await uow.get_for(PersonCollection).load_by_parent(
            workspace.ref_id,
        )

        inbox_tasks = None
        if (
            workspace.is_feature_available(WorkspaceFeature.INBOX_TASKS)
            and args.include_inbox_tasks
        ):
            inbox_tasks = await uow.get(
                FastInfoRepository
            ).find_all_inbox_task_summaries(
                parent_ref_id=inbox_task_collection.workspace.ref_id,
                allow_archived=allow_archived,
            )

        calendars = None
        if (
            workspace.is_feature_available(WorkspaceFeature.CALENDARS)
            and args.include_calendars
        ):
            calendars = await uow.get(FastInfoRepository).find_all_calendar_summaries(
                parent_ref_id=calendar_collection.workspace.ref_id,
                allow_archived=allow_archived,
            )
        
        habits = None
        if (
            workspace.is_feature_available(WorkspaceFeature.HABITS)
            and args.include_habits
        ):
            habits = await uow.get(FastInfoRepository).find_all_habit_summaries(
                parent_ref_id=habit_collection.workspace.ref_id,
                allow_archived=allow_archived,
            )
        
        chores = None
        if (
            workspace.is_feature_available(WorkspaceFeature.CHORES)
            and args.include_chores
        ):
            chores = await uow.get(FastInfoRepository).find_all_chore_summaries(
                parent_ref_id=chore_collection.workspace.ref_id,
                allow_archived=allow_archived,
            )
        
        big_plans = None
        if (
            workspace.is_feature_available(WorkspaceFeature.BIG_PLANS)
            and args.include_big_plans
        ):
            big_plans = await uow.get(FastInfoRepository).find_all_big_plan_summaries(
                parent_ref_id=big_plan_collection.workspace.ref_id,
                allow_archived=allow_archived,
            )
        
        vacations = None
        if (
            workspace.is_feature_available(WorkspaceFeature.VACATIONS)
            and args.include_vacations
        ):
            vacations = await uow.get(FastInfoRepository).find_all_vacation_summaries(
                parent_ref_id=vacation_collection.workspace.ref_id,
                allow_archived=allow_archived,
            )

        root_project = None
        projects = None
        if (
            workspace.is_feature_available(WorkspaceFeature.PROJECTS)
            and args.include_projects
        ):
            root_project_real = await uow.get(ProjectRepository).load_root_project(
                project_collection.ref_id
            )
            root_project = ProjectSummary(
                ref_id=root_project_real.ref_id,
                parent_project_ref_id=root_project_real.parent_ref_id,
                name=root_project_real.name,
                order_of_child_projects=root_project_real.order_of_child_projects,
            )
            projects = await uow.get(FastInfoRepository).find_all_project_summaries(
                parent_ref_id=project_collection.workspace.ref_id,
                allow_archived=allow_archived,
            )
        
        smart_lists = None
        if (
            workspace.is_feature_available(WorkspaceFeature.SMART_LISTS)
            and args.include_smart_lists
        ):
            smart_lists = await uow.get(
                FastInfoRepository
            ).find_all_smart_list_summaries(
                parent_ref_id=smart_list_collection.workspace.ref_id,
                allow_archived=allow_archived,
            )
        
        metrics = None
        if (
            workspace.is_feature_available(WorkspaceFeature.METRICS)
            and args.include_metrics
        ):
            metrics = await uow.get(FastInfoRepository).find_all_metric_summaries(
                parent_ref_id=metric_collection.workspace.ref_id,
                allow_archived=allow_archived,
            )
        
        persons = None
        if (
            workspace.is_feature_available(WorkspaceFeature.PERSONS)
            and args.include_persons
        ):
            persons = await uow.get(FastInfoRepository).find_all_person_summaries(
                parent_ref_id=person_collection.workspace.ref_id,
                allow_archived=allow_archived,
            )

        return GetSummariesResult(
            inbox_tasks=inbox_tasks,
            calendars=calendars,
            habits=habits,
            chores=chores,
            big_plans=big_plans,
            vacations=vacations,
            root_project=root_project,
            projects=projects,
            smart_lists=smart_lists,
            metrics=metrics,
            persons=persons,
        )
