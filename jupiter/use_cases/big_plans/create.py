"""The command for creating a big plan."""
from dataclasses import dataclass
from typing import Final, Optional

from jupiter.domain.adate import ADate
from jupiter.domain.big_plans.big_plan import BigPlan
from jupiter.domain.big_plans.big_plan_status import BigPlanStatus
from jupiter.domain.big_plans.infra.big_plan_engine import BigPlanEngine
from jupiter.domain.big_plans.infra.big_plan_notion_manager import BigPlanNotionManager
from jupiter.domain.big_plans.notion_big_plan import NotionBigPlan
from jupiter.domain.entity_name import EntityName
from jupiter.domain.inbox_tasks.service.big_plan_ref_options_update_service \
    import InboxTaskBigPlanRefOptionsUpdateService
from jupiter.domain.inbox_tasks.infra.inbox_task_engine import InboxTaskEngine
from jupiter.domain.inbox_tasks.infra.inbox_task_notion_manager import InboxTaskNotionManager
from jupiter.domain.projects.infra.project_engine import ProjectEngine
from jupiter.domain.projects.project_key import ProjectKey
from jupiter.domain.workspaces.infra.workspace_engine import WorkspaceEngine
from jupiter.framework.use_case import UseCase
from jupiter.utils.time_provider import TimeProvider


class BigPlanCreateUseCase(UseCase['BigPlanCreateUseCase.Args', None]):
    """The command for creating a big plan."""

    @dataclass()
    class Args:
        """Args."""
        project_key: Optional[ProjectKey]
        name: EntityName
        due_date: Optional[ADate]

    _time_provider: Final[TimeProvider]
    _workspace_engine: Final[WorkspaceEngine]
    _project_engine: Final[ProjectEngine]
    _inbox_task_engine: Final[InboxTaskEngine]
    _inbox_task_notion_manager: Final[InboxTaskNotionManager]
    _big_plan_engine: Final[BigPlanEngine]
    _big_plan_notion_manager: Final[BigPlanNotionManager]

    def __init__(
            self, time_provider: TimeProvider, workspace_engine: WorkspaceEngine, projects_engine: ProjectEngine,
            inbox_task_engine: InboxTaskEngine, inbox_task_notion_manager: InboxTaskNotionManager,
            big_plan_engine: BigPlanEngine, big_plan_notion_manager: BigPlanNotionManager) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._workspace_engine = workspace_engine
        self._project_engine = projects_engine
        self._inbox_task_engine = inbox_task_engine
        self._inbox_task_notion_manager = inbox_task_notion_manager
        self._big_plan_engine = big_plan_engine
        self._big_plan_notion_manager = big_plan_notion_manager

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
        notion_inbox_tasks_collection = \
            self._inbox_task_notion_manager.load_inbox_task_collection(inbox_task_collection.ref_id)

        with self._big_plan_engine.get_unit_of_work() as big_plan_uow:
            big_plan_collection = big_plan_uow.big_plan_collection_repository.load_by_project(project_ref_id)

            big_plan = BigPlan.new_big_plan(
                big_plan_collection_ref_id=big_plan_collection.ref_id,
                archived=False,
                name=args.name,
                status=BigPlanStatus.ACCEPTED,
                due_date=args.due_date,
                created_time=self._time_provider.get_current_time())
            big_plan = big_plan_uow.big_plan_repository.create(big_plan_collection, big_plan)
        notion_big_plan = NotionBigPlan.new_notion_row(big_plan, None)
        self._big_plan_notion_manager.upsert_big_plan(
            big_plan_collection.ref_id, notion_big_plan, notion_inbox_tasks_collection)

        InboxTaskBigPlanRefOptionsUpdateService(
            self._big_plan_engine, self._inbox_task_engine, self._inbox_task_notion_manager).sync(big_plan_collection)
