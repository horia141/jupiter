"""The command for clearing all branch and leaf type entities."""
from dataclasses import dataclass
from typing import Final

from jupiter.domain.big_plans.infra.big_plan_notion_manager import BigPlanNotionManager
from jupiter.domain.big_plans.service.remove_service import BigPlanRemoveService
from jupiter.domain.chores.infra.chore_notion_manager import ChoreNotionManager
from jupiter.domain.chores.service.remove_service import ChoreRemoveService
from jupiter.domain.habits.infra.habit_notion_manager import HabitNotionManager
from jupiter.domain.habits.service.remove_service import HabitRemoveService
from jupiter.domain.inbox_tasks.infra.inbox_task_notion_manager import (
    InboxTaskNotionManager,
)
from jupiter.domain.inbox_tasks.service.remove_service import InboxTaskRemoveService
from jupiter.domain.metrics.infra.metric_notion_manager import MetricNotionManager
from jupiter.domain.metrics.service.remove_service import MetricRemoveService
from jupiter.domain.persons.infra.person_notion_manager import PersonNotionManager
from jupiter.domain.persons.service.remove_service import PersonRemoveService
from jupiter.domain.projects.infra.project_notion_manager import ProjectNotionManager
from jupiter.domain.projects.project_key import ProjectKey
from jupiter.domain.push_integrations.email.infra.email_task_notion_manager import (
    EmailTaskNotionManager,
)
from jupiter.domain.push_integrations.email.service.remove_service import (
    EmailTaskRemoveService,
)
from jupiter.domain.push_integrations.group.infra.push_integration_group_notion_manager import (
    PushIntegrationGroupNotionManager,
)
from jupiter.domain.push_integrations.slack.infra.slack_task_notion_manager import (
    SlackTaskNotionManager,
)
from jupiter.domain.push_integrations.slack.service.remove_service import (
    SlackTaskRemoveService,
)
from jupiter.domain.remote.notion.token import NotionToken
from jupiter.domain.smart_lists.infra.smart_list_notion_manager import (
    SmartListNotionManager,
)
from jupiter.domain.smart_lists.service.remove_service import SmartListRemoveService
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.domain.timezone import Timezone
from jupiter.domain.vacations.infra.vacation_notion_manager import VacationNotionManager
from jupiter.domain.vacations.service.remove_service import VacationRemoveService
from jupiter.domain.workspaces.infra.workspace_notion_manager import (
    WorkspaceNotionManager,
)
from jupiter.domain.workspaces.workspace_name import WorkspaceName
from jupiter.framework.event import EventSource
from jupiter.framework.update_action import UpdateAction
from jupiter.framework.use_case import (
    MutationUseCaseInvocationRecorder,
    UseCaseArgsBase,
    ProgressReporter,
)
from jupiter.use_cases.infra.storage_engine import UseCaseStorageEngine
from jupiter.use_cases.infra.use_cases import (
    AppUseCaseContext,
    AppMutationUseCase,
)
from jupiter.utils.time_provider import TimeProvider


class ClearAllUseCase(AppMutationUseCase["ClearAllUseCase.Args", None]):
    """The command for clearing all branch and leaf type entities."""

    @dataclass(frozen=True)
    class Args(UseCaseArgsBase):
        """Args."""

        workspace_name: WorkspaceName
        workspace_timezone: Timezone
        default_project_key: ProjectKey
        notion_token: NotionToken

    _use_case_storage_engine: Final[UseCaseStorageEngine]
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
    _email_task_notion_manager: Final[EmailTaskNotionManager]

    def __init__(
        self,
        time_provider: TimeProvider,
        invocation_recorder: MutationUseCaseInvocationRecorder,
        storage_engine: DomainStorageEngine,
        use_case_storage_engine: UseCaseStorageEngine,
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
        slack_task_notion_manager: SlackTaskNotionManager,
        email_task_notion_manager: EmailTaskNotionManager,
    ) -> None:
        """Constructor."""
        super().__init__(time_provider, invocation_recorder, storage_engine)
        self._use_case_storage_engine = use_case_storage_engine
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
        self._push_integration_group_notion_manager = (
            push_integration_group_notion_manager
        )
        self._slack_task_notion_manager = slack_task_notion_manager
        self._email_task_notion_manager = email_task_notion_manager

    def _execute(
        self,
        progress_reporter: ProgressReporter,
        context: AppUseCaseContext,
        args: Args,
    ) -> None:
        """Execute the command's action."""
        workspace = context.workspace

        with self._storage_engine.get_unit_of_work() as uow:
            vacation_collection = uow.vacation_collection_repository.load_by_parent(
                workspace.ref_id
            )
            project_collection = uow.project_collection_repository.load_by_parent(
                workspace.ref_id
            )
            inbox_task_collection = uow.inbox_task_collection_repository.load_by_parent(
                workspace.ref_id
            )
            habit_collection = uow.habit_collection_repository.load_by_parent(
                workspace.ref_id
            )
            chore_collection = uow.chore_collection_repository.load_by_parent(
                workspace.ref_id
            )
            big_plan_collection = uow.big_plan_collection_repository.load_by_parent(
                workspace.ref_id
            )
            smart_list_collection = uow.smart_list_collection_repository.load_by_parent(
                workspace.ref_id
            )
            metric_collection = uow.metric_collection_repository.load_by_parent(
                workspace.ref_id
            )
            person_collection = uow.person_collection_repository.load_by_parent(
                workspace.ref_id
            )
            push_integration_group = (
                uow.push_integration_group_repository.load_by_parent(workspace.ref_id)
            )
            slack_task_collection = uow.slack_task_collection_repository.load_by_parent(
                push_integration_group.ref_id
            )
            email_task_collection = uow.email_task_collection_repository.load_by_parent(
                push_integration_group.ref_id
            )

        with progress_reporter.section("Resetting workspace"):
            with progress_reporter.start_updating_entity(
                "workspace", workspace.ref_id, str(workspace.name)
            ) as entity_reporter:
                with self._storage_engine.get_unit_of_work() as uow:
                    default_project = uow.project_repository.load_by_key(
                        project_collection.ref_id, args.default_project_key
                    )

                    workspace = workspace.update(
                        name=UpdateAction.change_to(args.workspace_name),
                        timezone=UpdateAction.change_to(args.workspace_timezone),
                        source=EventSource.CLI,
                        modification_time=self._time_provider.get_current_time(),
                    )
                    entity_reporter.mark_known_name(str(workspace.name))

                    workspace = workspace.change_default_project(
                        default_project_ref_id=default_project.ref_id,
                        source=EventSource.CLI,
                        modification_time=self._time_provider.get_current_time(),
                    )

                    uow.workspace_repository.save(workspace)
                    entity_reporter.mark_local_change()

                notion_workspace = self._workspace_notion_manager.load_workspace(
                    workspace.ref_id
                )
                notion_workspace = notion_workspace.join_with_entity(workspace)
                self._workspace_notion_manager.save_workspace(notion_workspace)
                entity_reporter.mark_remote_change()

        with progress_reporter.section("Clearing vacations"):
            with self._storage_engine.get_unit_of_work() as uow:
                all_vacations = uow.vacation_repository.find_all(
                    parent_ref_id=vacation_collection.ref_id, allow_archived=True
                )

            vacation_remove_service = VacationRemoveService(
                self._storage_engine, self._vacation_notion_manager
            )
            for vacation in all_vacations:
                vacation_remove_service.do_it(progress_reporter, vacation)

        with progress_reporter.section("Clearing habits"):
            with self._storage_engine.get_unit_of_work() as uow:
                all_habits = uow.habit_repository.find_all(
                    parent_ref_id=habit_collection.ref_id, allow_archived=True
                )
            habit_remove_service = HabitRemoveService(
                self._storage_engine,
                self._inbox_task_notion_manager,
                self._habit_notion_manager,
            )
            for habit in all_habits:
                habit_remove_service.remove(progress_reporter, habit.ref_id)

        with progress_reporter.section("Clearing chores"):
            with self._storage_engine.get_unit_of_work() as uow:
                all_chores = uow.chore_repository.find_all(
                    parent_ref_id=chore_collection.ref_id, allow_archived=True
                )
            chore_remove_service = ChoreRemoveService(
                self._storage_engine,
                self._inbox_task_notion_manager,
                self._chore_notion_manager,
            )
            for chore in all_chores:
                chore_remove_service.remove(progress_reporter, chore.ref_id)

        with progress_reporter.section("Clearing big plans"):
            with self._storage_engine.get_unit_of_work() as uow:
                all_big_plans = uow.big_plan_repository.find_all(
                    parent_ref_id=big_plan_collection.ref_id, allow_archived=True
                )
            big_plan_remove_service = BigPlanRemoveService(
                self._storage_engine,
                self._inbox_task_notion_manager,
                self._big_plan_notion_manager,
            )
            for big_plan in all_big_plans:
                big_plan_remove_service.remove(
                    progress_reporter, workspace, big_plan.ref_id
                )

        with progress_reporter.section("Clearing smart lists"):
            with self._storage_engine.get_unit_of_work() as uow:
                all_smart_lists = uow.smart_list_repository.find_all(
                    parent_ref_id=smart_list_collection.ref_id, allow_archived=True
                )
            smart_list_remove_service = SmartListRemoveService(
                self._storage_engine, self._smart_list_notion_manager
            )
            for smart_list in all_smart_lists:
                smart_list_remove_service.execute(
                    progress_reporter, smart_list_collection, smart_list
                )

        with progress_reporter.section("Clearing metrics"):
            with self._storage_engine.get_unit_of_work() as uow:
                all_metrics = uow.metric_repository.find_all(
                    parent_ref_id=metric_collection.ref_id, allow_archived=True
                )

                metric_collection = metric_collection.change_collection_project(
                    collection_project_ref_id=default_project.ref_id,
                    source=EventSource.CLI,
                    modified_time=self._time_provider.get_current_time(),
                )

                uow.metric_collection_repository.save(metric_collection)

            metric_remove_service = MetricRemoveService(
                self._storage_engine,
                self._inbox_task_notion_manager,
                self._metric_notion_manager,
            )
            for metric in all_metrics:
                metric_remove_service.execute(
                    progress_reporter, metric_collection, metric
                )

        with progress_reporter.section("Clearing person"):
            with self._storage_engine.get_unit_of_work() as uow:
                all_persons = uow.person_repository.find_all(
                    parent_ref_id=person_collection.ref_id, allow_archived=True
                )

                person_collection = person_collection.change_catch_up_project(
                    catch_up_project_ref_id=default_project.ref_id,
                    source=EventSource.CLI,
                    modified_time=self._time_provider.get_current_time(),
                )

                uow.person_collection_repository.save(person_collection)

            person_remove_service = PersonRemoveService(
                self._storage_engine,
                self._person_notion_manager,
                self._inbox_task_notion_manager,
            )
            for person in all_persons:
                person_remove_service.do_it(
                    progress_reporter, person_collection, person
                )

        with progress_reporter.section("Clearing Slack tasks"):
            with self._storage_engine.get_unit_of_work() as uow:

                all_slack_tasks = uow.slack_task_repository.find_all(
                    parent_ref_id=slack_task_collection.ref_id, allow_archived=True
                )
                slack_task_collection = slack_task_collection.change_generation_project(
                    generation_project_ref_id=default_project.ref_id,
                    source=EventSource.CLI,
                    modified_time=self._time_provider.get_current_time(),
                )

                uow.slack_task_collection_repository.save(slack_task_collection)

            slack_task_remove_service = SlackTaskRemoveService(
                self._storage_engine,
                self._inbox_task_notion_manager,
                self._slack_task_notion_manager,
            )
            for slack_task in all_slack_tasks:
                slack_task_remove_service.do_it(progress_reporter, slack_task)

        with progress_reporter.section("Clearing email tasks"):
            with self._storage_engine.get_unit_of_work() as uow:

                all_email_tasks = uow.email_task_repository.find_all(
                    parent_ref_id=email_task_collection.ref_id, allow_archived=True
                )
                email_task_collection = email_task_collection.change_generation_project(
                    generation_project_ref_id=default_project.ref_id,
                    source=EventSource.CLI,
                    modified_time=self._time_provider.get_current_time(),
                )

                uow.email_task_collection_repository.save(email_task_collection)

            email_task_remove_service = EmailTaskRemoveService(
                self._storage_engine,
                self._inbox_task_notion_manager,
                self._email_task_notion_manager,
            )
            for email_task in all_email_tasks:
                email_task_remove_service.do_it(progress_reporter, email_task)

        with progress_reporter.section("Clearing inbox tasks"):
            with self._storage_engine.get_unit_of_work() as uow:
                all_inbox_tasks = uow.inbox_task_repository.find_all(
                    parent_ref_id=inbox_task_collection.ref_id, allow_archived=True
                )
            inbox_task_remove_service = InboxTaskRemoveService(
                self._storage_engine, self._inbox_task_notion_manager
            )
            for inbox_task in all_inbox_tasks:
                inbox_task_remove_service.do_it(progress_reporter, inbox_task)

        with progress_reporter.section("Clearing use case invocation records"):
            with self._use_case_storage_engine.get_unit_of_work() as uow:
                uow.mutation_use_case_invocation_record_repository.clear_all()

        with progress_reporter.section("Setting the Notion API token"):
            with progress_reporter.start_updating_entity(
                "notion connection"
            ) as entity_reporter:
                with self._storage_engine.get_unit_of_work() as uow:
                    notion_connection = uow.notion_connection_repository.load_by_parent(
                        workspace.ref_id
                    )
                    entity_reporter.mark_known_entity_id(notion_connection.ref_id)
                    notion_connection = notion_connection.update_token(
                        args.notion_token,
                        EventSource.CLI,
                        self._time_provider.get_current_time(),
                    )
                    uow.notion_connection_repository.save(notion_connection)
                    entity_reporter.mark_local_change()
