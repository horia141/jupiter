"""The command for updating a chore."""
from typing import cast

from jupiter.core.domain.concept.chores.chore import Chore
from jupiter.core.domain.concept.chores.chore_name import ChoreName
from jupiter.core.domain.concept.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.concept.inbox_tasks.inbox_task_collection import (
    InboxTaskCollection,
)
from jupiter.core.domain.concept.projects.project import Project
from jupiter.core.domain.core import schedules
from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.core.difficulty import Difficulty
from jupiter.core.domain.core.eisen import Eisen
from jupiter.core.domain.core.recurring_task_due_at_day import RecurringTaskDueAtDay
from jupiter.core.domain.core.recurring_task_due_at_month import RecurringTaskDueAtMonth
from jupiter.core.domain.core.recurring_task_gen_params import RecurringTaskGenParams
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.domain.core.recurring_task_skip_rule import RecurringTaskSkipRule
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.update_action import UpdateAction
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
class ChoreUpdateArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId
    name: UpdateAction[ChoreName]
    period: UpdateAction[RecurringTaskPeriod]
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


@mutation_use_case(WorkspaceFeature.CHORES)
class ChoreUpdateUseCase(
    AppTransactionalLoggedInMutationUseCase[ChoreUpdateArgs, None]
):
    """The command for updating a chore."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: ChoreUpdateArgs,
    ) -> None:
        """Execute the command's action."""
        workspace = context.workspace

        chore = await uow.get_for(Chore).load_by_id(args.ref_id)

        project = await uow.get_for(Project).load_by_id(chore.project_ref_id)

        need_to_change_inbox_tasks = (
            args.name.should_change
            or args.period.should_change
            or args.eisen.should_change
            or args.difficulty.should_change
            or args.actionable_from_day.should_change
            or args.actionable_from_month.should_change
            or args.due_at_day.should_change
            or args.due_at_month.should_change
        )

        if (
            args.period.should_change
            or args.eisen.should_change
            or args.difficulty.should_change
            or args.actionable_from_day.should_change
            or args.actionable_from_month.should_change
            or args.due_at_day.should_change
            or args.due_at_month.should_change
            or args.skip_rule.should_change
        ):
            need_to_change_inbox_tasks = True
            chore_gen_params = UpdateAction.change_to(
                RecurringTaskGenParams(
                    args.period.or_else(chore.gen_params.period),
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

        chore = chore.update(
            ctx=context.domain_context,
            name=args.name,
            gen_params=chore_gen_params,
            must_do=args.must_do,
            start_at_date=args.start_at_date,
            end_at_date=args.end_at_date,
        )

        await uow.get_for(Chore).save(chore)
        await progress_reporter.mark_updated(chore)

        if need_to_change_inbox_tasks:
            inbox_task_collection = await uow.get_for(
                InboxTaskCollection
            ).load_by_parent(
                workspace.ref_id,
            )
            all_inbox_tasks = await uow.get_for(InboxTask).find_all_generic(
                parent_ref_id=inbox_task_collection.ref_id,
                allow_archived=True,
                chore_ref_id=[chore.ref_id],
            )

            for inbox_task in all_inbox_tasks:
                schedule = schedules.get_schedule(
                    chore.gen_params.period,
                    chore.name,
                    cast(Timestamp, inbox_task.recurring_gen_right_now),
                    chore.gen_params.skip_rule,
                    chore.gen_params.actionable_from_day,
                    chore.gen_params.actionable_from_month,
                    chore.gen_params.due_at_day,
                    chore.gen_params.due_at_month,
                )

                inbox_task = inbox_task.update_link_to_chore(
                    ctx=context.domain_context,
                    project_ref_id=project.ref_id,
                    name=schedule.full_name,
                    timeline=schedule.timeline,
                    actionable_date=schedule.actionable_date,
                    due_date=schedule.due_date,
                    eisen=chore.gen_params.eisen,
                    difficulty=chore.gen_params.difficulty,
                )

                await uow.get_for(InboxTask).save(inbox_task)
                await progress_reporter.mark_updated(inbox_task)
