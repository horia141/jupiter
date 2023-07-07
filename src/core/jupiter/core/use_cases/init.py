"""UseCase for initialising the workspace."""
from dataclasses import dataclass
from typing import Final

from jupiter.core.domain.auth.auth import Auth
from jupiter.core.domain.auth.auth_token_ext import AuthTokenExt
from jupiter.core.domain.auth.infra.auth_token_stamper import AuthTokenStamper
from jupiter.core.domain.auth.password_new_plain import PasswordNewPlain
from jupiter.core.domain.auth.recovery_token_plain import RecoveryTokenPlain
from jupiter.core.domain.big_plans.big_plan_collection import BigPlanCollection
from jupiter.core.domain.chores.chore_collection import ChoreCollection
from jupiter.core.domain.email_address import EmailAddress
from jupiter.core.domain.features import (
    FeatureFlags,
)
from jupiter.core.domain.habits.habit_collection import HabitCollection
from jupiter.core.domain.inbox_tasks.inbox_task_collection import InboxTaskCollection
from jupiter.core.domain.metrics.metric_collection import MetricCollection
from jupiter.core.domain.persons.person_collection import PersonCollection
from jupiter.core.domain.projects.project import Project
from jupiter.core.domain.projects.project_collection import ProjectCollection
from jupiter.core.domain.projects.project_name import ProjectName
from jupiter.core.domain.push_integrations.email.email_task_collection import (
    EmailTaskCollection,
)
from jupiter.core.domain.push_integrations.group.push_integration_group import (
    PushIntegrationGroup,
)
from jupiter.core.domain.push_integrations.slack.slack_task_collection import (
    SlackTaskCollection,
)
from jupiter.core.domain.smart_lists.smart_list_collection import SmartListCollection
from jupiter.core.domain.storage_engine import DomainStorageEngine
from jupiter.core.domain.timezone import Timezone
from jupiter.core.domain.user.user import User
from jupiter.core.domain.user.user_name import UserName
from jupiter.core.domain.user_workspace_link.user_workspace_link import (
    UserWorkspaceLink,
)
from jupiter.core.domain.vacations.vacation_collection import VacationCollection
from jupiter.core.domain.workspaces.workspace import Workspace
from jupiter.core.domain.workspaces.workspace_name import WorkspaceName
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.secure import secure_class
from jupiter.core.framework.use_case import (
    ContextProgressReporter,
    MutationUseCaseInvocationRecorder,
    ProgressReporterFactory,
    UseCaseArgsBase,
    UseCaseResultBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppGuestMutationUseCase,
    AppGuestUseCaseContext,
)
from jupiter.core.utils.feature_flag_controls import infer_feature_flag_controls
from jupiter.core.utils.global_properties import GlobalProperties
from jupiter.core.utils.time_provider import TimeProvider


@dataclass
class InitArgs(UseCaseArgsBase):
    """Init use case arguments."""

    user_email_address: EmailAddress
    user_name: UserName
    user_timezone: Timezone
    auth_password: PasswordNewPlain
    auth_password_repeat: PasswordNewPlain
    workspace_name: WorkspaceName
    workspace_first_project_name: ProjectName
    workspace_feature_flags: FeatureFlags


@dataclass
class InitResult(UseCaseResultBase):
    """Init use case result."""

    new_user: User
    new_workspace: Workspace
    auth_token_ext: AuthTokenExt
    recovery_token: RecoveryTokenPlain


@secure_class
class InitUseCase(AppGuestMutationUseCase[InitArgs, InitResult]):
    """UseCase for initialising the workspace."""

    _global_properties: Final[GlobalProperties]

    def __init__(
        self,
        time_provider: TimeProvider,
        invocation_recorder: MutationUseCaseInvocationRecorder,
        progress_reporter_factory: ProgressReporterFactory[AppGuestUseCaseContext],
        auth_token_stamper: AuthTokenStamper,
        storage_engine: DomainStorageEngine,
        global_properties: GlobalProperties,
    ) -> None:
        """Constructor."""
        super().__init__(
            time_provider,
            invocation_recorder,
            progress_reporter_factory,
            auth_token_stamper,
            storage_engine,
        )
        self._global_properties = global_properties

    async def _execute(
        self,
        progress_reporter: ContextProgressReporter,
        context: AppGuestUseCaseContext,
        args: InitArgs,
    ) -> InitResult:
        """Execute the command's action."""
        feature_flags_controls = infer_feature_flag_controls(self._global_properties)

        async with progress_reporter.section("Creating Local"):
            async with self._storage_engine.get_unit_of_work() as uow:
                async with progress_reporter.start_creating_entity(
                    "user", str(args.user_name)
                ) as entity_reporter:
                    new_user = User.new_user(
                        email_address=args.user_email_address,
                        name=args.user_name,
                        timezone=args.user_timezone,
                        source=EventSource.CLI,
                        created_time=self._time_provider.get_current_time(),
                    )
                    new_user = await uow.user_repository.create(new_user)
                    await entity_reporter.mark_known_entity_id(new_user.ref_id)
                    await entity_reporter.mark_local_change()

                    new_auth, new_recovery_token = Auth.new_auth(
                        user_ref_id=new_user.ref_id,
                        password=args.auth_password,
                        password_repeat=args.auth_password_repeat,
                        source=EventSource.CLI,
                        created_time=self._time_provider.get_current_time(),
                    )
                    new_auth = await uow.auth_repository.create(new_auth)
                    await entity_reporter.mark_other_progress("auth")

                async with progress_reporter.start_creating_entity(
                    "workspace",
                    str(args.workspace_name),
                ) as entity_reporter:
                    new_workspace = Workspace.new_workspace(
                        name=args.workspace_name,
                        feature_flag_controls=feature_flags_controls,
                        feature_flags=args.workspace_feature_flags,
                        source=EventSource.CLI,
                        created_time=self._time_provider.get_current_time(),
                    )
                    new_workspace = await uow.workspace_repository.create(new_workspace)
                    await entity_reporter.mark_known_entity_id(new_workspace.ref_id)
                    await entity_reporter.mark_local_change()

                    new_vacation_collection = (
                        VacationCollection.new_vacation_collection(
                            workspace_ref_id=new_workspace.ref_id,
                            source=EventSource.CLI,
                            created_time=self._time_provider.get_current_time(),
                        )
                    )
                    new_vacation_collection = (
                        await uow.vacation_collection_repository.create(
                            new_vacation_collection,
                        )
                    )
                    await entity_reporter.mark_other_progress("vacations collection")

                    new_project_collection = ProjectCollection.new_project_collection(
                        workspace_ref_id=new_workspace.ref_id,
                        source=EventSource.CLI,
                        created_time=self._time_provider.get_current_time(),
                    )
                    new_project_collection = (
                        await uow.project_collection_repository.create(
                            new_project_collection,
                        )
                    )
                    await entity_reporter.mark_other_progress("projects collection")

                    new_default_project = Project.new_project(
                        project_collection_ref_id=new_project_collection.ref_id,
                        name=args.workspace_first_project_name,
                        source=EventSource.CLI,
                        created_time=self._time_provider.get_current_time(),
                    )
                    new_default_project = await uow.project_repository.create(
                        new_default_project,
                    )

                    new_workspace = new_workspace.change_default_project(
                        default_project_ref_id=new_default_project.ref_id,
                        source=EventSource.CLI,
                        modification_time=self._time_provider.get_current_time(),
                    )
                    await uow.workspace_repository.save(new_workspace)
                    await entity_reporter.mark_other_progress("change default")

                    new_inbox_task_collection = (
                        InboxTaskCollection.new_inbox_task_collection(
                            workspace_ref_id=new_workspace.ref_id,
                            source=EventSource.CLI,
                            created_time=self._time_provider.get_current_time(),
                        )
                    )
                    new_inbox_task_collection = (
                        await uow.inbox_task_collection_repository.create(
                            new_inbox_task_collection,
                        )
                    )
                    await entity_reporter.mark_other_progress("inbox tasks collection")

                    new_habit_collection = HabitCollection.new_habit_collection(
                        workspace_ref_id=new_workspace.ref_id,
                        source=EventSource.CLI,
                        created_time=self._time_provider.get_current_time(),
                    )
                    new_habit_collection = await uow.habit_collection_repository.create(
                        new_habit_collection,
                    )
                    await entity_reporter.mark_other_progress("habits collection")

                    new_chore_collection = ChoreCollection.new_chore_collection(
                        workspace_ref_id=new_workspace.ref_id,
                        source=EventSource.CLI,
                        created_time=self._time_provider.get_current_time(),
                    )
                    new_chore_collection = await uow.chore_collection_repository.create(
                        new_chore_collection,
                    )
                    await entity_reporter.mark_other_progress("chores collection")

                    new_big_plan_collection = BigPlanCollection.new_big_plan_collection(
                        workspace_ref_id=new_workspace.ref_id,
                        source=EventSource.CLI,
                        created_time=self._time_provider.get_current_time(),
                    )
                    new_big_plan_collection = (
                        await uow.big_plan_collection_repository.create(
                            new_big_plan_collection,
                        )
                    )
                    await entity_reporter.mark_other_progress("big plans collection")

                    new_smart_list_collection = (
                        SmartListCollection.new_smart_list_collection(
                            workspace_ref_id=new_workspace.ref_id,
                            source=EventSource.CLI,
                            created_time=self._time_provider.get_current_time(),
                        )
                    )
                    new_smart_list_collection = (
                        await uow.smart_list_collection_repository.create(
                            new_smart_list_collection,
                        )
                    )
                    await entity_reporter.mark_other_progress("smart lists collection")

                    new_metric_collection = MetricCollection.new_metric_collection(
                        workspace_ref_id=new_workspace.ref_id,
                        collection_project_ref_id=new_default_project.ref_id,
                        source=EventSource.CLI,
                        created_time=self._time_provider.get_current_time(),
                    )
                    new_metric_collection = (
                        await uow.metric_collection_repository.create(
                            new_metric_collection,
                        )
                    )
                    await entity_reporter.mark_other_progress("metrics collection")

                    new_person_collection = PersonCollection.new_person_collection(
                        workspace_ref_id=new_workspace.ref_id,
                        catch_up_project_ref_id=new_default_project.ref_id,
                        source=EventSource.CLI,
                        created_time=self._time_provider.get_current_time(),
                    )
                    new_person_collection = (
                        await uow.person_collection_repository.create(
                            new_person_collection,
                        )
                    )
                    await entity_reporter.mark_other_progress("persons collection")

                    new_push_integration_group = (
                        PushIntegrationGroup.new_push_integration_group(
                            workspace_ref_id=new_workspace.ref_id,
                            source=EventSource.CLI,
                            created_time=self._time_provider.get_current_time(),
                        )
                    )
                    new_push_integration_group = (
                        await uow.push_integration_group_repository.create(
                            new_push_integration_group,
                        )
                    )
                    await entity_reporter.mark_other_progress("push integrations group")

                    new_slack_task_collection = SlackTaskCollection.new_slack_task_collection(
                        push_integration_group_ref_id=new_push_integration_group.ref_id,
                        generation_project_ref_id=new_default_project.ref_id,
                        source=EventSource.CLI,
                        created_time=self._time_provider.get_current_time(),
                    )
                    new_slack_task_collection = (
                        await uow.slack_task_collection_repository.create(
                            new_slack_task_collection,
                        )
                    )
                    await entity_reporter.mark_other_progress("Slack task collection")

                    new_email_task_collection = EmailTaskCollection.new_email_task_collection(
                        push_integration_group_ref_id=new_push_integration_group.ref_id,
                        generation_project_ref_id=new_default_project.ref_id,
                        source=EventSource.CLI,
                        created_time=self._time_provider.get_current_time(),
                    )
                    new_email_task_collection = (
                        await uow.email_task_collection_repository.create(
                            new_email_task_collection,
                        )
                    )
                    await entity_reporter.mark_other_progress("email task collection")

                async with progress_reporter.start_creating_entity(
                    "user workspace link", f"{new_user.name} <> {new_workspace.name}"
                ) as entity_reporter:
                    new_user_workspace_link = UserWorkspaceLink.new_user_workspace_link(
                        user_ref_id=new_user.ref_id,
                        workspace_ref_id=new_workspace.ref_id,
                        source=EventSource.CLI,
                        created_time=self._time_provider.get_current_time(),
                    )
                    new_user_workspace_link = (
                        await uow.user_workspace_link_repository.create(
                            new_user_workspace_link
                        )
                    )
                    await entity_reporter.mark_known_entity_id(
                        new_user_workspace_link.ref_id
                    )
                    await entity_reporter.mark_local_change()

        auth_token = self._auth_token_stamper.stamp_for_general(new_user)

        return InitResult(
            new_user=new_user,
            new_workspace=new_workspace,
            auth_token_ext=auth_token.to_ext(),
            recovery_token=new_recovery_token,
        )
