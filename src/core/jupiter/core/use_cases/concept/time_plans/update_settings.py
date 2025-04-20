"""Update settings around time plans."""

from jupiter.core.domain.application.gen.service.gen_service import GenService
from jupiter.core.domain.concept.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.concept.inbox_tasks.inbox_task_collection import InboxTaskCollection
from jupiter.core.domain.concept.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.concept.projects.project import Project
from jupiter.core.domain.concept.projects.project_collection import ProjectCollection
from jupiter.core.domain.concept.time_plans.time_plan import TimePlan, TimePlanRepository
from jupiter.core.domain.concept.time_plans.time_plan_domain import TimePlanDomain
from jupiter.core.domain.concept.time_plans.time_plan_generation_approach import (
    TimePlanGenerationApproach,
)
from jupiter.core.domain.concept.time_plans.time_plan_source import TimePlanSource
from jupiter.core.domain.core import schedules
from jupiter.core.domain.core.archival_reason import ArchivalReason
from jupiter.core.domain.core.difficulty import Difficulty
from jupiter.core.domain.core.eisen import Eisen
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.infra.generic_crown_archiver import generic_crown_archiver
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.domain.sync_target import SyncTarget
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.base.entity_name import EntityName
from jupiter.core.framework.update_action import UpdateAction
from jupiter.core.framework.use_case import ProgressReporter
from jupiter.core.framework.use_case_io import UseCaseArgsBase, use_case_args
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCase,
    AppLoggedInMutationUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
    mutation_use_case,
)


@use_case_args
class TimePlanUpdateSettingsArgs(UseCaseArgsBase):
    """Args."""

    periods: UpdateAction[list[RecurringTaskPeriod]]
    generation_approach: UpdateAction[TimePlanGenerationApproach]
    generation_in_advance_days: UpdateAction[dict[RecurringTaskPeriod, int]]
    planning_task_project_ref_id: UpdateAction[EntityId | None]
    planning_task_eisen: UpdateAction[Eisen | None]
    planning_task_difficulty: UpdateAction[Difficulty | None]


@mutation_use_case(WorkspaceFeature.TIME_PLANS)
class TimePlanUpdateSettingsUseCase(
    AppLoggedInMutationUseCase[TimePlanUpdateSettingsArgs, None]
):
    """Command for updating the settings for time plans in general."""

    async def _perform_mutation(
        self,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: TimePlanUpdateSettingsArgs,
    ) -> None:
        """Execute the command's action."""
        async with self._domain_storage_engine.get_unit_of_work() as uow:
            workspace = context.workspace

            time_plan_domain = await uow.get_for(TimePlanDomain).load_by_parent(
                workspace.ref_id
            )
            inbox_task_collection = await uow.get_for(InboxTaskCollection).load_by_parent(
                workspace.ref_id
            )
            project_collection = await uow.get_for(ProjectCollection).load_by_parent(
                workspace.ref_id
            )

            if workspace.is_feature_available(WorkspaceFeature.PROJECTS):
                if args.planning_task_project_ref_id.test(lambda x: x is None):
                    raise Exception("Planning task project ref id is required")
                if args.planning_task_project_ref_id.should_change:
                    project = await uow.get_for(Project).load_by_id(
                        args.planning_task_project_ref_id.just_changed
                    )
                    planning_task_project_ref_id = UpdateAction.change_to(project.ref_id)
                else:
                    planning_task_project_ref_id = UpdateAction.do_not_change()
            else:
                root_project = await uow.get_for(Project).find_all_generic(
                    parent_ref_id=project_collection.ref_id,
                    allow_archived=False,
                    parent_project_ref_id=None,
                )
                if len(root_project) != 1:
                    raise Exception("Root project not found")
                planning_task_project_ref_id = UpdateAction.change_to(root_project[0].ref_id)

            time_plan_domain = time_plan_domain.update(
                context.domain_context,
                periods=args.periods.transform(lambda s: set(s)),
                generation_approach=args.generation_approach,
                generation_in_advance_days=args.generation_in_advance_days,
                planning_task_project_ref_id=planning_task_project_ref_id,
                planning_task_eisen=args.planning_task_eisen,
                planning_task_difficulty=args.planning_task_difficulty,
            )
            await uow.get_for(TimePlanDomain).save(time_plan_domain)

        gen_service = GenService(
            domain_storage_engine=self._domain_storage_engine,
        )

        await gen_service.do_it(
            ctx=context.domain_context,
            progress_reporter=progress_reporter,
            user=context.user,
            workspace=context.workspace,
            gen_even_if_not_modified=True,
            today=self._time_provider.get_current_date(),
            gen_targets=[SyncTarget.TIME_PLANS],
            period=None,
        )

        async with self._domain_storage_engine.get_unit_of_work() as uow:
            for period in RecurringTaskPeriod:
                schedule = schedules.get_schedule(
                    period=period,
                    name=EntityName("Test"),
                    right_now=self._time_provider.get_current_date().to_timestamp_at_end_of_day(),
                )

                time_plan_for_periods = await uow.get(TimePlanRepository).find_all_in_range(
                    parent_ref_id=time_plan_domain.ref_id,
                    allow_archived=False,
                    filter_periods=[period],
                    filter_start_date=schedule.first_day,
                    filter_end_date=schedule.end_day,
                )

                if len(time_plan_for_periods) == 0:
                    continue
                if len(time_plan_for_periods) > 1:
                    raise Exception("Found multiple time plans for period")

                time_plan = time_plan_for_periods[0]

                if time_plan.source == TimePlanSource.USER:
                    continue

                planning_task = await uow.get_for(InboxTask).find_all_generic(
                    parent_ref_id=inbox_task_collection.ref_id,
                    allow_archived=False,
                    source=InboxTaskSource.TIME_PLAN,
                    source_entity_ref_id=time_plan.ref_id,
                )

                if len(planning_task) == 0:
                    planning_task = None
                elif len(planning_task) == 1:
                    planning_task = planning_task[0]
                else:
                    raise Exception("Found multiple planning tasks for time plan")

                if period not in time_plan_domain.periods or time_plan_domain.generation_approach.should_not_generate_a_time_plan:
                    await generic_crown_archiver(
                        context.domain_context,
                        uow,
                        progress_reporter,
                        TimePlan,
                        time_plan.ref_id,
                        ArchivalReason.USER,
                    )
                if planning_task and time_plan_domain.generation_approach.should_not_generate_a_planning_task:
                    await generic_crown_archiver(
                        context.domain_context,
                        uow,
                        progress_reporter,
                        InboxTask,
                        planning_task.ref_id,
                        ArchivalReason.USER,
                    )
