"""The command for associating a inbox task with a big plan."""

from jupiter.core.domain.big_plans.big_plan import BigPlan
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.inbox_tasks.inbox_task import (
    CannotModifyGeneratedTaskError,
    InboxTask,
)
from jupiter.core.domain.infra.generic_creator import generic_creator
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.domain.time_plans.time_plan import TimePlan
from jupiter.core.domain.time_plans.time_plan_activity import (
    TimePlanActivity,
    TimePlanActivityRespository,
    TimePlanAlreadyAssociatedWithTargetError,
)
from jupiter.core.domain.time_plans.time_plan_activity_feasability import (
    TimePlanActivityFeasability,
)
from jupiter.core.domain.time_plans.time_plan_activity_kind import TimePlanActivityKind
from jupiter.core.domain.time_plans.time_plan_activity_target import (
    TimePlanActivityTarget,
)
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.use_case import (
    ProgressReporter,
)
from jupiter.core.framework.use_case_io import UseCaseArgsBase, use_case_args
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
    mutation_use_case,
)


@use_case_args
class InboxTaskAssociateWithBigPlanArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId
    big_plan_ref_id: EntityId | None


@mutation_use_case([WorkspaceFeature.INBOX_TASKS, WorkspaceFeature.BIG_PLANS])
class InboxTaskAssociateWithBigPlanUseCase(
    AppTransactionalLoggedInMutationUseCase[InboxTaskAssociateWithBigPlanArgs, None],
):
    """The command for associating a inbox task with a big plan."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: InboxTaskAssociateWithBigPlanArgs,
    ) -> None:
        """Execute the command's action."""
        workspace = context.workspace
        inbox_task = await uow.get_for(InboxTask).load_by_id(args.ref_id)

        try:
            if args.big_plan_ref_id:
                big_plan = await uow.get_for(BigPlan).load_by_id(
                    args.big_plan_ref_id,
                )
                inbox_task = inbox_task.associate_with_big_plan(
                    ctx=context.domain_context,
                    project_ref_id=big_plan.project_ref_id,
                    big_plan_ref_id=args.big_plan_ref_id,
                )

                if workspace.is_feature_available(WorkspaceFeature.TIME_PLANS):
                    # We go to all timeplans where this inbox task has an activity
                    # and add an activity for the big plan if there isn't one.
                    # But we don't go to all timeplans and remove the big plan. That's
                    # done just one.
                    time_plan_ref_ids = await uow.get(
                        TimePlanActivityRespository
                    ).find_all_with_target(
                        target=TimePlanActivityTarget.INBOX_TASK,
                        target_ref_id=args.ref_id,
                    )

                    for time_plan_ref_id in time_plan_ref_ids:
                        try:
                            big_plan_activity = (
                                TimePlanActivity.new_activity_for_big_plan(
                                    ctx=context.domain_context,
                                    time_plan_ref_id=time_plan_ref_id,
                                    big_plan_ref_id=args.big_plan_ref_id,
                                    kind=TimePlanActivityKind.MAKE_PROGRESS,
                                    feasability=TimePlanActivityFeasability.MUST_DO,
                                )
                            )

                            _ = await generic_creator(
                                uow, progress_reporter, big_plan_activity
                            )
                            from rich import print

                            print(big_plan)
                            if (
                                big_plan.actionable_date is None
                                or big_plan.due_date is None
                            ):
                                time_plan = await uow.get_for(TimePlan).load_by_id(
                                    time_plan_ref_id
                                )
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
            else:
                inbox_task = inbox_task.release_from_big_plan(
                    ctx=context.domain_context,
                )
        except CannotModifyGeneratedTaskError as err:
            raise InputValidationError(
                f"Modifying a generated task's field {err.field} is not possible",
            ) from err

        await uow.get_for(InboxTask).save(inbox_task)
        await progress_reporter.mark_updated(inbox_task)
