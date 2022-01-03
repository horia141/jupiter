"""The command for creating a inbox task."""
import logging
from dataclasses import dataclass
from typing import Optional, Final

from jupiter.domain.adate import ADate
from jupiter.domain.big_plans.big_plan import BigPlan
from jupiter.domain.difficulty import Difficulty
from jupiter.domain.eisen import Eisen
from jupiter.domain.entity_name import EntityName
from jupiter.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.domain.inbox_tasks.inbox_task_name import InboxTaskName
from jupiter.domain.inbox_tasks.inbox_task_status import InboxTaskStatus
from jupiter.domain.inbox_tasks.infra.inbox_task_notion_manager import InboxTaskNotionManager
from jupiter.domain.inbox_tasks.notion_inbox_task import NotionInboxTask
from jupiter.domain.projects.project_key import ProjectKey
from jupiter.domain.storage_engine import StorageEngine
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.use_case import UseCase
from jupiter.utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class InboxTaskCreateUseCase(UseCase['InboxTaskCreateUseCase.Args', None]):
    """The command for creating a inbox task."""

    @dataclass()
    class Args:
        """Args."""
        project_key: Optional[ProjectKey]
        name: InboxTaskName
        big_plan_ref_id: Optional[EntityId]
        eisen: Optional[Eisen]
        difficulty: Optional[Difficulty]
        actionable_date: Optional[ADate]
        due_date: Optional[ADate]

    _time_provider: Final[TimeProvider]
    _storage_engine: Final[StorageEngine]
    _inbox_task_notion_manager: Final[InboxTaskNotionManager]

    def __init__(
            self, time_provider: TimeProvider, storage_engine: StorageEngine,
            inbox_task_notion_manager: InboxTaskNotionManager) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._storage_engine = storage_engine
        self._inbox_task_notion_manager = inbox_task_notion_manager

    def execute(self, args: Args) -> None:
        """Execute the command's action."""
        with self._storage_engine.get_unit_of_work() as uow:
            if args.project_key is not None:
                project = uow.project_repository.load_by_key(args.project_key)
                project_ref_id = project.ref_id
            else:
                workspace = uow.workspace_repository.load()
                project_ref_id = workspace.default_project_ref_id

            big_plan: Optional[BigPlan] = None
            big_plan_name: Optional[EntityName] = None
            if args.big_plan_ref_id:
                big_plan = uow.big_plan_repository.load_by_id(args.big_plan_ref_id)
                big_plan_name = big_plan.name

            inbox_task_collection = uow.inbox_task_collection_repository.load_by_project(project_ref_id)

            inbox_task = InboxTask.new_inbox_task(
                inbox_task_collection_ref_id=inbox_task_collection.ref_id,
                archived=False,
                name=args.name,
                status=InboxTaskStatus.ACCEPTED,
                big_plan=big_plan,
                eisen=args.eisen,
                difficulty=args.difficulty,
                actionable_date=args.actionable_date,
                due_date=args.due_date,
                created_time=self._time_provider.get_current_time())

            inbox_task = uow.inbox_task_repository.create(inbox_task_collection, inbox_task)
            LOGGER.info("Applied local changes")

        notion_inbox_task = NotionInboxTask.new_notion_row(inbox_task, NotionInboxTask.DirectInfo(big_plan_name))
        self._inbox_task_notion_manager.upsert_inbox_task(inbox_task_collection.ref_id, notion_inbox_task)
        LOGGER.info("Applied Notion changes")
