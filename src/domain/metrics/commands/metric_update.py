"""The command for updating a metric's properties."""
import typing
from dataclasses import dataclass
from typing import Final, Optional

from domain.common.difficulty import Difficulty
from domain.common.eisen import Eisen
from domain.common.entity_name import EntityName
from domain.common.recurring_task_due_at_day import RecurringTaskDueAtDay
from domain.common.recurring_task_due_at_month import RecurringTaskDueAtMonth
from domain.common.recurring_task_due_at_time import RecurringTaskDueAtTime
from domain.common.recurring_task_gen_params import RecurringTaskGenParams
from domain.common.recurring_task_period import RecurringTaskPeriod
from domain.common.timestamp import Timestamp
from domain.metrics.infra.metric_engine import MetricEngine
from domain.metrics.infra.metric_notion_manager import MetricNotionManager
from domain.metrics.metric_key import MetricKey
from domain.projects.project_key import ProjectKey
from models import schedules
from models.framework import Command, UpdateAction
from service.errors import ServiceError
from service.inbox_tasks import InboxTasksService
from service.projects import ProjectsService
from service.workspaces import WorkspacesService
from utils.global_properties import GlobalProperties
from utils.time_provider import TimeProvider


class MetricUpdateCommand(Command['MetricUpdateCommand.Args', None]):
    """The command for updating a metric's properties."""

    @dataclass()
    class Args:
        """Args."""
        key: MetricKey
        name: UpdateAction[EntityName]
        collection_project_key: UpdateAction[Optional[ProjectKey]]
        collection_period: UpdateAction[Optional[RecurringTaskPeriod]]
        collection_eisen: UpdateAction[typing.List[Eisen]]
        collection_difficulty: UpdateAction[Optional[Difficulty]]
        collection_actionable_from_day: UpdateAction[Optional[RecurringTaskDueAtDay]]
        collection_actionable_from_month: UpdateAction[Optional[RecurringTaskDueAtMonth]]
        collection_due_at_time: UpdateAction[Optional[RecurringTaskDueAtTime]]
        collection_due_at_day: UpdateAction[Optional[RecurringTaskDueAtDay]]
        collection_due_at_month: UpdateAction[Optional[RecurringTaskDueAtMonth]]

    _global_properties: Final[GlobalProperties]
    _time_provider: Final[TimeProvider]
    _metric_engine: Final[MetricEngine]
    _notion_manager: Final[MetricNotionManager]
    _workspaces_service: Final[WorkspacesService]
    _projects_service: Final[ProjectsService]
    _inbox_tasks_service: Final[InboxTasksService]

    def __init__(
            self, global_properties: GlobalProperties, time_provider: TimeProvider,
            metric_engine: MetricEngine,
            notion_manager: MetricNotionManager, workspaces_service: WorkspacesService,
            projects_service: ProjectsService, inbox_tasks_service: InboxTasksService) -> None:
        """Constructor."""
        self._global_properties = global_properties
        self._time_provider = time_provider
        self._metric_engine = metric_engine
        self._notion_manager = notion_manager
        self._workspaces_service = workspaces_service
        self._projects_service = projects_service
        self._inbox_tasks_service = inbox_tasks_service

    def execute(self, args: Args) -> None:
        """Execute the command's action."""
        with self._metric_engine.get_unit_of_work() as uow:
            metric = uow.metric_repository.get_by_key(args.key)

            # Change the metrics
            if args.name.should_change:
                metric.change_name(args.name.value, self._time_provider.get_current_time())
            if args.collection_project_key.should_change \
                    or args.collection_period.should_change \
                    or args.collection_eisen.should_change \
                    or args.collection_difficulty.should_change \
                    or args.collection_actionable_from_day.should_change \
                    or args.collection_actionable_from_month.should_change \
                    or args.collection_due_at_time.should_change \
                    or args.collection_due_at_day.should_change \
                    or args.collection_due_at_month:
                new_collection_period = None
                if args.collection_period.should_change:
                    new_collection_period = args.collection_period.value
                elif metric.collection_params is not None:
                    new_collection_period = metric.collection_params.period

                if new_collection_period is not None:
                    if args.collection_project_key.should_change:
                        if args.collection_project_key.value is not None:
                            project = self._projects_service.load_project_by_key(args.collection_project_key.value)
                            new_collection_project_ref_id = project.ref_id
                        else:
                            workspace = self._workspaces_service.load_workspace()
                            if workspace.default_project_ref_id is None:
                                raise ServiceError(
                                    "Cannot specify a collection period without a project (or a default one)")
                            new_collection_project_ref_id = workspace.default_project_ref_id
                    elif metric.collection_params is not None:
                        new_collection_project_ref_id = metric.collection_params.project_ref_id
                    else:
                        raise ServiceError("Cannot specify a collection period and no project")

                    new_collection_eisen = []
                    if args.collection_eisen.should_change:
                        new_collection_eisen = args.collection_eisen.value
                    elif metric.collection_params is not None:
                        new_collection_eisen = metric.collection_params.eisen

                    new_collection_difficulty = None
                    if args.collection_difficulty.should_change:
                        new_collection_difficulty = args.collection_difficulty.value
                    elif metric.collection_params is not None:
                        new_collection_difficulty = metric.collection_params.difficulty

                    new_collection_actionable_from_day = None
                    if args.collection_actionable_from_day.should_change:
                        new_collection_actionable_from_day = args.collection_actionable_from_day.value
                    elif metric.collection_params is not None:
                        new_collection_actionable_from_day = metric.collection_params.actionable_from_day

                    new_collection_actionable_from_month = None
                    if args.collection_actionable_from_month.should_change:
                        new_collection_actionable_from_month = args.collection_actionable_from_month.value
                    elif metric.collection_params is not None:
                        new_collection_actionable_from_month = metric.collection_params.actionable_from_month

                    new_collection_due_at_time = None
                    if args.collection_due_at_time.should_change:
                        new_collection_due_at_time = args.collection_due_at_time.value
                    elif metric.collection_params is not None:
                        new_collection_due_at_time = metric.collection_params.due_at_time

                    new_collection_due_at_day = None
                    if args.collection_due_at_day.should_change:
                        new_collection_due_at_day = args.collection_due_at_day.value
                    elif metric.collection_params is not None:
                        new_collection_due_at_day = metric.collection_params.due_at_day

                    new_collection_due_at_month = None
                    if args.collection_due_at_month.should_change:
                        new_collection_due_at_month = args.collection_due_at_month.value
                    elif metric.collection_params is not None:
                        new_collection_due_at_month = metric.collection_params.due_at_month

                    collection_params = RecurringTaskGenParams(
                        project_ref_id=new_collection_project_ref_id,
                        period=new_collection_period,
                        eisen=new_collection_eisen,
                        difficulty=new_collection_difficulty,
                        actionable_from_day=new_collection_actionable_from_day,
                        actionable_from_month=new_collection_actionable_from_month,
                        due_at_time=new_collection_due_at_time,
                        due_at_day=new_collection_due_at_day,
                        due_at_month=new_collection_due_at_month)

                metric.change_collection_params(collection_params, self._time_provider.get_current_time())

            uow.metric_repository.save(metric)

        self._notion_manager.upsert_metric(metric)

        # Change the inbox tasks
        metric_collection_tasks = self._inbox_tasks_service.load_all_inbox_tasks(
            allow_archived=True, filter_metric_ref_ids=[metric.ref_id])

        if metric.collection_params is None:
            # Situation 1: we need to get rid of any existing collection metrics because there's no collection anymore.
            for inbox_task in metric_collection_tasks:
                self._inbox_tasks_service.archive_inbox_task(inbox_task.ref_id)
        else:
            # Situation 2: we need to update the existing metrics.
            for inbox_task in metric_collection_tasks:
                schedule = schedules.get_schedule(
                    metric.collection_params.period, metric.name,
                    typing.cast(Timestamp, inbox_task.recurring_gen_right_now), self._global_properties.timezone,
                    None, metric.collection_params.actionable_from_day, metric.collection_params.actionable_from_month,
                    metric.collection_params.due_at_time, metric.collection_params.due_at_day,
                    metric.collection_params.due_at_month)
                if inbox_task.project_ref_id == metric.collection_params.project_ref_id:
                    # Situation 2a: we're handling the same project.
                    self._inbox_tasks_service.set_inbox_task_to_metric_link(
                        ref_id=inbox_task.ref_id,
                        name=schedule.full_name,
                        recurring_timeline=schedule.timeline,
                        recurring_period=metric.collection_params.period,
                        eisen=metric.collection_params.eisen,
                        difficulty=metric.collection_params.difficulty,
                        actionable_date=schedule.actionable_date,
                        due_time=schedule.due_time)
                else:
                    # Situation 2b: we're handling a new project.
                    self._inbox_tasks_service.hard_remove_inbox_task(inbox_task.ref_id)
                    self._inbox_tasks_service.create_inbox_task_for_metric(
                        project_ref_id=metric.collection_params.project_ref_id,
                        name=schedule.full_name,
                        metric_ref_id=metric.ref_id,
                        recurring_task_timeline=schedule.timeline,
                        recurring_task_period=metric.collection_params.period,
                        recurring_task_gen_right_now=self._time_provider.get_current_time(),
                        eisen=metric.collection_params.eisen,
                        difficulty=metric.collection_params.difficulty,
                        actionable_date=schedule.actionable_date,
                        due_date=schedule.due_time)
