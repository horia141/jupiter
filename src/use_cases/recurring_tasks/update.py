"""The command for updating a recurring task."""
import logging
from dataclasses import dataclass
from typing import Optional, List, Final, cast

from domain import schedules
from domain.adate import ADate
from domain.difficulty import Difficulty
from domain.eisen import Eisen
from domain.entity_name import EntityName
from domain.inbox_tasks.infra.inbox_task_engine import InboxTaskEngine
from domain.inbox_tasks.infra.inbox_task_notion_manager import InboxTaskNotionManager
from domain.inbox_tasks.notion_inbox_task import NotionInboxTask
from domain.recurring_task_due_at_day import RecurringTaskDueAtDay
from domain.recurring_task_due_at_month import RecurringTaskDueAtMonth
from domain.recurring_task_due_at_time import RecurringTaskDueAtTime
from domain.recurring_task_gen_params import RecurringTaskGenParams
from domain.recurring_task_period import RecurringTaskPeriod
from domain.recurring_task_skip_rule import RecurringTaskSkipRule
from domain.recurring_task_type import RecurringTaskType
from domain.recurring_tasks.infra.recurring_task_engine import RecurringTaskEngine
from domain.recurring_tasks.infra.recurring_task_notion_manager import RecurringTaskNotionManager
from framework.base.entity_id import EntityId
from framework.base.timestamp import Timestamp
from framework.update_action import UpdateAction
from framework.use_case import UseCase
from utils.global_properties import GlobalProperties
from utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class RecurringTaskUpdateUseCase(UseCase['RecurringTaskUpdateUseCase.Args', None]):
    """The command for updating a recurring task."""

    @dataclass()
    class Args:
        """Args."""
        ref_id: EntityId
        name: UpdateAction[EntityName]
        period: UpdateAction[RecurringTaskPeriod]
        the_type: UpdateAction[RecurringTaskType]
        eisen: UpdateAction[List[Eisen]]
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

    _global_properties: Final[GlobalProperties]
    _time_provider: Final[TimeProvider]
    _inbox_task_engine: Final[InboxTaskEngine]
    _inbox_task_notion_manager: Final[InboxTaskNotionManager]
    _recurring_task_engine: Final[RecurringTaskEngine]
    _recurring_task_notion_manager: Final[RecurringTaskNotionManager]

    def __init__(
            self, global_properties: GlobalProperties, time_provider: TimeProvider,
            inbox_task_engine: InboxTaskEngine, inbox_task_notion_manager: InboxTaskNotionManager,
            recurring_task_engine: RecurringTaskEngine,
            recurring_task_notion_manager: RecurringTaskNotionManager) -> None:
        """Constructor."""
        self._global_properties = global_properties
        self._time_provider = time_provider
        self._inbox_task_engine = inbox_task_engine
        self._inbox_task_notion_manager = inbox_task_notion_manager
        self._recurring_task_engine = recurring_task_engine
        self._recurring_task_notion_manager = recurring_task_notion_manager

    def execute(self, args: Args) -> None:
        """Execute the command's action."""
        need_to_change_inbox_tasks = False

        with self._recurring_task_engine.get_unit_of_work() as uow:
            recurring_task = uow.recurring_task_repository.load_by_id(args.ref_id)

            if args.name.should_change:
                need_to_change_inbox_tasks = True
                recurring_task.change_name(args.name.value, self._time_provider.get_current_time())

            if args.period.should_change:
                need_to_change_inbox_tasks = True
                recurring_task.change_period(args.period.value, self._time_provider.get_current_time())

            if args.the_type.should_change:
                need_to_change_inbox_tasks = True
                recurring_task.change_type(args.the_type.value, self._time_provider.get_current_time())

            if args.eisen.should_change or \
                args.difficulty.should_change or \
                args.actionable_from_day.should_change or \
                args.actionable_from_month.should_change or \
                args.due_at_time.should_change or \
                args.due_at_day.should_change or \
                args.due_at_month.should_change:
                need_to_change_inbox_tasks = True
                recurring_task.change_gen_params(
                    RecurringTaskGenParams(
                        recurring_task.project_ref_id,
                        recurring_task.period,
                        args.eisen.or_else(recurring_task.gen_params.eisen),
                        args.difficulty.or_else(recurring_task.gen_params.difficulty),
                        args.actionable_from_day.or_else(recurring_task.gen_params.actionable_from_day),
                        args.actionable_from_month.or_else(recurring_task.gen_params.actionable_from_month),
                        args.due_at_time.or_else(recurring_task.gen_params.due_at_time),
                        args.due_at_day.or_else(recurring_task.gen_params.due_at_day),
                        args.due_at_month.or_else(recurring_task.gen_params.due_at_month)
                    ),
                    self._time_provider.get_current_time())

            if args.must_do.should_change:
                recurring_task.change_must_do(args.must_do.value, self._time_provider.get_current_time())

            if args.skip_rule.should_change:
                recurring_task.change_skip_rule(args.skip_rule.value, self._time_provider.get_current_time())

            if args.start_at_date.should_change or args.end_at_date.should_change:
                recurring_task.change_active_interval(
                    args.start_at_date.or_else(recurring_task.start_at_date),
                    args.end_at_date.or_else(recurring_task.end_at_date),
                    self._time_provider.get_current_time())

        notion_recurring_task = \
            self._recurring_task_notion_manager.load_recurring_task(recurring_task.project_ref_id,
                                                                    recurring_task.ref_id)
        notion_recurring_task = notion_recurring_task.join_with_aggregate_root(recurring_task, None)
        self._recurring_task_notion_manager.save_recurring_task(recurring_task.project_ref_id, notion_recurring_task)

        if need_to_change_inbox_tasks:
            with self._inbox_task_engine.get_unit_of_work() as inbox_task_uow:
                all_inbox_tasks = \
                    inbox_task_uow.inbox_task_repository.find_all(
                        allow_archived=True, filter_recurring_task_ref_ids=[recurring_task.ref_id])

            for inbox_task in all_inbox_tasks:
                schedule = schedules.get_schedule(
                    recurring_task.period, recurring_task.name,
                    cast(Timestamp, inbox_task.recurring_gen_right_now), self._global_properties.timezone,
                    recurring_task.skip_rule, recurring_task.gen_params.actionable_from_day,
                    recurring_task.gen_params.actionable_from_month, recurring_task.gen_params.due_at_time,
                    recurring_task.gen_params.due_at_day, recurring_task.gen_params.due_at_month)

                inbox_task.update_link_to_recurring_task(schedule.full_name, schedule.timeline, recurring_task.the_type,
                                                         schedule.actionable_date, schedule.due_time,
                                                         recurring_task.gen_params.eisen,
                                                         recurring_task.gen_params.difficulty,
                                                         self._time_provider.get_current_time())

                with self._inbox_task_engine.get_unit_of_work() as inbox_task_uow:
                    inbox_task_uow.inbox_task_repository.save(inbox_task)

                notion_inbox_task = \
                    self._inbox_task_notion_manager.load_inbox_task(inbox_task.project_ref_id, inbox_task.ref_id)
                notion_inbox_task = notion_inbox_task.join_with_aggregate_root(
                    inbox_task, NotionInboxTask.DirectInfo(None))
                self._inbox_task_notion_manager.save_inbox_task(inbox_task.project_ref_id, notion_inbox_task)
                LOGGER.info("Applied Notion changes")
