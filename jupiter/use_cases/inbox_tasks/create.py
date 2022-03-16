"""The command for creating a inbox task."""
import logging
from dataclasses import dataclass
from typing import Optional, Final

from jupiter.domain.adate import ADate
from jupiter.domain.big_plans.big_plan import BigPlan
from jupiter.domain.difficulty import Difficulty
from jupiter.domain.eisen import Eisen
from jupiter.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.domain.inbox_tasks.inbox_task_name import InboxTaskName
from jupiter.domain.inbox_tasks.inbox_task_status import InboxTaskStatus
from jupiter.domain.inbox_tasks.infra.inbox_task_notion_manager import InboxTaskNotionManager
from jupiter.domain.inbox_tasks.notion_inbox_task import NotionInboxTask
from jupiter.domain.projects.project_key import ProjectKey
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.event import EventSource
from jupiter.framework.use_case import MutationUseCaseInvocationRecorder, UseCaseArgsBase
from jupiter.use_cases.infra.use_cases import AppMutationUseCase, AppUseCaseContext
from jupiter.utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class InboxTaskCreateUseCase(AppMutationUseCase['InboxTaskCreateUseCase.Args', None]):
    """The command for creating a inbox task."""

    @dataclass(frozen=True)
    class Args(UseCaseArgsBase):
        """Args."""
        project_key: Optional[ProjectKey]
        name: InboxTaskName
        big_plan_ref_id: Optional[EntityId]
        eisen: Optional[Eisen]
        difficulty: Optional[Difficulty]
        actionable_date: Optional[ADate]
        due_date: Optional[ADate]

    _inbox_task_notion_manager: Final[InboxTaskNotionManager]

    def __init__(
            self,
            time_provider: TimeProvider,
            invocation_recorder: MutationUseCaseInvocationRecorder,
            storage_engine: DomainStorageEngine,
            inbox_task_notion_manager: InboxTaskNotionManager) -> None:
        """Constructor."""
        super().__init__(time_provider, invocation_recorder, storage_engine)
        self._inbox_task_notion_manager = inbox_task_notion_manager

    def _execute(self, context: AppUseCaseContext, args: Args) -> None:
        """Execute the command's action."""
        workspace = context.workspace

        with self._storage_engine.get_unit_of_work() as uow:
            project_collection = uow.project_collection_repository.load_by_parent(workspace.ref_id)

            if args.project_key is not None:
                project = uow.project_repository.load_by_key(project_collection.ref_id, args.project_key)
                project_ref_id = project.ref_id
            else:
                project = uow.project_repository.load_by_id(workspace.default_project_ref_id)
                project_ref_id = workspace.default_project_ref_id

            big_plan: Optional[BigPlan] = None
            all_big_plans_map = {}
            if args.big_plan_ref_id:
                big_plan = uow.big_plan_repository.load_by_id(args.big_plan_ref_id)
                all_big_plans_map = {big_plan.ref_id: big_plan}

            inbox_task_collection = uow.inbox_task_collection_repository.load_by_parent(workspace.ref_id)

            inbox_task = InboxTask.new_inbox_task(
                inbox_task_collection_ref_id=inbox_task_collection.ref_id,
                archived=False,
                name=args.name,
                status=InboxTaskStatus.ACCEPTED,
                project_ref_id=project_ref_id,
                big_plan=big_plan,
                eisen=args.eisen,
                difficulty=args.difficulty,
                actionable_date=args.actionable_date,
                due_date=args.due_date,
                source=EventSource.CLI,
                created_time=self._time_provider.get_current_time())

            inbox_task = uow.inbox_task_repository.create(inbox_task)
            LOGGER.info("Applied local changes")

        direct_info = \
            NotionInboxTask.DirectInfo(all_projects_map={project.ref_id: project}, all_big_plans_map=all_big_plans_map)
        notion_inbox_task = NotionInboxTask.new_notion_entity(inbox_task, direct_info)
        self._inbox_task_notion_manager.upsert_leaf(inbox_task_collection.ref_id, notion_inbox_task, None)
        LOGGER.info("Applied Notion changes")
