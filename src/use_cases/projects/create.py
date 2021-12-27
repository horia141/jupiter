"""The command for creating a project."""
import logging
from dataclasses import dataclass
from typing import Final

from domain.big_plans.big_plan_collection import BigPlanCollection
from domain.big_plans.infra.big_plan_engine import BigPlanEngine
from domain.big_plans.infra.big_plan_notion_manager import BigPlanNotionManager
from domain.big_plans.notion_big_plan_collection import NotionBigPlanCollection
from domain.entity_name import EntityName
from domain.inbox_tasks.inbox_task_collection import InboxTaskCollection
from domain.inbox_tasks.infra.inbox_task_engine import InboxTaskEngine
from domain.inbox_tasks.infra.inbox_task_notion_manager import InboxTaskNotionManager
from domain.inbox_tasks.notion_inbox_task_collection import NotionInboxTaskCollection
from domain.projects.infra.project_engine import ProjectEngine
from domain.projects.infra.project_notion_manager import ProjectNotionManager
from domain.projects.notion_project import NotionProject
from domain.projects.project import Project
from domain.projects.project_key import ProjectKey
from domain.recurring_tasks.infra.recurring_task_engine import RecurringTaskEngine
from domain.recurring_tasks.infra.recurring_task_notion_manager import RecurringTaskNotionManager
from domain.recurring_tasks.notion_recurring_task_collection import NotionRecurringTaskCollection
from domain.recurring_tasks.recurring_task_collection import RecurringTaskCollection
from framework.use_case import UseCase
from utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class ProjectCreateUseCase(UseCase['ProjectCreateUseCase.Args', None]):
    """The command for creating a project."""

    @dataclass()
    class Args:
        """Args."""
        key: ProjectKey
        name: EntityName

    _time_provider: Final[TimeProvider]
    _project_engine: Final[ProjectEngine]
    _project_notion_manager: Final[ProjectNotionManager]
    _inbox_task_engine: Final[InboxTaskEngine]
    _inbox_task_notion_manager: Final[InboxTaskNotionManager]
    _recurring_task_engine: Final[RecurringTaskEngine]
    _recurring_task_notion_manager: Final[RecurringTaskNotionManager]
    _big_plan_engine: Final[BigPlanEngine]
    _big_plan_notion_manager: Final[BigPlanNotionManager]

    def __init__(
            self, time_provider: TimeProvider, project_engine: ProjectEngine,
            project_notion_manager: ProjectNotionManager,
            inbox_task_engine: InboxTaskEngine, inbox_task_notion_manager: InboxTaskNotionManager,
            recurring_task_engine: RecurringTaskEngine, recurring_task_notion_manager: RecurringTaskNotionManager,
            big_plan_engine: BigPlanEngine, big_plan_notion_manager: BigPlanNotionManager) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._project_engine = project_engine
        self._project_notion_manager = project_notion_manager
        self._inbox_task_engine = inbox_task_engine
        self._inbox_task_notion_manager = inbox_task_notion_manager
        self._recurring_task_engine = recurring_task_engine
        self._recurring_task_notion_manager = recurring_task_notion_manager
        self._big_plan_engine = big_plan_engine
        self._big_plan_notion_manager = big_plan_notion_manager

    def execute(self, args: Args) -> None:
        """Execute the command's action."""
        new_project = Project.new_project(args.key, args.name, self._time_provider.get_current_time())
        with self._project_engine.get_unit_of_work() as project_uow:
            new_project = project_uow.project_repository.create(new_project)
        LOGGER.info("Applied local changes")
        new_notion_project = NotionProject.new_notion_row(new_project)
        new_notion_project = self._project_notion_manager.upsert_project(new_notion_project)
        LOGGER.info("Applied Notion changes")
        new_inbox_task_collection = InboxTaskCollection.new_inbox_task_collection(
            new_project.ref_id, self._time_provider.get_current_time())
        with self._inbox_task_engine.get_unit_of_work() as inbox_task_uow:
            new_inbox_task_collection = \
                inbox_task_uow.inbox_task_collection_repository.create(new_inbox_task_collection)
        new_notion_inbox_task_collection = \
            NotionInboxTaskCollection.new_notion_row(new_inbox_task_collection)
        self._inbox_task_notion_manager.upsert_inbox_task_collection(
            new_notion_project, new_notion_inbox_task_collection)

        new_recurring_task_collection = RecurringTaskCollection.new_recurring_task_collection(
            new_project.ref_id, self._time_provider.get_current_time())
        with self._recurring_task_engine.get_unit_of_work() as recurring_task_uow:
            new_recurring_task_collection = \
                recurring_task_uow.recurring_task_collection_repository.create(new_recurring_task_collection)
        new_notion_recurring_task_collection = \
            NotionRecurringTaskCollection.new_notion_row(new_recurring_task_collection)
        self._recurring_task_notion_manager.upsert_recurring_task_collection(
            new_notion_project, new_notion_recurring_task_collection)

        new_big_plan_collection = BigPlanCollection.new_big_plan_collection(
            new_project.ref_id, self._time_provider.get_current_time())
        with self._big_plan_engine.get_unit_of_work() as uow:
            new_big_plan_collection = uow.big_plan_collection_repository.create(new_big_plan_collection)
        new_notion_big_plan_collection = NotionBigPlanCollection.new_notion_row(new_big_plan_collection)
        self._big_plan_notion_manager.upsert_big_plan_collection(
            new_notion_project, new_notion_big_plan_collection)
