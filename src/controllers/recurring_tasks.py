"""The controller for recurring tasks."""
import logging
from dataclasses import dataclass
from typing import Final, Iterable, Optional, List, Dict, Tuple, FrozenSet

import pendulum

from models import schedules
from models.basic import EntityId, Difficulty, Eisen, RecurringTaskPeriod, ProjectKey, EntityName, SyncPrefer
from repository.inbox_tasks import InboxTask
from repository.projects import Project
from repository.recurring_tasks import RecurringTask
from repository.vacations import Vacation
from service.inbox_tasks import InboxTasksService
from service.projects import ProjectsService
from service.recurring_tasks import RecurringTasksService
from service.vacations import VacationsService

LOGGER = logging.getLogger(__name__)


@dataclass()
class LoadAllRecurringTasksEntry:
    """A single entry in the load all recurring tasks response."""
    recurring_task: RecurringTask
    inbox_tasks: Iterable[InboxTask]


@dataclass()
class LoadAllRecurringTasksResponse:
    """Response object for the load_all_recurring_tasks controller method."""

    recurring_tasks: Iterable[LoadAllRecurringTasksEntry]


class RecurringTasksController:
    """The controller for recurring tasks."""

    _projects_service: Final[ProjectsService]
    _vacations_service: Final[VacationsService]
    _inbox_tasks_service: Final[InboxTasksService]
    _recurring_tasks_service: Final[RecurringTasksService]

    def __init__(
            self, projects_service: ProjectsService, vacations_service: VacationsService,
            inbox_tasks_service: InboxTasksService, recurring_tasks_service: RecurringTasksService) -> None:
        """Constructor."""
        self._projects_service = projects_service
        self._vacations_service = vacations_service
        self._inbox_tasks_service = inbox_tasks_service
        self._recurring_tasks_service = recurring_tasks_service

    def create_recurring_task(
            self, project_key: ProjectKey, name: str, period: RecurringTaskPeriod, group: EntityName,
            eisen: List[Eisen], difficulty: Optional[Difficulty], due_at_time: Optional[str],
            due_at_day: Optional[int], due_at_month: Optional[int], must_do: bool,
            skip_rule: Optional[str]) -> RecurringTask:
        """Create an recurring task."""
        project = self._projects_service.load_project_by_key(project_key)
        inbox_collection_link = self._inbox_tasks_service.get_notion_structure(project.ref_id)
        recurring_task = self._recurring_tasks_service.create_recurring_task(
            project_ref_id=project.ref_id,
            inbox_collection_link=inbox_collection_link,
            name=name,
            period=period,
            group=group,
            eisen=eisen,
            difficulty=difficulty,
            due_at_time=due_at_time,
            due_at_day=due_at_day,
            due_at_month=due_at_month,
            must_do=must_do,
            skip_rule=skip_rule)

        return recurring_task

    def archive_recurring_task(self, ref_id: EntityId) -> RecurringTask:
        """Archive an recurring task."""
        recurring_task = self._recurring_tasks_service.load_recurring_task_by_id(ref_id)
        all_inbox_tasks = self._inbox_tasks_service.load_all_inbox_tasks(
            filter_archived=False, filter_recurring_task_ref_ids=[recurring_task.ref_id])
        for inbox_task in all_inbox_tasks:
            self._inbox_tasks_service.archive_inbox_task(inbox_task.ref_id)
            LOGGER.info(f"Removing inbox task instance {inbox_task.name}")
        return self._recurring_tasks_service.archive_recurring_task(ref_id)

    def set_recurring_task_name(self, ref_id: EntityId, name: str) -> RecurringTask:
        """Change the name for a recurring task."""
        recurring_task = self._recurring_tasks_service.set_recurring_task_name(ref_id, name)
        all_inbox_tasks = self._inbox_tasks_service.load_all_inbox_tasks(
            filter_archived=False, filter_recurring_task_ref_ids=[recurring_task.ref_id])
        for inbox_task in all_inbox_tasks:
            schedule = schedules.get_schedule(
                recurring_task.period, recurring_task.name, pendulum.instance(inbox_task.created_date),
                recurring_task.skip_rule, recurring_task.due_at_time, recurring_task.due_at_day,
                recurring_task.due_at_month)
            self._inbox_tasks_service.set_inbox_task_name(inbox_task.ref_id, schedule.full_name)
        return recurring_task

    def set_recurring_task_period(self, ref_id: EntityId, period: RecurringTaskPeriod) -> RecurringTask:
        """Change the period for a recurring task."""
        recurring_task = self._recurring_tasks_service.set_recurring_task_period(ref_id, period)
        all_inbox_tasks = self._inbox_tasks_service.load_all_inbox_tasks(
            filter_archived=False, filter_recurring_task_ref_ids=[recurring_task.ref_id])
        for inbox_task in all_inbox_tasks:
            if inbox_task.is_considered_done:
                continue
            schedule = schedules.get_schedule(
                recurring_task.period, recurring_task.name, pendulum.instance(inbox_task.created_date),
                recurring_task.skip_rule, recurring_task.due_at_time, recurring_task.due_at_day,
                recurring_task.due_at_month)
            self._inbox_tasks_service.set_inbox_task_to_recurring_task_link(
                inbox_task.ref_id, schedule.full_name, schedule.period, schedule.timeline, schedule.due_time,
                recurring_task.eisen, recurring_task.difficulty)
        return recurring_task

    def set_recurring_task_group(self, ref_id: EntityId, group: EntityName) -> RecurringTask:
        """Change the group for a recurring task."""
        return self._recurring_tasks_service.set_recurring_task_group(ref_id, group)

    def set_recurring_task_eisen(self, ref_id: EntityId, eisen: List[Eisen]) -> RecurringTask:
        """Change the difficulty for a recurring task."""
        recurring_task = self._recurring_tasks_service.set_recurring_task_eisen(ref_id, eisen)
        all_inbox_tasks = self._inbox_tasks_service.load_all_inbox_tasks(
            filter_archived=False, filter_recurring_task_ref_ids=[recurring_task.ref_id])
        for inbox_task in all_inbox_tasks:
            self._inbox_tasks_service.set_inbox_task_eisen(inbox_task.ref_id, eisen)
        return recurring_task

    def set_recurring_task_difficulty(self, ref_id: EntityId, difficulty: Optional[Difficulty]) -> RecurringTask:
        """Change the difficulty for a recurring task."""
        recurring_task = self._recurring_tasks_service.set_recurring_task_difficulty(ref_id, difficulty)
        all_inbox_tasks = self._inbox_tasks_service.load_all_inbox_tasks(
            filter_archived=False, filter_recurring_task_ref_ids=[recurring_task.ref_id])
        for inbox_task in all_inbox_tasks:
            self._inbox_tasks_service.set_inbox_task_difficulty(inbox_task.ref_id, difficulty)
        return recurring_task

    def set_recurring_task_deadlines(
            self, ref_id: EntityId, due_at_time: Optional[str], due_at_day: Optional[int],
            due_at_month: Optional[int]) -> RecurringTask:
        """Change the deadlines for a recurring task."""
        recurring_task = self._recurring_tasks_service.set_recurring_task_deadlines(
            ref_id, due_at_time, due_at_day, due_at_month)
        all_inbox_tasks = self._inbox_tasks_service.load_all_inbox_tasks(
            filter_archived=False, filter_recurring_task_ref_ids=[recurring_task.ref_id])
        for inbox_task in all_inbox_tasks:
            schedule = schedules.get_schedule(
                recurring_task.period, recurring_task.name, pendulum.instance(inbox_task.created_date),
                recurring_task.skip_rule, due_at_time, due_at_day, due_at_month)
            self._inbox_tasks_service.set_inbox_task_due_date(inbox_task.ref_id, schedule.due_time)
        return recurring_task

    def set_recurring_task_must_do_state(self, ref_id: EntityId, must_do: bool) -> RecurringTask:
        """Change the skip rule for a recurring task."""
        return self._recurring_tasks_service.set_recurring_task_must_do_state(ref_id, must_do)

    def set_recurring_task_skip_rule(self, ref_id: EntityId, skip_rule: Optional[str]) -> RecurringTask:
        """Change the skip rule for a recurring task."""
        return self._recurring_tasks_service.set_recurring_task_skip_rule(ref_id, skip_rule)

    def set_recurring_task_suspended(self, ref_id: EntityId, suspended: bool) -> RecurringTask:
        """Change the suspended state for a recurring task."""
        return self._recurring_tasks_service.set_recurring_task_suspended(ref_id, suspended)

    def load_all_recurring_tasks(
            self, show_archived: bool = False, filter_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_project_keys: Optional[Iterable[ProjectKey]] = None) -> LoadAllRecurringTasksResponse:
        """Retrieve all recurring tasks."""
        filter_project_ref_ids: Optional[List[EntityId]] = None
        if filter_project_keys:
            projects = self._projects_service.load_all_projects(filter_keys=filter_project_keys)
            filter_project_ref_ids = [p.ref_id for p in projects]

        recurring_tasks = self._recurring_tasks_service.load_all_recurring_tasks(
            filter_archived=not show_archived, filter_ref_ids=filter_ref_ids,
            filter_project_ref_ids=filter_project_ref_ids)
        inbox_tasks = self._inbox_tasks_service.load_all_inbox_tasks(
            filter_archived=False, filter_recurring_task_ref_ids=(bp.ref_id for bp in recurring_tasks))

        return LoadAllRecurringTasksResponse(
            recurring_tasks=[LoadAllRecurringTasksEntry(
                                recurring_task=rt,
                                inbox_tasks=[it for it in inbox_tasks if it.recurring_task_ref_id == rt.ref_id])
                             for rt in recurring_tasks])

    def recurring_tasks_gen(
            self, right_now: pendulum.DateTime, project_key: ProjectKey,
            group_filter: Optional[Iterable[EntityName]] = None,
            period_filter: Optional[Iterable[RecurringTaskPeriod]] = None) -> None:
        """Generate recurring tasks to inbox tasks."""
        project = self._projects_service.load_project_by_key(project_key)
        all_vacations = self._vacations_service.load_all_vacations()
        all_recurring_tasks = self._recurring_tasks_service.load_all_recurring_tasks(
            filter_project_ref_ids=[project.ref_id])
        all_inbox_tasks = self._inbox_tasks_service.load_all_inbox_tasks(
            filter_archived=False, filter_project_ref_ids=[project.ref_id],
            filter_recurring_task_ref_ids=(rt.ref_id for rt in all_recurring_tasks))

        all_inbox_tasks_by_recurring_task_ref_id_and_timeline = {}
        for inbox_task in all_inbox_tasks:
            if inbox_task.recurring_task_ref_id is None or inbox_task.recurring_task_timeline is None:
                raise Exception(f"Expected that inbox task with id='{inbox_task.ref_id}'")
            all_inbox_tasks_by_recurring_task_ref_id_and_timeline[
                (inbox_task.recurring_task_ref_id, inbox_task.recurring_task_timeline)] = inbox_task

        for recurring_task in all_recurring_tasks:
            LOGGER.info(f"Generating inbox tasks for '{recurring_task.name}'")
            self._generate_inbox_tasks_for_recurring_task(
                project=project,
                right_now=right_now,
                group_filter=frozenset(group_filter) if group_filter else None,
                period_filter=frozenset(period_filter) if period_filter else None,
                all_vacations=list(all_vacations),
                recurring_task=recurring_task,
                all_inbox_tasks_by_recurring_task_ref_id_and_timeline=
                all_inbox_tasks_by_recurring_task_ref_id_and_timeline)

    def _generate_inbox_tasks_for_recurring_task(
            self,
            project: Project,
            right_now: pendulum.DateTime,
            group_filter: Optional[FrozenSet[EntityName]],
            period_filter: Optional[FrozenSet[RecurringTaskPeriod]],
            all_vacations: List[Vacation],
            recurring_task: RecurringTask,
            all_inbox_tasks_by_recurring_task_ref_id_and_timeline: Dict[Tuple[EntityId, str], InboxTask]) -> None:
        if recurring_task.suspended:
            LOGGER.info(f"Skipping '{recurring_task.name}' because it is suspended")
            return

        if group_filter is not None and recurring_task.group not in group_filter:
            LOGGER.info(f"Skipping '{recurring_task.name}' on account of group filtering")
            return

        if period_filter is not None and recurring_task.period not in period_filter:
            LOGGER.info(f"Skipping '{recurring_task.name}' on account of period filtering")
            return

        schedule = schedules.get_schedule(
            recurring_task.period.value, recurring_task.name, right_now, recurring_task.skip_rule,
            recurring_task.due_at_time, recurring_task.due_at_day, recurring_task.due_at_month)

        if not recurring_task.must_do:
            for vacation in all_vacations:
                if vacation.is_in_vacation(schedule.first_day, schedule.end_day):
                    LOGGER.info(
                        f"Skipping '{recurring_task.name}' on account of being fully withing vacation {vacation}")
                    return

        if schedule.should_skip:
            LOGGER.info(f"Skipping '{recurring_task.name}' on account of rule")
            return

        LOGGER.info(f"Upserting '{recurring_task.name}'")

        found_task = all_inbox_tasks_by_recurring_task_ref_id_and_timeline.get(
            (recurring_task.ref_id, schedule.timeline), None)

        if found_task:
            self._inbox_tasks_service.set_inbox_task_to_recurring_task_link(
                ref_id=found_task.ref_id,
                name=schedule.full_name,
                period=recurring_task.period,
                due_time=schedule.due_time,
                eisen=recurring_task.eisen,
                difficulty=recurring_task.difficulty,
                timeline=schedule.timeline)
        else:
            self._inbox_tasks_service.create_inbox_task_for_recurring_task(
                project_ref_id=project.ref_id,
                name=schedule.full_name,
                recurring_task_ref_id=recurring_task.ref_id,
                recurring_task_period=recurring_task.period,
                recurring_task_timeline=schedule.timeline,
                eisen=recurring_task.eisen,
                difficulty=recurring_task.difficulty,
                due_date=schedule.due_time)

    def recurring_tasks_sync(self, project_key: ProjectKey, sync_prefer: SyncPrefer) -> None:
        """Synchronise recurring tasks between Notion and local."""
        project = self._projects_service.load_project_by_key(project_key)
        project_page = self._projects_service.get_project_notion_structure(project.ref_id)

        self._inbox_tasks_service.upsert_notion_structure(project.ref_id, project_page)

        inbox_collection_link = self._inbox_tasks_service.get_notion_structure(project.ref_id)
        self._recurring_tasks_service.recurring_tasks_sync(
            project.ref_id, inbox_collection_link, sync_prefer)
        all_recurring_tasks = self._recurring_tasks_service.load_all_recurring_tasks(filter_archived=False)
        all_recurring_tasks_set = {rt.ref_id: rt for rt in all_recurring_tasks}
        all_inbox_tasks = self._inbox_tasks_service.load_all_inbox_tasks(
            filter_archived=False, filter_project_ref_ids=[project.ref_id],
            filter_recurring_task_ref_ids=[r.ref_id for r in all_recurring_tasks])

        for inbox_task in all_inbox_tasks:
            if inbox_task.is_considered_done:
                continue
            if inbox_task.recurring_task_ref_id is None:
                raise Exception(f"Expected that inbox task with id='{inbox_task.ref_id}'")
            recurring_task = all_recurring_tasks_set[inbox_task.recurring_task_ref_id]
            schedule = schedules.get_schedule(
                recurring_task.period.value, recurring_task.name, pendulum.instance(inbox_task.created_date),
                recurring_task.skip_rule, recurring_task.due_at_time, recurring_task.due_at_day,
                recurring_task.due_at_month)
            self._inbox_tasks_service.set_inbox_task_to_recurring_task_link(
                ref_id=inbox_task.ref_id,
                name=schedule.full_name,
                period=recurring_task.period,
                due_time=schedule.due_time,
                eisen=recurring_task.eisen,
                difficulty=recurring_task.difficulty,
                timeline=schedule.timeline)
            LOGGER.info(f"Applied Notion changes to inbox task {inbox_task}")
