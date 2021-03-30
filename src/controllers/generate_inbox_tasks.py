"""The controller for generating inbox tasks."""
import logging
from typing import Final, Iterable, Optional, List, Dict, Tuple, FrozenSet

import typing

from domain.metrics.infra.metric_engine import MetricEngine
from domain.metrics.metric import Metric, MetricCollectionParams
from domain.vacations.vacation import Vacation
from models import schedules
from models.basic import EntityId, RecurringTaskPeriod, ProjectKey, Timestamp, SyncTarget, MetricKey
from service.inbox_tasks import InboxTasksService, InboxTask
from service.projects import ProjectsService, Project
from service.recurring_tasks import RecurringTasksService, RecurringTask
from service.vacations import VacationsService
from service.workspaces import WorkspacesService
from utils.global_properties import GlobalProperties

LOGGER = logging.getLogger(__name__)


class GenerateInboxTasksController:
    """The controller for generating inbox tasks."""

    _global_properties: Final[GlobalProperties]
    _workspaces_service: Final[WorkspacesService]
    _projects_service: Final[ProjectsService]
    _vacations_service: Final[VacationsService]
    _inbox_tasks_service: Final[InboxTasksService]
    _recurring_tasks_service: Final[RecurringTasksService]
    _metric_engine: Final[MetricEngine]

    def __init__(
            self, global_properties: GlobalProperties, workspaces_service: WorkspacesService,
            projects_service: ProjectsService, vacations_service: VacationsService,
            inbox_tasks_service: InboxTasksService, recurring_tasks_service: RecurringTasksService,
            metric_engine: MetricEngine) -> None:
        """Constructor."""
        self._global_properties = global_properties
        self._workspaces_service = workspaces_service
        self._projects_service = projects_service
        self._vacations_service = vacations_service
        self._inbox_tasks_service = inbox_tasks_service
        self._recurring_tasks_service = recurring_tasks_service
        self._metric_engine = metric_engine

    def recurring_tasks_gen(
            self, right_now: Timestamp, gen_targets: Iterable[SyncTarget],
            filter_project_keys: Optional[Iterable[ProjectKey]],
            filter_recurring_task_ref_ids: Optional[Iterable[EntityId]],
            filter_metric_keys: Optional[Iterable[MetricKey]],
            filter_period: Optional[Iterable[RecurringTaskPeriod]], sync_even_if_not_modified: bool) -> None:
        """Generate recurring tasks to inbox tasks."""
        all_vacations = list(self._vacations_service.load_all_vacations())

        if SyncTarget.PROJECTS in gen_targets:
            for project in self._projects_service.load_all_projects(filter_keys=filter_project_keys):
                LOGGER.info(f"Generating tasks for project '{project.name}'")
                all_recurring_tasks = list(self._recurring_tasks_service.load_all_recurring_tasks(
                    filter_ref_ids=filter_recurring_task_ref_ids, filter_project_ref_ids=[project.ref_id]))
                if len(all_recurring_tasks) == 0:
                    continue
                all_inbox_tasks = self._inbox_tasks_service.load_all_inbox_tasks(
                    allow_archived=True, filter_project_ref_ids=[project.ref_id],
                    filter_recurring_task_ref_ids=(rt.ref_id for rt in all_recurring_tasks))

                all_inbox_tasks_by_recurring_task_ref_id_and_timeline = {}
                for inbox_task in all_inbox_tasks:
                    if inbox_task.recurring_task_ref_id is None or inbox_task.recurring_timeline is None:
                        raise Exception(f"Expected that inbox task with id='{inbox_task.ref_id}'")
                    all_inbox_tasks_by_recurring_task_ref_id_and_timeline[
                        (inbox_task.recurring_task_ref_id, inbox_task.recurring_timeline)] = inbox_task

                for recurring_task in all_recurring_tasks:
                    LOGGER.info(f"Generating inbox tasks for '{recurring_task.name}'")
                    self._generate_inbox_tasks_for_recurring_task(
                        project=project,
                        right_now=right_now,
                        period_filter=frozenset(filter_period) if filter_period else None,
                        all_vacations=all_vacations,
                        recurring_task=recurring_task,
                        all_inbox_tasks_by_recurring_task_ref_id_and_timeline=
                        all_inbox_tasks_by_recurring_task_ref_id_and_timeline,
                        sync_even_if_not_modified=sync_even_if_not_modified)

        if SyncTarget.METRICS in gen_targets:
            with self._metric_engine.get_unit_of_work() as uow:
                all_metrics = uow.metric_repository.find_all(filter_keys=filter_metric_keys)

                all_inbox_tasks = self._inbox_tasks_service.load_all_inbox_tasks(
                    allow_archived=True,
                    filter_metric_ref_ids=[m.ref_id for m in all_metrics])

                all_inbox_tasks_by_metric_ref_id_and_timeline = {}
                for inbox_task in all_inbox_tasks:
                    if inbox_task.metric_ref_id is None or inbox_task.recurring_timeline is None:
                        raise Exception(f"Expected that inbox task with id='{inbox_task.ref_id}'")
                    all_inbox_tasks_by_metric_ref_id_and_timeline[
                        (inbox_task.metric_ref_id, inbox_task.recurring_timeline)] = inbox_task

                for metric in all_metrics:
                    if metric.collection_params is None:
                        continue
                    LOGGER.info(f"Generating collection tasks for metric '{metric.name}'")

                    # MyPy not smart enough to infer that if (not A and not B) then (A or B)
                    project = self._projects_service.load_project_by_ref_id(metric.collection_params.project_ref_id)

                    self._generate_inbox_tasks_for_metric(
                        project=project,
                        right_now=right_now,
                        period_filter=frozenset(filter_period) if filter_period else None,
                        metric=metric,
                        collection_params=metric.collection_params,
                        all_inbox_tasks_by_metric_ref_id_and_timeline=
                        all_inbox_tasks_by_metric_ref_id_and_timeline,
                        sync_even_if_not_modified=sync_even_if_not_modified)

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
            recurring_task.skip_rule, recurring_task.actionable_from_day, recurring_task.actionable_from_month,
            recurring_task.due_at_time, recurring_task.due_at_day, recurring_task.due_at_month)

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

            self._inbox_tasks_service.set_inbox_task_to_recurring_task_link(
                ref_id=found_task.ref_id,
                name=schedule.full_name,
                actionable_date=schedule.actionable_date,
                due_time=schedule.due_time,
                eisen=recurring_task.eisen,
                difficulty=recurring_task.difficulty,
                timeline=schedule.timeline,
                period=recurring_task.period,
                the_type=recurring_task.the_type)
        else:
            self._inbox_tasks_service.create_inbox_task_for_recurring_task(
                project_ref_id=project.ref_id,
                name=schedule.full_name,
                recurring_task_ref_id=recurring_task.ref_id,
                recurring_task_timeline=schedule.timeline,
                recurring_task_period=recurring_task.period,
                recurring_task_type=recurring_task.the_type,
                recurring_task_gen_right_now=right_now,
                eisen=recurring_task.eisen,
                difficulty=recurring_task.difficulty,
                actionable_date=schedule.actionable_date,
                due_date=schedule.due_time)

    def _generate_inbox_tasks_for_metric(
            self,
            project: Project,
            right_now: Timestamp,
            period_filter: Optional[FrozenSet[RecurringTaskPeriod]],
            metric: Metric,
            collection_params: MetricCollectionParams,
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

        LOGGER.info(f"Upserting '{metric.name}'")

        found_task = all_inbox_tasks_by_metric_ref_id_and_timeline.get(
            (metric.ref_id, schedule.timeline), None)

        if found_task:
            if not sync_even_if_not_modified and found_task.last_modified_time >= metric.last_modified_time:
                LOGGER.info(f"Skipping update of '{found_task.name}' because it was not modified")
                return

            self._inbox_tasks_service.set_inbox_task_to_metric_link(
                ref_id=found_task.ref_id,
                name=schedule.full_name,
                recurring_timeline=schedule.timeline,
                recurring_period=collection_params.period,
                eisen=collection_params.eisen,
                difficulty=collection_params.difficulty,
                actionable_date=schedule.actionable_date,
                due_time=schedule.due_time)
        else:
            self._inbox_tasks_service.create_inbox_task_for_metric(
                project_ref_id=project.ref_id,
                name=schedule.full_name,
                metric_ref_id=metric.ref_id,
                recurring_task_timeline=schedule.timeline,
                recurring_task_period=collection_params.period,
                recurring_task_gen_right_now=right_now,
                eisen=collection_params.eisen,
                difficulty=collection_params.difficulty,
                actionable_date=schedule.actionable_date,
                due_date=schedule.due_time)
