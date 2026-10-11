"""The command for updating a chore."""

from jupiter.core.apps.chores.name import ChoreName
from jupiter.core.apps.chores.root import Chore
from jupiter.core.apps.chores.sub.stack.root import ChoreStack
from jupiter.core.apps.life_plan.sub.aspects.root import Aspect
from jupiter.core.apps.life_plan.sub.chapters.root import Chapter
from jupiter.core.apps.life_plan.sub.goals.root import Goal
from jupiter.core.common.difficulty import Difficulty
from jupiter.core.common.eisen import Eisen
from jupiter.core.common.recurring_task_due_at_day import RecurringTaskDueAtDay
from jupiter.core.common.recurring_task_due_at_month import (
    RecurringTaskDueAtMonth,
)
from jupiter.core.common.recurring_task_gen_params import RecurringTaskGenParams
from jupiter.core.common.recurring_task_skip_rule import RecurringTaskSkipRule
from jupiter.core.common.scheduling_params import (
    Schedulability,
    build_scheduling_params_update,
)
from jupiter.core.config import (
    JupiterLoggedInMutationContext,
)
from jupiter.core.crown_entity_support import (
    JupiterUpdateCrownEntityArgs,
    JupiterUpdateCrownEntityUseCase,
)
from jupiter.core.features import WorkspaceFeature
from jupiter.framework.base.adate import ADate
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.errors import InputValidationError
from jupiter.framework.progress_reporter.reporter import ProgressReporter
from jupiter.framework.storage.repository import DomainUnitOfWork
from jupiter.framework.update_action import UpdateAction
from jupiter.framework.use_case import (
    UnavailableForContextError,
    mutation_use_case,
)
from jupiter.framework.use_case_io import (
    UseCaseResultBase,
    use_case_args,
    use_case_result,
)


@use_case_args
class ChoreUpdateArgs(JupiterUpdateCrownEntityArgs):
    """PersonFindArgs."""

    ref_id: EntityId
    name: UpdateAction[ChoreName]
    aspect_ref_id: UpdateAction[EntityId]
    chapter_ref_id: UpdateAction[EntityId | None]
    goal_ref_id: UpdateAction[EntityId | None]
    stack_ref_id: UpdateAction[EntityId | None]
    is_key: UpdateAction[bool]
    eisen: UpdateAction[Eisen]
    difficulty: UpdateAction[Difficulty]
    actionable_from_day: UpdateAction[RecurringTaskDueAtDay | None]
    actionable_from_month: UpdateAction[RecurringTaskDueAtMonth | None]
    due_at_day: UpdateAction[RecurringTaskDueAtDay | None]
    due_at_month: UpdateAction[RecurringTaskDueAtMonth | None]
    must_do: UpdateAction[bool]
    skip_rule: UpdateAction[RecurringTaskSkipRule | None]
    start_at_date: UpdateAction[ADate]
    end_at_date: UpdateAction[ADate | None]
    schedulability: UpdateAction[Schedulability]
    scheduling_event_duration_mins: UpdateAction[int | None]
    scheduling_event_count: UpdateAction[int | None]
    suspended: UpdateAction[bool]


@use_case_result
class ChoreUpdateResult(UseCaseResultBase):
    """ChoreUpdate result."""

    updated_chore: Chore


@mutation_use_case(WorkspaceFeature.CHORES)
class ChoreUpdateUseCase(
    JupiterUpdateCrownEntityUseCase[ChoreUpdateArgs, ChoreUpdateResult]
):
    """The command for updating a chore.

    Only the chore itself changes. Its inbox tasks catch up the next time they are
    generated - via a regen, or the periodic gen run.
    """

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: JupiterLoggedInMutationContext,
        args: ChoreUpdateArgs,
    ) -> ChoreUpdateResult:
        """Execute the command's action."""
        workspace = context.workspace

        chore = await self.load_entity(uow, context.user.ref_id, Chore, args.ref_id)

        if not workspace.is_feature_available(WorkspaceFeature.LIFE_PLAN):
            if (
                args.aspect_ref_id.should_change
                and args.aspect_ref_id.just_the_value is not None
            ):
                raise UnavailableForContextError(WorkspaceFeature.LIFE_PLAN)
            if (
                args.chapter_ref_id.should_change
                and args.chapter_ref_id.just_the_value is not None
            ):
                raise UnavailableForContextError(WorkspaceFeature.LIFE_PLAN)
            if (
                args.goal_ref_id.should_change
                and args.goal_ref_id.just_the_value is not None
            ):
                raise UnavailableForContextError(WorkspaceFeature.LIFE_PLAN)

        if (
            args.eisen.should_change
            or args.difficulty.should_change
            or args.actionable_from_day.should_change
            or args.actionable_from_month.should_change
            or args.due_at_day.should_change
            or args.due_at_month.should_change
            or args.skip_rule.should_change
        ):
            chore_gen_params = UpdateAction.change_to(
                RecurringTaskGenParams(
                    chore.gen_params.period,
                    args.eisen.or_else(chore.gen_params.eisen),
                    args.difficulty.or_else(chore.gen_params.difficulty),
                    args.actionable_from_day.or_else(
                        chore.gen_params.actionable_from_day,
                    ),
                    args.actionable_from_month.or_else(
                        chore.gen_params.actionable_from_month,
                    ),
                    args.due_at_day.or_else(chore.gen_params.due_at_day),
                    args.due_at_month.or_else(chore.gen_params.due_at_month),
                    args.skip_rule.or_else(chore.gen_params.skip_rule),
                ),
            )
        else:
            chore_gen_params = UpdateAction.do_nothing()

        if workspace.is_feature_available(WorkspaceFeature.LIFE_PLAN):
            new_aspect_ref_id = args.aspect_ref_id.or_else(chore.aspect_ref_id)
            new_chapter_ref_id = args.chapter_ref_id.or_else(chore.chapter_ref_id)
            new_goal_ref_id = args.goal_ref_id.or_else(chore.goal_ref_id)
            aspect_changing = (
                args.aspect_ref_id.should_change
                and new_aspect_ref_id != chore.aspect_ref_id
            )
            chapter_changing = (
                args.chapter_ref_id.should_change
                and new_chapter_ref_id != chore.chapter_ref_id
            )
            goal_changing = (
                args.goal_ref_id.should_change and new_goal_ref_id != chore.goal_ref_id
            )

            # Shared writers can keep the owner's life-plan links, but cannot
            # retarget them without writer access to those entities.
            if aspect_changing or chapter_changing or goal_changing:
                aspect = await self.load_entity(
                    uow,
                    context.user.ref_id,
                    Aspect,
                    new_aspect_ref_id,
                )

                if chapter_changing and new_chapter_ref_id is not None:
                    chapter = await self.load_entity(
                        uow, context.user.ref_id, Chapter, new_chapter_ref_id
                    )
                    if chapter.aspect_ref_id != aspect.ref_id:
                        raise InputValidationError(
                            f"Chapter does not belong to aspect '{aspect.name}'"
                        )

                if goal_changing and new_goal_ref_id is not None:
                    goal = await self.load_entity(
                        uow, context.user.ref_id, Goal, new_goal_ref_id
                    )
                    if goal.aspect_ref_id != aspect.ref_id:
                        raise InputValidationError(
                            f"Goal does not belong to aspect '{aspect.name}'"
                        )

        new_stack_ref_id = args.stack_ref_id.or_else(chore.stack_ref_id)
        stack_changing = (
            args.stack_ref_id.should_change and new_stack_ref_id != chore.stack_ref_id
        )
        if stack_changing and new_stack_ref_id is not None:
            stack = await self.load_entity(
                uow, context.user.ref_id, ChoreStack, new_stack_ref_id
            )
            if stack.period != chore.gen_params.period:
                raise InputValidationError("Chore period must match the stack period")

        chore_scheduling_params = build_scheduling_params_update(
            chore.scheduling_params,
            args.schedulability,
            args.scheduling_event_duration_mins,
            args.scheduling_event_count,
            args.difficulty.or_else(chore.gen_params.difficulty),
        )

        chore = chore.update(
            ctx=context.domain_context,
            aspect_ref_id=args.aspect_ref_id,
            chapter_ref_id=args.chapter_ref_id,
            goal_ref_id=args.goal_ref_id,
            stack_ref_id=args.stack_ref_id,
            name=args.name,
            is_key=args.is_key,
            gen_params=chore_gen_params,
            scheduling_params=chore_scheduling_params,
            must_do=args.must_do,
            start_at_date=args.start_at_date,
            end_at_date=args.end_at_date,
            suspended=args.suspended,
        )

        chore = await uow.get_for(Chore).save(chore)
        await progress_reporter.mark_updated(chore)

        return ChoreUpdateResult(updated_chore=chore)
