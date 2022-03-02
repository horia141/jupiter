"""The command for updating a habit."""
import logging
from dataclasses import dataclass
from typing import Optional, Final, cast

from jupiter.domain import schedules
from jupiter.domain.difficulty import Difficulty
from jupiter.domain.eisen import Eisen
from jupiter.domain.habits.habit_name import HabitName
from jupiter.domain.habits.infra.habit_notion_manager import HabitNotionManager
from jupiter.domain.habits.notion_habit import NotionHabit
from jupiter.domain.inbox_tasks.infra.inbox_task_notion_manager import InboxTaskNotionManager
from jupiter.domain.inbox_tasks.notion_inbox_task import NotionInboxTask
from jupiter.domain.recurring_task_due_at_day import RecurringTaskDueAtDay
from jupiter.domain.recurring_task_due_at_month import RecurringTaskDueAtMonth
from jupiter.domain.recurring_task_due_at_time import RecurringTaskDueAtTime
from jupiter.domain.recurring_task_gen_params import RecurringTaskGenParams
from jupiter.domain.recurring_task_period import RecurringTaskPeriod
from jupiter.domain.recurring_task_skip_rule import RecurringTaskSkipRule
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.base.timestamp import Timestamp
from jupiter.framework.event import EventSource
from jupiter.framework.update_action import UpdateAction
from jupiter.framework.use_case import MutationUseCaseInvocationRecorder, UseCaseArgsBase
from jupiter.use_cases.infra.use_cases import AppMutationUseCase, AppUseCaseContext
from jupiter.utils.global_properties import GlobalProperties
from jupiter.utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class HabitUpdateUseCase(AppMutationUseCase['HabitUpdateUseCase.Args', None]):
    """The command for updating a habit."""

    @dataclass(frozen=True)
    class Args(UseCaseArgsBase):
        """Args."""
        ref_id: EntityId
        name: UpdateAction[HabitName]
        period: UpdateAction[RecurringTaskPeriod]
        eisen: UpdateAction[Eisen]
        difficulty: UpdateAction[Optional[Difficulty]]
        actionable_from_day: UpdateAction[Optional[RecurringTaskDueAtDay]]
        actionable_from_month: UpdateAction[Optional[RecurringTaskDueAtMonth]]
        due_at_time: UpdateAction[Optional[RecurringTaskDueAtTime]]
        due_at_day: UpdateAction[Optional[RecurringTaskDueAtDay]]
        due_at_month: UpdateAction[Optional[RecurringTaskDueAtMonth]]
        skip_rule: UpdateAction[Optional[RecurringTaskSkipRule]]
        repeats_in_period_count: UpdateAction[Optional[int]]

    _global_properties: Final[GlobalProperties]
    _inbox_task_notion_manager: Final[InboxTaskNotionManager]
    _habit_notion_manager: Final[HabitNotionManager]

    def __init__(
            self,
            global_properties: GlobalProperties,
            time_provider: TimeProvider,
            invocation_recorder: MutationUseCaseInvocationRecorder,
            storage_engine: DomainStorageEngine,
            inbox_task_notion_manager: InboxTaskNotionManager,
            habit_notion_manager: HabitNotionManager) -> None:
        """Constructor."""
        super().__init__(time_provider, invocation_recorder, storage_engine)
        self._global_properties = global_properties
        self._inbox_task_notion_manager = inbox_task_notion_manager
        self._habit_notion_manager = habit_notion_manager

    def _execute(self, context: AppUseCaseContext, args: Args) -> None:
        """Execute the command's action."""
        workspace = context.workspace

        with self._storage_engine.get_unit_of_work() as uow:
            habit = uow.habit_repository.load_by_id(args.ref_id)
            project = uow.project_repository.load_by_id(habit.project_ref_id)

            need_to_change_inbox_tasks = \
                args.name.should_change or \
                args.period.should_change or \
                args.eisen.should_change or \
                args.difficulty.should_change or \
                args.actionable_from_day.should_change or \
                args.actionable_from_month.should_change or \
                args.due_at_time.should_change or \
                args.due_at_day.should_change or \
                args.due_at_month.should_change or \
                args.repeats_in_period_count.should_change

            if args.period.should_change or \
                args.eisen.should_change or \
                args.difficulty.should_change or \
                args.actionable_from_day.should_change or \
                args.actionable_from_month.should_change or \
                args.due_at_time.should_change or \
                args.due_at_day.should_change or \
                args.due_at_month.should_change:
                need_to_change_inbox_tasks = True
                habit_gen_params = \
                    UpdateAction.change_to(
                        RecurringTaskGenParams(
                            args.period.or_else(habit.gen_params.period),
                            args.eisen.or_else(habit.gen_params.eisen),
                            args.difficulty.or_else(habit.gen_params.difficulty),
                            args.actionable_from_day.or_else(habit.gen_params.actionable_from_day),
                            args.actionable_from_month.or_else(habit.gen_params.actionable_from_month),
                            args.due_at_time.or_else(habit.gen_params.due_at_time),
                            args.due_at_day.or_else(habit.gen_params.due_at_day),
                            args.due_at_month.or_else(habit.gen_params.due_at_month)))
            else:
                habit_gen_params = UpdateAction.do_nothing()

            habit = \
                habit.update(
                    name=args.name,
                    gen_params=habit_gen_params,
                    skip_rule=args.skip_rule,
                    repeats_in_period_count=args.repeats_in_period_count,
                    source=EventSource.CLI,
                    modification_time=self._time_provider.get_current_time())

            uow.habit_repository.save(habit)

        habit_direct_info = NotionHabit.DirectInfo(project_name=project.name)
        notion_habit = self._habit_notion_manager.load_habit(habit.habit_collection_ref_id, habit.ref_id)
        notion_habit = notion_habit.join_with_entity(habit, habit_direct_info)
        self._habit_notion_manager.save_habit(habit.habit_collection_ref_id, notion_habit)

        if need_to_change_inbox_tasks:
            with self._storage_engine.get_unit_of_work() as uow:
                inbox_task_collection = uow.inbox_task_collection_repository.load_by_workspace(workspace.ref_id)
                all_inbox_tasks = \
                    uow.inbox_task_repository.find_all(
                        inbox_task_collection_ref_id=inbox_task_collection.ref_id,
                        allow_archived=True, filter_habit_ref_ids=[habit.ref_id])

            for inbox_task in all_inbox_tasks:
                schedule = schedules.get_schedule(
                    habit.gen_params.period, habit.name,
                    cast(Timestamp, inbox_task.recurring_gen_right_now), self._global_properties.timezone,
                    habit.skip_rule, habit.gen_params.actionable_from_day,
                    habit.gen_params.actionable_from_month, habit.gen_params.due_at_time,
                    habit.gen_params.due_at_day, habit.gen_params.due_at_month)

                inbox_task = \
                    inbox_task.update_link_to_habit(
                        project_ref_id=project.ref_id,
                        name=schedule.full_name,
                        timeline=schedule.timeline,
                        repeat_index=inbox_task.recurring_repeat_index,
                        actionable_date=schedule.actionable_date,
                        due_date=schedule.due_time,
                        eisen=habit.gen_params.eisen,
                        difficulty=habit.gen_params.difficulty,
                        source=EventSource.CLI,
                        modification_time=self._time_provider.get_current_time())

                with self._storage_engine.get_unit_of_work() as uow:
                    uow.inbox_task_repository.save(inbox_task)

                if inbox_task.archived:
                    continue

                inbox_task_direct_info = NotionInboxTask.DirectInfo(project_name=project.name, big_plan_name=None)
                notion_inbox_task = \
                    self._inbox_task_notion_manager.load_inbox_task(
                        inbox_task.inbox_task_collection_ref_id, inbox_task.ref_id)
                notion_inbox_task = notion_inbox_task.join_with_entity(inbox_task, inbox_task_direct_info)
                self._inbox_task_notion_manager.save_inbox_task(
                    inbox_task.inbox_task_collection_ref_id, notion_inbox_task)
                LOGGER.info("Applied Notion changes")
