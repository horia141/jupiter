"""The command for updating a recurring task."""
import logging
from dataclasses import dataclass
from typing import Optional, Final, cast

from jupiter.domain import schedules
from jupiter.domain.adate import ADate
from jupiter.domain.difficulty import Difficulty
from jupiter.domain.eisen import Eisen
from jupiter.domain.inbox_tasks.infra.inbox_task_notion_manager import InboxTaskNotionManager
from jupiter.domain.inbox_tasks.notion_inbox_task import NotionInboxTask
from jupiter.domain.recurring_task_due_at_day import RecurringTaskDueAtDay
from jupiter.domain.recurring_task_due_at_month import RecurringTaskDueAtMonth
from jupiter.domain.recurring_task_due_at_time import RecurringTaskDueAtTime
from jupiter.domain.recurring_task_gen_params import RecurringTaskGenParams
from jupiter.domain.recurring_task_period import RecurringTaskPeriod
from jupiter.domain.recurring_task_skip_rule import RecurringTaskSkipRule
from jupiter.domain.recurring_task_type import RecurringTaskType
from jupiter.domain.recurring_tasks.infra.recurring_task_notion_manager import RecurringTaskNotionManager
from jupiter.domain.recurring_tasks.recurring_task_name import RecurringTaskName
from jupiter.domain.storage_engine import StorageEngine
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.base.timestamp import Timestamp
from jupiter.framework.event import EventSource
from jupiter.framework.update_action import UpdateAction
from jupiter.framework.use_case import UseCase
from jupiter.utils.global_properties import GlobalProperties
from jupiter.utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class RecurringTaskUpdateUseCase(UseCase['RecurringTaskUpdateUseCase.Args', None]):
    """The command for updating a recurring task."""

    @dataclass()
    class Args:
        """Args."""
        ref_id: EntityId
        name: UpdateAction[RecurringTaskName]
        period: UpdateAction[RecurringTaskPeriod]
        the_type: UpdateAction[RecurringTaskType]
        eisen: UpdateAction[Eisen]
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
    _storage_engine: Final[StorageEngine]
    _inbox_task_notion_manager: Final[InboxTaskNotionManager]
    _recurring_task_notion_manager: Final[RecurringTaskNotionManager]

    def __init__(
            self, global_properties: GlobalProperties, time_provider: TimeProvider,
            storage_engine: StorageEngine, inbox_task_notion_manager: InboxTaskNotionManager,
            recurring_task_notion_manager: RecurringTaskNotionManager) -> None:
        """Constructor."""
        self._global_properties = global_properties
        self._time_provider = time_provider
        self._storage_engine = storage_engine
        self._inbox_task_notion_manager = inbox_task_notion_manager
        self._recurring_task_notion_manager = recurring_task_notion_manager

    def execute(self, args: Args) -> None:
        """Execute the command's action."""
        need_to_change_inbox_tasks = False

        with self._storage_engine.get_unit_of_work() as uow:
            recurring_task = uow.recurring_task_repository.load_by_id(args.ref_id)

            need_to_change_inbox_tasks = \
                args.name.should_change or \
                args.period.should_change or \
                args.the_type.should_change or \
                args.eisen.should_change or \
                args.difficulty.should_change or \
                args.actionable_from_day.should_change or \
                args.actionable_from_month.should_change or \
                args.due_at_time.should_change or \
                args.due_at_day.should_change or \
                args.due_at_month.should_change

            if args.eisen.should_change or \
                args.difficulty.should_change or \
                args.actionable_from_day.should_change or \
                args.actionable_from_month.should_change or \
                args.due_at_time.should_change or \
                args.due_at_day.should_change or \
                args.due_at_month.should_change:
                need_to_change_inbox_tasks = True
                recurring_task_gen_params = \
                    UpdateAction.change_to(
                        RecurringTaskGenParams(
                            recurring_task.project_ref_id,
                            recurring_task.period,
                            args.eisen.or_else(recurring_task.gen_params.eisen),
                            args.difficulty.or_else(recurring_task.gen_params.difficulty),
                            args.actionable_from_day.or_else(recurring_task.gen_params.actionable_from_day),
                            args.actionable_from_month.or_else(recurring_task.gen_params.actionable_from_month),
                            args.due_at_time.or_else(recurring_task.gen_params.due_at_time),
                            args.due_at_day.or_else(recurring_task.gen_params.due_at_day),
                            args.due_at_month.or_else(recurring_task.gen_params.due_at_month)))
            else:
                recurring_task_gen_params = UpdateAction.do_nothing()

            recurring_task.update(
                name=args.name, period=args.period, the_type=args.the_type, gen_params=recurring_task_gen_params,
                must_do=args.must_do, skip_rule=args.skip_rule, start_at_date=args.start_at_date,
                end_at_date=args.end_at_date, source=EventSource.CLI,
                modification_time=self._time_provider.get_current_time())

        notion_recurring_task = \
            self._recurring_task_notion_manager.load_recurring_task(
                recurring_task.recurring_task_collection_ref_id, recurring_task.ref_id)
        notion_recurring_task = notion_recurring_task.join_with_aggregate_root(recurring_task, None)
        self._recurring_task_notion_manager.save_recurring_task(
            recurring_task.recurring_task_collection_ref_id, notion_recurring_task)

        if need_to_change_inbox_tasks:
            with self._storage_engine.get_unit_of_work() as uow:
                all_inbox_tasks = \
                    uow.inbox_task_repository.find_all(
                        allow_archived=True, filter_recurring_task_ref_ids=[recurring_task.ref_id])

            for inbox_task in all_inbox_tasks:
                schedule = schedules.get_schedule(
                    recurring_task.period, recurring_task.name,
                    cast(Timestamp, inbox_task.recurring_gen_right_now), self._global_properties.timezone,
                    recurring_task.skip_rule, recurring_task.gen_params.actionable_from_day,
                    recurring_task.gen_params.actionable_from_month, recurring_task.gen_params.due_at_time,
                    recurring_task.gen_params.due_at_day, recurring_task.gen_params.due_at_month)

                inbox_task.update_link_to_recurring_task(
                    name=schedule.full_name,
                    timeline=schedule.timeline,
                    the_type=recurring_task.the_type,
                    actionable_date=schedule.actionable_date,
                    due_time=schedule.due_time,
                    eisen=recurring_task.gen_params.eisen,
                    difficulty=recurring_task.gen_params.difficulty,
                    source=EventSource.CLI,
                    modification_time=self._time_provider.get_current_time())

                with self._storage_engine.get_unit_of_work() as uow:
                    uow.inbox_task_repository.save(inbox_task)

                notion_inbox_task = \
                    self._inbox_task_notion_manager.load_inbox_task(
                        inbox_task.inbox_task_collection_ref_id, inbox_task.ref_id)
                notion_inbox_task = notion_inbox_task.join_with_aggregate_root(
                    inbox_task, NotionInboxTask.DirectInfo(None))
                self._inbox_task_notion_manager.save_inbox_task(
                    inbox_task.inbox_task_collection_ref_id, notion_inbox_task)
                LOGGER.info("Applied Notion changes")
