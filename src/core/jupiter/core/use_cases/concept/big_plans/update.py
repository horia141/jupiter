"""The command for updating a big plan."""

from jupiter.core.domain.application.gamification.service.record_score_service import (
    RecordScoreResult,
    RecordScoreService,
)
from jupiter.core.domain.concept.big_plans.big_plan import BigPlan
from jupiter.core.domain.concept.big_plans.big_plan_milestone import BigPlanMilestone
from jupiter.core.domain.concept.big_plans.big_plan_name import BigPlanName
from jupiter.core.domain.concept.big_plans.big_plan_status import BigPlanStatus
from jupiter.core.domain.concept.inbox_tasks.inbox_task import (
    InboxTask,
    InboxTaskRepository,
)
from jupiter.core.domain.concept.inbox_tasks.inbox_task_collection import (
    InboxTaskCollection,
)
from jupiter.core.domain.concept.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.core.difficulty import Difficulty
from jupiter.core.domain.core.eisen import Eisen
from jupiter.core.domain.features import UserFeature, WorkspaceFeature
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
class BigPlanUpdateArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId
    name: UpdateAction[BigPlanName]
    status: UpdateAction[BigPlanStatus]
    project_ref_id: UpdateAction[EntityId]
    is_key: UpdateAction[bool]
    eisen: UpdateAction[Eisen]
    difficulty: UpdateAction[Difficulty]
    actionable_date: UpdateAction[ADate | None]
    due_date: UpdateAction[ADate | None]


@use_case_result
class BigPlanUpdateResult(UseCaseResultBase):
    """InboxTaskUpdate result."""

    record_score_result: RecordScoreResult | None


@mutation_use_case(WorkspaceFeature.BIG_PLANS)
class BigPlanUpdateUseCase(
    AppTransactionalLoggedInMutationUseCase[BigPlanUpdateArgs, BigPlanUpdateResult]
):
    """The command for updating a big plan."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: BigPlanUpdateArgs,
    ) -> BigPlanUpdateResult:
        """Execute the command's action."""
        workspace = context.workspace
        big_plan = await uow.get_for(BigPlan).load_by_id(args.ref_id)

        # Check each milestone is within the new date bounds
        if args.actionable_date.should_change or args.due_date.should_change:
            # Get the new dates, falling back to existing ones if not changing
            new_actionable = args.actionable_date.or_else(big_plan.actionable_date)
            new_due = args.due_date.or_else(big_plan.due_date)

            milestones = await uow.get_for(BigPlanMilestone).find_all_generic(
                big_plan_ref_id=big_plan.ref_id,
                allow_archived=False,
            )

            for m in milestones:
                if new_actionable and m.date < new_actionable:
                    raise InputValidationError(
                        f"Milestone {m.name} date {m.date} is before new actionable date {new_actionable}"
                    )
                if new_due and m.date > new_due:
                    raise InputValidationError(
                        f"Milestone {m.name} date {m.date} is after new due date {new_due}"
                    )

        big_plan = big_plan.update(
            context.domain_context,
            name=args.name,
            status=args.status,
            project_ref_id=args.project_ref_id,
            is_key=args.is_key,
            eisen=args.eisen,
            difficulty=args.difficulty,
            actionable_date=args.actionable_date,
            due_date=args.due_date,
        )

        await uow.get_for(BigPlan).save(big_plan)
        await progress_reporter.mark_updated(big_plan)

        if args.project_ref_id.should_change:
            inbox_task_collection = await uow.get_for(
                InboxTaskCollection
            ).load_by_parent(
                workspace.ref_id,
            )
            all_inbox_tasks = await uow.get(
                InboxTaskRepository
            ).find_all_for_source_created_desc(
                parent_ref_id=inbox_task_collection.ref_id,
                allow_archived=True,
                source=InboxTaskSource.BIG_PLAN,
                source_entity_ref_id=big_plan.ref_id,
            )

            for inbox_task in all_inbox_tasks:
                inbox_task = inbox_task.update_link_to_big_plan(
                    context.domain_context,
                    big_plan.project_ref_id,
                    big_plan.ref_id,
                )
                await uow.get_for(InboxTask).save(inbox_task)
                await progress_reporter.mark_updated(inbox_task)

        record_score_result = None
        if context.user.is_feature_available(UserFeature.GAMIFICATION):
            record_score_result = await RecordScoreService().record_task(
                context.domain_context, uow, context.user, big_plan
            )

        return BigPlanUpdateResult(record_score_result=record_score_result)
