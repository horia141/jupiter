"""UseCase for initialising the workspace."""

from jupiter.core.domain.auth.auth import Auth
from jupiter.core.domain.auth.auth_token_ext import AuthTokenExt
from jupiter.core.domain.auth.password_new_plain import PasswordNewPlain
from jupiter.core.domain.auth.recovery_token_plain import RecoveryTokenPlain
from jupiter.core.domain.big_plans.big_plan_collection import BigPlanCollection
from jupiter.core.domain.chores.chore_collection import ChoreCollection
from jupiter.core.domain.core.difficulty import Difficulty
from jupiter.core.domain.core.eisen import Eisen
from jupiter.core.domain.core.email_address import EmailAddress
from jupiter.core.domain.core.notes.note_collection import NoteCollection
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.domain.core.timezone import Timezone
from jupiter.core.domain.docs.doc_collection import DocCollection
from jupiter.core.domain.features import (
    UserFeature,
    WorkspaceFeature,
)
from jupiter.core.domain.gamification.score_log import ScoreLog
from jupiter.core.domain.gc.gc_log import GCLog
from jupiter.core.domain.gen.gen_log import GenLog
from jupiter.core.domain.habits.habit_collection import HabitCollection
from jupiter.core.domain.inbox_tasks.inbox_task_collection import InboxTaskCollection
from jupiter.core.domain.journals.journal_collection import JournalCollection
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
from jupiter.core.domain.user.user import User
from jupiter.core.domain.user.user_name import UserName
from jupiter.core.domain.user_workspace_link.user_workspace_link import (
    UserWorkspaceLink,
)
from jupiter.core.domain.vacations.vacation_collection import VacationCollection
from jupiter.core.domain.workspaces.workspace import Workspace
from jupiter.core.domain.workspaces.workspace_name import WorkspaceName
from jupiter.core.framework.secure import secure_class
from jupiter.core.framework.use_case import (
    ProgressReporter,
)
from jupiter.core.framework.use_case_io import (
    UseCaseArgsBase,
    UseCaseResultBase,
    use_case_args,
    use_case_result,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppGuestMutationUseCase,
    AppGuestMutationUseCaseContext,
)
from jupiter.core.utils.feature_flag_controls import infer_feature_flag_controls


@use_case_args
class InitArgs(UseCaseArgsBase):
    """Init use case arguments."""

    user_email_address: EmailAddress
    user_name: UserName
    user_timezone: Timezone
    user_feature_flags: set[UserFeature]
    auth_password: PasswordNewPlain
    auth_password_repeat: PasswordNewPlain
    workspace_name: WorkspaceName
    workspace_first_project_name: ProjectName
    workspace_feature_flags: set[WorkspaceFeature]


@use_case_result
class InitResult(UseCaseResultBase):
    """Init use case result."""

    new_user: User
    new_workspace: Workspace
    auth_token_ext: AuthTokenExt
    recovery_token: RecoveryTokenPlain


@secure_class
class InitUseCase(AppGuestMutationUseCase[InitArgs, InitResult]):
    """UseCase for initialising the workspace."""

    async def _execute(
        self,
        progress_reporter: ProgressReporter,
        context: AppGuestMutationUseCaseContext,
        args: InitArgs,
    ) -> InitResult:
        """Execute the command's action."""
        (
            user_feature_flags_controls,
            workspace_feature_flags_controls,
        ) = infer_feature_flag_controls(self._global_properties)

        user_feature_flags = {}
        for user_feature in UserFeature:
            user_feature_flags[user_feature] = (
                True
                if user_feature in args.user_feature_flags
                else user_feature_flags_controls.standard_flag_for(user_feature)
            )

        workspace_feature_flags = {}
        for workspace_feature in WorkspaceFeature:
            workspace_feature_flags[workspace_feature] = (
                True
                if workspace_feature in args.workspace_feature_flags
                else workspace_feature_flags_controls.standard_flag_for(
                    workspace_feature
                )
            )

        async with self._domain_storage_engine.get_unit_of_work() as uow:
            new_user = User.new_user(
                ctx=context.domain_context,
                email_address=args.user_email_address,
                name=args.user_name,
                timezone=args.user_timezone,
                feature_flag_controls=user_feature_flags_controls,
                feature_flags=user_feature_flags,
            )
            new_user = await uow.repository_for(User).create(new_user)

            new_auth, new_recovery_token = Auth.new_auth(
                context.domain_context,
                user_ref_id=new_user.ref_id,
                password=args.auth_password,
                password_repeat=args.auth_password_repeat,
            )
            new_auth = await uow.repository_for(Auth).create(new_auth)

            new_score_log = ScoreLog.new_score_log(
                ctx=context.domain_context,
                user_ref_id=new_user.ref_id,
            )
            new_score_log = await uow.score_log_repository.create(new_score_log)

            new_workspace = Workspace.new_workspace(
                ctx=context.domain_context,
                name=args.workspace_name,
                feature_flag_controls=workspace_feature_flags_controls,
                feature_flags=workspace_feature_flags,
            )
            new_workspace = await uow.workspace_repository.create(new_workspace)

            new_vacation_collection = VacationCollection.new_vacation_collection(
                ctx=context.domain_context,
                workspace_ref_id=new_workspace.ref_id,
            )
            new_vacation_collection = await uow.vacation_collection_repository.create(
                new_vacation_collection,
            )

            new_project_collection = ProjectCollection.new_project_collection(
                ctx=context.domain_context,
                workspace_ref_id=new_workspace.ref_id,
            )
            new_project_collection = await uow.project_collection_repository.create(
                new_project_collection,
            )

            new_default_project = Project.new_project(
                ctx=context.domain_context,
                project_collection_ref_id=new_project_collection.ref_id,
                name=args.workspace_first_project_name,
            )
            new_default_project = await uow.project_repository.create(
                new_default_project,
            )

            new_workspace = new_workspace.change_default_project(
                ctx=context.domain_context,
                default_project_ref_id=new_default_project.ref_id,
            )
            await uow.workspace_repository.save(new_workspace)

            new_inbox_task_collection = InboxTaskCollection.new_inbox_task_collection(
                ctx=context.domain_context,
                workspace_ref_id=new_workspace.ref_id,
            )
            new_inbox_task_collection = (
                await uow.inbox_task_collection_repository.create(
                    new_inbox_task_collection,
                )
            )

            new_habit_collection = HabitCollection.new_habit_collection(
                ctx=context.domain_context,
                workspace_ref_id=new_workspace.ref_id,
            )
            new_habit_collection = await uow.habit_collection_repository.create(
                new_habit_collection,
            )

            new_chore_collection = ChoreCollection.new_chore_collection(
                ctx=context.domain_context,
                workspace_ref_id=new_workspace.ref_id,
            )
            new_chore_collection = await uow.chore_collection_repository.create(
                new_chore_collection,
            )

            new_big_plan_collection = BigPlanCollection.new_big_plan_collection(
                ctx=context.domain_context,
                workspace_ref_id=new_workspace.ref_id,
            )
            new_big_plan_collection = await uow.big_plan_collection_repository.create(
                new_big_plan_collection,
            )

            journal_collection = JournalCollection.new_journal_collection(
                ctx=context.domain_context,
                workspace_ref_id=new_workspace.ref_id,
                periods={RecurringTaskPeriod.WEEKLY},
                writing_task_eisen=Eisen.IMPORTANT,
                writing_task_difficulty=Difficulty.MEDIUM,
                writing_project_ref_id=new_default_project.ref_id,
            )
            journal_collection = await uow.journal_collection_repository.create(
                journal_collection,
            )

            new_doc_collection = DocCollection.new_doc_collection(
                ctx=context.domain_context,
                workspace_ref_id=new_workspace.ref_id,
            )
            new_doc_collection = await uow.doc_collection_repository.create(
                new_doc_collection
            )

            new_smart_list_collection = SmartListCollection.new_smart_list_collection(
                ctx=context.domain_context,
                workspace_ref_id=new_workspace.ref_id,
            )
            new_smart_list_collection = (
                await uow.smart_list_collection_repository.create(
                    new_smart_list_collection,
                )
            )

            new_metric_collection = MetricCollection.new_metric_collection(
                ctx=context.domain_context,
                workspace_ref_id=new_workspace.ref_id,
                collection_project_ref_id=new_default_project.ref_id,
            )
            new_metric_collection = await uow.metric_collection_repository.create(
                new_metric_collection,
            )

            new_person_collection = PersonCollection.new_person_collection(
                ctx=context.domain_context,
                workspace_ref_id=new_workspace.ref_id,
                catch_up_project_ref_id=new_default_project.ref_id,
            )
            new_person_collection = await uow.person_collection_repository.create(
                new_person_collection,
            )

            new_push_integration_group = (
                PushIntegrationGroup.new_push_integration_group(
                    ctx=context.domain_context,
                    workspace_ref_id=new_workspace.ref_id,
                )
            )
            new_push_integration_group = (
                await uow.push_integration_group_repository.create(
                    new_push_integration_group,
                )
            )

            new_slack_task_collection = SlackTaskCollection.new_slack_task_collection(
                ctx=context.domain_context,
                push_integration_group_ref_id=new_push_integration_group.ref_id,
                generation_project_ref_id=new_default_project.ref_id,
            )
            new_slack_task_collection = (
                await uow.slack_task_collection_repository.create(
                    new_slack_task_collection,
                )
            )

            new_email_task_collection = EmailTaskCollection.new_email_task_collection(
                ctx=context.domain_context,
                push_integration_group_ref_id=new_push_integration_group.ref_id,
                generation_project_ref_id=new_default_project.ref_id,
            )
            new_email_task_collection = (
                await uow.email_task_collection_repository.create(
                    new_email_task_collection,
                )
            )

            new_note_collection = NoteCollection.new_note_collection(
                ctx=context.domain_context,
                workspace_ref_id=new_workspace.ref_id,
            )
            new_note_collection = await uow.note_collection_repository.create(
                new_note_collection
            )

            new_gc_log = GCLog.new_gc_log(
                ctx=context.domain_context,
                workspace_ref_id=new_workspace.ref_id,
            )
            new_gc_log = await uow.gc_log_repository.create(new_gc_log)

            new_gen_log = GenLog.new_gen_log(
                ctx=context.domain_context,
                workspace_ref_id=new_workspace.ref_id,
            )
            new_gen_log = await uow.gen_log_repository.create(new_gen_log)

            new_user_workspace_link = UserWorkspaceLink.new_user_workspace_link(
                ctx=context.domain_context,
                user_ref_id=new_user.ref_id,
                workspace_ref_id=new_workspace.ref_id,
            )
            new_user_workspace_link = await uow.user_workspace_link_repository.create(
                new_user_workspace_link
            )

        async with self._search_storage_engine.get_unit_of_work() as search_uow:
            await search_uow.search_repository.create(
                new_workspace.ref_id, new_default_project
            )

        auth_token = self._auth_token_stamper.stamp_for_general(new_user)

        return InitResult(
            new_user=new_user,
            new_workspace=new_workspace,
            auth_token_ext=auth_token.to_ext(),
            recovery_token=new_recovery_token,
        )
