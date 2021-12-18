"""The command for creating a inbox task."""
import logging
from dataclasses import dataclass
from typing import Optional, List, Final

from domain.adate import ADate
from domain.big_plans.infra.big_plan_engine import BigPlanEngine
from domain.difficulty import Difficulty
from domain.eisen import Eisen
from domain.entity_name import EntityName
from domain.inbox_tasks.inbox_task import InboxTask
from domain.inbox_tasks.inbox_task_status import InboxTaskStatus
from domain.inbox_tasks.infra.inbox_task_engine import InboxTaskEngine
from domain.inbox_tasks.infra.inbox_task_notion_manager import InboxTaskNotionManager
from domain.inbox_tasks.notion_inbox_task import NotionInboxTask
from domain.projects.infra.project_engine import ProjectEngine
from domain.projects.project_key import ProjectKey
from domain.workspaces.infra.workspace_engine import WorkspaceEngine
from models.framework import Command, EntityId
from utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class InboxTaskCreateCommand(Command['InboxTaskCreateCommand.Args', None]):
    """The command for creating a inbox task."""

    @dataclass()
    class Args:
        """Args."""
        project_key: Optional[ProjectKey]
        name: EntityName
        big_plan_ref_id: Optional[EntityId]
        eisen: List[Eisen]
        difficulty: Optional[Difficulty]
        actionable_date: Optional[ADate]
        due_date: Optional[ADate]

    _time_provider: Final[TimeProvider]
    _workspace_engine: Final[WorkspaceEngine]
    _project_engine: Final[ProjectEngine]
    _inbox_task_engine: Final[InboxTaskEngine]
    _inbox_task_notion_manager: Final[InboxTaskNotionManager]
    _big_plan_engine: Final[BigPlanEngine]

    def __init__(
            self, time_provider: TimeProvider, workspace_engine: WorkspaceEngine, project_engine: ProjectEngine,
            inbox_task_engine: InboxTaskEngine, inbox_task_notion_manager: InboxTaskNotionManager,
            big_plan_engine: BigPlanEngine) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._workspace_engine = workspace_engine
        self._project_engine = project_engine
        self._inbox_task_engine = inbox_task_engine
        self._inbox_task_notion_manager = inbox_task_notion_manager
        self._big_plan_engine = big_plan_engine

    def execute(self, args: Args) -> None:
        """Execute the command's action."""
        if args.project_key is not None:
            with self._project_engine.get_unit_of_work() as project_uow:
                project = project_uow.project_repository.get_by_key(args.project_key)
            project_ref_id = project.ref_id
        else:
            with self._workspace_engine.get_unit_of_work() as workspace_uow:
                workspace = workspace_uow.workspace_repository.find()
            project_ref_id = workspace.default_project_ref_id

        big_plan_name: Optional[EntityName] = None
        if args.big_plan_ref_id:
            with self._big_plan_engine.get_unit_of_work() as big_plan_uow:
                big_plan = big_plan_uow.big_plan_repository.load_by_id(args.big_plan_ref_id)
                big_plan_name = big_plan.name

        with self._inbox_task_engine.get_unit_of_work() as inbox_task_uow:
            inbox_task_collection = inbox_task_uow.inbox_task_collection_repository.load_by_project(project_ref_id)

            inbox_task = InboxTask.new_inbox_task(
                inbox_task_collection_ref_id=inbox_task_collection.ref_id,
                archived=False,
                name=args.name,
                status=InboxTaskStatus.ACCEPTED,
                big_plan_ref_id=args.big_plan_ref_id,
                eisen=args.eisen,
                difficulty=args.difficulty,
                actionable_date=args.actionable_date,
                due_date=args.due_date,
                created_time=self._time_provider.get_current_time())

            inbox_task = inbox_task_uow.inbox_task_repository.create(inbox_task_collection, inbox_task)
            LOGGER.info("Applied local changes")
        notion_inbox_task = NotionInboxTask.new_notion_row(inbox_task, NotionInboxTask.DirectInfo(big_plan_name))
        self._inbox_task_notion_manager.upsert_inbox_task(inbox_task_collection, notion_inbox_task)
        LOGGER.info("Applied Notion changes")
