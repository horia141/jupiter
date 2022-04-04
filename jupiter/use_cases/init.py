"""UseCase for initialising the workspace."""
import logging
from dataclasses import dataclass
from typing import Final

from jupiter.domain.big_plans.big_plan_collection import BigPlanCollection
from jupiter.domain.big_plans.infra.big_plan_notion_manager import BigPlanNotionManager
from jupiter.domain.big_plans.notion_big_plan_collection import NotionBigPlanCollection
from jupiter.domain.chores.chore_collection import ChoreCollection
from jupiter.domain.chores.infra.chore_notion_manager import ChoreNotionManager
from jupiter.domain.chores.notion_chore_collection import NotionChoreCollection
from jupiter.domain.habits.habit_collection import HabitCollection
from jupiter.domain.habits.infra.habit_notion_manager import HabitNotionManager
from jupiter.domain.habits.notion_habit_collection import NotionHabitCollection
from jupiter.domain.inbox_tasks.inbox_task_collection import InboxTaskCollection
from jupiter.domain.inbox_tasks.infra.inbox_task_notion_manager import InboxTaskNotionManager
from jupiter.domain.inbox_tasks.notion_inbox_task_collection import NotionInboxTaskCollection
from jupiter.domain.metrics.infra.metric_notion_manager import MetricNotionManager
from jupiter.domain.metrics.metric_collection import MetricCollection
from jupiter.domain.metrics.notion_metric_collection import NotionMetricCollection
from jupiter.domain.persons.infra.person_notion_manager import PersonNotionManager
from jupiter.domain.persons.notion_person_collection import NotionPersonCollection
from jupiter.domain.persons.person_collection import PersonCollection
from jupiter.domain.projects.infra.project_notion_manager import ProjectNotionManager
from jupiter.domain.projects.notion_project import NotionProject
from jupiter.domain.projects.notion_project_collection import NotionProjectCollection
from jupiter.domain.projects.project import Project
from jupiter.domain.projects.project_collection import ProjectCollection
from jupiter.domain.projects.project_key import ProjectKey
from jupiter.domain.projects.project_name import ProjectName
from jupiter.domain.projects.service.project_label_update_service import ProjectLabelUpdateService
from jupiter.domain.push_integrations.group.infra.push_integration_group_notion_manager import \
    PushIntegrationGroupNotionManager
from jupiter.domain.push_integrations.group.notion_push_integration_group import NotionPushIntegrationGroup
from jupiter.domain.push_integrations.group.push_integration_group import PushIntegrationGroup
from jupiter.domain.push_integrations.slack.infra.slack_task_notion_manager import SlackTaskNotionManager
from jupiter.domain.push_integrations.slack.notion_slack_task_collection import NotionSlackTaskCollection
from jupiter.domain.push_integrations.slack.slack_task_collection import SlackTaskCollection
from jupiter.domain.remote.notion.connection import NotionConnection
from jupiter.domain.remote.notion.space_id import NotionSpaceId
from jupiter.domain.remote.notion.token import NotionToken
from jupiter.domain.smart_lists.infra.smart_list_notion_manager import SmartListNotionManager
from jupiter.domain.smart_lists.notion_smart_list_collection import NotionSmartListCollection
from jupiter.domain.smart_lists.smart_list_collection import SmartListCollection
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.domain.timezone import Timezone
from jupiter.domain.vacations.infra.vacation_notion_manager import VacationNotionManager
from jupiter.domain.vacations.notion_vacation_collection import NotionVacationCollection
from jupiter.domain.vacations.vacation_collection import VacationCollection
from jupiter.domain.workspaces.infra.workspace_notion_manager import WorkspaceNotionManager
from jupiter.domain.workspaces.notion_workspace import NotionWorkspace
from jupiter.domain.workspaces.workspace import Workspace
from jupiter.domain.workspaces.workspace_name import WorkspaceName
from jupiter.framework.event import EventSource
from jupiter.framework.use_case import UseCaseArgsBase, MutationEmptyContextUseCase, EmptyContext
from jupiter.utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class InitUseCase(MutationEmptyContextUseCase['InitUseCase.Args', None]):
    """UseCase for initialising the workspace."""

    @dataclass(frozen=True)
    class Args(UseCaseArgsBase):
        """Args."""
        name: WorkspaceName
        timezone: Timezone
        notion_space_id: NotionSpaceId
        notion_token: NotionToken
        first_project_key: ProjectKey
        first_project_name: ProjectName

    _time_provider: Final[TimeProvider]
    _storage_engine: Final[DomainStorageEngine]
    _workspace_notion_manager: Final[WorkspaceNotionManager]
    _vacation_notion_manager: Final[VacationNotionManager]
    _project_notion_manager: Final[ProjectNotionManager]
    _inbox_task_notion_manager: Final[InboxTaskNotionManager]
    _habit_notion_manager: Final[HabitNotionManager]
    _chore_notion_manager: Final[ChoreNotionManager]
    _big_plan_notion_manager: Final[BigPlanNotionManager]
    _smart_list_notion_manager: Final[SmartListNotionManager]
    _metric_notion_manager: Final[MetricNotionManager]
    _person_notion_manager: Final[PersonNotionManager]
    _push_integration_group_notion_manager: Final[PushIntegrationGroupNotionManager]
    _slack_task_notion_manager: Final[SlackTaskNotionManager]

    def __init__(
            self,
            time_provider: TimeProvider,
            storage_engine: DomainStorageEngine,
            workspace_notion_manager: WorkspaceNotionManager,
            vacation_notion_manager: VacationNotionManager,
            project_notion_manager: ProjectNotionManager,
            inbox_task_notion_manager: InboxTaskNotionManager,
            habit_notion_manager: HabitNotionManager,
            chore_notion_manager: ChoreNotionManager,
            big_plan_notion_manager: BigPlanNotionManager,
            smart_list_notion_manager: SmartListNotionManager,
            metric_notion_manager: MetricNotionManager,
            person_notion_manager: PersonNotionManager,
            push_integration_group_notion_manager: PushIntegrationGroupNotionManager,
            slack_task_notion_manager: SlackTaskNotionManager) -> None:
        """Constructor."""
        super().__init__()
        self._time_provider = time_provider
        self._storage_engine = storage_engine
        self._workspace_notion_manager = workspace_notion_manager
        self._vacation_notion_manager = vacation_notion_manager
        self._project_notion_manager = project_notion_manager
        self._inbox_task_notion_manager = inbox_task_notion_manager
        self._habit_notion_manager = habit_notion_manager
        self._chore_notion_manager = chore_notion_manager
        self._big_plan_notion_manager = big_plan_notion_manager
        self._metric_notion_manager = metric_notion_manager
        self._smart_list_notion_manager = smart_list_notion_manager
        self._person_notion_manager = person_notion_manager
        self._push_integration_group_notion_manager = push_integration_group_notion_manager
        self._slack_task_notion_manager = slack_task_notion_manager

    def _execute(self, context: EmptyContext, args: Args) -> None:
        """Execute the command's action."""
        LOGGER.info("Creating workspace")
        with self._storage_engine.get_unit_of_work() as uow:
            new_workspace = \
                Workspace.new_workspace(
                    name=args.name, timezone=args.timezone,
                    source=EventSource.CLI, created_time=self._time_provider.get_current_time())
            new_workspace = uow.workspace_repository.create(new_workspace)

            new_notion_connection = NotionConnection.new_notion_connection(
                workspace_ref_id=new_workspace.ref_id, space_id=args.notion_space_id, token=args.notion_token,
                source=EventSource.CLI, created_time=self._time_provider.get_current_time())
            new_notion_connection = uow.notion_connection_repository.create(new_notion_connection)

            new_vacation_collection = VacationCollection.new_vacation_collection(
                workspace_ref_id=new_workspace.ref_id, source=EventSource.CLI,
                created_time=self._time_provider.get_current_time())
            new_vacation_collection = uow.vacation_collection_repository.create(new_vacation_collection)

            new_project_collection = ProjectCollection.new_project_collection(
                workspace_ref_id=new_workspace.ref_id, source=EventSource.CLI,
                created_time=self._time_provider.get_current_time())
            new_project_collection = uow.project_collection_repository.create(new_project_collection)

            new_default_project = \
                Project.new_project(
                    project_collection_ref_id=new_project_collection.ref_id, key=args.first_project_key,
                    name=args.first_project_name, source=EventSource.CLI,
                    created_time=self._time_provider.get_current_time())
            new_default_project = uow.project_repository.create(new_default_project)

            LOGGER.info("Created first project")
            new_workspace = \
                new_workspace.change_default_project(
                    default_project_ref_id=new_default_project.ref_id, source=EventSource.CLI,
                    modification_time=self._time_provider.get_current_time())
            uow.workspace_repository.save(new_workspace)

            new_inbox_task_collection = \
                InboxTaskCollection.new_inbox_task_collection(
                    workspace_ref_id=new_workspace.ref_id, source=EventSource.CLI,
                    created_time=self._time_provider.get_current_time())
            new_inbox_task_collection = uow.inbox_task_collection_repository.create(new_inbox_task_collection)

            new_habit_collection = \
                HabitCollection.new_habit_collection(
                    workspace_ref_id=new_workspace.ref_id, source=EventSource.CLI,
                    created_time=self._time_provider.get_current_time())
            new_habit_collection = \
                uow.habit_collection_repository.create(new_habit_collection)

            new_chore_collection = \
                ChoreCollection.new_chore_collection(
                    workspace_ref_id=new_workspace.ref_id, source=EventSource.CLI,
                    created_time=self._time_provider.get_current_time())
            new_chore_collection = \
                uow.chore_collection_repository.create(new_chore_collection)

            new_big_plan_collection = \
                BigPlanCollection.new_big_plan_collection(
                    workspace_ref_id=new_workspace.ref_id, source=EventSource.CLI,
                    created_time=self._time_provider.get_current_time())
            new_big_plan_collection = uow.big_plan_collection_repository.create(new_big_plan_collection)

            new_smart_list_collection = \
                SmartListCollection.new_smart_list_collection(
                    workspace_ref_id=new_workspace.ref_id, source=EventSource.CLI,
                    created_time=self._time_provider.get_current_time())
            new_smart_list_collection = uow.smart_list_collection_repository.create(new_smart_list_collection)

            new_metric_collection = \
                MetricCollection.new_metric_collection(
                    workspace_ref_id=new_workspace.ref_id,
                    collection_project_ref_id=new_default_project.ref_id,
                    source=EventSource.CLI,
                    created_time=self._time_provider.get_current_time())
            new_metric_collection = uow.metric_collection_repository.create(new_metric_collection)

            new_person_collection = \
                PersonCollection.new_person_collection(
                    workspace_ref_id=new_workspace.ref_id,
                    catch_up_project_ref_id=new_default_project.ref_id,
                    source=EventSource.CLI,
                    created_time=self._time_provider.get_current_time())
            new_person_collection = uow.person_collection_repository.create(new_person_collection)

            new_push_integration_group = \
                PushIntegrationGroup.new_push_integration_group(
                    workspace_ref_id=new_workspace.ref_id,
                    source=EventSource.CLI,
                    created_time=self._time_provider.get_current_time())
            new_push_integration_group = uow.push_integration_group_repository.create(new_push_integration_group)

            new_slack_task_collection = \
                SlackTaskCollection.new_slack_task_collection(
                    push_integration_group_ref_id=new_push_integration_group.ref_id,
                    generation_project_ref_id=new_default_project.ref_id,
                    source=EventSource.CLI,
                    created_time=self._time_provider.get_current_time())
            new_slack_task_collection = uow.slack_task_collection_repository.create(new_slack_task_collection)

        LOGGER.info("Applied local changes")

        new_notion_workspace = NotionWorkspace.new_notion_entity(new_workspace)
        new_notion_workspace = self._workspace_notion_manager.upsert_workspace(new_notion_workspace)

        LOGGER.info("Creating vacations structure")
        new_notion_vacation_collection = NotionVacationCollection.new_notion_entity(new_vacation_collection)
        self._vacation_notion_manager.upsert_trunk(new_notion_workspace, new_notion_vacation_collection)

        LOGGER.info("Creating projects structure")
        new_notion_project_collection = NotionProjectCollection.new_notion_entity(new_project_collection)
        self._project_notion_manager.upsert_trunk(new_notion_workspace, new_notion_project_collection)
        new_notion_default_project = NotionProject.new_notion_entity(new_default_project, None)
        self._project_notion_manager.upsert_leaf(new_project_collection.ref_id, new_notion_default_project, None)

        LOGGER.info("Creating inbox tasks structure")
        new_notion_inbox_task_collection = NotionInboxTaskCollection.new_notion_entity(new_inbox_task_collection)
        self._inbox_task_notion_manager.upsert_trunk(new_notion_workspace, new_notion_inbox_task_collection)

        LOGGER.info("Creating habits structure")
        new_notion_habit_collection = NotionHabitCollection.new_notion_entity(new_habit_collection)
        self._habit_notion_manager.upsert_trunk(new_notion_workspace, new_notion_habit_collection)

        LOGGER.info("Creating chores structure")
        new_notion_chore_collection = NotionChoreCollection.new_notion_entity(new_chore_collection)
        self._chore_notion_manager.upsert_trunk(new_notion_workspace, new_notion_chore_collection)

        LOGGER.info("Creating big plans structure")
        new_notion_big_plan_collection = NotionBigPlanCollection.new_notion_entity(new_big_plan_collection)
        self._big_plan_notion_manager.upsert_trunk(new_notion_workspace, new_notion_big_plan_collection)

        LOGGER.info("Creating lists structure")
        new_notion_smart_list_collection = NotionSmartListCollection.new_notion_entity(new_smart_list_collection)
        self._smart_list_notion_manager.upsert_trunk(new_notion_workspace, new_notion_smart_list_collection)

        LOGGER.info("Creating metrics structure")
        new_notion_metric_collection = NotionMetricCollection.new_notion_entity(new_metric_collection)
        self._metric_notion_manager.upsert_trunk(new_notion_workspace, new_notion_metric_collection)

        LOGGER.info("Creating the persons structure")
        new_notion_person_collection = NotionPersonCollection.new_notion_entity(new_person_collection)
        self._person_notion_manager.upsert_trunk(new_notion_workspace, new_notion_person_collection)

        LOGGER.info("Creating the push integration group structure")
        new_notion_push_integration_group = NotionPushIntegrationGroup.new_notion_entity(new_push_integration_group)
        self._push_integration_group_notion_manager.upsert_push_integration_group(
            new_notion_workspace, new_notion_push_integration_group)

        LOGGER.info("Creating the Slack task structure")
        new_notion_slack_task_collection = NotionSlackTaskCollection.new_notion_entity(new_slack_task_collection)
        self._slack_task_notion_manager.upsert_trunk(
            new_notion_push_integration_group, new_notion_slack_task_collection)

        ProjectLabelUpdateService(
            self._storage_engine,
            self._inbox_task_notion_manager,
            self._habit_notion_manager,
            self._chore_notion_manager,
            self._big_plan_notion_manager) \
            .sync(new_workspace, [new_default_project])

        LOGGER.info("Applied Notion changes")
