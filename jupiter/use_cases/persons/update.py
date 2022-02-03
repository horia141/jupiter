"""Update a person."""
import logging
import typing
from dataclasses import dataclass
from typing import Final, Optional

from jupiter.domain import schedules
from jupiter.domain.difficulty import Difficulty
from jupiter.domain.eisen import Eisen
from jupiter.domain.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.domain.inbox_tasks.infra.inbox_task_notion_manager import InboxTaskNotionManager
from jupiter.domain.inbox_tasks.notion_inbox_task import NotionInboxTask
from jupiter.domain.inbox_tasks.service.archive_service import InboxTaskArchiveService
from jupiter.domain.persons.infra.person_notion_manager import PersonNotionManager
from jupiter.domain.persons.person_birthday import PersonBirthday
from jupiter.domain.persons.person_name import PersonName
from jupiter.domain.persons.person_relationship import PersonRelationship
from jupiter.domain.recurring_task_due_at_day import RecurringTaskDueAtDay
from jupiter.domain.recurring_task_due_at_month import RecurringTaskDueAtMonth
from jupiter.domain.recurring_task_due_at_time import RecurringTaskDueAtTime
from jupiter.domain.recurring_task_gen_params import RecurringTaskGenParams
from jupiter.domain.recurring_task_period import RecurringTaskPeriod
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


class PersonUpdateUseCase(AppMutationUseCase['PersonUpdateUseCase.Args', None]):
    """The command for updating a person."""

    @dataclass(frozen=True)
    class Args(UseCaseArgsBase):
        """Args."""
        ref_id: EntityId
        name: UpdateAction[PersonName]
        relationship: UpdateAction[PersonRelationship]
        catch_up_period: UpdateAction[Optional[RecurringTaskPeriod]]
        catch_up_eisen: UpdateAction[Eisen]
        catch_up_difficulty: UpdateAction[Optional[Difficulty]]
        catch_up_actionable_from_day: UpdateAction[Optional[RecurringTaskDueAtDay]]
        catch_up_actionable_from_month: UpdateAction[Optional[RecurringTaskDueAtMonth]]
        catch_up_due_at_time: UpdateAction[Optional[RecurringTaskDueAtTime]]
        catch_up_due_at_day: UpdateAction[Optional[RecurringTaskDueAtDay]]
        catch_up_due_at_month: UpdateAction[Optional[RecurringTaskDueAtMonth]]
        birthday: UpdateAction[Optional[PersonBirthday]]

    _global_properties: Final[GlobalProperties]
    _inbox_task_notion_manager: Final[InboxTaskNotionManager]
    _person_notion_manager: Final[PersonNotionManager]

    def __init__(
            self,
            global_properties: GlobalProperties,
            time_provider: TimeProvider,
            invocation_recorder: MutationUseCaseInvocationRecorder,
            storage_engine: DomainStorageEngine,
            inbox_task_notion_manager: InboxTaskNotionManager,
            person_notion_manager: PersonNotionManager) -> None:
        """Constructor."""
        super().__init__(time_provider, invocation_recorder, storage_engine)
        self._global_properties = global_properties
        self._inbox_task_notion_manager = inbox_task_notion_manager
        self._person_notion_manager = person_notion_manager

    def _execute(self, context: AppUseCaseContext, args: Args) -> None:
        """Execute the command's action."""
        workspace = context.workspace

        with self._storage_engine.get_unit_of_work() as uow:
            person_collection = uow.person_collection_repository.load_by_workspace(workspace.ref_id)
            person = uow.person_repository.load_by_id(args.ref_id)

            # Change the person.
            catch_up_params: UpdateAction[Optional[RecurringTaskGenParams]]
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

                    catch_up_params = UpdateAction.change_to(RecurringTaskGenParams(
                        period=new_catch_up_period,
                        eisen=new_catch_up_eisen,
                        difficulty=new_catch_up_difficulty,
                        actionable_from_day=new_catch_up_actionable_from_day,
                        actionable_from_month=new_catch_up_actionable_from_month,
                        due_at_time=new_catch_up_due_at_time,
                        due_at_day=new_catch_up_due_at_day,
                        due_at_month=new_catch_up_due_at_month))
                else:
                    catch_up_params = UpdateAction.change_to(None)
            else:
                catch_up_params = UpdateAction.do_nothing()

            person = \
                person.update(
                    name=args.name, relationship=args.relationship, birthday=args.birthday,
                    catch_up_params=catch_up_params, source=EventSource.CLI,
                    modification_time=self._time_provider.get_current_time())

            uow.person_repository.save(person)

        notion_person = self._person_notion_manager.load_person(person_collection.ref_id, person.ref_id)
        notion_person = notion_person.join_with_aggregate_root(person, None)
        self._person_notion_manager.save_person(person_collection.ref_id, notion_person)

        # TODO(horia141): also create tasks here!
        # TODO(horia141): what if we change other person properties not just catch up params?
        # Change the catch up inbox tasks
        with self._storage_engine.get_unit_of_work() as uow:
            project = uow.project_repository.load_by_id(person_collection.catch_up_project_ref_id)
            inbox_task_collection = uow.inbox_task_collection_repository.load_by_workspace(workspace.ref_id)
            person_catch_up_tasks = \
                uow.inbox_task_repository.find_all(
                    inbox_task_collection_ref_id=inbox_task_collection.ref_id,
                    allow_archived=True, filter_sources=[InboxTaskSource.PERSON_CATCH_UP],
                    filter_person_ref_ids=[person.ref_id])
            person_birthday_tasks = \
                uow.inbox_task_repository.find_all(
                    inbox_task_collection_ref_id=inbox_task_collection.ref_id,
                    allow_archived=True, filter_sources=[InboxTaskSource.PERSON_BIRTHDAY],
                    filter_person_ref_ids=[person.ref_id])

        if person.catch_up_params is None:
            # Situation 1: we need to get rid of any existing catch ups persons because there's no collection catch ups.
            inbox_task_archive_service = \
                InboxTaskArchiveService(
                    source=EventSource.CLI, time_provider=self._time_provider, storage_engine=self._storage_engine,
                    inbox_task_notion_manager=self._inbox_task_notion_manager)
            for inbox_task in person_catch_up_tasks:
                inbox_task_archive_service.do_it(inbox_task)
        else:
            # Situation 2: we need to update the existing persons.
            for inbox_task in person_catch_up_tasks:
                schedule = schedules.get_schedule(
                    person.catch_up_params.period, person.name,
                    typing.cast(Timestamp, inbox_task.recurring_gen_right_now), self._global_properties.timezone,
                    None, person.catch_up_params.actionable_from_day, person.catch_up_params.actionable_from_month,
                    person.catch_up_params.due_at_time, person.catch_up_params.due_at_day,
                    person.catch_up_params.due_at_month)

                inbox_task = \
                    inbox_task.update_link_to_person_catch_up(
                        project_ref_id=project.ref_id,
                        name=schedule.full_name,
                        recurring_timeline=schedule.timeline,
                        eisen=person.catch_up_params.eisen,
                        difficulty=person.catch_up_params.difficulty,
                        actionable_date=schedule.actionable_date,
                        due_time=schedule.due_time,
                        source=EventSource.CLI,
                        modification_time=self._time_provider.get_current_time())
                # Situation 2a: we're handling the same project.
                with self._storage_engine.get_unit_of_work() as uow:
                    uow.inbox_task_repository.save(inbox_task)

                direct_info = NotionInboxTask.DirectInfo(project_name=project.name, big_plan_name=None)
                notion_inbox_task = \
                    self._inbox_task_notion_manager.load_inbox_task(
                        inbox_task.inbox_task_collection_ref_id, inbox_task.ref_id)
                notion_inbox_task = notion_inbox_task.join_with_aggregate_root(inbox_task, direct_info)
                self._inbox_task_notion_manager.save_inbox_task(
                    inbox_task.inbox_task_collection_ref_id, notion_inbox_task)
                LOGGER.info("Applied Notion changes")

        # Change the birthday inbox tasks
        if person.birthday is None:
            # Situation 1: we need to get rid of any existing catch ups persons because there's no collection catch ups.
            inbox_task_archive_service = \
                InboxTaskArchiveService(
                    source=EventSource.CLI, time_provider=self._time_provider, storage_engine=self._storage_engine,
                    inbox_task_notion_manager=self._inbox_task_notion_manager)
            for inbox_task in person_birthday_tasks:
                inbox_task_archive_service.do_it(inbox_task)
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

                inbox_task = \
                    inbox_task.update_link_to_person_birthday(
                        project_ref_id=project.ref_id,
                        name=schedule.full_name,
                        recurring_timeline=schedule.timeline,
                        preparation_days_cnt=person.preparation_days_cnt_for_birthday,
                        due_time=schedule.due_time,
                        source=EventSource.CLI,
                        modification_time=self._time_provider.get_current_time())
                # Situation 2a: we're handling the same project.
                with self._storage_engine.get_unit_of_work() as uow:
                    uow.inbox_task_repository.save(inbox_task)

                direct_info = NotionInboxTask.DirectInfo(project_name=project.name, big_plan_name=None)
                notion_inbox_task = \
                    self._inbox_task_notion_manager.load_inbox_task(
                        inbox_task.inbox_task_collection_ref_id, inbox_task.ref_id)
                notion_inbox_task = notion_inbox_task.join_with_aggregate_root(inbox_task, direct_info)
                self._inbox_task_notion_manager.save_inbox_task(
                    inbox_task.inbox_task_collection_ref_id, notion_inbox_task)
                LOGGER.info("Applied Notion changes")
