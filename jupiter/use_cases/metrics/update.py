"""The command for updating a metric's properties."""
import logging
import typing
from dataclasses import dataclass
from typing import Final, Optional

from jupiter.domain import schedules
from jupiter.domain.difficulty import Difficulty
from jupiter.domain.eisen import Eisen
from jupiter.domain.entity_icon import EntityIcon
from jupiter.domain.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.domain.inbox_tasks.infra.inbox_task_notion_manager import InboxTaskNotionManager
from jupiter.domain.inbox_tasks.notion_inbox_task import NotionInboxTask
from jupiter.domain.inbox_tasks.service.archive_service import InboxTaskArchiveService
from jupiter.domain.metrics.infra.metric_notion_manager import MetricNotionManager
from jupiter.domain.metrics.metric_key import MetricKey
from jupiter.domain.metrics.metric_name import MetricName
from jupiter.domain.recurring_task_due_at_day import RecurringTaskDueAtDay
from jupiter.domain.recurring_task_due_at_month import RecurringTaskDueAtMonth
from jupiter.domain.recurring_task_due_at_time import RecurringTaskDueAtTime
from jupiter.domain.recurring_task_gen_params import RecurringTaskGenParams
from jupiter.domain.recurring_task_period import RecurringTaskPeriod
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.framework.base.timestamp import Timestamp
from jupiter.framework.event import EventSource
from jupiter.framework.update_action import UpdateAction
from jupiter.framework.use_case import MutationUseCaseInvocationRecorder, UseCaseArgsBase
from jupiter.use_cases.infra.use_cases import AppMutationUseCase, AppUseCaseContext
from jupiter.utils.global_properties import GlobalProperties
from jupiter.utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class MetricUpdateUseCase(AppMutationUseCase['MetricUpdateUseCase.Args', None]):
    """The command for updating a metric's properties."""

    @dataclass(frozen=True)
    class Args(UseCaseArgsBase):
        """Args."""
        key: MetricKey
        name: UpdateAction[MetricName]
        icon: UpdateAction[Optional[EntityIcon]]
        collection_period: UpdateAction[Optional[RecurringTaskPeriod]]
        collection_eisen: UpdateAction[Eisen]
        collection_difficulty: UpdateAction[Optional[Difficulty]]
        collection_actionable_from_day: UpdateAction[Optional[RecurringTaskDueAtDay]]
        collection_actionable_from_month: UpdateAction[Optional[RecurringTaskDueAtMonth]]
        collection_due_at_time: UpdateAction[Optional[RecurringTaskDueAtTime]]
        collection_due_at_day: UpdateAction[Optional[RecurringTaskDueAtDay]]
        collection_due_at_month: UpdateAction[Optional[RecurringTaskDueAtMonth]]

    _global_properties: Final[GlobalProperties]
    _inbox_task_notion_manager: Final[InboxTaskNotionManager]
    _metric_notion_manager: Final[MetricNotionManager]

    def __init__(
            self,
            global_properties: GlobalProperties,
            time_provider: TimeProvider,
            invocation_recorder: MutationUseCaseInvocationRecorder,
            storage_engine: DomainStorageEngine,
            inbox_task_notion_manager: InboxTaskNotionManager,
            metric_notion_manager: MetricNotionManager) -> None:
        """Constructor."""
        super().__init__(time_provider, invocation_recorder, storage_engine)
        self._global_properties = global_properties
        self._inbox_task_notion_manager = inbox_task_notion_manager
        self._metric_notion_manager = metric_notion_manager

    def _execute(self, context: AppUseCaseContext, args: Args) -> None:
        """Execute the command's action."""
        workspace = context.workspace

        with self._storage_engine.get_unit_of_work() as uow:
            metric_collection = uow.metric_collection_repository.load_by_workspace(workspace.ref_id)
            metric = uow.metric_repository.load_by_key(metric_collection.ref_id, args.key)

            # Change the metrics
            collection_params: UpdateAction[Optional[RecurringTaskGenParams]]
            if args.collection_period.should_change \
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

                    collection_params = \
                        UpdateAction.change_to(RecurringTaskGenParams(
                            period=new_collection_period,
                            eisen=new_collection_eisen,
                            difficulty=new_collection_difficulty,
                            actionable_from_day=new_collection_actionable_from_day,
                            actionable_from_month=new_collection_actionable_from_month,
                            due_at_time=new_collection_due_at_time,
                            due_at_day=new_collection_due_at_day,
                            due_at_month=new_collection_due_at_month))
                else:
                    collection_params = UpdateAction.change_to(None)
            else:
                collection_params = UpdateAction.do_nothing()

            metric = \
                metric.update(
                    name=args.name,
                    icon=args.icon,
                    collection_params=collection_params,
                    source=EventSource.CLI,
                    modification_time=self._time_provider.get_current_time())

            uow.metric_repository.save(metric)

            inbox_task_collection = uow.inbox_task_collection_repository.load_by_workspace(workspace.ref_id)

            metric_collection_tasks = \
                uow.inbox_task_repository.find_all(
                    inbox_task_collection_ref_id=inbox_task_collection.ref_id,
                    filter_sources=[InboxTaskSource.METRIC],
                    allow_archived=True,
                    filter_metric_ref_ids=[metric.ref_id])

        notion_metric = self._metric_notion_manager.load_metric(metric_collection.ref_id, metric.ref_id)
        notion_metric = notion_metric.join_with_entity(metric)
        self._metric_notion_manager.save_metric(metric_collection.ref_id, notion_metric)

        # Change the inbox tasks
        if metric.collection_params is None:
            # Situation 1: we need to get rid of any existing collection metrics because there's no collection anymore.
            inbox_task_archive_service = \
                InboxTaskArchiveService(
                    source=EventSource.CLI, time_provider=self._time_provider, storage_engine=self._storage_engine,
                    inbox_task_notion_manager=self._inbox_task_notion_manager)
            for inbox_task in metric_collection_tasks:
                inbox_task_archive_service.do_it(inbox_task)
        else:
            # Situation 2: we need to update the existing metrics.
            with self._storage_engine.get_unit_of_work() as uow:
                project = uow.project_repository.load_by_id(metric_collection.collection_project_ref_id)

            for inbox_task in metric_collection_tasks:
                schedule = schedules.get_schedule(
                    metric.collection_params.period, metric.name,
                    typing.cast(Timestamp, inbox_task.recurring_gen_right_now), self._global_properties.timezone,
                    None, metric.collection_params.actionable_from_day, metric.collection_params.actionable_from_month,
                    metric.collection_params.due_at_time, metric.collection_params.due_at_day,
                    metric.collection_params.due_at_month)

                inbox_task = inbox_task.update_link_to_metric(
                    project_ref_id=project.ref_id,
                    name=schedule.full_name,
                    recurring_timeline=schedule.timeline,
                    eisen=metric.collection_params.eisen,
                    difficulty=metric.collection_params.difficulty,
                    actionable_date=schedule.actionable_date,
                    due_time=schedule.due_time,
                    source=EventSource.CLI,
                    modification_time=self._time_provider.get_current_time())

                with self._storage_engine.get_unit_of_work() as uow:
                    uow.inbox_task_repository.save(inbox_task)

                if inbox_task.archived:
                    continue

                direct_info = NotionInboxTask.DirectInfo(project_name=project.name, big_plan_name=None)
                notion_inbox_task = \
                    self._inbox_task_notion_manager.load_inbox_task(
                        inbox_task.inbox_task_collection_ref_id, inbox_task.ref_id)
                notion_inbox_task = notion_inbox_task.join_with_entity(inbox_task, direct_info)
                self._inbox_task_notion_manager.save_inbox_task(
                    inbox_task.inbox_task_collection_ref_id, notion_inbox_task)
                LOGGER.info("Applied Notion changes")
