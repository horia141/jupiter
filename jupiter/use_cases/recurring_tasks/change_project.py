"""The command for changing the project for a recurring task."""
import logging
from dataclasses import dataclass
from typing import Final, Optional, cast

from jupiter.domain import schedules
from jupiter.domain.recurring_tasks.infra.recurring_task_notion_manager import RecurringTaskNotionManager
from jupiter.domain.recurring_tasks.notion_recurring_task import NotionRecurringTask
from jupiter.domain.inbox_tasks.infra.inbox_task_notion_manager import InboxTaskNotionManager
from jupiter.domain.inbox_tasks.notion_inbox_task import NotionInboxTask
from jupiter.domain.projects.project_key import ProjectKey
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.base.timestamp import Timestamp
from jupiter.framework.event import EventSource
from jupiter.framework.use_case import MutationUseCaseInvocationRecorder, UseCaseArgsBase
from jupiter.use_cases.infra.use_cases import AppMutationUseCase, AppUseCaseContext
from jupiter.utils.global_properties import GlobalProperties
from jupiter.utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class RecurringTaskChangeProjectUseCase(AppMutationUseCase['RecurringTaskChangeProjectUseCase.Args', None]):
    """The command for changing the project of a recurring task."""

    @dataclass(frozen=True)
    class Args(UseCaseArgsBase):
        """Args."""
        ref_id: EntityId
        project_key: Optional[ProjectKey]

    _global_properties: Final[GlobalProperties]
    _inbox_task_notion_manager: Final[InboxTaskNotionManager]
    _recurring_task_notion_manager: Final[RecurringTaskNotionManager]

    def __init__(
            self,
            global_properties: GlobalProperties,
            time_provider: TimeProvider,
            invocation_recorder: MutationUseCaseInvocationRecorder,
            storage_engine: DomainStorageEngine,
            inbox_task_notion_manager: InboxTaskNotionManager,
            recurring_task_notion_manager: RecurringTaskNotionManager) -> None:
        """Constructor."""
        super().__init__(time_provider, invocation_recorder, storage_engine)
        self._global_properties = global_properties
        self._inbox_task_notion_manager = inbox_task_notion_manager
        self._recurring_task_notion_manager = recurring_task_notion_manager

    def _execute(self, context: AppUseCaseContext, args: Args) -> None:
        """Execute the command's action."""
        workspace = context.workspace

        with self._storage_engine.get_unit_of_work() as uow:
            project_collection = uow.project_collection_repository.load_by_workspace(workspace.ref_id)

            if args.project_key:
                project = uow.project_repository.load_by_key(project_collection.ref_id, args.project_key)
            else:
                project = uow.project_repository.load_by_id(workspace.default_project_ref_id)

            recurring_task = uow.recurring_task_repository.load_by_id(args.ref_id)

            recurring_task = \
                recurring_task.change_project(
                    project_ref_id=project.ref_id, source=EventSource.CLI,
                    modification_time=self._time_provider.get_current_time())

            uow.recurring_task_repository.save(recurring_task)

            inbox_task_collection = uow.inbox_task_collection_repository.load_by_workspace(workspace.ref_id)
            all_inbox_tasks = \
                uow.inbox_task_repository.find_all(
                    inbox_task_collection_ref_id=inbox_task_collection.ref_id,
                    allow_archived=True, filter_recurring_task_ref_ids=[recurring_task.ref_id])

            for inbox_task in all_inbox_tasks:
                schedule = schedules.get_schedule(
                    recurring_task.gen_params.period, recurring_task.name,
                    cast(Timestamp, inbox_task.recurring_gen_right_now), self._global_properties.timezone,
                    recurring_task.skip_rule, recurring_task.gen_params.actionable_from_day,
                    recurring_task.gen_params.actionable_from_month, recurring_task.gen_params.due_at_time,
                    recurring_task.gen_params.due_at_day, recurring_task.gen_params.due_at_month)

                inbox_task = inbox_task.update_link_to_recurring_task(
                    project_ref_id=project.ref_id,
                    name=schedule.full_name,
                    timeline=schedule.timeline,
                    the_type=recurring_task.the_type,
                    actionable_date=schedule.actionable_date,
                    due_date=schedule.due_time,
                    eisen=recurring_task.gen_params.eisen,
                    difficulty=recurring_task.gen_params.difficulty,
                    source=EventSource.CLI,
                    modification_time=self._time_provider.get_current_time())
                uow.inbox_task_repository.save(inbox_task)
                LOGGER.info(f'Updating the associated inbox task "{inbox_task.name}"')

        recurring_task_direct_info = NotionRecurringTask.DirectInfo(project_name=project.name)

        notion_recurring_task = \
            self._recurring_task_notion_manager.load_recurring_task(
                recurring_task.recurring_task_collection_ref_id, recurring_task.ref_id)
        notion_recurring_task = \
            notion_recurring_task.join_with_aggregate_root(recurring_task, recurring_task_direct_info)
        self._recurring_task_notion_manager.save_recurring_task(
            recurring_task.recurring_task_collection_ref_id, notion_recurring_task)

        for inbox_task in all_inbox_tasks:
            inbox_task_direct_info = \
                NotionInboxTask.DirectInfo(project_name=project.name, big_plan_name=None)
            notion_inbox_task = \
                self._inbox_task_notion_manager.load_inbox_task(
                    inbox_task.inbox_task_collection_ref_id, inbox_task.ref_id)
            notion_inbox_task = \
                notion_inbox_task.join_with_aggregate_root(inbox_task, inbox_task_direct_info)
            self._inbox_task_notion_manager.save_inbox_task(
                inbox_task.inbox_task_collection_ref_id, notion_inbox_task)
            LOGGER.info("Applied Notion changes")
