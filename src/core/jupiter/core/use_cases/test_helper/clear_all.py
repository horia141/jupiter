"""The command for clearing all branch and leaf type entities."""

from jupiter.core.domain.concept.auth.auth import Auth
from jupiter.core.domain.concept.auth.password_new_plain import PasswordNewPlain
from jupiter.core.domain.concept.auth.password_plain import PasswordPlain
from jupiter.core.domain.concept.journals.journal_collection import JournalCollection
from jupiter.core.domain.concept.metrics.metric_collection import MetricCollection
from jupiter.core.domain.concept.persons.person_collection import PersonCollection
from jupiter.core.domain.concept.projects.project import Project, ProjectRepository
from jupiter.core.domain.concept.projects.project_collection import ProjectCollection
from jupiter.core.domain.concept.projects.project_name import ProjectName
from jupiter.core.domain.concept.push_integrations.email.email_task_collection import (
    EmailTaskCollection,
)
from jupiter.core.domain.concept.push_integrations.group.push_integration_group import (
    PushIntegrationGroup,
)
from jupiter.core.domain.concept.push_integrations.slack.slack_task_collection import (
    SlackTaskCollection,
)
from jupiter.core.domain.concept.time_plans.time_plan_domain import TimePlanDomain
from jupiter.core.domain.concept.time_plans.time_plan_generation_approach import TimePlanGenerationApproach
from jupiter.core.domain.concept.user.user import User
from jupiter.core.domain.concept.user.user_name import UserName
from jupiter.core.domain.concept.workspaces.workspace import Workspace
from jupiter.core.domain.concept.workspaces.workspace_name import WorkspaceName
from jupiter.core.domain.core.difficulty import Difficulty
from jupiter.core.domain.core.eisen import Eisen
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.domain.core.timezone import Timezone
from jupiter.core.domain.env import Env
from jupiter.core.domain.features import UserFeature, WorkspaceFeature
from jupiter.core.domain.infra.generic_root_remover import generic_root_remover
from jupiter.core.framework.update_action import UpdateAction
from jupiter.core.framework.use_case import (
    ProgressReporter,
)
from jupiter.core.framework.use_case_io import UseCaseArgsBase, use_case_args
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCase,
    AppLoggedInMutationUseCaseContext,
    mutation_use_case,
)
from jupiter.core.utils.feature_flag_controls import infer_feature_flag_controls


@use_case_args
class ClearAllArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    user_name: UserName
    user_timezone: Timezone
    user_feature_flags: set[UserFeature] | None
    auth_current_password: PasswordPlain
    auth_new_password: PasswordNewPlain
    auth_new_password_repeat: PasswordNewPlain
    workspace_name: WorkspaceName
    workspace_root_project_name: ProjectName
    workspace_feature_flags: set[WorkspaceFeature] | None


@mutation_use_case(exclude_env=[Env.PRODUCTION])
class ClearAllUseCase(AppLoggedInMutationUseCase[ClearAllArgs, None]):
    """The command for clearing all branch and leaf type entities."""

    async def _perform_mutation(
        self,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: ClearAllArgs,
    ) -> None:
        """Execute the command's action."""
        user = context.user
        workspace = context.workspace

        async with self._domain_storage_engine.get_unit_of_work() as uow:
            (
                user_feature_flags_controls,
                workspace_feature_flags_controls,
            ) = infer_feature_flag_controls(self._global_properties)

            project_collection = await uow.get_for(ProjectCollection).load_by_parent(
                workspace.ref_id,
            )
            metric_collection = await uow.get_for(MetricCollection).load_by_parent(
                workspace.ref_id,
            )
            person_collection = await uow.get_for(PersonCollection).load_by_parent(
                workspace.ref_id,
            )
            push_integration_group = await uow.get_for(
                PushIntegrationGroup
            ).load_by_parent(
                workspace.ref_id,
            )
            slack_task_collection = await uow.get_for(
                SlackTaskCollection
            ).load_by_parent(
                push_integration_group.ref_id,
            )
            email_task_collection = await uow.get_for(
                EmailTaskCollection
            ).load_by_parent(
                push_integration_group.ref_id,
            )

            async with progress_reporter.section("Setting things back to default"):
                user = user.update(
                    ctx=context.domain_context,
                    name=UpdateAction.change_to(args.user_name),
                    timezone=UpdateAction.change_to(args.user_timezone),
                )

                if args.user_feature_flags is not None:
                    user_feature_flags = {}
                    for user_feature in UserFeature:
                        user_feature_flags[user_feature] = (
                            user_feature in args.user_feature_flags
                        )

                    user = user.change_feature_flags(
                        ctx=context.domain_context,
                        feature_flag_controls=user_feature_flags_controls,
                        feature_flags=user_feature_flags,
                    )

                await uow.get_for(User).save(user)

                auth = await uow.get_for(Auth).load_by_parent(parent_ref_id=user.ref_id)
                auth = auth.change_password(
                    ctx=context.domain_context,
                    current_password=args.auth_current_password,
                    new_password=args.auth_new_password,
                    new_password_repeat=args.auth_new_password_repeat,
                )
                await uow.get_for(Auth).save(auth)

                workspace = workspace.update(
                    ctx=context.domain_context,
                    name=UpdateAction.change_to(args.workspace_name),
                )

                if args.workspace_feature_flags is not None:
                    workspace_feature_flags = {}
                    for workspace_feature in WorkspaceFeature:
                        workspace_feature_flags[workspace_feature] = (
                            workspace_feature in args.workspace_feature_flags
                        )

                    workspace = workspace.change_feature_flags(
                        ctx=context.domain_context,
                        feature_flag_controls=workspace_feature_flags_controls,
                        feature_flags=workspace_feature_flags,
                    )

                await uow.get_for(Workspace).save(workspace)

                root_project = await uow.get(ProjectRepository).load_root_project(
                    project_collection.ref_id
                )
                root_project = root_project.update(
                    ctx=context.domain_context,
                    name=UpdateAction.change_to(args.workspace_root_project_name),
                )
                await uow.get_for(Project).save(root_project)

                time_plan_domain = await uow.get_for(TimePlanDomain).load_by_parent(
                    workspace.ref_id
                )
                time_plan_domain = time_plan_domain.update(
                    context.domain_context,
                    periods=UpdateAction.change_to(set()),
                    generation_approach=UpdateAction.change_to(TimePlanGenerationApproach.BOTH_PLAN_AND_TASK),
                    planning_task_project_ref_id=UpdateAction.change_to(
                        root_project.ref_id
                    ),
                    planning_task_eisen=UpdateAction.change_to(Eisen.IMPORTANT),
                    planning_task_difficulty=UpdateAction.change_to(Difficulty.MEDIUM),
                )
                await uow.get_for(TimePlanDomain).save(time_plan_domain)

                journal_collection = await uow.get_for(
                    JournalCollection
                ).load_by_parent(workspace.ref_id)
                journal_collection = journal_collection.change_periods(
                    context.domain_context, periods={RecurringTaskPeriod.WEEKLY}
                ).change_writing_tasks(
                    context.domain_context,
                    writing_task_project_ref_id=UpdateAction.change_to(
                        root_project.ref_id
                    ),
                    writing_task_eisen=UpdateAction.change_to(Eisen.IMPORTANT),
                    writing_task_difficulty=UpdateAction.change_to(Difficulty.MEDIUM),
                )
                await uow.get_for(JournalCollection).save(journal_collection)

                metric_collection = metric_collection.change_collection_project(
                    context.domain_context,
                    collection_project_ref_id=root_project.ref_id,
                )

                person_collection = person_collection.change_catch_up_project(
                    context.domain_context,
                    catch_up_project_ref_id=root_project.ref_id,
                )

                slack_task_collection = slack_task_collection.change_generation_project(
                    context.domain_context,
                    generation_project_ref_id=root_project.ref_id,
                )

                email_task_collection = email_task_collection.change_generation_project(
                    context.domain_context,
                    generation_project_ref_id=root_project.ref_id,
                )

            await generic_root_remover(
                context.domain_context, uow, progress_reporter, User, user.ref_id
            )
            await generic_root_remover(
                context.domain_context,
                uow,
                progress_reporter,
                Workspace,
                workspace.ref_id,
            )

        async with progress_reporter.section("Clearing use case invocation records"):
            async with self._use_case_storage_engine.get_unit_of_work() as uc_uow:
                await uc_uow.mutation_use_case_invocation_record_repository.clear_all(
                    workspace.ref_id
                )

        async with progress_reporter.section("Clearing the search index"):
            async with self._search_storage_engine.get_unit_of_work() as search_uow:
                await search_uow.search_repository.drop(workspace.ref_id)
