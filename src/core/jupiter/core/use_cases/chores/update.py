"""The command for updating a chore."""
from dataclasses import dataclass
from typing import Iterable, Optional, cast

from jupiter.core.domain import schedules
from jupiter.core.domain.adate import ADate
from jupiter.core.domain.chores.chore_name import ChoreName
from jupiter.core.domain.difficulty import Difficulty
from jupiter.core.domain.eisen import Eisen
from jupiter.core.domain.features import Feature
from jupiter.core.domain.recurring_task_due_at_day import RecurringTaskDueAtDay
from jupiter.core.domain.recurring_task_due_at_month import RecurringTaskDueAtMonth
from jupiter.core.domain.recurring_task_due_at_time import RecurringTaskDueAtTime
from jupiter.core.domain.recurring_task_gen_params import RecurringTaskGenParams
from jupiter.core.domain.recurring_task_period import RecurringTaskPeriod
from jupiter.core.domain.recurring_task_skip_rule import RecurringTaskSkipRule
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.update_action import UpdateAction
from jupiter.core.framework.use_case import (
    ProgressReporter,
    UseCaseArgsBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCase,
    AppLoggedInUseCaseContext,
)


@dataclass
class ChoreUpdateArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId
    name: UpdateAction[ChoreName]
    period: UpdateAction[RecurringTaskPeriod]
    eisen: UpdateAction[Optional[Eisen]]
    difficulty: UpdateAction[Optional[Difficulty]]
    actionable_from_day: UpdateAction[Optional[RecurringTaskDueAtDay]]
    actionable_from_month: UpdateAction[Optional[RecurringTaskDueAtMonth]]
    due_at_time: UpdateAction[Optional[RecurringTaskDueAtTime]]
    due_at_day: UpdateAction[Optional[RecurringTaskDueAtDay]]
    due_at_month: UpdateAction[Optional[RecurringTaskDueAtMonth]]
    must_do: UpdateAction[bool]
    skip_rule: UpdateAction[Optional[RecurringTaskSkipRule]]
    start_at_date: UpdateAction[ADate]
    end_at_date: UpdateAction[Optional[ADate]]


class ChoreUpdateUseCase(AppLoggedInMutationUseCase[ChoreUpdateArgs, None]):
    """The command for updating a chore."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[Feature] | Feature | None:
        """The feature the use case is scope to."""
        return Feature.CHORES

    async def _perform_mutation(
        self,
        progress_reporter: ProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: ChoreUpdateArgs,
    ) -> None:
        """Execute the command's action."""
        user = context.user
        workspace = context.workspace

        async with self._domain_storage_engine.get_unit_of_work() as uow:
            chore = await uow.chore_repository.load_by_id(args.ref_id)

            project = await uow.project_repository.load_by_id(chore.project_ref_id)

            need_to_change_inbox_tasks = (
                args.name.should_change
                or args.period.should_change
                or args.eisen.should_change
                or args.difficulty.should_change
                or args.actionable_from_day.should_change
                or args.actionable_from_month.should_change
                or args.due_at_time.should_change
                or args.due_at_day.should_change
                or args.due_at_month.should_change
            )

            if (
                args.period.should_change
                or args.eisen.should_change
                or args.difficulty.should_change
                or args.actionable_from_day.should_change
                or args.actionable_from_month.should_change
                or args.due_at_time.should_change
                or args.due_at_day.should_change
                or args.due_at_month.should_change
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
                        args.due_at_time.or_else(chore.gen_params.due_at_time),
                        args.due_at_day.or_else(chore.gen_params.due_at_day),
                        args.due_at_month.or_else(chore.gen_params.due_at_month),
                    ),
                )
            else:
                chore_gen_params = UpdateAction.do_nothing()

            chore = chore.update(
                name=args.name,
                gen_params=chore_gen_params,
                must_do=args.must_do,
                start_at_date=args.start_at_date,
                end_at_date=args.end_at_date,
                skip_rule=args.skip_rule,
                source=EventSource.CLI,
                modification_time=self._time_provider.get_current_time(),
            )

            await uow.chore_repository.save(chore)
            await progress_reporter.mark_updated(chore)

            if need_to_change_inbox_tasks:
                inbox_task_collection = (
                    await uow.inbox_task_collection_repository.load_by_parent(
                        workspace.ref_id,
                    )
                )
                all_inbox_tasks = await uow.inbox_task_repository.find_all_with_filters(
                    parent_ref_id=inbox_task_collection.ref_id,
                    allow_archived=True,
                    filter_chore_ref_ids=[chore.ref_id],
                )

                for inbox_task in all_inbox_tasks:
                    schedule = schedules.get_schedule(
                        chore.gen_params.period,
                        chore.name,
                        cast(Timestamp, inbox_task.recurring_gen_right_now),
                        user.timezone,
                        chore.skip_rule,
                        chore.gen_params.actionable_from_day,
                        chore.gen_params.actionable_from_month,
                        chore.gen_params.due_at_time,
                        chore.gen_params.due_at_day,
                        chore.gen_params.due_at_month,
                    )

                    inbox_task = inbox_task.update_link_to_chore(
                        project_ref_id=project.ref_id,
                        name=schedule.full_name,
                        timeline=schedule.timeline,
                        actionable_date=schedule.actionable_date,
                        due_date=schedule.due_time,
                        eisen=chore.gen_params.eisen,
                        difficulty=chore.gen_params.difficulty,
                        source=EventSource.CLI,
                        modification_time=self._time_provider.get_current_time(),
                    )

                    await uow.inbox_task_repository.save(inbox_task)
                    await progress_reporter.mark_updated(inbox_task)
