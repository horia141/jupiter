"""Update a person."""
import logging
import typing
from dataclasses import dataclass
from typing import Final, Optional, List

from domain.difficulty import Difficulty
from domain.eisen import Eisen
from domain.entity_name import EntityName
from domain.inbox_tasks.inbox_task_source import InboxTaskSource
from domain.inbox_tasks.infra.inbox_task_engine import InboxTaskEngine
from domain.inbox_tasks.infra.inbox_task_notion_manager import InboxTaskNotionManager
from domain.inbox_tasks.notion_inbox_task import NotionInboxTask
from domain.inbox_tasks.service.archive_service import InboxTaskArchiveService
from domain.prm.infra.prm_engine import PrmEngine
from domain.prm.infra.prm_notion_manager import PrmNotionManager
from domain.prm.person_birthday import PersonBirthday
from domain.prm.person_relationship import PersonRelationship
from domain.recurring_task_due_at_day import RecurringTaskDueAtDay
from domain.recurring_task_due_at_month import RecurringTaskDueAtMonth
from domain.recurring_task_due_at_time import RecurringTaskDueAtTime
from domain.recurring_task_gen_params import RecurringTaskGenParams
from domain.recurring_task_period import RecurringTaskPeriod
from domain.timestamp import Timestamp
from domain import schedules
from framework.update_action import UpdateAction
from framework.entity_id import EntityId
from framework.use_case import UseCase
from utils.global_properties import GlobalProperties
from utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class PersonUpdateUseCase(UseCase['PersonUpdateUseCase.Args', None]):
    """The command for updating a person."""

    @dataclass()
    class Args:
        """Args."""
        ref_id: EntityId
        name: UpdateAction[EntityName]
        relationship: UpdateAction[PersonRelationship]
        catch_up_period: UpdateAction[Optional[RecurringTaskPeriod]]
        catch_up_eisen: UpdateAction[List[Eisen]]
        catch_up_difficulty: UpdateAction[Optional[Difficulty]]
        catch_up_actionable_from_day: UpdateAction[Optional[RecurringTaskDueAtDay]]
        catch_up_actionable_from_month: UpdateAction[Optional[RecurringTaskDueAtMonth]]
        catch_up_due_at_time: UpdateAction[Optional[RecurringTaskDueAtTime]]
        catch_up_due_at_day: UpdateAction[Optional[RecurringTaskDueAtDay]]
        catch_up_due_at_month: UpdateAction[Optional[RecurringTaskDueAtMonth]]
        birthday: UpdateAction[Optional[PersonBirthday]]

    _global_properties: Final[GlobalProperties]
    _time_provider: Final[TimeProvider]
    _prm_engine: Final[PrmEngine]
    _prm_notion_manager: Final[PrmNotionManager]
    _inbox_task_engine: Final[InboxTaskEngine]
    _inbox_task_notion_manager: Final[InboxTaskNotionManager]

    def __init__(
            self, global_properties: GlobalProperties, time_provider: TimeProvider,
            inbox_task_engine: InboxTaskEngine, inbox_task_notion_manager: InboxTaskNotionManager,
            prm_engine: PrmEngine, prm_notion_manager: PrmNotionManager) -> None:
        """Constructor."""
        self._global_properties = global_properties
        self._time_provider = time_provider
        self._inbox_task_engine = inbox_task_engine
        self._inbox_task_notion_manager = inbox_task_notion_manager
        self._prm_engine = prm_engine
        self._prm_notion_manager = prm_notion_manager

    def execute(self, args: Args) -> None:
        """Execute the command's action."""
        with self._prm_engine.get_unit_of_work() as uow:
            person = uow.person_repository.load_by_id(args.ref_id)

            # Change the person.
            if args.name.should_change:
                person.change_name(args.name.value, self._time_provider.get_current_time())
            if args.relationship.should_change:
                person.change_relationship(args.relationship.value, self._time_provider.get_current_time())
            if args.catch_up_period.should_change \
                    or args.catch_up_eisen.should_change \
                    or args.catch_up_difficulty.should_change \
                    or args.catch_up_actionable_from_day.should_change \
                    or args.catch_up_actionable_from_month.should_change \
                    or args.catch_up_due_at_time.should_change \
                    or args.catch_up_due_at_day.should_change \
                    or args.catch_up_due_at_month:
                new_catch_up_period = None
                if args.catch_up_period.should_change:
                    new_catch_up_period = args.catch_up_period.value
                elif person.catch_up_params is not None:
                    new_catch_up_period = person.catch_up_params.period

                if new_catch_up_period is not None:
                    prm_database = uow.prm_database_repository.load()
                    new_catch_up_project_ref_id = prm_database.catch_up_project_ref_id

                    new_catch_up_eisen = []
                    if args.catch_up_eisen.should_change:
                        new_catch_up_eisen = args.catch_up_eisen.value
                    elif person.catch_up_params is not None:
                        new_catch_up_eisen = person.catch_up_params.eisen

                    new_catch_up_difficulty = None
                    if args.catch_up_difficulty.should_change:
                        new_catch_up_difficulty = args.catch_up_difficulty.value
                    elif person.catch_up_params is not None:
                        new_catch_up_difficulty = person.catch_up_params.difficulty

                    new_catch_up_actionable_from_day = None
                    if args.catch_up_actionable_from_day.should_change:
                        new_catch_up_actionable_from_day = args.catch_up_actionable_from_day.value
                    elif person.catch_up_params is not None:
                        new_catch_up_actionable_from_day = person.catch_up_params.actionable_from_day

                    new_catch_up_actionable_from_month = None
                    if args.catch_up_actionable_from_month.should_change:
                        new_catch_up_actionable_from_month = args.catch_up_actionable_from_month.value
                    elif person.catch_up_params is not None:
                        new_catch_up_actionable_from_month = person.catch_up_params.actionable_from_month

                    new_catch_up_due_at_time = None
                    if args.catch_up_due_at_time.should_change:
                        new_catch_up_due_at_time = args.catch_up_due_at_time.value
                    elif person.catch_up_params is not None:
                        new_catch_up_due_at_time = person.catch_up_params.due_at_time

                    new_catch_up_due_at_day = None
                    if args.catch_up_due_at_day.should_change:
                        new_catch_up_due_at_day = args.catch_up_due_at_day.value
                    elif person.catch_up_params is not None:
                        new_catch_up_due_at_day = person.catch_up_params.due_at_day

                    new_catch_up_due_at_month = None
                    if args.catch_up_due_at_month.should_change:
                        new_catch_up_due_at_month = args.catch_up_due_at_month.value
                    elif person.catch_up_params is not None:
                        new_catch_up_due_at_month = person.catch_up_params.due_at_month

                    catch_up_params = RecurringTaskGenParams(
                        project_ref_id=new_catch_up_project_ref_id,
                        period=new_catch_up_period,
                        eisen=new_catch_up_eisen,
                        difficulty=new_catch_up_difficulty,
                        actionable_from_day=new_catch_up_actionable_from_day,
                        actionable_from_month=new_catch_up_actionable_from_month,
                        due_at_time=new_catch_up_due_at_time,
                        due_at_day=new_catch_up_due_at_day,
                        due_at_month=new_catch_up_due_at_month)

                    person.change_catch_up_params(catch_up_params, self._time_provider.get_current_time())
            if args.birthday.should_change:
                person.change_birthday(args.birthday.value, self._time_provider.get_current_time())

            uow.person_repository.save(person)

        notion_person = self._prm_notion_manager.load_person(person.ref_id)
        notion_person = notion_person.join_with_aggregate_root(person, None)
        self._prm_notion_manager.save_person(notion_person)

        # Change the catch up inbox tasks
        with self._inbox_task_engine.get_unit_of_work() as inbox_task_uow:
            person_catch_up_tasks = inbox_task_uow.inbox_task_repository.find_all(
                allow_archived=True, filter_sources=[InboxTaskSource.PERSON_CATCH_UP],
                filter_person_ref_ids=[person.ref_id])

        if person.catch_up_params is None:
            # Situation 1: we need to get rid of any existing catch ups persons because there's no collection catch ups.
            for inbox_task in person_catch_up_tasks:
                InboxTaskArchiveService(
                    self._time_provider, self._inbox_task_engine, self._inbox_task_notion_manager).do_it(inbox_task)
        else:
            # Situation 2: we need to update the existing persons.
            for inbox_task in person_catch_up_tasks:
                schedule = schedules.get_schedule(
                    person.catch_up_params.period, person.name,
                    typing.cast(Timestamp, inbox_task.recurring_gen_right_now), self._global_properties.timezone,
                    None, person.catch_up_params.actionable_from_day, person.catch_up_params.actionable_from_month,
                    person.catch_up_params.due_at_time, person.catch_up_params.due_at_day,
                    person.catch_up_params.due_at_month)

                inbox_task.update_link_to_person_catch_up(
                    name=schedule.full_name, recurring_timeline=schedule.timeline,
                    eisen=person.catch_up_params.eisen,
                    difficulty=person.catch_up_params.difficulty,
                    actionable_date=schedule.actionable_date, due_time=schedule.due_time,
                    modification_time=self._time_provider.get_current_time())
                # Situation 2a: we're handling the same project.
                with self._inbox_task_engine.get_unit_of_work() as inbox_task_uow:
                    inbox_task_uow.inbox_task_repository.save(inbox_task)

                notion_inbox_task = self._inbox_task_notion_manager.load_inbox_task(inbox_task.project_ref_id,
                                                                                    inbox_task.ref_id)
                notion_inbox_task = notion_inbox_task.join_with_aggregate_root(
                    inbox_task, NotionInboxTask.DirectInfo(None))
                self._inbox_task_notion_manager.save_inbox_task(inbox_task.project_ref_id, notion_inbox_task)
                LOGGER.info("Applied Notion changes")

        # Change the birthday inbox tasks
        with self._inbox_task_engine.get_unit_of_work() as inbox_task_uow:
            person_birthday_tasks = inbox_task_uow.inbox_task_repository.find_all(
                allow_archived=True, filter_sources=[InboxTaskSource.PERSON_BIRTHDAY],
                filter_person_ref_ids=[person.ref_id])

        if person.birthday is None:
            # Situation 1: we need to get rid of any existing catch ups persons because there's no collection catch ups.
            for inbox_task in person_birthday_tasks:
                InboxTaskArchiveService(
                    self._time_provider, self._inbox_task_engine, self._inbox_task_notion_manager)\
                    .do_it(inbox_task)
        else:
            # Situation 2: we need to update the existing persons.
            for inbox_task in person_birthday_tasks:
                schedule = schedules.get_schedule(
                    RecurringTaskPeriod.YEARLY, person.name,
                    typing.cast(Timestamp, inbox_task.recurring_gen_right_now),
                    self._global_properties.timezone,
                    None, None, None, None,
                    RecurringTaskDueAtDay.from_raw(RecurringTaskPeriod.MONTHLY, person.birthday.day),
                    RecurringTaskDueAtMonth.from_raw(RecurringTaskPeriod.YEARLY, person.birthday.month))

                inbox_task.update_link_to_person_birthday(
                    name=schedule.full_name, recurring_timeline=schedule.timeline,
                    preparation_days_cnt=person.preparation_days_cnt_for_birthday, due_time=schedule.due_time,
                    modification_time=self._time_provider.get_current_time())
                # Situation 2a: we're handling the same project.
                with self._inbox_task_engine.get_unit_of_work() as inbox_task_uow:
                    inbox_task_uow.inbox_task_repository.save(inbox_task)

                notion_inbox_task = self._inbox_task_notion_manager.load_inbox_task(inbox_task.project_ref_id,
                                                                                    inbox_task.ref_id)
                notion_inbox_task = notion_inbox_task.join_with_aggregate_root(
                    inbox_task, NotionInboxTask.DirectInfo(None))
                self._inbox_task_notion_manager.save_inbox_task(inbox_task.project_ref_id, notion_inbox_task)
                LOGGER.info("Applied Notion changes")
