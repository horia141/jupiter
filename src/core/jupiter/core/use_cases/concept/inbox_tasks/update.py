"""The command for updating a inbox task."""

from jupiter.core.domain.application.gamification.service.record_score_service import (
    RecordScoreResult,
    RecordScoreService,
)
from jupiter.core.domain.concept.big_plans.big_plan import BigPlan
from jupiter.core.domain.concept.big_plans.big_plan_stats import BigPlanStatsRepository
from jupiter.core.domain.concept.inbox_tasks.inbox_task import (
    CannotModifyGeneratedTaskError,
    InboxTask,
)
from jupiter.core.domain.concept.inbox_tasks.inbox_task_name import InboxTaskName
from jupiter.core.domain.concept.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.concept.inbox_tasks.inbox_task_status import InboxTaskStatus
from jupiter.core.domain.concept.time_plans.time_plan import TimePlan
from jupiter.core.domain.concept.time_plans.time_plan_activity import (
    TimePlanActivity,
    TimePlanActivityRespository,
    TimePlanAlreadyAssociatedWithTargetError,
)
from jupiter.core.domain.concept.time_plans.time_plan_activity_feasability import (
    TimePlanActivityFeasability,
)
from jupiter.core.domain.concept.time_plans.time_plan_activity_kind import (
    TimePlanActivityKind,
)
from jupiter.core.domain.concept.time_plans.time_plan_activity_target import (
    TimePlanActivityTarget,
)
from jupiter.core.domain.concept.workspaces.workspace import Workspace
from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.core.difficulty import Difficulty
from jupiter.core.domain.core.eisen import Eisen
from jupiter.core.domain.features import (
    FeatureUnavailableError,
    UserFeature,
    WorkspaceFeature,
)
from jupiter.core.domain.infra.generic_creator import generic_creator
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.update_action import UpdateAction
from jupiter.core.framework.use_case import (
    ProgressReporter,
)
from jupiter.core.framework.use_case_io import (
    UseCaseArgsBase,
    UseCaseResultBase,
    use_case_args,
    use_case_result,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
    mutation_use_case,
)


@use_case_args
class InboxTaskUpdateArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId
    name: UpdateAction[InboxTaskName]
    status: UpdateAction[InboxTaskStatus]
    project_ref_id: UpdateAction[EntityId]
    big_plan_ref_id: UpdateAction[EntityId | None]
    eisen: UpdateAction[Eisen]
    difficulty: UpdateAction[Difficulty]
    actionable_date: UpdateAction[ADate | None]
    due_date: UpdateAction[ADate | None]


@use_case_result
class InboxTaskUpdateResult(UseCaseResultBase):
    """InboxTaskUpdate result."""

    record_score_result: RecordScoreResult | None


@mutation_use_case(WorkspaceFeature.INBOX_TASKS)
class InboxTaskUpdateUseCase(
    AppTransactionalLoggedInMutationUseCase[InboxTaskUpdateArgs, InboxTaskUpdateResult]
):
    """The command for updating a inbox task."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: InboxTaskUpdateArgs,
    ) -> InboxTaskUpdateResult:
        """Execute the command's action."""
        workspace = context.workspace
        inbox_task = await uow.get_for(InboxTask).load_by_id(args.ref_id)

        try:
            the_project: UpdateAction[EntityId]
            previous_big_plan: BigPlan | None
            new_big_plan: BigPlan | None

            if inbox_task.source == InboxTaskSource.BIG_PLAN:
                previous_big_plan = await uow.get_for(BigPlan).load_by_id(
                    inbox_task.source_entity_ref_id_for_sure
                )
            else:
                previous_big_plan = None

            if args.big_plan_ref_id.should_change:
                if args.big_plan_ref_id.just_the_value is not None:
                    if not workspace.is_feature_available(WorkspaceFeature.BIG_PLANS):
                        raise FeatureUnavailableError(WorkspaceFeature.BIG_PLANS)

                    new_big_plan = await uow.get_for(BigPlan).load_by_id(
                        args.big_plan_ref_id.just_the_value,
                    )

                    if (
                        args.project_ref_id.should_change
                        and args.project_ref_id.just_the_value
                        != new_big_plan.project_ref_id
                    ):
                        raise InputValidationError(
                            "Changing the project of a task and associating it with a big plan at the same time is not allowed"
                        )

                    the_project = UpdateAction.change_to(new_big_plan.project_ref_id)

                    new_big_plan = await self._process_time_plans_for_big_plan(
                        uow,
                        progress_reporter,
                        context,
                        workspace,
                        inbox_task,
                        new_big_plan,
                    )
                else:
                    the_project = args.project_ref_id
                    new_big_plan = None
            else:
                the_project = args.project_ref_id
                new_big_plan = previous_big_plan

            new_inbox_task = inbox_task.update(
                ctx=context.domain_context,
                name=args.name,
                project_ref_id=the_project,
                big_plan_ref_id=args.big_plan_ref_id,
                status=args.status,
                eisen=args.eisen,
                difficulty=args.difficulty,
                actionable_date=args.actionable_date,
                due_date=args.due_date,
            )

            await self._process_big_plan_stats(
                uow,
                progress_reporter,
                context,
                inbox_task,
                new_inbox_task,
                previous_big_plan,
                new_big_plan,
            )
        except CannotModifyGeneratedTaskError as err:
            raise err
            # raise InputValidationError(
            #     f"Modifing a generated task's field {err.field} is not possible",
            # ) from err

        await uow.get_for(InboxTask).save(new_inbox_task)
        await progress_reporter.mark_updated(new_inbox_task)

        record_score_result = None
        if context.user.is_feature_available(UserFeature.GAMIFICATION):
            record_score_result = await RecordScoreService().record_task(
                context.domain_context, uow, context.user, inbox_task
            )

        return InboxTaskUpdateResult(record_score_result=record_score_result)

    async def _process_time_plans_for_big_plan(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        workspace: Workspace,
        inbox_task_before_update: InboxTask,
        big_plan: BigPlan,
    ) -> BigPlan:
        if not workspace.is_feature_available(WorkspaceFeature.TIME_PLANS):
            # If no time plans, nothing to do here.
            return big_plan

        if inbox_task_before_update.source_entity_ref_id == big_plan.ref_id:
            # If the inbox task is already associated with the big plan, nothing to do here.
            return big_plan

        # We go to all timeplans where this inbox task has an activity
        # and add an activity for the big plan if there isn't one.
        # But we don't go to all timeplans and remove the big plan. That's
        # done just one.
        time_plan_ref_ids = await uow.get(
            TimePlanActivityRespository
        ).find_all_with_target(
            target=TimePlanActivityTarget.INBOX_TASK,
            target_ref_id=inbox_task_before_update.ref_id,
        )

        for time_plan_ref_id in time_plan_ref_ids:
            try:
                big_plan_activity = TimePlanActivity.new_activity_for_big_plan(
                    ctx=context.domain_context,
                    time_plan_ref_id=time_plan_ref_id,
                    big_plan_ref_id=big_plan.ref_id,
                    kind=TimePlanActivityKind.MAKE_PROGRESS,
                    feasability=TimePlanActivityFeasability.MUST_DO,
                )

                _ = await generic_creator(uow, progress_reporter, big_plan_activity)

                if big_plan.actionable_date is None or big_plan.due_date is None:
                    time_plan = await uow.get_for(TimePlan).load_by_id(time_plan_ref_id)
                    big_plan = big_plan.change_dates_via_time_plan(
                        context.domain_context,
                        actionable_date=time_plan.start_date,
                        due_date=time_plan.end_date,
                    )
                    await uow.get_for(BigPlan).save(big_plan)
                    await progress_reporter.mark_updated(big_plan)
            except TimePlanAlreadyAssociatedWithTargetError:
                # We were already working on this plan, no need to panic
                pass

        return big_plan

    async def _process_big_plan_stats(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        inbox_task_before_update: InboxTask,
        inbox_task_after_update: InboxTask,
        previous_big_plan: BigPlan | None,
        new_big_plan: BigPlan | None,
    ) -> None:
        if previous_big_plan == new_big_plan:
            if new_big_plan is None:
                return

            if (
                not inbox_task_before_update.is_completed
                and inbox_task_after_update.is_completed
            ):
                await uow.get(BigPlanStatsRepository).mark_inbox_task_done(
                    new_big_plan.ref_id,
                )
            elif (
                inbox_task_before_update.is_completed
                and not inbox_task_after_update.is_completed
            ):
                await uow.get(BigPlanStatsRepository).mark_inbox_task_undone(
                    new_big_plan.ref_id,
                )
        else:
            if previous_big_plan is not None:
                await uow.get(BigPlanStatsRepository).mark_remove_inbox_task(
                    previous_big_plan.ref_id,
                    inbox_task_before_update.is_completed,
                )

            if new_big_plan is not None:
                await uow.get(BigPlanStatsRepository).mark_add_inbox_task(
                    new_big_plan.ref_id,
                )
                if inbox_task_after_update.is_completed:
                    await uow.get(BigPlanStatsRepository).mark_inbox_task_done(
                        new_big_plan.ref_id,
                    )
