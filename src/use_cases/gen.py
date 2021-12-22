"""The command for generating new tasks."""
import logging
import typing
from dataclasses import dataclass
from typing import Final, Iterable, Optional, List, Dict, Tuple, FrozenSet

from domain.inbox_tasks.inbox_task import InboxTask
from domain.inbox_tasks.inbox_task_source import InboxTaskSource
from domain.inbox_tasks.infra.inbox_task_engine import InboxTaskEngine
from domain.inbox_tasks.infra.inbox_task_notion_manager import InboxTaskNotionManager
from domain.inbox_tasks.notion_inbox_task import NotionInboxTask
from domain.metrics.infra.metric_engine import MetricEngine
from domain.metrics.metric import Metric
from domain.metrics.metric_key import MetricKey
from domain.prm.infra.prm_engine import PrmEngine
from domain.prm.person import Person
from domain.prm.person_birthday import PersonBirthday
from domain.projects.infra.project_engine import ProjectEngine
from domain.projects.project import Project
from domain.projects.project_key import ProjectKey
from domain.recurring_task_due_at_day import RecurringTaskDueAtDay
from domain.recurring_task_due_at_month import RecurringTaskDueAtMonth
from domain.recurring_task_gen_params import RecurringTaskGenParams
from domain.recurring_task_period import RecurringTaskPeriod
from domain.recurring_tasks.infra.recurring_task_engine import RecurringTaskEngine
from domain.recurring_tasks.recurring_task import RecurringTask
from domain.sync_target import SyncTarget
from domain.timestamp import Timestamp
from domain.vacations.infra.vacation_engine import VacationEngine
from domain.vacations.vacation import Vacation
from models import schedules
from models.framework import Command
from models.framework import EntityId
from utils.global_properties import GlobalProperties
from utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class GenCommand(Command['GenCommand.Args', None]):
    """The command for generating new tasks."""

    @dataclass()
    class Args:
        """Args."""
        right_now: Timestamp
        gen_targets: Iterable[SyncTarget]
        filter_project_keys: Optional[Iterable[ProjectKey]]
        filter_recurring_task_ref_ids: Optional[Iterable[EntityId]]
        filter_metric_keys: Optional[Iterable[MetricKey]]
        filter_person_ref_ids: Optional[Iterable[EntityId]]
        filter_period: Optional[Iterable[RecurringTaskPeriod]]
        sync_even_if_not_modified: bool

    _global_properties: Final[GlobalProperties]
    _time_provider: Final[TimeProvider]
    _project_engine: Final[ProjectEngine]
    _vacation_engine: Final[VacationEngine]
    _inbox_task_engine: Final[InboxTaskEngine]
    _inbox_task_notion_manager: Final[InboxTaskNotionManager]
    _recurring_task_engine: Final[RecurringTaskEngine]
    _metric_engine: Final[MetricEngine]
    _prm_engine: Final[PrmEngine]

    def __init__(
            self,
            global_properties: GlobalProperties, time_provider: TimeProvider,
            project_engine: ProjectEngine, vacation_engine: VacationEngine,
            inbox_task_engine: InboxTaskEngine, inbox_task_notion_manager: InboxTaskNotionManager,
            recurring_task_engine: RecurringTaskEngine, metric_engine: MetricEngine, prm_engine: PrmEngine) -> None:
        """Constructor."""
        self._global_properties = global_properties
        self._time_provider = time_provider
        self._project_engine = project_engine
        self._vacation_engine = vacation_engine
        self._inbox_task_engine = inbox_task_engine
        self._inbox_task_notion_manager = inbox_task_notion_manager
        self._recurring_task_engine = recurring_task_engine
        self._metric_engine = metric_engine
        self._prm_engine = prm_engine

    def execute(self, args: Args) -> None:
        """Execute the command's action."""
        with self._vacation_engine.get_unit_of_work() as vacation_uow:
            all_vacations = list(vacation_uow.vacation_repository.find_all())

        with self._project_engine.get_unit_of_work() as project_uow:
            all_projects = project_uow.project_repository.find_all()
            all_syncable_projects = project_uow.project_repository.find_all(filter_keys=args.filter_project_keys)
        all_projects_by_ref_id = {p.ref_id: p for p in all_projects}

        if SyncTarget.PROJECTS in args.gen_targets:
            for project in all_syncable_projects:
                LOGGER.info(f"Generating tasks for project '{project.name}'")
                with self._recurring_task_engine.get_unit_of_work() as recurring_task_uow:
                    recurring_task_collection = \
                        recurring_task_uow.recurring_task_collection_repository.load_by_project(project.ref_id)
                    all_recurring_tasks = \
                        list(recurring_task_uow.recurring_task_repository.find_all(
                            filter_ref_ids=args.filter_recurring_task_ref_ids,
                            filter_recurring_task_collection_ref_ids=[recurring_task_collection.ref_id]))
                if len(all_recurring_tasks) == 0:
                    continue
                with self._inbox_task_engine.get_unit_of_work() as uow:
                    inbox_task_collection = uow.inbox_task_collection_repository.load_by_project(project.ref_id)
                    all_collection_inbox_tasks = uow.inbox_task_repository.find_all(
                        allow_archived=True, filter_inbox_task_collection_ref_ids=[inbox_task_collection.ref_id],
                        filter_recurring_task_ref_ids=(rt.ref_id for rt in all_recurring_tasks))

                all_inbox_tasks_by_recurring_task_ref_id_and_timeline = {}
                for inbox_task in all_collection_inbox_tasks:
                    if inbox_task.recurring_task_ref_id is None or inbox_task.recurring_timeline is None:
                        raise Exception(f"Expected that inbox task with id='{inbox_task.ref_id}'")
                    all_inbox_tasks_by_recurring_task_ref_id_and_timeline[
                        (inbox_task.recurring_task_ref_id, inbox_task.recurring_timeline)] = inbox_task

                for recurring_task in all_recurring_tasks:
                    LOGGER.info(f"Generating inbox tasks for '{recurring_task.name}'")
                    self._generate_inbox_tasks_for_recurring_task(
                        project=project,
                        right_now=args.right_now,
                        period_filter=frozenset(args.filter_period) if args.filter_period else None,
                        all_vacations=all_vacations,
                        recurring_task=recurring_task,
                        all_inbox_tasks_by_recurring_task_ref_id_and_timeline=
                        all_inbox_tasks_by_recurring_task_ref_id_and_timeline,
                        sync_even_if_not_modified=args.sync_even_if_not_modified)

        if SyncTarget.METRICS in args.gen_targets:
            with self._metric_engine.get_unit_of_work() as metric_uow:
                all_metrics = metric_uow.metric_repository.find_all(filter_keys=args.filter_metric_keys)

                with self._inbox_task_engine.get_unit_of_work() as uow:
                    all_collection_inbox_tasks = uow.inbox_task_repository.find_all(
                        allow_archived=True,
                        filter_metric_ref_ids=[m.ref_id for m in all_metrics])

                all_collection_inbox_tasks_by_metric_ref_id_and_timeline = {}
                for inbox_task in all_collection_inbox_tasks:
                    if inbox_task.metric_ref_id is None or inbox_task.recurring_timeline is None:
                        raise Exception(f"Expected that inbox task with id='{inbox_task.ref_id}'")
                    all_collection_inbox_tasks_by_metric_ref_id_and_timeline[
                        (inbox_task.metric_ref_id, inbox_task.recurring_timeline)] = inbox_task

                for metric in all_metrics:
                    if metric.collection_params is None:
                        continue
                    LOGGER.info(f"Generating collection tasks for metric '{metric.name}'")

                    # MyPy not smart enough to infer that if (not A and not B) then (A or B)
                    project = all_projects_by_ref_id[metric.collection_params.project_ref_id]

                    self._generate_collection_inbox_tasks_for_metric(
                        project=project,
                        right_now=args.right_now,
                        period_filter=frozenset(args.filter_period) if args.filter_period else None,
                        metric=metric,
                        collection_params=metric.collection_params,
                        all_inbox_tasks_by_metric_ref_id_and_timeline=
                        all_collection_inbox_tasks_by_metric_ref_id_and_timeline,
                        sync_even_if_not_modified=args.sync_even_if_not_modified)

        if SyncTarget.PRM in args.gen_targets:
            with self._prm_engine.get_unit_of_work() as prm_uow:
                prm_database = prm_uow.prm_database_repository.load()
                all_persons = prm_uow.person_repository.find_all(filter_ref_ids=args.filter_person_ref_ids)

            project = all_projects_by_ref_id[prm_database.catch_up_project_ref_id]

            with self._inbox_task_engine.get_unit_of_work() as uow:
                all_catch_up_inbox_tasks = uow.inbox_task_repository.find_all(
                    allow_archived=True,
                    filter_sources=[InboxTaskSource.PERSON_CATCH_UP],
                    filter_person_ref_ids=[m.ref_id for m in all_persons])
                all_birthday_inbox_tasks = uow.inbox_task_repository.find_all(
                    allow_archived=True,
                    filter_sources=[InboxTaskSource.PERSON_BIRTHDAY],
                    filter_person_ref_ids=[m.ref_id for m in all_persons])

            all_catch_up_inbox_tasks_by_person_ref_id_and_timeline = {}
            for inbox_task in all_catch_up_inbox_tasks:
                if inbox_task.person_ref_id is None or inbox_task.recurring_timeline is None:
                    raise Exception(f"Expected that inbox task with id='{inbox_task.ref_id}'")
                all_catch_up_inbox_tasks_by_person_ref_id_and_timeline[
                    (inbox_task.person_ref_id, inbox_task.recurring_timeline)] = inbox_task

            for person in all_persons:
                if person.catch_up_params is None:
                    continue
                LOGGER.info(f"Generating catch up tasks for person '{person.name}'")

                # MyPy not smart enough to infer that if (not A and not B) then (A or B)

                self._generate_catch_up_inbox_tasks_for_person(
                    project=project,
                    right_now=args.right_now,
                    period_filter=frozenset(args.filter_period) if args.filter_period else None,
                    person=person,
                    catch_up_params=person.catch_up_params,
                    all_inbox_tasks_by_person_ref_id_and_timeline=
                    all_catch_up_inbox_tasks_by_person_ref_id_and_timeline,
                    sync_even_if_not_modified=args.sync_even_if_not_modified)

            all_birthday_inbox_tasks_by_person_ref_id_and_timeline = {}
            for inbox_task in all_birthday_inbox_tasks:
                if inbox_task.person_ref_id is None or inbox_task.recurring_timeline is None:
                    raise Exception(f"Expected that inbox task with id='{inbox_task.ref_id}'")
                all_birthday_inbox_tasks_by_person_ref_id_and_timeline[
                    (inbox_task.person_ref_id, inbox_task.recurring_timeline)] = inbox_task

            for person in all_persons:
                if person.birthday is None:
                    continue
                LOGGER.info(f"Generating birthday inbox tasks for person '{person.name}'")

                self._generate_birthday_inbox_task_for_person(
                    project=project,
                    right_now=args.right_now,
                    person=person,
                    birthday=person.birthday,
                    all_inbox_tasks_by_person_ref_id_and_timeline=
                    all_birthday_inbox_tasks_by_person_ref_id_and_timeline,
                    sync_even_if_not_modified=args.sync_even_if_not_modified)

    def _generate_inbox_tasks_for_recurring_task(
            self,
            project: Project,
            right_now: Timestamp,
            period_filter: Optional[FrozenSet[RecurringTaskPeriod]],
            all_vacations: List[Vacation],
            recurring_task: RecurringTask,
            all_inbox_tasks_by_recurring_task_ref_id_and_timeline: Dict[Tuple[EntityId, str], InboxTask],
            sync_even_if_not_modified: bool) -> None:
        if recurring_task.suspended:
            LOGGER.info(f"Skipping '{recurring_task.name}' because it is suspended")
            return

        if period_filter is not None and recurring_task.period not in period_filter:
            LOGGER.info(f"Skipping '{recurring_task.name}' on account of period filtering")
            return

        schedule = schedules.get_schedule(
            recurring_task.period, recurring_task.name, right_now, self._global_properties.timezone,
            recurring_task.skip_rule, recurring_task.gen_params.actionable_from_day,
            recurring_task.gen_params.actionable_from_month, recurring_task.gen_params.due_at_time,
            recurring_task.gen_params.due_at_day, recurring_task.gen_params.due_at_month)

        if not recurring_task.must_do:
            for vacation in all_vacations:
                if vacation.is_in_vacation(schedule.first_day, schedule.end_day):
                    LOGGER.info(
                        f"Skipping '{recurring_task.name}' on account of being fully withing vacation {vacation}")
                    return

        if not recurring_task.is_in_active_interval(schedule.first_day, schedule.end_day):
            LOGGER.info(f"Skipping '{recurring_task.name}' on account of being outside the active interval")
            return

        if schedule.should_skip:
            LOGGER.info(f"Skipping '{recurring_task.name}' on account of rule")
            return

        LOGGER.info(f"Upserting '{recurring_task.name}'")

        found_task = all_inbox_tasks_by_recurring_task_ref_id_and_timeline.get(
            (recurring_task.ref_id, schedule.timeline), None)

        if found_task:
            if not sync_even_if_not_modified and found_task.last_modified_time >= recurring_task.last_modified_time:
                LOGGER.info(f"Skipping update of '{found_task.name}' because it was not modified")
                return

            found_task.update_link_to_recurring_task(name=schedule.full_name, timeline=schedule.timeline,
                                                     the_type=recurring_task.the_type,
                                                     actionable_date=schedule.actionable_date,
                                                     due_time=schedule.due_time, eisen=recurring_task.gen_params.eisen,
                                                     difficulty=recurring_task.gen_params.difficulty,
                                                     modification_time=self._time_provider.get_current_time())

            with self._inbox_task_engine.get_unit_of_work() as uow:
                uow.inbox_task_repository.save(found_task)

            notion_inbox_task = \
                self._inbox_task_notion_manager.load_inbox_task(found_task.project_ref_id, found_task.ref_id)
            notion_inbox_task = notion_inbox_task.join_with_aggregate_root(found_task, NotionInboxTask.DirectInfo(None))
            self._inbox_task_notion_manager.save_inbox_task(found_task.project_ref_id, notion_inbox_task)
            LOGGER.info("Applied Notion changes")
        else:
            with self._inbox_task_engine.get_unit_of_work() as read_uow:
                inbox_task_collection = read_uow.inbox_task_collection_repository.load_by_project(project.ref_id)

                inbox_task = InboxTask.new_inbox_task_for_recurring_task(
                    inbox_task_collection_ref_id=inbox_task_collection.ref_id,
                    name=schedule.full_name,
                    recurring_task_ref_id=recurring_task.ref_id,
                    recurring_task_timeline=schedule.timeline,
                    recurring_task_type=recurring_task.the_type,
                    recurring_task_gen_right_now=right_now,
                    eisen=recurring_task.gen_params.eisen,
                    difficulty=recurring_task.gen_params.difficulty,
                    actionable_date=schedule.actionable_date,
                    due_date=schedule.due_time,
                    created_time=self._time_provider.get_current_time())

                inbox_task = read_uow.inbox_task_repository.create(inbox_task_collection, inbox_task)
                LOGGER.info("Applied local changes")
            notion_inbox_task = NotionInboxTask.new_notion_row(inbox_task, NotionInboxTask.DirectInfo(None))
            self._inbox_task_notion_manager.upsert_inbox_task(inbox_task_collection, notion_inbox_task)
            LOGGER.info("Applied Notion changes")

    def _generate_collection_inbox_tasks_for_metric(
            self,
            project: Project,
            right_now: Timestamp,
            period_filter: Optional[FrozenSet[RecurringTaskPeriod]],
            metric: Metric,
            collection_params: RecurringTaskGenParams,
            all_inbox_tasks_by_metric_ref_id_and_timeline: Dict[Tuple[EntityId, str], InboxTask],
            sync_even_if_not_modified: bool) -> None:
        if period_filter is not None and collection_params.period not in period_filter:
            LOGGER.info(f"Skipping '{metric.name}' on account of period filtering")
            return

        schedule = schedules.get_schedule(
            typing.cast(RecurringTaskPeriod, collection_params.period), metric.name, right_now,
            self._global_properties.timezone, None, collection_params.actionable_from_day,
            collection_params.actionable_from_month, collection_params.due_at_time, collection_params.due_at_day,
            collection_params.due_at_month)

        LOGGER.info(f"Upserting collection inbox task for '{metric.name}'")

        found_task = all_inbox_tasks_by_metric_ref_id_and_timeline.get(
            (metric.ref_id, schedule.timeline), None)

        if found_task:
            if not sync_even_if_not_modified and found_task.last_modified_time >= metric.last_modified_time:
                LOGGER.info(f"Skipping update of '{found_task.name}' because it was not modified")
                return

            found_task.update_link_to_metric(name=schedule.full_name, recurring_timeline=schedule.timeline,
                                             eisen=collection_params.eisen, difficulty=collection_params.difficulty,
                                             actionable_date=schedule.actionable_date, due_time=schedule.due_time,
                                             modification_time=self._time_provider.get_current_time())

            with self._inbox_task_engine.get_unit_of_work() as uow:
                uow.inbox_task_repository.save(found_task)

            notion_inbox_task = self._inbox_task_notion_manager.load_inbox_task(found_task.project_ref_id,
                                                                                found_task.ref_id)
            notion_inbox_task = notion_inbox_task.join_with_aggregate_root(found_task, NotionInboxTask.DirectInfo(None))
            self._inbox_task_notion_manager.save_inbox_task(found_task.project_ref_id, notion_inbox_task)
            LOGGER.info("Applied Notion changes")
        else:
            with self._inbox_task_engine.get_unit_of_work() as inbox_task_uow:
                inbox_task_collection = inbox_task_uow.inbox_task_collection_repository.load_by_project(project.ref_id)

                inbox_task = InboxTask.new_inbox_task_for_metric(
                    inbox_task_collection_ref_id=inbox_task_collection.ref_id,
                    name=schedule.full_name,
                    metric_ref_id=metric.ref_id,
                    recurring_task_timeline=schedule.timeline,
                    recurring_task_gen_right_now=right_now,
                    eisen=collection_params.eisen,
                    difficulty=collection_params.difficulty,
                    actionable_date=schedule.actionable_date,
                    due_date=schedule.due_time,
                    created_time=self._time_provider.get_current_time())

                inbox_task = inbox_task_uow.inbox_task_repository.create(inbox_task_collection, inbox_task)
                LOGGER.info("Applied local changes")
            notion_inbox_task = NotionInboxTask.new_notion_row(inbox_task, NotionInboxTask.DirectInfo(None))
            self._inbox_task_notion_manager.upsert_inbox_task(inbox_task_collection, notion_inbox_task)
            LOGGER.info("Applied Notion changes")

    def _generate_catch_up_inbox_tasks_for_person(
            self,
            project: Project,
            right_now: Timestamp,
            period_filter: Optional[FrozenSet[RecurringTaskPeriod]],
            person: Person,
            catch_up_params: RecurringTaskGenParams,
            all_inbox_tasks_by_person_ref_id_and_timeline: Dict[Tuple[EntityId, str], InboxTask],
            sync_even_if_not_modified: bool) -> None:
        if period_filter is not None and catch_up_params.period not in period_filter:
            LOGGER.info(f"Skipping '{person.name}' on account of period filtering")
            return

        schedule = schedules.get_schedule(
            typing.cast(RecurringTaskPeriod, catch_up_params.period), person.name, right_now,
            self._global_properties.timezone, None, catch_up_params.actionable_from_day,
            catch_up_params.actionable_from_month, catch_up_params.due_at_time, catch_up_params.due_at_day,
            catch_up_params.due_at_month)

        LOGGER.info(f"Upserting catch up task for '{person.name}'")

        found_task = all_inbox_tasks_by_person_ref_id_and_timeline.get(
            (person.ref_id, schedule.timeline), None)

        if found_task:
            if not sync_even_if_not_modified and found_task.last_modified_time >= person.last_modified_time:
                LOGGER.info(f"Skipping update of '{found_task.name}' because it was not modified")
                return

            found_task.update_link_to_person_catch_up(
                name=schedule.full_name, recurring_timeline=schedule.timeline, eisen=catch_up_params.eisen,
                difficulty=catch_up_params.difficulty, actionable_date=schedule.actionable_date,
                due_time=schedule.due_time, modification_time=self._time_provider.get_current_time())

            with self._inbox_task_engine.get_unit_of_work() as uow:
                uow.inbox_task_repository.save(found_task)

            notion_inbox_task = \
                self._inbox_task_notion_manager.load_inbox_task(found_task.project_ref_id, found_task.ref_id)
            notion_inbox_task = notion_inbox_task.join_with_aggregate_root(found_task, NotionInboxTask.DirectInfo(None))
            self._inbox_task_notion_manager.save_inbox_task(found_task.project_ref_id, notion_inbox_task)
            LOGGER.info("Applied Notion changes")
        else:
            with self._inbox_task_engine.get_unit_of_work() as read_uow:
                inbox_task_collection = read_uow.inbox_task_collection_repository.load_by_project(project.ref_id)

                inbox_task = InboxTask.new_inbox_task_for_person_catch_up(
                    inbox_task_collection_ref_id=inbox_task_collection.ref_id,
                    name=schedule.full_name,
                    person_ref_id=person.ref_id,
                    recurring_task_timeline=schedule.timeline,
                    recurring_task_gen_right_now=right_now,
                    eisen=catch_up_params.eisen,
                    difficulty=catch_up_params.difficulty,
                    actionable_date=schedule.actionable_date,
                    due_date=schedule.due_time,
                    created_time=self._time_provider.get_current_time())

                inbox_task = read_uow.inbox_task_repository.create(inbox_task_collection, inbox_task)
                LOGGER.info("Applied local changes")
            notion_inbox_task = NotionInboxTask.new_notion_row(inbox_task, NotionInboxTask.DirectInfo(None))
            self._inbox_task_notion_manager.upsert_inbox_task(inbox_task_collection, notion_inbox_task)
            LOGGER.info("Applied Notion changes")

    def _generate_birthday_inbox_task_for_person(
            self,
            project: Project,
            right_now: Timestamp,
            person: Person,
            birthday: PersonBirthday,
            all_inbox_tasks_by_person_ref_id_and_timeline: Dict[Tuple[EntityId, str], InboxTask],
            sync_even_if_not_modified: bool) -> None:

        schedule = schedules.get_schedule(
            RecurringTaskPeriod.YEARLY, person.name, right_now,
            self._global_properties.timezone, None, None,
            None, None, RecurringTaskDueAtDay.from_raw(RecurringTaskPeriod.MONTHLY, birthday.day),
            RecurringTaskDueAtMonth.from_raw(RecurringTaskPeriod.YEARLY, birthday.month))

        LOGGER.info(f"Upserting birthday inbox task for '{person.name}'")

        found_task = all_inbox_tasks_by_person_ref_id_and_timeline.get(
            (person.ref_id, schedule.timeline), None)

        if found_task:
            if not sync_even_if_not_modified and found_task.last_modified_time >= person.last_modified_time:
                LOGGER.info(f"Skipping update of '{found_task.name}' because it was not modified")
                return

            found_task.update_link_to_person_birthday(
                name=schedule.full_name, recurring_timeline=schedule.timeline,
                preparation_days_cnt=person.preparation_days_cnt_for_birthday, due_time=schedule.due_time,
                modification_time=self._time_provider.get_current_time())

            with self._inbox_task_engine.get_unit_of_work() as uow:
                uow.inbox_task_repository.save(found_task)

            notion_inbox_task = \
                self._inbox_task_notion_manager.load_inbox_task(found_task.project_ref_id, found_task.ref_id)
            notion_inbox_task = notion_inbox_task.join_with_aggregate_root(found_task, NotionInboxTask.DirectInfo(None))
            self._inbox_task_notion_manager.save_inbox_task(found_task.project_ref_id, notion_inbox_task)
            LOGGER.info("Applied Notion changes")
        else:
            with self._inbox_task_engine.get_unit_of_work() as read_uow:
                inbox_task_collection = read_uow.inbox_task_collection_repository.load_by_project(project.ref_id)

                inbox_task = InboxTask.new_inbox_task_for_person_birthday(
                    inbox_task_collection_ref_id=inbox_task_collection.ref_id,
                    name=schedule.full_name,
                    person_ref_id=person.ref_id,
                    recurring_task_timeline=schedule.timeline,
                    preparation_days_cnt=person.preparation_days_cnt_for_birthday,
                    recurring_task_gen_right_now=right_now,
                    due_date=schedule.due_time,
                    created_time=self._time_provider.get_current_time())

                inbox_task = read_uow.inbox_task_repository.create(inbox_task_collection, inbox_task)
                LOGGER.info("Applied local changes")
            notion_inbox_task = NotionInboxTask.new_notion_row(inbox_task, NotionInboxTask.DirectInfo(None))
            self._inbox_task_notion_manager.upsert_inbox_task(inbox_task_collection, notion_inbox_task)
            LOGGER.info("Applied Notion changes")
