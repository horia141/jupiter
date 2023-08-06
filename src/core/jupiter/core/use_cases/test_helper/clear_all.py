"""The command for clearing all branch and leaf type entities."""
from dataclasses import dataclass
from typing import Final

from jupiter.core.domain.auth.infra.auth_token_stamper import AuthTokenStamper
from jupiter.core.domain.auth.password_new_plain import PasswordNewPlain
from jupiter.core.domain.auth.password_plain import PasswordPlain
from jupiter.core.domain.big_plans.service.remove_service import BigPlanRemoveService
from jupiter.core.domain.chores.service.remove_service import ChoreRemoveService
from jupiter.core.domain.features import FeatureFlags
from jupiter.core.domain.habits.service.remove_service import HabitRemoveService
from jupiter.core.domain.inbox_tasks.service.remove_service import (
    InboxTaskRemoveService,
)
from jupiter.core.domain.metrics.service.remove_service import MetricRemoveService
from jupiter.core.domain.persons.service.remove_service import PersonRemoveService
from jupiter.core.domain.projects.service.remove_service import ProjectRemoveService
from jupiter.core.domain.push_integrations.email.service.remove_service import (
    EmailTaskRemoveService,
)
from jupiter.core.domain.push_integrations.slack.service.remove_service import (
    SlackTaskRemoveService,
)
from jupiter.core.domain.smart_lists.service.remove_service import (
    SmartListRemoveService,
)
from jupiter.core.domain.storage_engine import DomainStorageEngine, SearchStorageEngine
from jupiter.core.domain.timezone import Timezone
from jupiter.core.domain.user.user_name import UserName
from jupiter.core.domain.vacations.service.remove_service import VacationRemoveService
from jupiter.core.domain.workspaces.workspace_name import WorkspaceName
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.update_action import UpdateAction
from jupiter.core.framework.use_case import (
    ContextProgressReporter,
    MutationUseCaseInvocationRecorder,
    ProgressReporterFactory,
    UseCaseArgsBase,
)
from jupiter.core.use_cases.infra.storage_engine import UseCaseStorageEngine
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCase,
    AppLoggedInUseCaseContext,
)
from jupiter.core.utils.feature_flag_controls import infer_feature_flag_controls
from jupiter.core.utils.global_properties import GlobalProperties
from jupiter.core.utils.time_provider import TimeProvider


@dataclass
class ClearAllArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    user_name: UserName
    user_timezone: Timezone
    auth_current_password: PasswordPlain
    auth_new_password: PasswordNewPlain
    auth_new_password_repeat: PasswordNewPlain
    workspace_name: WorkspaceName
    workspace_default_project_ref_id: EntityId
    workspace_feature_flags: FeatureFlags


class ClearAllUseCase(AppLoggedInMutationUseCase[ClearAllArgs, None]):
    """The command for clearing all branch and leaf type entities."""

    _use_case_storage_engine: Final[UseCaseStorageEngine]
    _global_properties: Final[GlobalProperties]

    def __init__(
        self,
        time_provider: TimeProvider,
        invocation_recorder: MutationUseCaseInvocationRecorder,
        progress_reporter_factory: ProgressReporterFactory[AppLoggedInUseCaseContext],
        auth_token_stamper: AuthTokenStamper,
        domain_storage_engine: DomainStorageEngine,
        search_storage_engine: SearchStorageEngine,
        use_case_storage_engine: UseCaseStorageEngine,
        global_properties: GlobalProperties,
    ) -> None:
        """Constructor."""
        super().__init__(
            time_provider,
            invocation_recorder,
            progress_reporter_factory,
            auth_token_stamper,
            domain_storage_engine,
            search_storage_engine
        )
        self._use_case_storage_engine = use_case_storage_engine
        self._global_properties = global_properties

    async def _perform_mutation(
        self,
        progress_reporter: ContextProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: ClearAllArgs,
    ) -> None:
        """Execute the command's action."""
        user = context.user
        workspace = context.workspace
        feature_flags_controls = infer_feature_flag_controls(self._global_properties)

        async with self._domain_storage_engine.get_unit_of_work() as uow:
            vacation_collection = (
                await uow.vacation_collection_repository.load_by_parent(
                    workspace.ref_id,
                )
            )
            project_collection = await uow.project_collection_repository.load_by_parent(
                workspace.ref_id,
            )
            inbox_task_collection = (
                await uow.inbox_task_collection_repository.load_by_parent(
                    workspace.ref_id,
                )
            )
            habit_collection = await uow.habit_collection_repository.load_by_parent(
                workspace.ref_id,
            )
            chore_collection = await uow.chore_collection_repository.load_by_parent(
                workspace.ref_id,
            )
            big_plan_collection = (
                await uow.big_plan_collection_repository.load_by_parent(
                    workspace.ref_id,
                )
            )
            smart_list_collection = (
                await uow.smart_list_collection_repository.load_by_parent(
                    workspace.ref_id,
                )
            )
            metric_collection = await uow.metric_collection_repository.load_by_parent(
                workspace.ref_id,
            )
            person_collection = await uow.person_collection_repository.load_by_parent(
                workspace.ref_id,
            )
            push_integration_group = (
                await uow.push_integration_group_repository.load_by_parent(
                    workspace.ref_id,
                )
            )
            slack_task_collection = (
                await uow.slack_task_collection_repository.load_by_parent(
                    push_integration_group.ref_id,
                )
            )
            email_task_collection = (
                await uow.email_task_collection_repository.load_by_parent(
                    push_integration_group.ref_id,
                )
            )

        async with progress_reporter.section("Resseting user"):
            async with progress_reporter.start_updating_entity(
                "user", user.ref_id, str(user.name)
            ) as entity_reporter:
                async with self._domain_storage_engine.get_unit_of_work() as uow:
                    user = user.update(
                        name=UpdateAction.change_to(args.user_name),
                        timezone=UpdateAction.change_to(args.user_timezone),
                        source=EventSource.CLI,
                        modification_time=self._time_provider.get_current_time(),
                    )
                    await entity_reporter.mark_known_name(str(user.name))
                    await uow.user_repository.save(user)
                    await entity_reporter.mark_local_change()

            async with progress_reporter.start_updating_entity(
                "auth for", user.ref_id, str(user.name)
            ) as entity_reporter:
                async with self._domain_storage_engine.get_unit_of_work() as uow:
                    auth = await uow.auth_repository.load_by_parent(
                        parent_ref_id=user.ref_id
                    )
                    auth = auth.change_password(
                        current_password=args.auth_current_password,
                        new_password=args.auth_new_password,
                        new_password_repeat=args.auth_new_password_repeat,
                        source=EventSource.CLI,
                        modification_time=self._time_provider.get_current_time(),
                    )
                    await uow.auth_repository.save(auth)
                    await entity_reporter.mark_local_change()

        async with progress_reporter.section("Resetting workspace"):
            async with progress_reporter.start_updating_entity(
                "workspace",
                workspace.ref_id,
                str(workspace.name),
            ) as entity_reporter:
                async with self._domain_storage_engine.get_unit_of_work() as uow:
                    default_project = await uow.project_repository.load_by_id(
                        args.workspace_default_project_ref_id,
                    )

                    workspace = workspace.update(
                        name=UpdateAction.change_to(args.workspace_name),
                        source=EventSource.CLI,
                        modification_time=self._time_provider.get_current_time(),
                    )
                    await entity_reporter.mark_known_name(str(workspace.name))

                    workspace = workspace.change_default_project(
                        default_project_ref_id=default_project.ref_id,
                        source=EventSource.CLI,
                        modification_time=self._time_provider.get_current_time(),
                    )
                    workspace = workspace.change_feature_flags(
                        feature_flag_controls=feature_flags_controls,
                        feature_flags=args.workspace_feature_flags,
                        source=EventSource.CLI,
                        modification_time=self._time_provider.get_current_time(),
                    )

                    await uow.workspace_repository.save(workspace)
                    await entity_reporter.mark_local_change()

        async with progress_reporter.section("Clearing vacations"):
            async with self._domain_storage_engine.get_unit_of_work() as uow:
                all_vacations = await uow.vacation_repository.find_all(
                    parent_ref_id=vacation_collection.ref_id,
                    allow_archived=True,
                )

            vacation_remove_service = VacationRemoveService(
                self._domain_storage_engine,
            )
            for vacation in all_vacations:
                await vacation_remove_service.do_it(progress_reporter, vacation)

        async with progress_reporter.section("Clearing projects"):
            async with self._domain_storage_engine.get_unit_of_work() as uow:
                all_projects = await uow.project_repository.find_all(
                    parent_ref_id=project_collection.ref_id,
                    allow_archived=True,
                )

            project_remove_service = ProjectRemoveService(
                EventSource.CLI,
                self._time_provider,
                self._domain_storage_engine,
            )
            for project in all_projects:
                if project.ref_id == args.workspace_default_project_ref_id:
                    continue
                await project_remove_service.do_it(
                    progress_reporter, workspace, project.ref_id
                )

        async with progress_reporter.section("Clearing habits"):
            async with self._domain_storage_engine.get_unit_of_work() as uow:
                all_habits = await uow.habit_repository.find_all(
                    parent_ref_id=habit_collection.ref_id,
                    allow_archived=True,
                )
            habit_remove_service = HabitRemoveService(
                self._domain_storage_engine,
            )
            for habit in all_habits:
                await habit_remove_service.remove(progress_reporter, habit.ref_id)

        async with progress_reporter.section("Clearing chores"):
            async with self._domain_storage_engine.get_unit_of_work() as uow:
                all_chores = await uow.chore_repository.find_all(
                    parent_ref_id=chore_collection.ref_id,
                    allow_archived=True,
                )
            chore_remove_service = ChoreRemoveService(
                self._domain_storage_engine,
            )
            for chore in all_chores:
                await chore_remove_service.remove(progress_reporter, chore.ref_id)

        async with progress_reporter.section("Clearing big plans"):
            async with self._domain_storage_engine.get_unit_of_work() as uow:
                all_big_plans = await uow.big_plan_repository.find_all(
                    parent_ref_id=big_plan_collection.ref_id,
                    allow_archived=True,
                )
            big_plan_remove_service = BigPlanRemoveService(
                self._domain_storage_engine,
            )
            for big_plan in all_big_plans:
                await big_plan_remove_service.remove(
                    progress_reporter,
                    workspace,
                    big_plan.ref_id,
                )

        async with progress_reporter.section("Clearing smart lists"):
            async with self._domain_storage_engine.get_unit_of_work() as uow:
                all_smart_lists = await uow.smart_list_repository.find_all(
                    parent_ref_id=smart_list_collection.ref_id,
                    allow_archived=True,
                )
            smart_list_remove_service = SmartListRemoveService(
                self._domain_storage_engine,
            )
            for smart_list in all_smart_lists:
                await smart_list_remove_service.execute(
                    progress_reporter,
                    smart_list_collection,
                    smart_list,
                )

        async with progress_reporter.section("Clearing metrics"):
            async with self._domain_storage_engine.get_unit_of_work() as uow:
                all_metrics = await uow.metric_repository.find_all(
                    parent_ref_id=metric_collection.ref_id,
                    allow_archived=True,
                )

                metric_collection = metric_collection.change_collection_project(
                    collection_project_ref_id=default_project.ref_id,
                    source=EventSource.CLI,
                    modified_time=self._time_provider.get_current_time(),
                )

                await uow.metric_collection_repository.save(metric_collection)

            metric_remove_service = MetricRemoveService(
                self._domain_storage_engine,
            )
            for metric in all_metrics:
                await metric_remove_service.execute(
                    progress_reporter,
                    workspace,
                    metric_collection,
                    metric,
                )

        async with progress_reporter.section("Clearing person"):
            async with self._domain_storage_engine.get_unit_of_work() as uow:
                all_persons = await uow.person_repository.find_all(
                    parent_ref_id=person_collection.ref_id,
                    allow_archived=True,
                )

                person_collection = person_collection.change_catch_up_project(
                    catch_up_project_ref_id=default_project.ref_id,
                    source=EventSource.CLI,
                    modified_time=self._time_provider.get_current_time(),
                )

                await uow.person_collection_repository.save(person_collection)

            person_remove_service = PersonRemoveService(
                self._domain_storage_engine,
            )
            for person in all_persons:
                await person_remove_service.do_it(
                    progress_reporter,
                    person_collection,
                    person,
                )

        async with progress_reporter.section("Clearing Slack tasks"):
            async with self._domain_storage_engine.get_unit_of_work() as uow:
                all_slack_tasks = await uow.slack_task_repository.find_all(
                    parent_ref_id=slack_task_collection.ref_id,
                    allow_archived=True,
                )
                slack_task_collection = slack_task_collection.change_generation_project(
                    generation_project_ref_id=default_project.ref_id,
                    source=EventSource.CLI,
                    modified_time=self._time_provider.get_current_time(),
                )

                await uow.slack_task_collection_repository.save(slack_task_collection)

            slack_task_remove_service = SlackTaskRemoveService(
                self._domain_storage_engine,
            )
            for slack_task in all_slack_tasks:
                await slack_task_remove_service.do_it(progress_reporter, slack_task)

        async with progress_reporter.section("Clearing email tasks"):
            async with self._domain_storage_engine.get_unit_of_work() as uow:
                all_email_tasks = await uow.email_task_repository.find_all(
                    parent_ref_id=email_task_collection.ref_id,
                    allow_archived=True,
                )
                email_task_collection = email_task_collection.change_generation_project(
                    generation_project_ref_id=default_project.ref_id,
                    source=EventSource.CLI,
                    modified_time=self._time_provider.get_current_time(),
                )

                await uow.email_task_collection_repository.save(email_task_collection)

            email_task_remove_service = EmailTaskRemoveService(
                self._domain_storage_engine,
            )
            for email_task in all_email_tasks:
                await email_task_remove_service.do_it(progress_reporter, email_task)

        async with progress_reporter.section("Clearing inbox tasks"):
            async with self._domain_storage_engine.get_unit_of_work() as uow:
                all_inbox_tasks = await uow.inbox_task_repository.find_all(
                    parent_ref_id=inbox_task_collection.ref_id,
                    allow_archived=True,
                )
            inbox_task_remove_service = InboxTaskRemoveService(
                self._domain_storage_engine,
            )
            for inbox_task in all_inbox_tasks:
                await inbox_task_remove_service.do_it(progress_reporter, inbox_task)

        async with progress_reporter.section("Clearing use case invocation records"):
            async with self._use_case_storage_engine.get_unit_of_work() as uow:
                await uow.mutation_use_case_invocation_record_repository.clear_all()
