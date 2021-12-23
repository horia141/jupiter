"""The command for creating a recurring task."""
import logging
from dataclasses import dataclass
from typing import Optional, List, Final

from domain.adate import ADate
from domain.difficulty import Difficulty
from domain.eisen import Eisen
from domain.entity_name import EntityName
from domain.inbox_tasks.infra.inbox_task_engine import InboxTaskEngine
from domain.inbox_tasks.infra.inbox_task_notion_manager import InboxTaskNotionManager
from domain.projects.infra.project_engine import ProjectEngine
from domain.projects.project_key import ProjectKey
from domain.recurring_task_due_at_day import RecurringTaskDueAtDay
from domain.recurring_task_due_at_month import RecurringTaskDueAtMonth
from domain.recurring_task_due_at_time import RecurringTaskDueAtTime
from domain.recurring_task_gen_params import RecurringTaskGenParams
from domain.recurring_task_period import RecurringTaskPeriod
from domain.recurring_task_skip_rule import RecurringTaskSkipRule
from domain.recurring_task_type import RecurringTaskType
from domain.recurring_tasks.infra.recurring_task_engine import RecurringTaskEngine
from domain.recurring_tasks.infra.recurring_task_notion_manager import RecurringTaskNotionManager
from domain.recurring_tasks.notion_recurring_task import NotionRecurringTask
from domain.recurring_tasks.recurring_task import RecurringTask
from domain.workspaces.infra.workspace_engine import WorkspaceEngine
from framework.use_case import UseCase
from utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class RecurringTaskCreateUseCase(UseCase['RecurringTaskCreateUseCase.Args', None]):
    """The command for creating a recurring task."""

    @dataclass()
    class Args:
        """Args."""
        project_key: Optional[ProjectKey]
        name: EntityName
        period: RecurringTaskPeriod
        the_type: RecurringTaskType
        eisen: List[Eisen]
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

    _time_provider: Final[TimeProvider]
    _workspace_engine: Final[WorkspaceEngine]
    _project_engine: Final[ProjectEngine]
    _inbox_task_engine: Final[InboxTaskEngine]
    _inbox_task_notion_manager: Final[InboxTaskNotionManager]
    _recurring_task_engine: Final[RecurringTaskEngine]
    _recurring_task_notion_manager: Final[RecurringTaskNotionManager]

    def __init__(
            self, time_provider: TimeProvider, workspace_engine: WorkspaceEngine,
            project_engine: ProjectEngine, inbox_task_engine: InboxTaskEngine,
            inbox_task_notion_manager: InboxTaskNotionManager, recurring_task_engine: RecurringTaskEngine,
            recurring_task_notion_manager: RecurringTaskNotionManager) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._workspace_engine = workspace_engine
        self._project_engine = project_engine
        self._inbox_task_engine = inbox_task_engine
        self._inbox_task_notion_manager = inbox_task_notion_manager
        self._recurring_task_engine = recurring_task_engine
        self._recurring_task_notion_manager = recurring_task_notion_manager

    def execute(self, args: Args) -> None:
        """Execute the command's action."""
        if args.project_key is not None:
            with self._project_engine.get_unit_of_work() as project_uow:
                project = project_uow.project_repository.load_by_key(args.project_key)
            project_ref_id = project.ref_id
        else:
            with self._workspace_engine.get_unit_of_work() as workspace_uow:
                workspace = workspace_uow.workspace_repository.load()
            project_ref_id = workspace.default_project_ref_id

        with self._inbox_task_engine.get_unit_of_work() as inbox_task_uow:
            inbox_task_collection = inbox_task_uow.inbox_task_collection_repository.load_by_project(project_ref_id)
        notion_inbox_task_collection = self._inbox_task_notion_manager.get_inbox_task_collection(inbox_task_collection)

        with self._recurring_task_engine.get_unit_of_work() as recurring_task_uow:
            recurring_task_collection = \
                recurring_task_uow.recurring_task_collection_repository.load_by_project(project_ref_id)

            recurring_task = RecurringTask.new_recurring_task(
                recurring_task_collection_ref_id=recurring_task_collection.ref_id,
                archived=False,
                name=args.name,
                period=args.period,
                the_type=args.the_type,
                gen_params=RecurringTaskGenParams(
                    project_ref_id=project.ref_id,
                    period=args.period,
                    eisen=args.eisen,
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
                created_time=self._time_provider.get_current_time())
            recurring_task = \
                recurring_task_uow.recurring_task_repository.create(recurring_task_collection, recurring_task)
            LOGGER.info("Applied local changes")
        notion_recurring_task = NotionRecurringTask.new_notion_row(recurring_task, None)
        self._recurring_task_notion_manager.upsert_recurring_task(
            recurring_task_collection, notion_recurring_task, notion_inbox_task_collection)
        LOGGER.info("Applied Notion changes")
