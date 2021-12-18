"""The command for archiving a project."""
import logging
from dataclasses import dataclass
from typing import Final

from domain.big_plans.infra.big_plan_engine import BigPlanEngine
from domain.big_plans.infra.big_plan_notion_manager import BigPlanNotionManager
from domain.errors import ServiceError
from domain.inbox_tasks.infra.inbox_task_engine import InboxTaskEngine
from domain.inbox_tasks.infra.inbox_task_notion_manager import InboxTaskNotionManager
from domain.metrics.infra.metric_engine import MetricEngine
from domain.prm.infra.prm_engine import PrmEngine
from domain.projects.infra.project_engine import ProjectEngine
from domain.projects.infra.project_notion_manager import ProjectNotionManager
from domain.projects.project_key import ProjectKey
from domain.recurring_tasks.infra.recurring_task_engine import RecurringTaskEngine
from domain.recurring_tasks.infra.recurring_task_notion_manager import RecurringTaskNotionManager
from domain.workspaces.infra.workspace_engine import WorkspaceEngine
from models.framework import Command
from utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class ProjectArchiveCommand(Command['ProjectArchiveCommand.Args', None]):
    """The command for archiving a project."""

    @dataclass()
    class Args:
        """Args."""
        key: ProjectKey

    _time_provider: Final[TimeProvider]
    _workspace_engine: Final[WorkspaceEngine]
    _project_engine: Final[ProjectEngine]
    _project_notion_manager: Final[ProjectNotionManager]
    _inbox_task_engine: Final[InboxTaskEngine]
    _inbox_task_notion_manager: Final[InboxTaskNotionManager]
    _recurring_task_engine: Final[RecurringTaskEngine]
    _recurring_task_notion_manager: Final[RecurringTaskNotionManager]
    _big_plan_engine: Final[BigPlanEngine]
    _big_plan_notion_manager: Final[BigPlanNotionManager]
    _metric_engine: Final[MetricEngine]
    _prm_engine: Final[PrmEngine]

    def __init__(
            self, time_provider: TimeProvider, workspace_engine: WorkspaceEngine, project_engine: ProjectEngine,
            project_notion_manager: ProjectNotionManager,
            inbox_task_engine: InboxTaskEngine, inbox_task_notion_manager: InboxTaskNotionManager,
            recurring_task_engine: RecurringTaskEngine, recurring_task_notion_manager: RecurringTaskNotionManager,
            big_plan_engine: BigPlanEngine, big_plan_notion_manager: BigPlanNotionManager,
            metric_engine: MetricEngine, prm_engine: PrmEngine) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._workspace_engine = workspace_engine
        self._project_engine = project_engine
        self._project_notion_manager = project_notion_manager
        self._inbox_task_engine = inbox_task_engine
        self._inbox_task_notion_manager = inbox_task_notion_manager
        self._recurring_task_engine = recurring_task_engine
        self._recurring_task_notion_manager = recurring_task_notion_manager
        self._big_plan_engine = big_plan_engine
        self._big_plan_notion_manager = big_plan_notion_manager
        self._metric_engine = metric_engine
        self._prm_engine = prm_engine

    def execute(self, args: Args) -> None:
        """Execute the command's action."""
        with self._project_engine.get_unit_of_work() as project_uow:
            project = project_uow.project_repository.get_by_key(args.key)

        with self._workspace_engine.get_unit_of_work() as workspace_uow:
            workspace = workspace_uow.workspace_repository.find()
        if workspace.default_project_ref_id == project.ref_id:
            raise ServiceError("Cannot archive project because it is the default workspace one")
        with self._metric_engine.get_unit_of_work() as metric_uow:
            metrics = metric_uow.metric_repository.find_all(allow_archived=True)
        for metric in metrics:
            if metric.collection_params is not None and metric.collection_params.project_ref_id == project.ref_id:
                raise ServiceError(
                    "Cannot archive project because it is the collection project " +
                    f"for metric '{metric.name} archived={metric.archived}'")
        with self._prm_engine.get_unit_of_work() as prm_uow:
            prm_database = prm_uow.prm_database_repository.find()
        if prm_database.catch_up_project_ref_id == project.ref_id:
            raise ServiceError("Cannot archive project because it is the collection project for the PRM database")

        with self._inbox_task_engine.get_unit_of_work() as inbox_task_uow:
            inbox_task_collection = inbox_task_uow.inbox_task_collection_repository.load_by_project(project.ref_id)
            for inbox_task in inbox_task_uow.inbox_task_repository.find_all(
                    filter_inbox_task_collection_ref_ids=[inbox_task_collection.ref_id]):
                inbox_task.mark_archived(self._time_provider.get_current_time())
                inbox_task_uow.inbox_task_repository.save(inbox_task)
        self._inbox_task_notion_manager.remove_inbox_tasks_collection(inbox_task_collection)

        with self._big_plan_engine.get_unit_of_work() as big_plan_uow:
            big_plan_collection = big_plan_uow.big_plan_collection_repository.load_by_project(project.ref_id)
            for big_plan in big_plan_uow.big_plan_repository.find_all(
                    filter_big_plan_collection_ref_ids=[big_plan_collection.ref_id]):
                big_plan.mark_archived(self._time_provider.get_current_time())
                big_plan_uow.big_plan_repository.save(big_plan)
        self._big_plan_notion_manager.remove_big_plans_collection(big_plan_collection)

        with self._recurring_task_engine.get_unit_of_work() as recurring_task_uow:
            recurring_task_collection = \
                recurring_task_uow.recurring_task_collection_repository.load_by_project(project.ref_id)
            for recurring_task in recurring_task_uow.recurring_task_repository.find_all(
                    filter_recurring_task_collection_ref_ids=[recurring_task_collection.ref_id]):
                recurring_task.mark_archived(self._time_provider.get_current_time())
                recurring_task_uow.recurring_task_repository.save(recurring_task)
        self._recurring_task_notion_manager.remove_recurring_tasks_collection(recurring_task_collection)

        project.mark_archived(self._time_provider.get_current_time())

        with self._project_engine.get_unit_of_work() as project_uow_s:
            project_uow_s.project_repository.save(project)
        LOGGER.info("Applied local changes")
        self._project_notion_manager.archive(project)
        LOGGER.info("Applied Notion changes")
