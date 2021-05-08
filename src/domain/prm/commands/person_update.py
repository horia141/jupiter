"""Update a person."""
import logging
from dataclasses import dataclass
from typing import Final, Optional, List

import typing

from domain.prm.infra.prm_engine import PrmEngine
from domain.prm.infra.prm_notion_manager import PrmNotionManager
from domain.prm.person_birthday import PersonBirthday
from domain.prm.person_relationship import PersonRelationship
from domain.shared import RecurringTaskGenParams
from models import schedules
from models.basic import RecurringTaskPeriod, Eisen, Difficulty, EntityId, BasicValidator, Timestamp
from models.framework import Command, UpdateAction
from service.inbox_tasks import InboxTasksService
from service.workspaces import WorkspacesService
from utils.global_properties import GlobalProperties
from utils.time_provider import TimeProvider


LOGGER = logging.getLogger(__name__)


class PersonUpdateCommand(Command['PersonUpdateCommand.Args', None]):
    """The command for updating a person."""

    @dataclass()
    class Args:
        """Args."""
        ref_id: EntityId
        name: UpdateAction[str]
        relationship: UpdateAction[PersonRelationship]
        catch_up_period: UpdateAction[Optional[RecurringTaskPeriod]]
        catch_up_eisen: UpdateAction[List[Eisen]]
        catch_up_difficulty: UpdateAction[Optional[Difficulty]]
        catch_up_actionable_from_day: UpdateAction[Optional[int]]
        catch_up_actionable_from_month: UpdateAction[Optional[int]]
        catch_up_due_at_time: UpdateAction[Optional[str]]
        catch_up_due_at_day: UpdateAction[Optional[int]]
        catch_up_due_at_month: UpdateAction[Optional[int]]
        birthday: UpdateAction[Optional[PersonBirthday]]

    _global_properties: Final[GlobalProperties]
    _time_provider: Final[TimeProvider]
    _basic_validator: Final[BasicValidator]
    _engine: Final[PrmEngine]
    _notion_manager: Final[PrmNotionManager]
    _workspaces_service: Final[WorkspacesService]
    _inbox_tasks_service: Final[InboxTasksService]

    def __init__(
            self, global_properties: GlobalProperties, time_provider: TimeProvider, basic_validator: BasicValidator,
            engine: PrmEngine, notion_manager: PrmNotionManager, inbox_tasks_service: InboxTasksService,
            workspaces_service: WorkspacesService) -> None:
        """Constructor."""
        self._global_properties = global_properties
        self._time_provider = time_provider
        self._basic_validator = basic_validator
        self._engine = engine
        self._notion_manager = notion_manager
        self._workspaces_service = workspaces_service
        self._inbox_tasks_service = inbox_tasks_service

    def execute(self, args: Args) -> None:
        """Execute the command's action."""
        with self._engine.get_unit_of_work() as uow:
            person = uow.person_repository.get_by_id(args.ref_id)

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
                        new_catch_up_actionable_from_day = \
                            self._basic_validator.recurring_task_due_at_day_validate_and_clean(
                                new_catch_up_period, args.catch_up_actionable_from_day.value)
                    elif person.catch_up_params is not None:
                        new_catch_up_actionable_from_day = person.catch_up_params.actionable_from_day

                    new_catch_up_actionable_from_month = None
                    if args.catch_up_actionable_from_month.should_change:
                        new_catch_up_actionable_from_month = \
                            self._basic_validator.recurring_task_due_at_month_validate_and_clean(
                                new_catch_up_period, args.catch_up_actionable_from_month.value)
                    elif person.catch_up_params is not None:
                        new_catch_up_actionable_from_month = person.catch_up_params.actionable_from_month

                    new_catch_up_due_at_time = None
                    if args.catch_up_due_at_time.should_change:
                        new_catch_up_due_at_time = args.catch_up_due_at_time.value
                    elif person.catch_up_params is not None:
                        new_catch_up_due_at_time = person.catch_up_params.due_at_time

                    new_catch_up_due_at_day = None
                    if args.catch_up_due_at_day.should_change:
                        new_catch_up_due_at_day = self._basic_validator.recurring_task_due_at_day_validate_and_clean(
                            new_catch_up_period, args.catch_up_due_at_day.value)
                    elif person.catch_up_params is not None:
                        new_catch_up_due_at_day = person.catch_up_params.due_at_day

                    new_catch_up_due_at_month = None
                    if args.catch_up_due_at_month.should_change:
                        new_catch_up_due_at_month = \
                            self._basic_validator.recurring_task_due_at_month_validate_and_clean(
                                new_catch_up_period, args.catch_up_due_at_month.value)
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

        notion_person = self._notion_manager.load_person_by_ref_id(person.ref_id)
        notion_person = notion_person.join_with_aggregate_root(person)
        self._notion_manager.save_person(notion_person)

        # Change the inbox tasks
        person_catch_up_tasks = self._inbox_tasks_service.load_all_inbox_tasks(
            allow_archived=True, filter_person_ref_ids=[person.ref_id])

        if person.catch_up_params is None:
            # Situation 1: we need to get rid of any existing catch ups persons because there's no collection catch ups.
            for inbox_task in person_catch_up_tasks:
                self._inbox_tasks_service.archive_inbox_task(inbox_task.ref_id)
        else:
            # Situation 2: we need to update the existing persons.
            for inbox_task in person_catch_up_tasks:
                schedule = schedules.get_schedule(
                    person.catch_up_params.period, person.name,
                    typing.cast(Timestamp, inbox_task.recurring_gen_right_now), self._global_properties.timezone,
                    None, person.catch_up_params.actionable_from_day, person.catch_up_params.actionable_from_month,
                    person.catch_up_params.due_at_time, person.catch_up_params.due_at_day,
                    person.catch_up_params.due_at_month)
                # Situation 2a: we're handling the same project.
                self._inbox_tasks_service.set_inbox_task_to_person_link(
                    ref_id=inbox_task.ref_id,
                    name=schedule.full_name,
                    recurring_timeline=schedule.timeline,
                    recurring_period=person.catch_up_params.period,
                    eisen=person.catch_up_params.eisen,
                    difficulty=person.catch_up_params.difficulty,
                    actionable_date=schedule.actionable_date,
                    due_time=schedule.due_time)
