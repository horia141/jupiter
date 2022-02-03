"""The command for creating a recurring task."""
import logging
from dataclasses import dataclass
from typing import Optional, Final

from jupiter.domain.adate import ADate
from jupiter.domain.difficulty import Difficulty
from jupiter.domain.eisen import Eisen
from jupiter.domain.inbox_tasks.infra.inbox_task_notion_manager import InboxTaskNotionManager
from jupiter.domain.projects.project_key import ProjectKey
from jupiter.domain.recurring_task_due_at_day import RecurringTaskDueAtDay
from jupiter.domain.recurring_task_due_at_month import RecurringTaskDueAtMonth
from jupiter.domain.recurring_task_due_at_time import RecurringTaskDueAtTime
from jupiter.domain.recurring_task_gen_params import RecurringTaskGenParams
from jupiter.domain.recurring_task_period import RecurringTaskPeriod
from jupiter.domain.recurring_task_skip_rule import RecurringTaskSkipRule
from jupiter.domain.recurring_task_type import RecurringTaskType
from jupiter.domain.recurring_tasks.infra.recurring_task_notion_manager import RecurringTaskNotionManager
from jupiter.domain.recurring_tasks.notion_recurring_task import NotionRecurringTask
from jupiter.domain.recurring_tasks.recurring_task import RecurringTask
from jupiter.domain.recurring_tasks.recurring_task_name import RecurringTaskName
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.framework.event import EventSource
from jupiter.framework.use_case import MutationUseCaseInvocationRecorder, UseCaseArgsBase
from jupiter.use_cases.infra.use_cases import AppMutationUseCase, AppUseCaseContext
from jupiter.utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class RecurringTaskCreateUseCase(AppMutationUseCase['RecurringTaskCreateUseCase.Args', None]):
    """The command for creating a recurring task."""

    @dataclass()
    class Args(UseCaseArgsBase):
        """Args."""
        project_key: Optional[ProjectKey]
        name: RecurringTaskName
        period: RecurringTaskPeriod
        the_type: RecurringTaskType
        eisen: Optional[Eisen]
        difficulty: Optional[Difficulty]
        actionable_from_day: Optional[RecurringTaskDueAtDay]
        actionable_from_month: Optional[RecurringTaskDueAtMonth]
        due_at_time: Optional[RecurringTaskDueAtTime]
        due_at_day: Optional[RecurringTaskDueAtDay]
        due_at_month: Optional[RecurringTaskDueAtMonth]
        must_do: bool
        skip_rule: Optional[RecurringTaskSkipRule]
        start_at_date: Optional[ADate]
        end_at_date: Optional[ADate]

    _inbox_task_notion_manager: Final[InboxTaskNotionManager]
    _recurring_task_notion_manager: Final[RecurringTaskNotionManager]

    def __init__(
            self,
            time_provider: TimeProvider,
            invocation_recorder: MutationUseCaseInvocationRecorder,
            storage_engine: DomainStorageEngine,
            inbox_task_notion_manager: InboxTaskNotionManager,
            recurring_task_notion_manager: RecurringTaskNotionManager) -> None:
        """Constructor."""
        super().__init__(time_provider, invocation_recorder, storage_engine)
        self._inbox_task_notion_manager = inbox_task_notion_manager
        self._recurring_task_notion_manager = recurring_task_notion_manager

    def _execute(self, context: AppUseCaseContext, args: Args) -> None:
        """Execute the command's action."""
        workspace = context.workspace

        with self._storage_engine.get_unit_of_work() as uow:
            project_collection = uow.project_collection_repository.load_by_workspace(workspace.ref_id)

            if args.project_key is not None:
                project = uow.project_repository.load_by_key(project_collection.ref_id, args.project_key)
                project_ref_id = project.ref_id
            else:
                project = uow.project_repository.load_by_id(workspace.default_project_ref_id)
                project_ref_id = workspace.default_project_ref_id

            inbox_task_collection = uow.inbox_task_collection_repository.load_by_workspace(workspace.ref_id)
            recurring_task_collection = uow.recurring_task_collection_repository.load_by_workspace(workspace.ref_id)

            recurring_task = RecurringTask.new_recurring_task(
                recurring_task_collection_ref_id=recurring_task_collection.ref_id,
                archived=False,
                project_ref_id=project_ref_id,
                name=args.name,
                the_type=args.the_type,
                gen_params=RecurringTaskGenParams(
                    period=args.period,
                    eisen=args.eisen if args.eisen else Eisen.REGULAR,
                    difficulty=args.difficulty,
                    actionable_from_day=args.actionable_from_day,
                    actionable_from_month=args.actionable_from_month,
                    due_at_time=args.due_at_time,
                    due_at_day=args.due_at_day,
                    due_at_month=args.due_at_month),
                must_do=args.must_do,
                skip_rule=args.skip_rule,
                start_at_date=args.start_at_date,
                end_at_date=args.end_at_date,
                suspended=False,
                source=EventSource.CLI,
                created_time=self._time_provider.get_current_time())
            recurring_task = \
                uow.recurring_task_repository.create(recurring_task)
            LOGGER.info("Applied local changes")

        notion_inbox_task_collection = \
            self._inbox_task_notion_manager.load_inbox_task_collection(inbox_task_collection.ref_id)

        direct_info = NotionRecurringTask.DirectInfo(project_name=project.name)
        notion_recurring_task = NotionRecurringTask.new_notion_row(recurring_task, direct_info)
        self._recurring_task_notion_manager.upsert_recurring_task(
            recurring_task_collection.ref_id, notion_recurring_task, notion_inbox_task_collection)
        LOGGER.info("Applied Notion changes")
