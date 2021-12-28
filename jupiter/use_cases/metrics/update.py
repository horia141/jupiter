"""The command for updating a metric's properties."""
import logging
import typing
from dataclasses import dataclass
from typing import Final, Optional

from jupiter.domain import schedules
from jupiter.domain.difficulty import Difficulty
from jupiter.domain.eisen import Eisen
from jupiter.domain.entity_name import EntityName
from jupiter.domain.inbox_tasks.infra.inbox_task_engine import InboxTaskEngine
from jupiter.domain.inbox_tasks.infra.inbox_task_notion_manager import InboxTaskNotionManager
from jupiter.domain.inbox_tasks.notion_inbox_task import NotionInboxTask
from jupiter.domain.inbox_tasks.service.archive_service import InboxTaskArchiveService
from jupiter.domain.inbox_tasks.service.change_project_service import InboxTaskChangeProjectService
from jupiter.domain.metrics.infra.metric_engine import MetricEngine
from jupiter.domain.metrics.infra.metric_notion_manager import MetricNotionManager
from jupiter.domain.metrics.metric_key import MetricKey
from jupiter.domain.projects.infra.project_engine import ProjectEngine
from jupiter.domain.projects.project_key import ProjectKey
from jupiter.domain.recurring_task_due_at_day import RecurringTaskDueAtDay
from jupiter.domain.recurring_task_due_at_month import RecurringTaskDueAtMonth
from jupiter.domain.recurring_task_due_at_time import RecurringTaskDueAtTime
from jupiter.domain.recurring_task_gen_params import RecurringTaskGenParams
from jupiter.domain.recurring_task_period import RecurringTaskPeriod
from jupiter.domain.workspaces.infra.workspace_engine import WorkspaceEngine
from jupiter.framework.base.timestamp import Timestamp
from jupiter.framework.errors import InputValidationError
from jupiter.framework.update_action import UpdateAction
from jupiter.framework.use_case import UseCase
from jupiter.utils.global_properties import GlobalProperties
from jupiter.utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class MetricUpdateUseCase(UseCase['MetricUpdateUseCase.Args', None]):
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
    _workspace_engine: Final[WorkspaceEngine]
    _project_engine: Final[ProjectEngine]
    _inbox_task_engine: Final[InboxTaskEngine]
    _inbox_task_notion_manager: Final[InboxTaskNotionManager]
    _metric_engine: Final[MetricEngine]
    _metric_notion_manager: Final[MetricNotionManager]

    def __init__(self, global_properties: GlobalProperties, time_provider: TimeProvider,
                 workspace_engine: WorkspaceEngine, project_engine: ProjectEngine,
                 inbox_task_engine: InboxTaskEngine, inbox_task_notion_manager: InboxTaskNotionManager,
                 metric_engine: MetricEngine,
                 metric_notion_manager: MetricNotionManager) -> None:
        """Constructor."""
        self._global_properties = global_properties
        self._time_provider = time_provider
        self._workspace_engine = workspace_engine
        self._project_engine = project_engine
        self._inbox_task_engine = inbox_task_engine
        self._inbox_task_notion_manager = inbox_task_notion_manager
        self._metric_engine = metric_engine
        self._metric_notion_manager = metric_notion_manager

    def execute(self, args: Args) -> None:
        """Execute the command's action."""
        with self._metric_engine.get_unit_of_work() as uow:
            metric = uow.metric_repository.load_by_key(args.key)

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
                            with self._project_engine.get_unit_of_work() as project_uow:
                                project = project_uow.project_repository.load_by_key(args.collection_project_key.value)
                            new_collection_project_ref_id = project.ref_id
                        else:
                            with self._workspace_engine.get_unit_of_work() as workspace_uow:
                                workspace = workspace_uow.workspace_repository.load()
                            new_collection_project_ref_id = workspace.default_project_ref_id
                    elif metric.collection_params is not None:
                        new_collection_project_ref_id = metric.collection_params.project_ref_id
                    else:
                        raise InputValidationError("Cannot specify a collection period and no project")

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

        notion_metric = self._metric_notion_manager.load_metric(metric.ref_id)
        notion_metric = notion_metric.join_with_aggregate_root(metric)
        self._metric_notion_manager.save_metric(notion_metric)

        # Change the inbox tasks
        with self._inbox_task_engine.get_unit_of_work() as inbox_task_uow:
            metric_collection_tasks = inbox_task_uow.inbox_task_repository.find_all(
                allow_archived=True, filter_metric_ref_ids=[metric.ref_id])

        if metric.collection_params is None:
            # Situation 1: we need to get rid of any existing collection metrics because there's no collection anymore.
            inbox_task_archive_service = \
                InboxTaskArchiveService(
                    self._time_provider, self._inbox_task_engine, self._inbox_task_notion_manager)
            for inbox_task in metric_collection_tasks:
                inbox_task_archive_service.do_it(inbox_task)
        else:
            # Situation 2: we need to update the existing metrics.
            inbox_task_change_project_service = \
                InboxTaskChangeProjectService(
                    self._time_provider, self._inbox_task_engine, self._inbox_task_notion_manager)
            for inbox_task in metric_collection_tasks:
                schedule = schedules.get_schedule(
                    metric.collection_params.period, metric.name,
                    typing.cast(Timestamp, inbox_task.recurring_gen_right_now), self._global_properties.timezone,
                    None, metric.collection_params.actionable_from_day, metric.collection_params.actionable_from_month,
                    metric.collection_params.due_at_time, metric.collection_params.due_at_day,
                    metric.collection_params.due_at_month)

                inbox_task.update_link_to_metric(name=schedule.full_name, recurring_timeline=schedule.timeline,
                                                 eisen=metric.collection_params.eisen,
                                                 difficulty=metric.collection_params.difficulty,
                                                 actionable_date=schedule.actionable_date, due_time=schedule.due_time,
                                                 modification_time=self._time_provider.get_current_time())

                with self._inbox_task_engine.get_unit_of_work() as inbox_task_uow:
                    inbox_task_uow.inbox_task_repository.save(inbox_task)

                notion_inbox_task = \
                    self._inbox_task_notion_manager.load_inbox_task(
                        inbox_task.inbox_task_collection_ref_id, inbox_task.ref_id)
                notion_inbox_task = notion_inbox_task.join_with_aggregate_root(
                    inbox_task, NotionInboxTask.DirectInfo(None))
                self._inbox_task_notion_manager.save_inbox_task(
                    inbox_task.inbox_task_collection_ref_id, notion_inbox_task)
                LOGGER.info("Applied Notion changes")

                if inbox_task.project_ref_id != metric.collection_params.project_ref_id:
                    # Situation 2a: we're handling the same project.
                    inbox_task_change_project_service.do_it(inbox_task, metric.collection_params.project_ref_id)
